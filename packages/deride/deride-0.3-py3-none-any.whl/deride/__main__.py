#! /usr/bin/env python
#
# Copyright (c) 2020 Alberto Mardegan <mardy@users.sourceforge.net>
#
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.


# For python 2.7 compatibility:
from __future__ import print_function

from clang.cindex import Config as ClangConfig
from clang.cindex import AvailabilityKind, CursorKind, TypeKind
from clang.cindex import Index
from clang.cindex import TranslationUnit

from jinja2 import Environment, FileSystemLoader

import logging
import os
import re
import sys

from .includes import IncludePathsExtractor

OperatorNames = {
    ',': 'comma',
    '!': 'logical_not',
    '!=': 'inequality',
    '%': 'modulus',
    '%=': 'modulus_assignment',
    '&': 'address_of_or_bitwise_and',
    '&&': 'logical_and',
    '&=': 'bitwise_and_assignment',
    '()': 'function_call_or_cast',
    '*': 'multiplication_or_dereference',
    '*=': 'multiplication_assignment',
    '+': 'addition_or_unary_plus',
    '++': 'increment1',
    '+=': 'addition_assignment',
    '-': 'subtraction_or_unary_negation',
    '--': 'decrement1',
    '-=': 'subtraction_assignment',
    '->': 'member_selection',
    '->*': 'pointer_to_member_selection',
    '/': 'division',
    '/=': 'division_assignment',
    '<': 'less_than',
    '<<': 'left_shift',
    '<<=': 'left_shift_assignment',
    '<=': 'less_than_or_equal_to',
    '=': 'assignment',
    '==': 'equality',
    '>': 'greater_than',
    '>=': 'greater_than_or_equal_to',
    '>>': 'right_shift',
    '>>=': 'right_shift_assignment',
    '[]': 'array_subscript',
    '^': 'exclusive_or',
    '^=': 'exclusive_or_assignment',
    '|': 'bitwise_inclusive_or',
    '|=': 'bitwise_inclusive_or_assignment',
    '||': 'logical_or',
    '~': 'complement',
}


class MethodMockMode:
    QT_SIGNALS = 0
    GLIBMM_SIGNALS = 1
    VIRTUAL_METHOD = 2
    CALLBACK = 3


class ConcatenationMode:
    CAMELCASE = 0
    UNDERSCORE = 1


class Config:
    def __init__(self):
        self.indent = '    '
        self.mock_mode = MethodMockMode.CALLBACK
        self.concatenation_mode = ConcatenationMode.CAMELCASE
        self.standalone_function_mocker = 'Mock'

    @property
    def mock_using_callbacks(self):
        return self.mock_mode == MethodMockMode.CALLBACK

    @property
    def mock_using_qt_signals(self):
        return self.mock_mode == MethodMockMode.QT_SIGNALS


class Pimpl:
    def __init__(self, var_type=None,
                 use_q_declare_private=False, class_name=None,
                 pointer_template=None, node=None):
        self.extra_mock_includes = []
        if use_q_declare_private:
            self.var_type = class_name + 'Private'
        else:
            self.var_type = var_type if var_type \
                else ('Mock' + class_name + 'Impl')
        self.var_name = 'd'
        self.class_ptr_name = 'pClass'
        self.is_smart_pointer = False
        self.class_name = class_name

    @classmethod
    def from_node(cls, node):
        template = None
        ref = None
        for n in node.get_children():
            if n.kind == CursorKind.TYPE_REF:
                ref = n
            elif n.kind == CursorKind.TEMPLATE_REF:
                template = n.spelling
        if not ref:
            return Pimpl()
        return Pimpl(var_type=ref.type.get_declaration().spelling,
                     pointer_template=template)


class Context:
    def __init__(self, input_header=None, basename=None, pimpl=None,
                 current_class=None):
        self.input_header = input_header
        self.basename = basename
        self.pimpl = pimpl
        self.current_class = current_class


def resolve_typedef(cursor):
    while cursor.kind == CursorKind.TYPEDEF_DECL:
        cursor = cursor.underlying_typedef_type.get_declaration()
    return cursor


def variable_type_is_defined(cursor):
    """ Returns true if the type of the variable is defined; then we cannot use
    it as the type of our mock implementation class. """
    for child in cursor.get_children():
        if child.kind == CursorKind.TYPE_REF:
            ref = resolve_typedef(child.referenced)
            if ref.kind == CursorKind.CLASS_DECL and ref.is_definition():
                return True
    return False


class Node(object):
    def __init__(self, node, parent, context=None, config=None):
        self.node = node
        self.parent = parent
        self.config = config or parent.config
        self.context = context or parent.context
        self.name = node.spelling if node.spelling != '~.hpp' else ''

    def namespaced_child(self, child_name):
        """ Returns the child node name with all namespaces """
        parts = [self.name]
        if child_name:
            parts.append(child_name)
        n = self.parent
        while n:
            if n.name:
                parts.insert(0, n.name)
            n = n.parent
        return '::'.join(parts)

    @property
    def namespaced_name(self):
        """ Returns the node name with all namespaces """
        return self.namespaced_child(None)

    @property
    def namespace(self):
        return self.parent.child_namespace if self.parent else ''

    @property
    def child_namespace(self):
        # classes and other nodes who create a namespace should override this
        return self.namespace

    def fix_case(self, identifier):
        if self.config.concatenation_mode == ConcatenationMode.CAMELCASE:
            parts = [p for p in identifier.split('_') if p != '']
        elif self.config.concatenation_mode == ConcatenationMode.UNDERSCORE:
            parts = [p.lower()
                     for p in re.findAll(r'([A-Z]+[0-9a-z]*)', identifier)
                     if p != '']
        return self.concatenate(*parts)

    def concatenate(self, *args):
        def upper_first(s):
            return s[0].upper() + s[1:]
        if self.config.concatenation_mode == ConcatenationMode.CAMELCASE:
            ret = args[0]
            ret += ''.join([upper_first(s) for s in args[1:]])
        elif self.config.concatenation_mode == ConcatenationMode.UNDERSCORE:
            ret = '_'.join(args)
        return ret

    def __repr__(self):
        return '{} ({})'.format(self.name, self.node.type.spelling)


class Argument(Node):
    def __init__(self, parent, *args):
        super(Argument, self).__init__(parent, *args)
        self.type = self.node.type.spelling
        self.is_blocker = False
        self.is_rvalue_ref = (self.node.type.kind == TypeKind.RVALUEREFERENCE)
        for n in self.node.get_children():
            if n.kind == CursorKind.TYPE_REF:
                # QPrivateSignal is a QObject's private struct created to
                # prevent other classes from emitting the signal. We need to
                # prevent it from being exposed in the API, but we'll create it
                # when emitting the signal.
                decl = n.type.get_declaration()
                if decl.spelling == 'QPrivateSignal':
                    self.is_blocker = True
                    self.name = n.type.spelling + '()'

    def as_parameter(self):
        t = '{}' if not self.is_rvalue_ref else 'std::move({})'
        return t.format(self.name)


class ReturnType(object):
    def __init__(self, vtype):
        self.vtype = vtype
        self.is_void = True if vtype.kind == TypeKind.VOID else False
        self.spelling = vtype.spelling
        self.needs_pointer = False
        if vtype.kind == TypeKind.LVALUEREFERENCE:
            self.needs_pointer = True
            vtype = vtype.get_pointee()
        self.type_name = vtype.spelling


class Callable(Node):
    """ This is the base class for functions and class methods. """

    def __init__(self, node, parent, context=None, config=None):
        super(Callable, self).__init__(node, parent)
        self.compute_unique_name()
        self.ret_type = ReturnType(self.node.result_type)
        self.is_qt_signal = False
        self.args = []
        for n in self.node.get_children():
            if n.kind == CursorKind.PARM_DECL:
                self.args.append(Argument(n, self))
            elif n.kind == CursorKind.ANNOTATE_ATTR:
                if n.spelling == 'qt_signal':
                    self.is_qt_signal = True
        # Fixup missing names
        i = 0
        for a in self.args:
            if not a.name:
                a.name = 'param{}'.format(i)
            i += 1

    @property
    def arg_line(self):
        return ', '.join(['{} {}'.format(a.type, a.name) for a in self.args
                          if not a.is_blocker])

    @property
    def arg_types(self):
        return ', '.join(['{}'.format(a.type) for a in self.args
                          if not a.is_blocker])

    @property
    def arg_names(self):
        return ', '.join([a.as_parameter() for a in self.args])

    def compute_unique_name(self):
        self.unique_name = self.name
        if self.unique_name.startswith('operator'):
            operator = self.unique_name[8:]
            if operator in OperatorNames:
                operator_name_parts = OperatorNames[operator].split('_')
                operator_name_parts.append('operator')
                self.unique_name = self.concatenate(*operator_name_parts)

    def has_return_value(self):
        return self.node.result_type.kind != TypeKind.VOID


class Function(Callable):
    def __init__(self, node, parent):
        super(Function, self).__init__(node, parent)


class MemberVariable(object):
    def __init__(self, type_name, var_name, vtype=None):
        self.var_name = var_name
        self.type_name = type_name
        self.init_value = None
        self.needs_pointer = False

        if vtype:
            if vtype.kind == TypeKind.LVALUEREFERENCE:
                self.needs_pointer = True
                vtype = vtype.get_pointee()
            self.type_name = vtype.spelling

            if self.needs_pointer or vtype.kind == TypeKind.POINTER:
                self.init_value = 'nullptr'

        self.reset_value = self.init_value or '{}'


class Method(Callable):
    def __init__(self, node, parent):
        super(Method, self).__init__(node, parent)
        self.pimpl = self.parent.pimpl
        self.compute_cached_variables()

    def __repr__(self):
        return '{} ({})'.format(self.name, self.namespaced_name)

    def compute_cached_variables(self):
        self.callback_hook_type = 'std::function<{ret_type}({args})>'.format(
            ret_type=self.node.result_type.spelling,
            args=self.arg_types)
        self.callback_hook_name = 'm_{}Cb'.format(self.unique_name)

    def set_overload_suffix(self, suffix):
        self.unique_name = self.unique_name + suffix
        self.compute_cached_variables()

    def get_needed_member_variables(self):
        ret = []
        if not self.ret_type.is_void:
            ret.append(MemberVariable(self.ret_type.vtype.spelling,
                                      f'm_{self.unique_name}Result',
                                      vtype=self.ret_type.vtype))
        if self.config.mock_mode == MethodMockMode.CALLBACK \
                and not self.is_qt_signal:
            ret.append(MemberVariable(self.callback_hook_type,
                                      self.callback_hook_name))
        return ret

    @property
    def is_static(self):
        return self.node.is_static_method()


class Constructor(Method):
    def compute_unique_name(self):
        self.unique_name = 'constructor'

    def compute_cached_variables(self):
        self.callback_type = 'std::function<void({})>'.format(self.arg_types)
        self.callback_name = 'm_{}Cb'.format(self.unique_name)

    def get_needed_member_variables(self, definition=False):
        callback_type = self.callback_type
        if not definition:
            callback_type = 'static ' + callback_type
        return [MemberVariable(callback_type, self.callback_name)]


class Destructor(Method):
    pass


class BaseClass(Node):
    """ This is a base class of the class we want to mock. We need to track
    these classes because if they only have constructors which take parameters,
    we will need to figure out what parameters need to be passed.
    """
    def __init__(self, node, parent):
        for n in node.get_children():
            if n.kind == CursorKind.TYPE_REF:
                node = n.type.get_declaration()
                break
        super(BaseClass, self).__init__(node, parent)
        # TODO


class Class(Node):
    QObjectMethods = ['metaObject', 'qt_metacast', 'qt_metacall',
                      'qt_static_metacall']
    QPimplMethod = 'd_func'

    def __init__(self, node, parent, context=None, config=None):
        super(Class, self).__init__(node, parent, context, config)
        self.mock_name = 'Mock' + self.name
        self.pimpl = None
        method_nodes = []
        constructor_nodes = []
        destructor_nodes = []
        self.base_classes = []
        use_q_declare_private = False
        pimpl_member = None
        for n in node.get_children():
            # Ignore methods marked as `= deleted`
            if n.availability == AvailabilityKind.NOT_AVAILABLE:
                continue
            # Ignore methods marked as ` = default`
            if n.is_default_method():
                continue
            if n.kind == CursorKind.CXX_METHOD:
                if n.spelling in Class.QObjectMethods:
                    continue
                if n.spelling == Class.QPimplMethod:
                    use_q_declare_private = True
                    continue
                # If the method is defined inline, there's nothing to mock
                if n.get_definition() is not None:
                    continue
                method_nodes.append(n)
            elif n.kind == CursorKind.CONSTRUCTOR:
                if n.get_definition() is not None:
                    continue
                constructor_nodes.append(n)
            elif n.kind == CursorKind.DESTRUCTOR:
                if n.get_definition() is not None:
                    continue
                destructor_nodes.append(n)

            # Find a PIMPL pointer: tuple with declaration, type (not defined!)
            # and variable name
            elif n.kind == CursorKind.FIELD_DECL and \
                    not variable_type_is_defined(n):
                pimpl_member = n
            elif n.kind == CursorKind.CXX_BASE_SPECIFIER:
                self.base_classes.append(BaseClass(n, self.parent))

        if use_q_declare_private:
            self.pimpl = Pimpl(use_q_declare_private=True,
                               class_name=self.name,
                               node=pimpl_member)
        elif pimpl_member:
            self.pimpl = Pimpl.from_node(pimpl_member)
        else:
            self.pimpl = Pimpl(class_name=self.name)

        context = self.context

        # Find methods
        self.methods = [Method(n, self) for n in method_nodes]
        if self.config.pattern:
            classes_regex = re.compile(self.config.pattern)
            self.methods = [m for m in self.methods
                            if classes_regex.match(m.namespaced_name)]

        self.constructors = [
            Constructor(n, self) for n in constructor_nodes]
        self.destructors = [
            Destructor(n, self) for n in destructor_nodes]

        overloaded_methods = self.find_overloaded_methods()
        for methods in overloaded_methods.values():
            for i, m in enumerate(methods):
                m.set_overload_suffix(str(i))

    @property
    def child_namespace(self):
        if self.namespace:
            return '{}::{}'.format(self.namespace, self.name)
        else:
            return self.name

    def find_overloaded_methods(self):
        overloaded_methods = {}
        for m in self.methods + self.constructors:
            overloads = overloaded_methods.setdefault(m.unique_name, [])
            overloads.append(m)
        return {k: v for k, v in overloaded_methods.items() if len(v) > 1}


class Namespace(Node):
    def __init__(self, node, parent, context=None, config=None):
        super(Namespace, self).__init__(node, parent, context, config)
        namespace_nodes, class_nodes, function_nodes = \
            self.mockable_nodes(node)
        self.namespaces = [Namespace(n, self) for n in namespace_nodes]
        self.classes = [Class(n, self) for n in class_nodes]
        self.functions = [Function(n, self) for n in function_nodes]
        # Filter out classes with no methods
        self.classes = [c for c in self.classes if c.methods]

        # Filter out namespaces with no classes or functions
        self.namespaces = [n for n in self.namespaces
                           if n.classes or n.functions]
        if self.classes:
            log.debug('Found classes: {}'.format(self.classes))
        if self.namespaces:
            log.debug('Found namespaces: {}'.format(self.namespaces))
        if self.functions:
            log.debug('Found functions: {}'.format(self.functions))

    def mockable_nodes(self, parent_node):
        basenames = [os.path.basename(f) for f in self.config.files]
        pattern_regex = re.compile(self.config.pattern) \
            if self.config.pattern else None
        classes = []
        functions = []
        namespaces = []
        for n in parent_node.get_children():
            # TODO: if config.pattern is given, we must filter the nodes
            # according to it.
            # Otherwise just exclude definitions not found in the input include
            # files.
            if self.config.pattern:
                namespaced_name = self.namespaced_child(n.spelling)
                if not pattern_regex.search(namespaced_name):
                    continue
            elif os.path.basename(n.location.file.name) not in basenames:
                continue
            if n.kind == CursorKind.CLASS_DECL:
                if not n.is_definition():
                    continue
                classes.append(n)
            elif n.kind in (CursorKind.NAMESPACE,
                            CursorKind.UNEXPOSED_DECL):
                if not n.is_definition():
                    continue
                namespaces.append(n)
            elif n.kind == CursorKind.FUNCTION_DECL:
                functions.append(n)

        return namespaces, classes, functions


class InputTranslationUnit(Namespace):
    def __init__(self, node, context, config):
        super(InputTranslationUnit, self).__init__(node, None, context, config)

    def generate_mock(self, indent_level=0):
        if not self.functions \
                and not self.classes \
                and not self.namespaces:
            return ''
        return j2_env.get_template('mock_cpp.h.j2').render(
            config=self.config,
            context=self.context,
            namespaces=[self])

    def generate_implementation(self, indent_level=0):
        return j2_env.get_template('mock_cpp.cpp.j2').render(
            config=self.config,
            context=self.context,
            namespaces=[self])


def traverse(node, level=0):
    print('%s %-35s %-20s %-10s [%-6s:%s - %-6s:%s] %s %s ' % (' ' * level,
          node.kind, node.spelling, node.type.spelling, node.extent.start.line,
          node.extent.start.column, node.extent.end.line,
          node.extent.end.column, node.location.file, ''))
    if node.kind == CursorKind.CALL_EXPR:
        print('Call expression')
        for arg in node.get_arguments():
            print("ARG=%s %s" % (arg.kind, arg.spelling))

    for child in node.get_children():
        traverse(child, level+2)


def process_include(idx, input_file, config):
    if config.basepath and input_file.startswith(config.basepath):
        strip_index = len(config.basepath)
        relative_input_file = input_file[strip_index:].lstrip('/')
    else:
        relative_input_file = input_file

    includes = [config.basepath] if config.basepath else []
    includes += config.includes
    include_args = [('-I' + inc) for inc in includes]
    include_extractor = IncludePathsExtractor('c++')
    include_args += include_extractor.clang_args
    options = TranslationUnit.PARSE_INCOMPLETE
    tmp_file = b"~.hpp"
    tmp_file_contents = """\
        #define QT_ANNOTATE_ACCESS_SPECIFIER(x) __attribute__((annotate(#x)))
        #include "{include}"
        """.format(include=relative_input_file)
    tu = idx.parse(tmp_file,
                   unsaved_files=[(tmp_file, tmp_file_contents)],
                   args=include_args + ['--language', 'c++', '-fPIC'],
                   options=options)
    for diagnostic in tu.diagnostics:
        print(str(diagnostic), sep='aa', file=sys.stderr)
    c = tu.cursor
    # traverse(c)

    basename = config.prefix + \
        os.path.splitext(os.path.basename(input_file))[0]
    if config.output:
        output_file_no_ext = os.path.join(config.output, basename)
    else:
        output_file_no_ext = basename
    context = Context(basename=basename, input_header=relative_input_file)
    t = InputTranslationUnit(c, context, config)
    with open(output_file_no_ext + '.h', 'w') as f:
        f.write(t.generate_mock())
    with open(output_file_no_ext + '.cpp', 'w') as f:
        f.write(t.generate_implementation())


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', action='store',
                        help="Path for output file")
    parser.add_argument('-p', '--prefix', action='store', default='mock_',
                        help="Prefix to be added to output file names")
    parser.add_argument(
        '--pattern', action='store',
        help="""Regular expression matching classes to be extracted. By
            default, deride will extract all classes defined in the input
            header file""")
    parser.add_argument('-l', '--libclang', action='store',
                        help="Name or path of libclang")
    parser.add_argument(
        '-I', '--include', action='append', default=[],
        help="""Additional include paths needed for resolving the symbols used
            in the header (can be used multiple times)""")
    parser.add_argument(
        '-b', '--basepath', action='store',
        help="""Path relative to which the include files will be resolved.
            This path is implicitly added to the include path.""")
    parser.add_argument(
        '--debug', action='store_true',
        help="""Print debug output""")
    parser.add_argument(
        'files', action='append',
        help="""The include file containing the class(es) whose mocks should
            be generated""")
    args = parser.parse_args()

    debug_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=debug_level)

    if args.libclang:
        ClangConfig.set_library_file(args.libclang)

    idx = Index.create(excludeDecls=True)

    config = Config()
    config.cmdline = ' '.join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    config.files = args.files
    config.basepath = args.basepath
    config.includes = args.include
    config.output = args.output
    config.prefix = args.prefix
    config.pattern = args.pattern
    for input_file in config.files:
        process_include(idx, input_file, config)


log = logging.getLogger("Deride")
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
j2_env = Environment(loader=FileSystemLoader(THIS_DIR + "/templates/"),
                     lstrip_blocks=True,
                     trim_blocks=True)

if __name__ == "__main__":
    sys.exit(main())

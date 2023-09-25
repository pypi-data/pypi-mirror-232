#
# Copyright (c) 2023 Alberto Mardegan <mardy@users.sourceforge.net>
#
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import logging
import subprocess


log = logging.getLogger("Deride")


class IncludePathsExtractor:
    def __init__(self, language):
        output = subprocess.check_output([
            'gcc', '-Wp,-v', '-x', language, '-', '-fsyntax-only'
        ], input='', stderr=subprocess.STDOUT)
        lines = output.split(b'\n')
        self.system_includes = []
        for line in lines:
            line = line.strip()
            if line.startswith(b'/'):
                self.system_includes.append(line.decode('utf-8'))

    @property
    def clang_args(self):
        args = []
        for include in self.system_includes:
            args += ['-isystem', include]
        return args

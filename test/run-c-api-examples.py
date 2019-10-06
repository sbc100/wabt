#!/usr/bin/env python
#
# Copyright 2016 WebAssembly Community Group participants
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function
import argparse

import os
import subprocess
import sys

ALL_EXAMPLES = [
    'callback',
    'finalize',
    'global',
    'hello',
    'hostref',
    'memory',
    'multi',
    'reflect',
    'serialize',
    'start',
    'table',
    'threads',
    'trap',
]

# We don't currently yet support shared modules which is required for threads.
SKIP_EXAMPLES = [
  'threads', # We don't yet support threads
  'finalize', # This test is really slow
]


def run_test(test_exe):
    print('Running.. %s' % test_exe)
    proc = subprocess.Popen([test_exe], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = proc.communicate()
    if proc.returncode == 0:
        return 0
    print("Failed with returncode=%d" % proc.returncode)
    print(stdout)
    print('FAIL(%d): %s' % (proc.returncode, test_exe))
    return 1


def error(msg):
    print(msg)
    sys.exit(1)


def check_for_missing(found):
    # Check that all the expected examples are found

    basenames = [os.path.splitext(f)[0] for f in found]
    for e in ALL_EXAMPLES:
        if e not in basenames:
            error('Example binary not found: %s' % e)
    for e in basenames:
        if e not in ALL_EXAMPLES:
            error('Unexpected example found: %s' % e)



def main():
    print('Running c-api examples..')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(script_dir)
    upstream_dir = os.path.join(root, 'third_party', 'wasm-c-api', 'example')
    examples_found = [f for f in os.listdir(upstream_dir) if os.path.splitext(f)[1] == '.wasm']
    examples_found = [os.path.splitext(f)[0] for f in examples_found]
    check_for_missing(examples_found)

    def should_skip(e):
        return any(e.startswith(skip) for skip in SKIP_EXAMPLES)

    to_run = [e for e in examples_found if not should_skip(e)]

    bindir = os.path.join(root, 'bin', 'c-api-examples')
    os.chdir(bindir)
    count = 0
    fail_count = 0
    for f in to_run:
        exe = os.path.join(bindir, f)
        if not os.path.exists(exe):
            error('test executable not found: %s' % exe)

        count += 1
        if run_test(exe) != 0:
            fail_count += 1

    if fail_count:
        print('[%d/%d] c-api examples failed' % (fail_count, count))
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())

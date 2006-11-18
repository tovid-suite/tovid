#! /usr/bin/env python
# test.py

"""libtovid test script

Execute this script to run tests on the modules in libtovid. These tests
consist of executing each module standalone; it is presumed that each module
to be tested contains at least the following:

  import doctest
  if __name__ == '__main__':
      doctest.testmod(verbose=True)

This causes all the module documentation (namely, the Python code examples
therein) to be verified by executing it through 'doctest'. Modules may contain
additional self-testing procedures, such as comprehensive unit tests.
"""

import os

modules = [\
    'cli.py',
    'config.py',
    'media.py',
    'opts.py',
    'standards.py',
    'stats.py',
    'utils.py']

for mod in modules:
    print "Testing: %s" % mod
    os.system('python %s -v' % mod)

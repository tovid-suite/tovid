#! /usr/bin/env python
# runtest.py

"""libtovid test script

Execute this script to run tests on the modules in libtovid. These tests
consist of executing each libtovid module standalone; it is presumed that
each module to be tested contains at least the following:

    import unittest
    if __name__ == '__main__':
        unittest.main()

which runs unit tests, or:

    import doctest
    if __name__ == '__main__':
        doctest.testmod(verbose=True)

which does an automated verification of the docstrings in each module.

NB -- You're going to get lots of output, so a >log.txt is advised.
"""

import os
import commands
from glob import glob

libtovid_modules = [
    'author.py',
    'cli.py',
    'deps.py',
    'encode.py',
    'filetypes.py',
    'layout.py',
    'media.py',
    'opts.py',
    'standard.py',
    'stats.py',
    'utils.py',
    'xml.py',
]

subdirs = [
    'backend',
    'metagui',
    'render',
    'template',
    'test',
]

subdir_modules = []
for subdir in subdirs:
    subdir_modules.extend(glob('%s/*.py' % subdir))

all_modules = libtovid_modules + subdir_modules

if __name__ == '__main__':
    # Execute each module
    for mod in all_modules:
        print "Testing: %s" % mod
        try:
            print commands.getoutput('python %s' % mod)
        except KeyboardInterrupt:
            print "Test interrupted."
            exit()

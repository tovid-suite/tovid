#! /usr/bin/env python
# install.py

"""Dependency-checker and installer for tovid.
"""

import os
import sys
from libtovid import deps
from libtovid import output as color

if __name__ == '__main__':
    alldeps = deps.all
    alldeps['foo'] = 'http://foo.bar.org/'
    for dep, url in alldeps.items():
        try:
            deps.require(dep, "Installation aborted.", url)
        except:
            pass
        else:
            print color.green("Found:") + dep
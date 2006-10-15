#! /usr/bin/env python
# config.py

"""This module provides functions for loading and saving tovid preferences from
an INI-style configuration file."""

# TODO: Finish writing this module

__all__ = ['load', 'save']

import os
from ConfigParser import ConfigParser

# Default tovid configuration file
_config_file = os.path.expanduser('~/.tovid.config')
# Default configuration
_config_default = {
    'log.dir': '/tmp',
    'default.workdir': '.'
    }

def load(self, filename):
    """Load configuration data from the given file."""
    #infile = open(filename, 'r')
    cp = ConfigParser()
    cp.read(filename)

    for line in infile.readlines():
        argval = line.split('=')
        if len(argval) == 2:
            left, right = argval
            if left == 'WORKING_DIR':
                if right.startswith('~'):
                    self.workdir = os.path.expanduser(right)
                else:
                    self.workdir = os.path.abspath(right)
                # TODO: Also do os.path.expandvars()?
                self.workdir = self.workdir.rstrip('\n')
    
def save(self, filename):
    """Save the current configuration to the given file."""
    pass

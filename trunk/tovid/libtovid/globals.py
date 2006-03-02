#! /usr/bin/env python
# globals.py

__all__ = ['Config']

import os

from libtovid.utils import which

class Config:
    """Borg class for holding global config and user preferences."""
    _shared_state = {}
    initialized = False

    def __init__(self):
        self.__dict__ = self._shared_state
        if not self.initialized:
            self.one_time_init()
            self.initialized = True
        
    def one_time_init(self):
        """Do one-time initialization of class data."""
        self.read_config(os.path.expanduser('~/.tovid/preferences'))
        self.logfile = os.path.abspath('libtovid.log')

    def read_config(self, file):
        """Read configuration from the given file."""
        infile = open(file, 'r')
        for line in infile.readlines():
            argval = line.split('=')
            if len(argval) == 2:
                left, right = argval
                if left == 'WORKING_DIR':
                    if right[0] == '~':
                        self.workdir = os.path.expanduser(right)
                    else:
                        self.workdir = os.path.abspath(right)
                    # TODO: Also do os.path.expandvars()?
                    self.workdir = self.workdir.rstrip('\n')
        
    def save_config(self, file):
        """Save the current configuration to the given file."""
        pass

#! /usr/bin/env python
# globals.py

__all__ = ['Config']

import sys
import re
import string

from libtovid.utils import which

class Config:
    """Borg class for holding global config and user preferences."""
    __shared_state = {}
    initialized = False

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.initialized:
            # Do one-time initialization of class data
            self.check_deps()
            self.initialized = True
        

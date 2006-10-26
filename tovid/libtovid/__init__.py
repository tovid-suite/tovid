#! /usr/bin/env python
# __init__.py

"""Provides a Python interface to the functionality of tovid.
"""

__all__ = [\
    # Subdirectories
    'gui',
    'encoders',
    'render',
    # .py files
    'animation',
    'cli',
    'disc',
    'effect',
    'flipbook',
    'globals',
    'layer',
    'media',
    'menu',
    'opts',
    'stats',
    'standards',
    'tdl',
    'textmenu',
    'utils',
    'video']

import sys
import logging

# Global logger
log = logging.getLogger('libtovid')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stdout))
# TODO: Support logging to a file with a different severity level

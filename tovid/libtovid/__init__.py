#! /usr/bin/env python
# __init__.py

"""Provides a Python interface to the functionality of tovid.
"""

## \mainpage How to use libtovid
# 
# \section intro Introduction
# 
# The classes needed for a developer to use libtovid are mostly:
# 
#  - Layers in layer.py, to put something in your canvas
#  - Effects in effect.py, for several effects, which you can extend
#  - Flipbook for animation
#  - cairo_ module for drawing primitives
#  - Video in video.py, if you want to deal with videos and convert them
#      `-> is that true ?
#  - Tween and Keyframe in animation.py, for key-framing
#
#
# <i>You'll find this page in %libtovid/__init__.py</i>


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

#@+leo-ver=4-thin
#@+node:eric.20090722212922.2510:@shadow __init__.py
"""Backends, which do some task using a command-line program.

This module is split into submodules, each named after the command-line
program they predominantly rely on. Backends which use several of these
submodules may be defined here in ``__init__.py``.
"""

# Submodules
__all__ = [
    'ffmpeg',
    'mpeg2enc',
    'mplayer',
    'mplex',
    'spumux',
    'transcode',
]

#@-node:eric.20090722212922.2510:@shadow __init__.py
#@-leo

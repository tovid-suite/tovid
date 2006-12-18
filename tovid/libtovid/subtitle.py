#! /usr/bin/env python
# subtitle.py

"""This module provides an interface to the subtitling program spumux.

spumux deals with two different kinds of subtitles:

    Image-based, with one or more transparent .png files and button regions
        (used for menu navigational features)
    Text-based, rendering a .sub/.srt/etc. file in a given font and size
        (used for alternate-language dialogue subtitles)

Example usage:

    >>> menu_sub = Subtitle('spu',
            {'highlight': 'highlight.png'})
    >>> mux_subs(menu_sub, 'menu.mpg')

    >>> ja_sub = Subtitle('textsub',
            {'filename': 'japanese.srt', 'characterset': 'UTF-8'})
    >>> mux_subs(ja_sub, 'bebop.mpg')
"""

__all__ = [\
    'Button',
    'Subtitle',
    'get_xml',
    'spumux',
    'add_textsubs']

import sys
import os
import tempfile
# from xml.dom import getDOMImplementation

from libtovid.cli import Command
from libtovid.opts import Option, OptionDict
from libtovid.media import load_media, MediaFile
from libtovid.spumux import Textsub, SPU, Button


###
### TODO: Fix obsoleted stuff below
###




if __name__ == '__main__':
    pass

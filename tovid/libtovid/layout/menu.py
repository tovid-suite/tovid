#! /usr/bin/env python
# menu.py

"""This module provides menu encapsulation and MPEG generation.
"""

__all__ = ['Menu']

from libtovid import log
from libtovid import media
# from libtovid.templates import textmenu

class Menu:
    """A menu for navigating the titles on a video disc.
    """
    def __init__(self, videos, format, tvsys, style):
        """Create a menu linking to the given Videos."""
        self.videos = videos
        self.format = format
        self.tvsys = tvsys
        self.style = style
        # TODO: Remove(?)
        self.parent = None
        self.children = []

    def generate(self, outfile):
        """Generate the Menu, saving to outfile."""
        target = media.standard_media(self.format, self.tvsys)
        target.filename = outfile
        # TODO: Proper safe area. Hardcoded to 90% for now.
        width, height = target.scale
        target.scale = (int(width * 0.9), int(height * 0.9))
        # TODO: Generate menu, using target as output

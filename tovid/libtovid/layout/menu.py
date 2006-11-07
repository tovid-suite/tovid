#! /usr/bin/env python
# menu.py

"""This module provides menu encapsulation and MPEG generation.
"""

__all__ = ['Menu']

# From standard library
import sys
import os
from copy import copy

# From libtovid
from libtovid.opts import Option, OptionDict
from libtovid import textmenu
from libtovid.flipbook import Flipbook
from libtovid import log
from libtovid import standards

class Menu:
    """A menu for navigating the titles on a video disc.

    Menus are generated based on a collection of user-settable options. These
    define the target format, and titles to be listed on the menu, among other
    things such as font, color, and background.
    
    The primary output from a Menu is an .mpg video file suitable for use as
    a video disc navigational menu.
    """
    # Dictionary of valid options with documentation
    optiondefs = [
        Option('out', 'NAME', None,
            """Output prefix or menu name."""),

        Option('titles', '"TITLE" [, "TITLE"]', [],
            """Comma-separated list of quoted titles; these are the titles that
            will be displayed (and linked) from the menu."""),

        Option('format', 'vcd|svcd|dvd', 'dvd',
            """Generate a menu compliant with the specified disc format"""),
        Option('tvsys', 'pal|ntsc', 'ntsc',
            """Make the menu for the specified TV system"""),
        Option('background', 'IMAGE', None,
            """Use IMAGE (in most any graphic format) as a background."""),
        Option('audio', 'AUDIOFILE', None,
            """Use AUDIOFILE for background music while the menu plays."""),
        Option('font', 'FONTNAME', 'Helvetica',
            """Use FONTNAME for the menu text."""),
        Option('fontsize', 'NUM', '24',
            """Use a font size of NUM pixels."""),
        Option('align', 'west|north|east|south|center', 'northwest'),
        Option('textcolor', 'COLOR', 'white',
            """Color of menu text. COLOR may be a hexadecimal triplet (#RRGGBB or
            #RGB), or a color name from 'convert -list color."""),
        Option('highlightcolor', 'COLOR', 'red',
            """Color of menu highlights."""),
        Option('selectcolor', 'COLOR', 'green',
            """Color of menu selections."""),

        # Thumbnail menus and effects
        Option('thumbnails', 'FILE [, FILE ...]', [],
            """Create thumbnails of the provided list of video files, which
            should correspond to the given -titles list."""),
        Option('choices', '[list|thumbnails]', 'list',
                """Display links as a list of titles, or as a grid of labeled
                thumbnail videos."""),
        Option('border', 'NUM', '0',
                """Add a border of NUM pixels around thumbnails."""),
        Option('effects', 'shadow|round|glass [, ...]', [],
                """Add the listed effects to the thumbnails.""")
    ]

    def __init__(self, custom_options=None):
        """Initialize Menu with a string or list of options."""
        self.options = OptionDict(self.optiondefs)
        self.options.override(custom_options)
        self.parent = None
        self.children = []

    def preproc(self):
        width, height = standards.get_resolution(self.options['format'],
                                                 self.options['tvsys'])
        samprate = standards.get_samprate(self.options['format'])

        # Make sure number of thumbs and titles match
        if self.options['thumbnails']:
            numthumbs = len(self.options['thumbnails'])
            numtitles = len(self.options['titles'])
            if numthumbs > numtitles:
                log.error('More thumbnails than titles!')
            elif numthumbs < numtitles:
                log.error('More titles than thumbnails!')

        self.options['samprate'] = samprate
        # TODO: Proper safe area. Hardcoded to 90% for now.
        self.options['expand'] = (width, height)
        self.options['scale'] = (int(width * 0.9), int(height * 0.9))

    def generate(self):
        """Generate the element, and return the filename of the
        resulting menu."""
        self.preproc()
        # TODO: Raise exceptions
        # Generate a menu of the appropriate format
        if self.options['thumbnails']:
            log.error("Not implemented yet. Meanwhile, try 'genvid'.")
        else:
            log.info('Generating a DVD menu with text titles...')
            textmenu.generate(self.options)

#! /usr/bin/env python2.4
# menu.py

__all__ = ['Menu']

import sys
import os
from copy import copy

import libtovid
from libtovid.opts import OptionDef, OptionDict
from libtovid.log import Log
from libtovid import textmenu
from libtovid import thumbmenu

log = Log('menu.py')

class Menu:
    """A menu for navigating the titles on a video disc.

    Menus are generated based on a collection of user-settable options. These
    define the target format, and titles to be listed on the menu, among other
    things such as font, color, and background.
    
    The primary output from a Menu is an .mpg video file suitable for use as
    a video disc navigational menu.
    """
    # Dictionary of valid options with documentation
    optiondefs = {
        'out': OptionDef('out', 'NAME', None,
            """Output prefix or menu name."""),

        'titles': OptionDef('titles', '"TITLE" [, "TITLE"]', [],
            """Comma-separated list of quoted titles; these are the titles that
            will be displayed (and linked) from the menu."""),

        'format': OptionDef('format', 'vcd|svcd|dvd', 'dvd',
            """Generate a menu compliant with the specified disc format"""),
        'tvsys': OptionDef('tvsys', 'pal|ntsc', 'ntsc',
            """Make the menu for the specified TV system"""),
        'background': OptionDef('background', 'IMAGE', None,
            """Use IMAGE (in most any graphic format) as a background."""),
        'audio': OptionDef('audio', 'AUDIOFILE', None,
            """Use AUDIOFILE for background music while the menu plays."""),
        'font':
            OptionDef('font', 'FONTNAME', 'Helvetica',
            """Use FONTNAME for the menu text."""),
        'fontsize':
            OptionDef('fontsize', 'NUM', '24',
            """Use a font size of NUM pixels."""),
        'align':
            OptionDef('align', 'west|north|east|south|center', 'northwest'),
        'textcolor':
            OptionDef('textcolor', 'COLOR', 'white',
            """Color of menu text. COLOR may be a hexadecimal triplet (#RRGGBB or
            #RGB), or a color name from 'convert -list color."""),
        'highlightcolor':
            OptionDef('highlightcolor', 'COLOR', 'red',
            """Color of menu highlights."""),
        'selectcolor':
            OptionDef('selectcolor', 'COLOR', 'green',
            """Color of menu selections."""),

        # Thumbnail menus and effects
        'thumbnails':
            OptionDef('thumbnails', 'FILE [, FILE ...]', [],
            """Create thumbnails of the provided list of video files, which
            should correspond to the given -titles list."""),
        'choices':
            OptionDef('choices', '[list|thumbnails]', 'list',
                """Display links as a list of titles, or as a grid of labeled
                thumbnail videos."""),
        'border':
            OptionDef('border', 'NUM', '0',
                """Add a border of NUM pixels around thumbnails."""),
        'effects':
            OptionDef('effects', 'shadow|round|glass [, ...]', [],
                """Add the listed effects to the thumbnails.""")
    }

    def __init__(self, custom_options=[]):
        """Initialize Menu with a string or list of options."""
        self.options = OptionDict(self.optiondefs)
        self.options.override(custom_options)
        self.parent = None
        self.children = []

    def preproc(self):
        if self.options['format'] == 'dvd':
            width = 720
            samprate = 48000
            if self.options['tvsys'] == 'ntsc':
                height = 480
            else:
                height = 576
        else:
            width = 352
            samprate = 44100
            if self.options['tvsys'] == 'ntsc':
                height = 240
            else:
                height = 288

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
            log.info('Generating a menu with thumbnail videos...')
            thumbmenu.generate(self.options)
        else:
            log.info('Generating a DVD menu with text titles...')
            textmenu.generate(self.options)


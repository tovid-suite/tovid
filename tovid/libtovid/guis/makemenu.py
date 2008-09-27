#! /usr/bin/env python
# makemenu.py

from libtovid.metagui import *

_ntsc = Flag('NTSC', '-ntsc', True)
_ntscfilm = Flag('NTSC Film', '-ntscfilm', False)
_pal = Flag('PAL', '-pal', False)

_dvd = Flag('DVD', '-dvd', True)
_vcd = Flag('VCD', '-vcd', False)
_svcd = Flag('SVCD', '-svcd', False)

_background = Filename('Background image', '-background')
_crop = Flag('Crop', '-crop', True)
_scale = Flag('Scale', '-scale', False)
_audio = Filename('Background audio', '-audio')
_length = Number('Duration', '-length', 30,
    'Menu duration', 1, 600, 'spin', 'seconds')
_menu_title = Text('Menu title', '-menu-title')
_font = Font('Menu font', '-font')
_fontsize = Number('Font size', '-fontsize', 24,
    'Menu font size', 10, 100, 'spin', 'pixels')
_menu_title_fontsize = Number('Title font size', '-menu-title-fontsze', 32,
    'Menu title (heading) font size', 10, 100, 'spin', 'pixels')
_fontdeco = Text('Font decoration', '-fontdeco')
_align = Choice('Text alignment', '-align', 'left',
    'Align/justify the menu text', 'left|center|middle|right')
_textcolor = Color('Menu text color', '-textcolor')

# DVD-only
_button = Text('Button character', '-button', '>',
    'A single character to use for a menu cursor, or one of '
    '"play", "movie", or "utf8 xxxx".')

_highlightcolor = Color('Highlight color', '-highlightcolor')
_selectcolor = Color('Select color', '-selectcolor')
_button_outline = Color('Outline color', '-button-outline')
_button_font = Font('Button font', '-button-font')

_debug = Flag('Debug', '-debug', False)
_nosafearea = Flag('No safe area', '-nosafearea', False)
_overwrite = Flag('Overwrite', '-overwrite', False)
_noask = Flag('No prompting', '-noask', False)
_quiet = Flag('Quiet', '-quiet', False)

TITLES = List("Titles", '', '',
    "Video titles to include on the menu",
    Filename())

OUT_PREFIX = Filename("Output name", '', '',
    "Name of output file (will be given a .mpg extension)",
    'save', "Choose an output name")


def run():
    pass

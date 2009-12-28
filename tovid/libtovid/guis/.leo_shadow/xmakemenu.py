#@+leo-ver=4-thin
#@+node:eric.20090722212922.3287:@shadow makemenu.py
#@+others
#@+node:eric.20090722212922.3288:makemenu declarations
# makemenu.py

from libtovid.metagui import *

# Menu TV system
_ntsc = Flag('NTSC', '-ntsc', True)
_ntscfilm = Flag('NTSC Film', '-ntscfilm', False)
_pal = Flag('PAL', '-pal', False)
TVSYS = FlagGroup('TV system', 'exclusive', _ntsc, _ntscfilm, _pal)

# Menu format
_vcd = Flag('VCD', '-vcd', False)
_svcd = Flag('SVCD', '-svcd', False)
_dvd = Flag('DVD', '-dvd', True,
    'Create a menu in DVD format. Extra features are enabled for DVD menus.',
    enables=['-button', '-button-font', '-button-outline',
        '-highlightcolor', '-selectcolor'])

FORMAT = FlagGroup('Menu format', 'exclusive', _vcd, _svcd, _dvd)

# DVD-only options (enabled by -dvd)
_button = Text('Button character', '-button', '>',
    'A single character to use for a menu cursor, or one of '
    '"play", "movie", or "utf8 xxxx".')

_highlightcolor = Color('Highlight color', '-highlightcolor')
_selectcolor = Color('Select color', '-selectcolor')
_button_outline = Color('Outline color', '-button-outline')
_button_font = Font('Button font', '-button-font')

DVD_ONLY = VPanel('DVD menu elements',
    _button,
    _button_font,
    _button_outline,
    _highlightcolor,
    _selectcolor,
)

# Background
_background = Filename('BG image', '-background')
_crop = Flag('Crop', '-crop', True)
_scale = Flag('Scale', '-scale', False)
_audio = Filename('BG audio', '-audio')
_length = Number('Duration', '-length', 30,
    'Menu duration', 1, 600, 'seconds')
_nosafearea = Flag('No safe area', '-nosafearea', False)

# Fonts
_menu_title = Text('Menu title', '-menu-title')
_font = Font('Menu font', '-font')
_fontsize = Number('Font size', '-fontsize', 24,
    'Menu font size', 10, 100, 'pixels')
_menu_title_fontsize = Number('Title font size', '-menu-title-fontsze', 32,
    'Menu title (heading) font size', 10, 100, 'pixels')
_fontdeco = Text('Font decoration', '-fontdeco')
_align = Choice('Text alignment', '-align', 'left',
    'Align/justify the menu text', 'left|center|middle|right')
_textcolor = Color('Menu text color', '-textcolor')

# Behavior
_debug = Flag('Debug', '-debug', False)
_overwrite = Flag('Overwrite', '-overwrite', False)
_noask = Flag('No prompting', '-noask', False)
_quiet = Flag('Quiet', '-quiet', False)



TITLES = List("Titles", '<titles>', '',
    "Video titles to include on the menu",
    Filename())

OUT_PREFIX = Filename("Output name", '-out', '',
    "Name of output file (will be given a .mpg extension)",
    'save', "Choose an output name")


MAIN = VPanel('Makemenu options',
    HPanel('', FORMAT, DVD_ONLY, TVSYS),
    VPanel('Background',
        _background,
        _audio,
        HPanel('',
            FlagGroup('Fit image', 'exclusive', _crop, _scale),
            _nosafearea,
            _length
        ),
    ),

    _menu_title,
    _menu_title_fontsize,

    _textcolor,
    _font,
    _fontsize,
    _align,
    _fontdeco,

    _debug,
    _overwrite,
    _noask,
    _quiet,

    TITLES,
    OUT_PREFIX,
)

#@-node:eric.20090722212922.3288:makemenu declarations
#@+node:eric.20090722212922.3289:run
def run():
    app = Application('makemenu', MAIN)
    gui = GUI("tovid metagui", 640, 720, app)
    gui.run()

#@-node:eric.20090722212922.3289:run
#@-others
if __name__ == '__main__':
    run()

#@-node:eric.20090722212922.3287:@shadow makemenu.py
#@-leo

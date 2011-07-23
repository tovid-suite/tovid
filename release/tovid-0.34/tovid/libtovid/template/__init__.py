"""This module provides an interface to menu-generation templates.

libtovid.templates should provide an assortment of "plug-in" style templates
for menu generation, and perhaps one day also for disc layout or video
encoding profiles).
"""

__all__ = [
    'Style',
    'textmenu',
    'thumbmenu',
]

class Style:
    """Contains style attributes, including font, color, and alignment."""
    def __init__(self, font='helvetica', fontsize=12, textcolor='white',
                 highlightcolor='green', selectcolor='red', align='center'):
        self.font = font
        self.fontsize = fontsize
        self.textcolor = textcolor
        self.highlightcolor = highlightcolor
        self.selectcolor = selectcolor
        self.align = align


# todisc options
# 
# Style control
# 
# -showcase IMAGE|VIDEO
# -textmenu
# -background IMAGE|VIDEO
# -menu-font
# -menu-fontsize
# -menu-fade
# -thumb-shape
# -3dthumbs
# -thumb-font
# -thumb-fontsize
# -submenu-stroke-color
# -submenu-title-color
# -button-style rect|text|text-rect
# -rotate
# -wave
# -showcase-framestyle none|glass
# -title-color
# -stroke-color
# -highlightcolor
# -selectcolor
# -text-mist
# -text-mist-color
# -text-mist-opacity
# -opacity
# -blur
# -thumb-mist-color
# -thumb-text-color
# -showcase-titles-align
# -tile3x1
# 
# Audio:
# 
# -bgaudio
# -menu-audiolength
# -menu-audio-fade
# -submenu-audio
# -submenu-audiolength
# -submenu-audio-fade
# 
# 
# Other
# 
# -files
# -titles
# -submenus
# -ani-submenus
# -static
# -submneu-titles
# -chapters
# -menu-title
# -menu-length
# -intro VIDEO
# -seek
# -showcase-seek
# -loop
# -playall
# -chain-videos
# -subtitles lang1 lang2 ...
# -audio-lang chan1 chan2 ...
# -aspect
# -widescreen
# 
# Execution control
# 
# -debug
# -noask
# -tovidopts

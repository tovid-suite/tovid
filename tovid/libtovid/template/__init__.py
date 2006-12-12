#! /usr/bin/env python
# __init__.py (template)

"""This module provides an interface to menu-generation templates. There's
currently only textmenu.

libtovid.templates should provide an assortment of "plug-in" style templates
for menu generation, and perhaps one day also for disc layout or video encoding profiles).
"""

__all__ = [\
    'textmenu',
    'Style']

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

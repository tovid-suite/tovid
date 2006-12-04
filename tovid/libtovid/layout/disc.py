#! /usr/bin/env python
# disc.py

__all__ = ['Disc']

import doctest
from libtovid.layout import vcdimager, dvdauthor
"""
A disc may contain:

Videos only (one titleset with N videos)

    ts = Titleset(videos)
    disc.add_titleset(ts)

Videos with a single menu (one titleset with N videos and a TS menu)

    ts = Titleset(videos)
    ts.add_menu()
    disc.add_titleset(ts)

Topmenu/submenus (N titlesets each with a menu, VMGM menu links to them)

    ts1 = Titleset(videos)
    ts2 = Titleset(morevideos)
    ts1.add_menu()
    ts2.add_menu()
    disc.add_titleset(ts1)
    disc.add_titleset(ts2)
"""

class Disc:
    """A video disc containing video titles and optional menus.
    
    Needed for authoring:
        title
        format/tvsys
        top menu
        titlesets
    """
    def __init__(self, name, format, tvsys, videos=[]):
        """Create a Disc with the given properties.
        
            format:   'vcd', 'svcd', or 'dvd'
            tvsys:    'pal' or 'ntsc'
            title:    String containing the title of the disc
            videos:   List of Videos to include on the disc
        """
        self.name = name
        self.format = format
        self.tvsys = tvsys
        self.videos = videos
        self.topmenu = None
        self.menus = []
    
    def generate(self):
        """Author the disc."""
        if self.format == 'dvd':
            xml = vcdimager.get_xml(self)
        elif self.format in ['vcd', 'svcd']:
            xml = dvdauthor.get_xml(self)
        # TODO: Fix output filename
        outfile = open(self.name, 'w')
        outfile.write(xml)
        # TODO: Author generated xml file


if __name__ == '__main__':
    doctest.testmod(verbose=True)

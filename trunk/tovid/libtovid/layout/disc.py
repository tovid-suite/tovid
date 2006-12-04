#! /usr/bin/env python
# disc.py

__all__ = ['Disc']

import doctest
from libtovid.layout import vcdimager, dvdauthor

class Disc:
    """A video disc containing video titles and optional menus.
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

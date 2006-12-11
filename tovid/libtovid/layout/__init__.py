#! /usr/bin/env python
# __init__.py

"""This module provides an interface for structuring the content of video discs.
"""

all = [\
    'Disc',
    'Menu',
    'Video',
    'Group',
    'dvdauthor',
    'vcdimager']

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

from libtovid import media

class Menu:
    """A menu for navigating the titles on a video disc.
    
    Needed for encoding/generation:
        menu title
        output name
        format/tvsys
        video filenames
        video titles
        style
    Needed for authoring:
        videos
    """
    def __init__(self, videos, format, tvsys, style):
        """Create a menu linking to the given Videos."""
        self.videos = videos
        self.format = format
        self.tvsys = tvsys
        self.style = style

    def generate(self, outfile):
        """Generate the Menu, saving to outfile."""
        target = media.standard_media(self.format, self.tvsys)
        target.filename = outfile
        # TODO: Proper safe area. Hardcoded to 90% for now.
        width, height = target.scale
        target.scale = (int(width * 0.9), int(height * 0.9))
        # TODO: Generate menu, using target as output


from libtovid.transcode import encode

class Video:
    """A video title for inclusion on a video disc.

    Needed for encoding:
        input filename
        output name
        format/tvsys
    Needed for authoring:
        output filename
        format/tvsys
        widescreen
        length and/or chapter points
    Needed for menu generation:
        title
        output filename (for generating thumbs)
        widescreen
        chapter points
    """

    def __init__(self, infile, title, format, tvsys):
        self.infile = infile
        self.title = title
        self.format = format
        self.tvsys = tvsys

    def generate(self, outfile, method='ffmpeg'):
        """Generate (encode) the video to the given output filename."""
        encode.encode(self.infile, outfile,
                      self.format, self.tvsys, method)

class Group:
    """A group title for inclusion on a video disc.

    Needed for menu generation:
        title
    """

    def __init__(self, infile, title, format, tvsys):
        self.infile = infile
        self.title = title
        self.format = format
        self.tvsys = tvsys

    def generate(self, outfile, method='ffmpeg'):
        """Generate the group."""
        # TODO: Fixme


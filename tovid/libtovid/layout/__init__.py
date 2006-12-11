#! /usr/bin/env python
# __init__.py

"""This module provides an interface for structuring the content of video discs.

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

all = [\
    'Disc',
    'Menu',
    'Video',
    'Group',
    'dvdauthor',
    'vcdimager']

from libtovid.layout import vcdimager, dvdauthor

all = [\
    'Video',
    'Menu',
    'Titleset',
    'Disc',
    'dvdauthor',
    'vcdimager']


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

    def __init__(self, filename, title, format, tvsys):
        self.filename = filename
        self.title = title
        self.format = format
        self.tvsys = tvsys


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


class Titleset:
    """A group of videos, with an optional Menu.
    """
    def __init__(self, videos=None):
        """Create a Titleset containing the given Videos.
        """
        self.videos = videos or []
        self.menu = None
    

class Disc:
    """A video disc containing one or more Titlesets, and an optional
    Menu for navigating to each Titleset.
    
    Needed for authoring:
        title
        format/tvsys
        top menu
        titlesets
    """
    def __init__(self, name, format, tvsys, titlesets=None):
        """Create a Disc with the given properties.
        
            format:    'vcd', 'svcd', or 'dvd'
            tvsys:     'pal' or 'ntsc'
            title:     String containing the title of the disc
            titlesets: List of Titlesets
        """
        self.name = name
        self.format = format
        self.tvsys = tvsys
        self.topmenu = None
        self.titlesets = titlesets or []
   

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

#! /usr/bin/env python
# layout.py

"""This module provides an interface for structuring the content of video discs.
"""

"""Note to developers:

The layout submodule is changing fast. The video/menu/disc submodules have
merged into this file (at least for now). I'm also considering separating
dvdauthor.py and vcdimager.py, which will do _authoring_ based on the
_layout_ classes defined here. I'm thinking of just moving this __init__.py
to libtovid/layout.py, and eliminating the layout subdirectory.

The classes here represent the merging of ideas from libtovid/__init__.py
(the 0.30 target interface mockup) and libtovid/layout/dvdauthor.py, which
are designed as a direct implementation of dvdauthor's XML structure.

My goal is to end up with a more general disc-structuring API with simple
hierarchical navigation:

    Disc
        [Menu]
        Titleset
            [Menu]
            Video [Video ...]
        [Titleset]
            ...

A Disc would be instantiated like this:

    disc = Disc("mydvd", 'dvd', 'ntsc')

This would give you a "blank" disc, which you could then add videos, menus
etc. to. Say you have some encoded videos:

    videos = [Video("foo.mpg"), Video("bar.mpg")]

To have just videos on the disc, there'd be a single Titleset:

    titleset = Titleset(videos)
    disc.add_titleset(titleset)

If the videos should have a menu, then the Titleset holds the menu:

    menu = Menu(videos)
    titleset.add_menu(menu)

For multiple Titlesets, there'd need to be a top-level menu.

    morevideos = [Video('baz.mpg'), Video('bam.mpg')]
    menu2 = Menu(morevideos)
    titleset2 = Titleset(morevideos)
    titleset2.add_menu(menu2)
    disc.add_titleset(titleset2)

"""

all = [\
    'Disc',
    'Menu',
    'Video',
    'Group',
    'Titleset',
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

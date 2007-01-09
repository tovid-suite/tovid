#! /usr/bin/env python
# layout.py

"""This module provides an interface for structuring the content of video discs.

Note to developers:

The layout module is changing fast. The video/menu/disc submodules have
merged into this file, providing all disc-layout classes in one place.

The classes here represent the merging of ideas from libtovid/__init__.py
(the 0.30 target interface mockup) and libtovid/author/dvdauthor.py, which
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

Please direct comments to wapcaplet on the freenode.net IRC channel #tovid.
"""

# TODO:
# Orient these classes toward describing only what the authoring step needs
# (basic high-level meta-information about each thing)
# The idea is that these are created _after_ videos are encoded & menus are
# generated, but before the disc is authored

# Consider eliminating format/tvsys from all except Disc (maybe that too);
# they are only meaningful for authoring if mixing pal/ntsc on the same disc
# (and format is determined by whether the Disc is passed to vcdimager.py or
# dvdauthor.py). Something higher-level will deal with format/tvsys instead.


__all__ = [\
    'Disc',
    'Menu',
    'Video',
    'Group',
    'Titleset']

class Video:
    """A video title for inclusion on a video disc.

    filename
    aspect
    audio track language?
    subtitle language?
    chapters
    """
    def __init__(self, filename, title=''):
        self.filename = filename
        self.title = title
        self.chapters = []


class Group:
    """A group title for inclusion on a video disc.

    list of filenames in group
    chapters
    """
    def __init__(self, filenames, title):
        self.filenames = filenames
        self.title = title


class Menu:
    """A menu for navigating the titles on a video disc.
    
    filename
    buttons/videos
    aspect
    language?
    """
    def __init__(self, filename, videos):
        """Create a menu linking to the given Videos."""
        self.filename = filename
        self.videos = videos


class Titleset:
    """A group of videos, with an optional Menu.
    """
    def __init__(self, videos=None, menu=None):
        """Create a Titleset containing the given Videos.
        """
        self.videos = videos or []
        self.menu = menu
    

class Disc:
    """A video disc containing one or more Titlesets, and an optional
    top Menu for navigating to each Titleset.
    
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

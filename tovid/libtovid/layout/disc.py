#! /usr/bin/env python
# disc.py

# TODO: Merge with dvdauthor.py

"""This module provides a Python interface for creating, customizing, and
authoring a video disc.
"""

__all__ = ['Disc']

import doctest
from copy import copy
from libtovid.opts import Option, OptionDict
from libtovid.layout.menu import Menu
from libtovid.layout.video import Video
#from libtovid.layout import dvdauthor

"""
Some ideas:

dvd = Disc('dvd', 'ntsc', 'My disc')
# TODO: Allow Video format/tvsys to inherit from Disc?
v1 = Video('dvd', 'ntsc', '/pub/foo1.avi')
v2 = Video('dvd', 'ntsc', '/pub/bar2.mov')
videos = [v1, v2]
menu = Menu(videos, 'dvd', 'ntsc', Style(font='helvetica', color='yellow'))
ts = Titleset(videos, menu)
dvd.addTitleset(ts)
v3 = Video('half-dvd', 'ntsc', '/pub/baz3.mpg')
topmenu = Menu([ts, v3], 'dvd', 'ntsc', Style(font='times', color='blue'))
dvd.addMenu(topmenu)

Consider creating a Disc/Menu/Video/Titleset hierarchy structure that can
be authored by passing it to one of several functions, say
    get_dvdauthor_xml(disc)
    get_vcdimager_xml(disc)
Or even:
    author(disc)
where the appropriate format is inferred, get_?_xml() is called, and the
appropriate program run to produce a ready-to-burn directory or image.

Minimal disc structure requirements:

A disc may contain one of the following structure hierarchies:

* Flat videos that play one after the other
* Videos accessible through a menu that appears when the disc is inserted
* Groups of videos, each with their own menu, with submenus accessible through
  a top-level (VMGM) menu

"""

class Titleset:
    def __init__(self, videos, menu=None):
        """Create a Titleset containing the given Videos.
        
            videos: A list of Videos to include in the titleset
            menu:   A Menu associated with the given Videos, or None
    
        """
        self.videos = videos
        self.menu = menu

class Disc:
    """A video disc containing video titles and optional menus.
    """
    def __init__(self, format, tvsys, title='', video_files=[]):
        """Create a Disc with the given properties.
        
            format:      'vcd', 'svcd', or 'dvd'
            tvsys:       'pal' or 'ntsc'
            title:       String containing the title of the disc
            video_files: List of filenames of videos to include on the disc
        """
        self.format = format
        self.tvsys = tvsys
        self.title = title
        self.video_files = video_files
    
    def generate(self):
        """Write dvdauthor or vcdimager XML for the element, to
        the file specified by the disc's 'out' option."""
        if self.format == 'dvd':
            xml = self.dvd_disc_xml()
        elif self.format in ['vcd', 'svcd']:
            xml = self.vcd_disc_xml()
        outfile = open(self.options['out'], 'w')
        outfile.write(xml)


    # ===========================================================
    # Disc XML generators

    def dvd_disc_xml(self):
        """Return a string containing dvdauthor XML for this disc.
        
            name (self.name)
            children (self.children)
            topmenu (self.children[0])
            outfile (topmenu['out'])
            topmenu.children
            
        """
        xml = '<dvdauthor dest="%s">\n' % self.name.replace(' ', '_')
        xml += '<vmgm>\n'
        # If there's a topmenu, write vmgm-level XML for it
        if len(self.children) == 1:
            topmenu = self.children[0]
            xml += '  <menus>\n'
            xml += '    <video />\n'
            xml += '    <pgc entry="title">\n'
            xml += '      <vob file="%s" />\n' % topmenu['out']
            num = 1
            for submenu in topmenu.children:
                xml += '      <button>jump titleset %d menu;</button>\n' % num
                num += 1
            xml += '    </pgc>\n'
    
        xml += '</vmgm>\n'
        # TODO: add titlesets for each submenu
        for menu in topmenu.children:
            xml += '<titleset>\n'
            xml += self.dvd_menu_xml(menu)
            for video in menu.children:
                xml += self.dvd_video_xml(video)
            xml += '</titleset>\n'
            
        xml += '</dvdauthor>\n'
        return xml
    
    
    # ===========================================================
    # Menu XML generators
    
    def dvd_menu_xml(self, menu):
        """Return a string containing dvdauthor XML for the given Menu.

            menu['out']
            menu.children
        """
        xml = '<menus>\n'
        xml += '  <video />\n'
        xml += '  <pgc entry="root">\n'
        xml += '  <vob file="%s" />\n' % menu['out']
        # For each child ('titles' target), add a button
        num = 1
        for target in menu.children:
            xml += '    <button>jump title %d;</button>\n' % num
            num += 1
        xml += '    <button>jump vmgm menu;</button>\n'
        xml += '  </pgc>\n'
        xml += '</menus>\n'
        return xml
    
    
    # ===========================================================
    # Video XML generators
    
    def dvd_video_xml(self, video):
        """Return a string containing dvdauthor XML for the given Video.

            video['chapters']
            video['out']
        """
        chap_str = '0'
        for chap in video['chapters']:
            chap_str += ',' + chap
    
        xml = '  <pgc>\n'
        xml += '    <vob file="%s" chapters="%s" />\n' % \
                (video['out'], chap_str)
        xml += '    <post>call menu;</post>\n'
        xml += '  </pgc>\n'
        return xml
    

# ===========================================================
# Self-test; executed when this script is run standalone
if __name__ == '__main__':
    doctest.testmod(verbose=True)

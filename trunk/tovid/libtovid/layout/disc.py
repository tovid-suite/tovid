#! /usr/bin/env python
# disc.py

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
        # TODO: Remove these(?)
        self.parent = None
        self.children = []
    
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
    
    def vcd_disc_xml(self):
        xml = """<?xml version="1.0"?>
        <!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
          "http://www.gnu.org/software/vcdimager/videocd.dtd">
        <videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
        """
        # format == vcd|svcd, version=1.0 (svcd) | 2.0 (vcd)
        format = self.options['format']
        if format == 'vcd':
            version = "2.0"
        else:
            version = "1.0"
        xml += 'class="%s" version="%s">\n' % (format, version)
    
        if format == 'svcd':
            xml += '<option name="update scan offsets" value="true" />'
    
        xml += """<info>
          <album-id>VIDEO_DISC</album-id>
          <volume-count>1</volume-count>
          <volume-number>1</volume-number>
          <restriction>0</restriction>
        </info>
        <pvd>
          <volume-id>VIDEO_DISC</volume-id>
          <system-id>CD-RTOS CD-BRIDGE</system-id>
        </pvd>
        """
        # TODO:
        # segment-items
        # sequence-items
        # pbc + selections
        xml += '</videocd>'

    def dvd_disc_xml(self):
        """Return a string containing dvdauthor XML for this disc."""
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
        """Return a string containing dvdauthor XML for the given Menu."""
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
        """Return a string containing dvdauthor XML for the given Video."""
    
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

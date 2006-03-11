#! /usr/bin/env python2.4
# disc.py

__all__ = ['Disc']

import string
import sys
from copy import copy

import libtovid
from libtovid.opts import OptionDef

class Disc:
    """A video disc containing video titles and optional menus."""
    # Dictionary of valid options with documentation
    optiondefs = { 
        'name': OptionDef('name', '"Disc title"', '',
            """Title of the disc"""),

        'format':
            OptionDef('format', 'vcd|svcd|dvd', 'dvd',
            """Create a disc of the specified format."""),
        'tvsys':
            OptionDef('tvsys', 'pal|ntsc', 'ntsc',
            """Make the disc for the specified TV system."""),
        'topmenu':
            OptionDef('topmenu', 'MENUNAME', None,
            """Use MENUNAME for the top-level menu on the disc."""),
        'out':
            OptionDef('out', 'FILE', None,
            """Filename to write disc navigational structure to.""")
    }

    def __init__(self, options):
        """Initialize Disc with a string or list of options."""
        # Start with defaults
        self.options = libtovid.opts.get_defaults(self.optiondefs)
        # Overwrite defaults with options from list
        custom = libtovid.opts.parse(options, self.optiondefs)
        self.options.update(custom)
        self.parents = []
        self.children = []

    def generate(self):
        """Write dvdauthor or vcdimager XML for the element, to
        the file specified by the disc's 'out' option."""
        if self.options['format'] == 'dvd':
            xml = self.dvd_disc_xml()
        elif self.options['format'] in ['vcd', 'svcd']:
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
            # TODO: Add buttons for each submenu
            # <button>jump titleset N menu;</button>
            num = 1
            for submenus in topmenu.children:
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
"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    write_dvdauthor_xml(proj)
"""

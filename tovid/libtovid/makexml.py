#! /usr/bin/env python

"""This module takes a tovid Project, finds all the Disc elements present
therein, and generates vcdxbuild|dvdauthor XML for the disc (and all its
menu/video navigational hierarchy), writing the results to the filename
contained in each Disc element's 'out' option.
"""

import string, sys
from libtovid import Project

def vcdimager_xml(project):
    xml = """<?xml version="1.0"?>
    <!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
      "http://www.gnu.org/software/vcdimager/videocd.dtd">
    <videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
    """
    # format == vcd|svcd, version=1.0 (svcd) | 2.0 (vcd)
    xml += 'class="%s" version="%s">\n' % (format, version)

    # For SVCD:
    # xml += '<option name="update scan offsets" value="true" />'

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
    # segment-items
    # sequence-items
    # pbc + selections
    xml += '</videocd>'
    return xml

    
def dvdauthor_xml(project):
    """Write dvdauthor XML files for the given project, returning a list
    of resulting filenames."""

    xmlfiles = []
    for disc in project.get_elements('Disc'):
        # Write a dvdauthor XML file for each disc
        xmlfile = "%s.xml" % disc.name.replace(' ', '_')
        xmlfiles.append(xmlfile)
        xml = _disc_xml(disc)
        # TODO: write xml to the file
        print xml


def _disc_xml(disc):
    xml = '<dvdauthor dest="%s">\n' % disc.name.replace(' ', '_')
    xml += '<vmgm>\n'
    # If there's a topmenu, write vmgm-level XML for it
    if len(disc.children) == 1:
        topmenu = disc.children[0]
        xml += '  <menus>\n'
        xml += '    <video />\n'
        xml += '    <pgc entry="title">\n'
        xml += '      <vob file="%s" />\n' % topmenu.get('out')
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
        xml += _menu_xml(menu)
        for video in menu.children:
            xml += _video_xml(video)
        xml += '</titleset>\n'
        
    xml += '</dvdauthor>\n'
    return xml


def _menu_xml(menu):
    """Return a string containing dvdauthor XML for the given menu element."""
    xml = '<menus>\n'
    xml += '  <video />\n'
    xml += '  <pgc entry="root">\n'
    xml += '  <vob file="%s" />\n' % menu.get('out')
    # For each child ('linksto' target), add a button
    num = 1
    for target in menu.children:
        xml += '    <button>jump title %d;</button>\n' % num
        num += 1
    xml += '    <button>jump vmgm menu;</button>\n'
    xml += '  </pgc>\n'
    xml += '</menus>\n'
    return xml


def _video_xml(video):
    """Return a string containing dvdauthor XML for the given video element."""

    xml = '  <pgc>\n'
    xml += '    <vob file="%s" chapters="0" />\n' % video.get('out')
    xml += '    <post>call menu;</post>\n'
    xml += '  </pgc>\n'
    return xml


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    dvdauthor_xml(proj)

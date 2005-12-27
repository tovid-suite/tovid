#! /usr/bin/env python

# ===========================================================
#

# TODO: Exception handling

"""This module takes a tovid Project, finds all the Disc elements present
therein, and generates vcdxbuild|dvdauthor XML for the disc (and all its
menu/video navigational hierarchy), writing the results to the filename
contained in each Disc element's 'out' option.
"""

import string, sys
from libtovid import Project


def write_project_xml(project):
    """Write dvdauthor or vcdimager XML for each disc in the given project."""
    for disc in project.get_elements('Disc'):
        if disc.get('format') == 'dvd':
            xml = dvd_disc_xml(disc)
        elif disc.get('format') in ['vcd', 'svcd']:
            xml = vcd_disc_xml(disc)
        outfile = open(disc.get('out'), 'w')
        outfile.write(xml)


# ===========================================================
# Disc XML generators

def vcd_disc_xml(disc):
    xml = """<?xml version="1.0"?>
    <!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
      "http://www.gnu.org/software/vcdimager/videocd.dtd">
    <videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
    """
    # format == vcd|svcd, version=1.0 (svcd) | 2.0 (vcd)
    format = disc.get('format')
    if format == 'vcd': version = "2.0" else: version = "1.0"
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
    # segment-items
    # sequence-items
    # pbc + selections
    xml += '</videocd>'


def dvd_disc_xml(disc):
    """Return a string containing dvdauthor XML for the given disc element."""
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
        xml += dvd_menu_xml(menu)
        for video in menu.children:
            xml += dvd_video_xml(video)
        xml += '</titleset>\n'
        
    xml += '</dvdauthor>\n'
    return xml


# ===========================================================
# Menu XML generators

def dvd_menu_xml(menu):
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


# ===========================================================
# Video XML generators

def dvd_video_xml(video):
    """Return a string containing dvdauthor XML for the given video element."""

    chap_str = '0'
    for chap in video.get('chapters'):
        chap_str += ',' + chap

    xml = '  <pgc>\n'
    xml += '    <vob file="%s" chapters="%s" />\n' % \
            (video.get('out'), chap_str)
    xml += '    <post>call menu;</post>\n'
    xml += '  </pgc>\n'
    return xml


# ===========================================================
# Self-test; executed when this script is run standalone
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    write_dvdauthor_xml(proj)

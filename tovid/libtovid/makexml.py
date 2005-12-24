#! /usr/bin/env python

import string, sys
from libtovid import Project

def gen_dvdauthor_xml(project):
    """Write dvdauthor XML files for the given project, returning a list
    of resulting filenames."""

    xmlfiles = []
    for disc in project.get_elements('Disc'):
        # Write a dvdauthor XML file for each disc
        xmlfile = "%s.xml" % disc.name.replace(' ', '_')
        xmlfiles.append(xmlfile)
        xml = disc_xml(disc, project)
        # TODO: write xml to the file
        print xml


def disc_xml(disc, project):
    xml = '<dvdauthor dest="%s">\n' % disc.name.replace(' ', '_')
    xml += '<vmgm>\n'
    # If there's a topmenu, write vmgm-level XML for it
    if disc.get('topmenu'):
        topmenu = project.get(disc.get('topmenu'))
        xml += '  <menus>\n'
        xml += '    <video />\n'
        xml += '    <pgc entry="title">\n'
        xml += '      <vob file="%s" />\n' % topmenu.get('out')
        # TODO: Add buttons for each submenu
        # <button>jump titleset N menu;</button>
        xml += '    </pgc>\n'

    xml += '</vmgm>\n'
    # TODO: add titlesets for each submenu
    for menu in topmenu.children:
        xml += '<titleset>\n'
        xml += menu_xml(menu, project)
        for video in menu.children:
            xml += video_xml(video, project)
        xml += '</titleset>\n'
        
    xml += '</dvdauthor>\n'
    return xml


def menu_xml(menu, project):
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
    xml += '  </pgc>\n'
    xml += '</menus>\n'
    return xml


def video_xml(video, project):
    """Return a string containing dvdauthor XML for the given video element."""

    xml = '  <pgc>\n'
    xml += '    <vob file="%s" chapters="0" />\n' % video.get('out')
    xml += '  </pgc>\n'
    return xml


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    gen_dvdauthor_xml(proj)

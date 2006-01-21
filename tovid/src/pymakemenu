#! /usr/bin/env python

# pymakemenu
# Generate an (S)VCD/DVD menu MPEG
# (to replace the 'makemenu' shell script)

import sys, libtovid
from libtovid import Menu, Parser, Project

if __name__ == '__main__':
    """Parse the provided command-line arguments as a Menu element."""

    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print 'Usage: pymakemenu [options] "Title 1" "Title 2" ... -out NAME'
        print "See the 'makemenu' manual page for more details."
        sys.exit()
        
    # If a TDL file name was provided, parse and generate Menus in it
    elif len(sys.argv) == 3 and sys.argv[1] == '-tdl':
        print "Generating menus from TDL: '%s'" % sys.argv[2]
        proj = Project.Project()
        proj.load_file(sys.argv[2])

        for menu in proj.get_elements('Menu'):
            print "Generating menu: '%s'" % menu.name
            libtovid.Menu.generate(menu)

    else:
        print "pymakemenu"
        # Insert a dummy element/name declaration
        tdl = 'Menu "FOO MENU" '
        for arg in sys.argv[1:]:
            tdl += '%s ' % arg

        print "TDL string:"
        print tdl

        # TODO: Fix this dumb redundancy in naming (same for Project.Project
        # above)
        par = Parser.Parser()
        elems = par.parse_string(tdl)
        print "Parsed Menu element:"
        print elems[0].tdl_string()
        print "Generating menu..."
        Menu.generate(elems[0])

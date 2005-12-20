#! /usr/bin/env python

# ===========================================================
# Project
# ===========================================================

import sys
import Parser

# ===========================================================
class Project:
    """A collection of related TDL elements comprising a
    complete video disc project (or a multiple-disc project)."""

    def __init__(self):
        # Highest-level elements in the project (those with no other parent)
        self.topelements = []

    
    def load_file(self, filename):
        """Load project data from the given TDL file."""
        self.elemdict = {}
        p = Parser.Parser()
        for element in p.parse_file(filename):
            self.elemdict[element.name] = element
        self.build_hierarchy()
        

    def save_file(self, filename):
        """Save project data as a TDL text file."""
        outfile = open(filename, 'w')
        outfile.write(self.tdl_tring())


    def build_hierarchy(self):
        """Determine the hierarchy among the defined elements, and
        handle undefined or orphaned elements."""

        for name, element in self.elemdict.iteritems():
            if element.tag == 'Disc':
                # Link to 'topmenu' target, if it exists
                linkname = element.get('topmenu')
                if self.elemdict.has_key(linkname):
                    element.children.append(self.elemdict[linkname])
                    self.elemdict[linkname].parents.append(element)
                else:
                    print "Disc \"%s\" links to undefined topmenu \"%s\"" % \
                            (name, linkname)

            elif element.tag == 'Menu':
                # Link to all 'linksto' targets, if they exist
                print element.get('linksto')
                for linkname in element.get('linksto'):
                    if self.elemdict.has_key(linkname):
                        print "build_hierarchy: making %s a child of %s" % \
                                (linkname, name)
                        element.children.append(self.elemdict[linkname])
                        self.elemdict[linkname].parents.append(element)
                    else:
                        print "Menu \"%s\" links to undefined element \"%s\"" % \
                                (name, linkname)

        # Look for orphans (topitems)
        self.topitems = []
        for name, element in self.elemdict.iteritems():
            if element.parents == []:
                self.topitems.append(element)
                print "Element: %s has no parents" % name


    def tdl_string(self):
        """Convert the project to a TDL string and return it."""
        projstring = ""
        for name, element in self.elemdict.iteritems():
            projstring += "%s\n" % element.tdl_string()
        return projstring


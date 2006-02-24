#! /usr/bin/env python
# Project.py

__all__ = ['Project']

# TODO: Exception handling

import sys

from TDL import Parser

# ===========================================================
class Project:
    """A collection of related TDL elements comprising a
    complete video disc project (or a multiple-disc project)."""

    def __init__(self):
        pass

    
    def load_file(self, filename):
        """Load project data from the given TDL file."""
        self.elemdict = {}
        p = Parser()
        # Index elemdict by element name for easy access
        for element in p.parse_file(filename):
            self.elemdict[element.name] = element
        self.build_hierarchy()
        

    def save_file(self, filename):
        """Save project data as a TDL text file."""
        try:
            outfile = open(filename, 'w')
        except:
            log.error('Could not open file "%s"' % filename)
        else:
            outfile.write(self.tdl_tring())
            outfile.close()


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
                # Link to all 'titles' targets, if they exist
                print element.get('titles')
                for linkname in element.get('titles'):
                    if self.elemdict.has_key(linkname):
                        print "build_hierarchy: making %s a child of %s" % \
                                (linkname, name)
                        element.children.append(self.elemdict[linkname])
                        self.elemdict[linkname].parents.append(element)

                    # TODO: Find a way to link 'back' to this menu's parent
                    # elif string.lower(linkname) == 'back': ?

                    else:
                        print "Menu \"%s\" links to undefined element \"%s\"" % \
                                (name, linkname)
            

        # Look for orphans (topitems)
        self.topitems = []
        for name, element in self.elemdict.iteritems():
            if len(element.parents) == 0:
                self.topitems.append(element)
                print "Element: %s has no parents" % name


    def get(self, name):
        """Return the element with the given name, or None if not found."""
        if name in self.elemdict:
            return self.elemdict[name]
        else:
            return None

    def get_elements(self, type):
        """Return a list of elements of the given type in this project."""
        elements = []
        for name, element in self.elemdict.iteritems():
            if element.tag == type:
                elements.append(element)
        return elements


    def tdl_string(self):
        """Convert the project to a TDL string and return it."""
        projstring = ""
        for name, element in self.elemdict.iteritems():
            projstring += "%s\n" % element.tdl_string()
        return projstring


# ===========================================================
#
# Unit test
#
# ===========================================================

# TODO: Write a proper unit test
# See http://docs.python.org/lib/module-unittest.html

#! /usr/bin/env python2.4
# project.py

__all__ = ['Project']

# TODO: Exception handling

import sys

import libtovid
from libtovid.tdl import Parser
from libtovid.log import Log
from libtovid.disc import Disc
from libtovid.menu import Menu
from libtovid.video import Video

log = Log('project.py')

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
            if isinstance(element, Disc):
                # Link to 'topmenu' target, if it exists
                linkname = element['topmenu']
                if self.elemdict.has_key(linkname):
                    element.children.append(self.elemdict[linkname])
                    self.elemdict[linkname].parents.append(element)
                else:
                    log.error("Disc \"%s\" links to undefined topmenu \"%s\"" % \
                            (name, linkname))

            elif isinstance(element, Menu):
                # Link to all 'titles' targets, if they exist
                for linkname in element['titles']:
                    if self.elemdict.has_key(linkname):
                        log.debug("Making %s a child of %s" % \
                                (linkname, name))
                        element.children.append(self.elemdict[linkname])
                        self.elemdict[linkname].parents.append(element)

                    # TODO: Find a way to link 'back' to this menu's parent
                    # elif string.lower(linkname) == 'back': ?

                    else:
                        log.error("Menu \"%s\" links to undefined element \"%s\"" % \
                                (name, linkname))
            

        # Look for orphans (topitems)
        self.topitems = []
        for name, element in self.elemdict.iteritems():
            if len(element.parents) == 0:
                self.topitems.append(element)
                log.error("Element: %s has no parents" % name)


    def get(self, name):
        """Return the element with the given name, or None if not found."""
        if name in self.elemdict:
            return self.elemdict[name]
        else:
            return None


    def to_string(self):
        """Return the project, formatted as a string."""
        result = ''
        for name, element in self.elemdict.iteritems():
            result += '%s\n' % element.to_string()
        return result


# ===========================================================
#
# Unit test
#
# ===========================================================

# TODO: Write a proper unit test
# See http://docs.python.org/lib/module-unittest.html

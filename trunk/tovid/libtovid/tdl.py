#! /usr/bin/env python2.4
# tdl.py

__doc__ = \
"""TODO"""

__all__ = ['element_classes']

import sys
import copy
import shlex

import libtovid
from libtovid import utils
from libtovid.video import Video
from libtovid.menu import Menu
from libtovid.disc import Disc
from libtovid.opts import OptionDef
from libtovid.log import Log

log = Log('tdl.py')

element_classes = {
    'Disc':  Disc,
    'Menu':  Menu,
    'Video': Video
}


def new_element(elemstring):
    """Return a new Disc, Menu, or Video created from the given string.
    Example: elemstring = 'Menu "Main menu" -format dvd -tvsys ntsc'."""
    tokens = utils.tokenize(elemstring)
    type = tokens.pop(0)
    name = tokens.pop(0)
    opts = tokens + ['out', name]
    newelem = element_classes[type](opts)
    newelem.indent = utils.indent_level(elemstring)
    return newelem

def get_elements(filename):
    """Get a list of elements from the given filename."""
    lines = utils.get_code_lines(filename)
    # Condense lines so there's only one element definition per line
    condlines = []
    lastline = ''
    while len(lines) > 0:
        curline = lines.pop(0)
        tokens = utils.tokenize(curline)
        if tokens[0] in element_classes:
            if lastline:
                condlines.append(lastline)
            lastline = curline.rstrip(' \r\n')
        else:
            lastline += ' ' + curline.lstrip().rstrip(' \r\n')
    condlines.append(lastline)
    # Create and return a list of elements
    elems = []
    for line in condlines:
        elems.append(new_element(line))
    return elems

def parse(filename):
    """Parse a file and return a dictionary of Discs, Menus, and Videos
    indexed by name."""
    elems = get_elements(filename)
    stack = [elems[0]]
    for elem in elems[1:]:
        if elem.indent > stack[-1].indent:
            pass
        elif elem.indent < stack[-1].indent:
            stack.pop()
            stack.pop()
        elif elem.indent == stack[-1].indent:
            stack.pop()
        stack[-1].children.append(elem)
        elem.parent = stack[-1]
        stack.append(elem)
    return elems

class Project:
    """A collection of related TDL elements comprising a
    complete video disc project (or a multiple-disc project)."""

    def __init__(self):
        pass
    
    def load_file(self, filename):
        """Load project data from the given TDL file."""
        self.elemdict = {}
        # Index elemdict by element name for easy access
        #for element in parse(filename):
        #    self.elemdict[element.name] = element
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



# TODO: Write a proper unit test
# See http://docs.python.org/lib/module-unittest.html

if __name__ == '__main__':
    elems = parse(sys.argv[1])
    for elem in elems:
        print "%s %s" % (elem.__class__, elem.options['out'])
        print utils.pretty_dict(elem.options)
        for child in elem.children:
            print child


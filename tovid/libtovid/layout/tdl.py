#! /usr/bin/env python
# tdl.py

__all__ = ['element_classes']

# From standard library
import sys
# From libtovid
from libtovid.utils import tokenize, pretty_dict, get_code_lines, indent_level
from libtovid import Video
from libtovid import Menu
from libtovid import Disc
from libtovid import log

element_classes = {
    'Disc':  Disc,
    'Menu':  Menu,
    'Video': Video
}

def new_element(elemstring):
    """Return a new Disc, Menu, or Video created from the given string.
    Example: elemstring = 'Menu "Main menu" -format dvd -tvsys ntsc'."""
    tokens = tokenize(elemstring)
    type = tokens.pop(0)
    name = tokens.pop(0)
    opts = tokens + ['out', name]
    newelem = element_classes[type](opts)
    newelem.indent = indent_level(elemstring)
    return newelem

def get_elements(filename):
    """Get a list of elements from the given filename."""
    lines = get_code_lines(filename)
    # Condense lines so there's only one element definition per line
    condlines = []
    lastline = ''
    while len(lines) > 0:
        curline = lines.pop(0)
        tokens = tokenize(curline)
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


class Project:
    """A video disc project with one or more discs."""

    def __init__(self):
        pass
    
    def load_file(self, filename):
        """Load project data from the given TDL file."""
        elems = get_elements(filename)
        stack = [elems[0]]
        for elem in elems[1:]:
            # Indentation same as top; new child
            if elem.indent > stack[-1].indent:
                pass
            # Indentation same as top; new sibling
            elif elem.indent == stack[-1].indent:
                stack.pop()
            # Indentation less than top; new uncle
            elif elem.indent < stack[-1].indent:
                stack.pop()
                stack.pop()
            stack[-1].children.append(elem)
            elem.parent = stack[-1]
            stack.append(elem)
        self.elems = elems

    def save_file(self, filename):
        """Save project data as a TDL text file."""
        pass


# TODO: Write a proper unit test
# See http://docs.python.org/lib/module-unittest.html

if __name__ == '__main__':
    # TODO: this is broken since 'parse' does not exist anymore
    elems = parse(sys.argv[1])
    for elem in elems:
        print "%s %s" % (elem.__class__, elem.options['out'])
        print pretty_dict(elem.options)
        for child in elem.children:
            print child


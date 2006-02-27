#! /usr/bin/env python
# tdl.py

# ===========================================================
__doc__ = \
"""This module contains a definition of the tovid design language (TDL),
including:

    * Valid Element types (i.e., 'Video', 'Menu', 'Disc')
    * Valid options for each type of element
    * Argument format, default value, and documentation
      for each accepted option

Essentially, TDL is a user-interface API for tovid, designed to provide a
generalized interface, which may then be implemented by an actual frontend
(command-line, GUI, text-file input, etc.)


Hacking this module:

This module can do some pretty interesting things on its own, with a little bit
of interaction. Run 'python' to get an interactive shell, and try some of the
following.

First, tell python where to find this module:

    >>> from libtovid import TDL
    >>>

The first thing of interest is what elements are available in TDL:

    >>> for elem in TDL.element_defs:
    ...     print elem
    ...
    Menu
    Disc
    Video
    >>>

You can see that TDL has three different kinds of element: Menu, Disc, and
Video. What options are available for a Menu element?

    >>> for option in TDL.element_defs['Menu']:
    ...     print option
    ...
    highlightcolor
    font
    format
    tvsys
    selectcolor
    textcolor
    fontsize
    background
    audio
    alignment
    titles 
    >>>

Say you want to know the purpose of the Menu 'background' option:

    >>> print TDL.element_defs['Menu']['background'].doc
    Use IMAGE (in most any graphic format) as a background.
    >>>

You can also display full usage notes for an option, by using the
usage_string() function:

    >>> print TDL.element_defs['Menu']['background'].usage_string()
    -background IMAGE (default None)
        Use IMAGE (in most any graphic format) as a background.
    >>>

To display full usage notes for an element, do like this:

    >>> print TDL.usage('Menu')
    -highlightcolor [#RRGGBB|#RGB|COLORNAME] (default red)
        Undocumented option

    -font FONTNAME (default Helvetica)
        Use FONTNAME for the menu text.

    -format [vcd|svcd|dvd] (default dvd)
        Generate a menu compliant with the specified disc format
    
    (...)

    >>>

Let's create a new Menu element, named "Main menu":

    >>> menu = TDL.Element('Menu', "Main menu")

Behind the scenes, a new element is created, and filled with all the default
options befitting a Menu element. You can check it out by displaying the TDL
string representation of the element, like so:

    >>> print menu.tdl_string()
    Menu "Main menu"
        textcolor white
        format dvd
        tvsys ntsc
        selectcolor green
        highlightcolor red
        fontsize 24
        background None
        font Helvetica
        titles []
        alignment left
        audio None
    >>>

Let's say you don't like Helvetica, and want to use the "Times" font instead:

    >>> menu.set('font', "Times")
    >>>

And you would like to change the background:

    >>> menu.set('background', "/pub/images/foo.jpg")
    >>>

These values may then later be retrieved, by doing:

    >>> font = menu.get('font')
    >>> font
    'Times'
    >>>

Elements basically serve as a container for a bunch of info related to a disc,
menu, or video. You might also think of them as templates, defining a
customizable framework, with self-contained documentation.
"""

__all__ = ['element_defs', 'usage', 'Parser']

# TODO: Finish restructuring
"""Restructuring thoughts:

The Parser below is basically tovid's own 'getopts', with a customizable
list of acceptable options (Video.optiondefs, etc.) Handling of options
should be separate from interpretation of TDL element declarations;
part of the complexity arises from trying to do both.

Instead, perhaps something like this:

    getopts(optdefs): parses input, matching against optdefs; returns
        matching (set) options found, w/ defaults for all others.
        Better suited to parsing command-line options; no need to
        create artificial Menu/Video/Disc elements from pytovid, etc.
    tdl.getelements(string|file): looks for Menu/Video/Disc declarations, builds
        project hierarchy.
        
Merge tdl.py and project.py.

Note: Learn more about PendingDeprecationWarning (possibly for use by libtovid
for deprecating features). Mentioned here:

    http://www.python.org/doc/2.3.5/lib/module-exceptions.html

    
"""
import sys
import copy
import shlex

import libtovid
from libtovid.video import Video
from libtovid.menu import Menu
from libtovid.disc import Disc
from libtovid.option import OptionDef
from libtovid.log import Log
from libtovid.element import Element

log = Log('tdl.py')



# ===========================================================
# Dictionary of TDL options, categorized by element tag
element_defs = {
    'Video': Video.optiondefs,
    'Menu':  Menu.optiondefs,
    'Disc':  Disc.optiondefs
}


def usage(elem):
    """Return a string containing usage notes for the given element type."""
    usage_str = ''
    for opt, optdef in element_defs[elem].iteritems():
        usage_str += optdef.usage_string() + '\n'
    return usage_str
        



# ===========================================================
class Parser:
    """Parse a provided file, stream, or string, and return a list of TDL
    Elements found within.
    
    This parser doesn't know much about TDL; it can handle any simple element-attribute
    text language resembling the following:

        ElementTag "Identifying name"
            -option1 value
            -option2 value
            -listoption1 list, of, values
            -booloption1
            -booloption2
    """


    def __init__(self, interactive = False):
        # Someday allow more interactive parsing
        # (such as when parsing from stdin)
        self.interactive = interactive

    # TODO: Find an elegant shortcut (preferably a single function)
    # to replace all these (mostly redundant) parse_X functions

    def parse_stdin(self):
        """Parse all text from stdin until EOF (^D)"""

        # shlex uses stdin by default
        self.lexer = shlex.shlex(posix = True)
        return self.parse()


    def parse_file(self, filename):
        """Parse all text in a file"""

        # Open file and create a lexer for it
        stream = open(filename, "r")
        self.lexer = shlex.shlex(stream, filename, posix = True)
        # Parse, close file, and return
        result = self.parse()
        stream.close()
        return result


    def parse_string(self, str):
        """Parse all text in a string"""

        # Create a lexer for the string
        self.lexer = shlex.shlex(str, posix = True)
        return self.parse()


    def parse_args(self, args):
        """Parse all text in a list of strings such as sys.argv"""
        print args

        # Create a lexer
        self.lexer = shlex.shlex(posix = False)
        # Push args onto the lexer (in reverse order)
        self.lexer.push_token(None)
        while len(args) > 0:
            self.lexer.push_token(args.pop())
        return self.parse()

    def next_token(self):
        """Return the next token in the lexer."""
        tok = self.lexer.get_token()
        if tok:
            log.debug("next_token: Got '%s'" % tok)
        else:
            log.debug("next_token: Got EOF")
        return tok

    def is_keyword(self, arg):
        """Return True if the given argument is an element option name."""
        # If it matches 'Menu', 'Disc', 'Video'
        if arg in element_defs:
            return True
        # If it matches any 'Menu' option, 'Disc' option, or 'Video' option
        for tag in element_defs:
            if arg.lstrip('-') in element_defs[tag]:
                return True
        return False

    def error(self, message):
        """Print an error message and raise an exception."""
        log.debug(self.lexer.error_leader())
        log.error(message)
        sys.exit()
        
    # TODO: Modularize this function better, splitting some chunks
    # into other (private) functions
    def parse(self):
        """Parse all text in self.lexer and return a
        list of Elements filled with appropriate
        attributes"""
        # Set rules for splitting tokens
        self.lexer.wordchars = self.lexer.wordchars + ".:-%()/"
        self.lexer.whitespace_split = False
        # Begin with an empty list of elements
        element = None
        self.elements = []

        # Parse all input
        while True:
            token = self.next_token()

            # Exit on EOF
            if not token:
                break

            elif token in ['Disc', 'Menu', 'Video']:
                name = self.next_token()
                if self.is_keyword(name):
                    self.error('Expecting name to follow %s (got %s)' % \
                            (token, name))
                if token == 'Disc':
                    element = Disc(name)
                elif token == 'Menu':
                    element = Menu(name)
                elif token == 'Video':
                    element = Video(name)
                self.elements.append(element)

            # If a valid option for the current element is found, set its value
            # appropriately (depending on number of arguments)
            elif element and token.lstrip('-') in element.options:
                opt = token.lstrip('-')

                # How many arguments are expected for this
                # option? (0, 1, or unlimited)
                expected_args = element.optiondefs[opt].num_args()
                print "%s expects %s args" % (opt, expected_args)

                # Is this option an alias (short-form) of another option?
                # (i.e., -vcd == -format vcd)
                if element.optiondefs[opt].alias:
                    key, value = element.optiondefs[opt].alias
                    element.set(key, value)
                    
                # No args? Must just be a flag--set it to True
                elif expected_args == 0:
                    element.set(opt, True)

                # One arg? Easy...
                elif expected_args == 1:
                    arg = self.next_token()
                    if self.is_keyword(arg):
                        self.error('-%s option expects an argument.' % opt)
                    # TODO: Get validation working properly
                    # if element_defs[element.tag][opt].is_valid(arg):
                    #     element.set(opt, arg)
                    # else:
                    #     print "Invalid argument to -%s: %s" % (opt, arg)
                    element.set(opt, arg)

                # Unlimited (-1) number of args? Create a list,
                # and look for comma-separation.
                elif expected_args < 0:
                    arglist = []
                    next = self.next_token()
                    # While the next token is not a keyword
                    if self.is_keyword(next):
                        self.error('-%s option expects one or more arguments.' \
                                % opt)
                    # Until the next keyword is reached, add to list
                    while next and not self.is_keyword(next):
                        # Ignore any surrounding [ , , ]
                        arglist.append(next.lstrip('[').rstrip(',]'))
                        next = self.next_token()
                    # Put the last-read token back
                    self.lexer.push_token(next)
                    element.set(opt, arglist)
            else:
                self.error("Unrecognized token: %s" % token)

        return self.elements


    
# ===========================================================
#
# Unit test
#
# ===========================================================

# TODO: Write a proper unit test
# See http://docs.python.org/lib/module-unittest.html


# Self-test; executed when this module is run as a standalone script
if __name__ == "__main__":
    # Print all element/option definitions
    for elem in element_defs:
        print "%s element options:" % elem
        for key, optdef in element_defs[elem].iteritems():
            print optdef.usage_string()

    # Create one of each element and display them (to ensure that
    # default values are copied correctly)
    vid = Element('Video', "Test video")
    menu = Element('Menu', "Test menu")
    disc = Element('Disc', "Test disc")
    vid.tdl_string()
    menu.tdl_string()
    disc.tdl_string()



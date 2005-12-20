#! /usr/bin/env python

# ===========================================================
# Parser
# ===========================================================

import os
import sys
import string
import shlex

# ===========================================================
"""This module contains a text parser for a simple option-attribute
language. The current implementation is designed to work with the
tovid design language defined in libtovid/TDL.py.

To use this parser in your own module:

    import libtovid.Parser

To create a parser for the TDL language:

    parser = Parser.Parser(TDL)

To parse 'foo.tdl' containing text in the TDL language:

    parser.parse_file("foo.tdl")

"""

# Currently, Parser.py is generalized enough to handle
# any TDL-like language; none of the TDL module's classes
# are used directly right now.
import TDL

# ===========================================================
class Parser:
    """Parse a provided file, stream, or string, and return a list of TDL
    Elements found within.
    
    This parser handles a simple element/attribute text language resembling the
    following:

        ElementTag "Identifying name"
            -option1 value
            -option2 value
            -listoption1 list, of, values
            -booloption1
            -booloption2

    This implementation parses the language defined in TDL.py."""


    def __init__(self, lang = TDL, interactive = False):
        # Someday allow more interactive parsing
        # (such as when parsing from stdin)
        self.lang = lang
        self.interactive = interactive


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

        # Create a lexer
        self.lexer = shlex.shlex(posix = True)
        # Push args onto the lexer (in reverse order)
        self.lexer.push_token(None)
        while len(args) > 0:
            self.lexer.push_token(args.pop())
        return self.parse()


    def next_token(self):
        """Get the next token and print it out.
        
        This is a wrapper for lexer.get_token(), mainly for
        producing debugging output. Cleanup later."""

        tok = self.lexer.get_token()
        if tok:
            #print "Got '%s'" % tok
            pass
        else:
            #print "Got EOF"
            pass
        return tok


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

            # If an element in the language (TDL) is found (that is,
            # 'Disc', 'Menu', or 'Video' was encountered), get a
            # new Element object, and add it to the list
            elif token in self.lang.elements:

                tag = token                # e.g., "Menu"
                name = self.next_token()   # e.g., "Music videos"
                # Get a new element with the given type and name
                element = self.lang.Element(tag, name)
                #print "New element created:"
                #print element.tdl_string()

                # Add the element to the list
                self.elements.append(element)


            # If a valid option for the current element is found, set its value
            # appropriately (depending on number of arguments)
            elif element and token.lstrip('-') in element.options:
                opt = token.lstrip('-')

                # How many arguments are expected for this
                # option? (0, 1, or unlimited)
                expected_args = self.lang.element_options[element.tag][opt].num_args()
                #print "%s expects %s args" % (opt, expected_args)

                # No args? Must just be a flag--set it to True
                if expected_args == 0:
                    element.set(opt, True)

                # One arg? Easy...
                elif expected_args == 1:
                    element.set(opt, self.next_token())

                # Unlimited (-1) number of args? Create a list,
                # and look for comma-separation.
                elif expected_args < 0:
                    arglist = []

                    next = self.next_token()
                    # Ignore optional opening bracket
                    if next == '[':
                        next = self.next_token()

                    # Append the first argument to the list
                    arglist.append(next)

                    # Read the next token, and keep appending
                    # as long as there are more commas
                    next = self.next_token()
                    while next == ',':
                        next = self.next_token()
                        arglist.append(next)
                        next = self.next_token()

                    # Ignore optional closing bracket
                    if next == ']':
                        pass
                    else:
                        # Put the last-read token back
                        self.lexer.push_token(next)

                    element.set(opt, arglist)


            else:
                print self.lexer.error_leader()
                print "parse(): Unrecognized token: %s" % token


        return self.elements


# ===========================================================
#
# Unit test
#
# ===========================================================

#import unittest

# Test case
#class TestTDLParser(unittest.TestCase):
#    """Test the Parser using TDL"""


# Self-test; executed when this module is run as a standalone script
if __name__ == "__main__":
    p = Parser()

    # If there were no args, parse from stdin
    if len(sys.argv) <= 1 :
        print "Parsing TDL from standard input (press Ctrl-D to stop)"
        elements = p.parse_stdin()

    # If first arg is a filename (of an existing file),
    # parse that file
    elif os.path.isfile(sys.argv[1]):
        print "Parsing TDL in file: " + sys.argv[1]
        elements = p.parse_file(sys.argv[1])

    # Otherwise, parse all command-line arguments given
    else:
        print "Parsing TDL on the command-line"
        del sys.argv[0]
        elements = p.parse_args(sys.argv)

    print "Done parsing. Elements found:"

    if len(elements) > 0:
        for element in elements:
            print element.tdl_string()
    else:
        print "None"


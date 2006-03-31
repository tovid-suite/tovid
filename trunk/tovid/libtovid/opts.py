#! /usr/bin/env python2.4
# opts.py

"""Provides command-line-style option definition, documentation, and parsing.

Option: Definition of an option, its arguments, default value, and docs
OptionDict: Dictionary of user-defined options

Essentially, an "option" is a named attribute/value pair, as you would
find in a typical command-line. In:

    $ tovid -format dvd -in foo.avi

'format' and 'in' are the options; each of them has an argument. In the
current implementation, the leading '-' may be omitted, or repeated.

OptionDict is a Python dictionary of attribute/value pairs, with a slim wrapper.
Use OptionDict to store a collection of options and values, for easy access.
"""
__all__ = ['Option', 'OptionDict', 'get_defaults', 'tokenize', 'parse']

# From standard library
import re
import sys
from copy import copy
import textwrap
import logging
# From libtovid
from libtovid.utils import trim, tokenize

log = logging.getLogger('libtovid.opts')

class Option:
    """A command-line-style option, expected argument formatting, default value,
    and notes on usage and purpose.
    
    For example:
        
        debug_opt = Option(
            'debug',
            'none|some|all',
            'some',
            "Amount of debugging information to display"
           )

    This defines a 'debug' option, along with a human-readable string showing
    expected argument formatting, a default value, and a string documenting the
    option's purpose and/or usage information."""

    def __init__(self, name, argformat, default=None,
                 doc='Undocumented option', alias=None):
        """Create a new option definition with the given attributes."""
        self.name = name
        self.argformat = argformat
        self.default = default
        self.doc = trim(doc)
        self.alias = alias
        # If an alias was provided, generate documentation.
        # i.e., alias=('tvsys', 'ntsc') means this option is the same as
        # giving the 'tvsys' option with 'ntsc' as the argument.
        if self.alias:
            self.doc = 'Same as -%s %s.' % alias

    def num_args(self):
        """Return the number of arguments expected by this option, or -1 if
        unlimited."""
        if self.default.__class__ == bool:
            # Boolean: no argument
            return 0
        elif self.default.__class__ == list:
            # List: unlimited arguments
            return -1
        else:
            # Unary: one argument
            return 1
    
    def is_valid(self, arg):
        """Return True if the given argument matches what's expected,
        False otherwise. Expected/allowed values are inferred from
        the argformat string.
        
        self.argformat patterns to consider:
            opta|optb|optc      # Either opta, optb, or optc
            [100-999]           # Any integer between 100 and 999
            NUM:NUM             # Any two integers separated by a colon
            VAR                 # A single string (VAR can be any all-caps word)
            VAR [, VAR]         # List of strings
            (empty)             # Boolean; no argument required

        All very experimental...
        """
        # TODO: Eliminate hackery; find a more robust way of doing this.
        # Also, pretty inefficient, since regexp matching is done every
        # time this function is called.

        # Empty argformat means boolean/no argument expected
        if self.argformat == '':
            if arg in [True, False, '']:
                return True
            else:
                return False

        # Any alphanumeric word (any string)
        if re.compile('^\w+$').match(self.argformat):
            if arg.__class__ == str:
                return True
            else:
                return False

        # Square-bracketed values are ranges, i.e. [1-99]
        match = re.compile('^\[\d+-\d+\]$').match(self.argformat)
        if match:
            # Get min/max by stripping and splitting argformat
            limits = re.split('-', match.group().strip('[]'))
            self.min = int(limits[0])
            self.max = int(limits[1])
            if int(arg) >= self.min and int(arg) <= self.max:
                return True
            else:
                return False

        # Values separated by | are mutually-exclusive
        if re.compile('[-\w]+\|[-\w]+').match(self.argformat):
            if arg in self.argformat.split('|'):
                return True
            else:
                return False

        # For now, accept any unknown cases
        return True

    def usage(self):
        """Return a string containing "usage notes" for this option."""
        usage = "-%s %s (default: %s)\n" % \
                (self.name, self.argformat, self.default)
        for line in textwrap.wrap(self.doc, 60):
            usage += '    ' + line + '\n'
        usage += '\n'
        return usage


class OptionDict:
    """A dictionary of user-configurable options."""
    def __init__(self, optiondefs=[]):
        """Create an option dictionary using the given list of Options."""
        self._data = {}
        self.defdict = {}
        for opt in optiondefs:
            self._data[opt.name] = copy(opt.default)
            self.defdict[opt.name] = opt

    def update(self, custom):
        """Update the option dictionary with custom options. options may be
        a string, a list of option/argument tokens, or a dictionary of
        option/value pairs."""
        if custom.__class__ == str or custom.__class__ == list:
            custom = self._parse(custom)
        self._data.update(custom)

    def usage(self):
        """Return a string containing usage notes for all option definitions."""
        usage = ''
        for opt in self.defdict.itervalues():
            usage += opt.usage()
        return usage

    def __getitem__(self, key):
        """Return the value indexed by key, or None if not present."""
        if key in self._data:
            return self._data[key]
        else:
            return None

    def __setitem__(self, key, value):
        self._data[key] = value

    def _parse(self, options):
        """Parse a string or list of options, returning a dictionary of those
        that match self.defdict."""
        custom = {}
        # If options is a string, tokenize it before proceeding
        if options.__class__ == str:
            options = tokenize(options)
        while len(options) > 0:
            opt = options.pop(0).lstrip('-')
            if opt not in self.defdict:
                log.error("Unrecognized option: %s. Ignoring." % opt)
            else:
                expected_args = self.defdict[opt].num_args()
                log.debug("%s expects %s args" % (opt, expected_args))
                # Is this option an alias (short-form) of another option?
                # (i.e., -vcd == -format vcd)
                if self.defdict[opt].alias:
                    key, value = self.defdict[opt].alias
                    custom[key] = value
                # No args
                elif expected_args == 0:
                    custom[opt] = True
                # One arg
                elif expected_args == 1:
                    arg = options.pop(0)
                    custom[opt] = arg
                # Comma-separated list of args
                elif expected_args < 0:
                    arglist = []
                    next = options.pop(0)
                    # If next is a keyword in defs, print error
                    if next in self.defdict:
                        log.error('"%s" option expects one or more arguments ' \
                                '(got keyword "%s")' % (opt, next))
                    # Until the next keyword is reached, add to list
                    while next and next.lstrip('-') not in self.defdict:
                        # Ignore any surrounding [ , , ]
                        arglist.append(next.lstrip('[').rstrip(',]'))
                        next = options.pop(0)
                    # Put the last token back
                    options.insert(0, next)
                    custom[opt] = arglist
        return custom
    

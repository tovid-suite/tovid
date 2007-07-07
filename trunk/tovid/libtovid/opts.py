#! /usr/bin/env python
# opts.py

"""This module is for defining command-line-style "options", and for reading
and storing their values as specified by the user. Two classes are provided:

    Option: Definition of an option, its arguments, default value, and docs
    OptionDict: An indexed collection of user-defined options

This is libtovid's alternative to 'getopt'. If you're writing a program that
needs to accept width and height values, create a list of Options with expected
arguments, default values, and documentation:

    >>> options = [
    ...    Option('width', 'NUM', 8.5, 'Width of output in inches'),
    ...    Option('height', 'NUM', 11.0, 'Height of output in inches')
    ...    ]

Nice enough, but it's not really useful until you create an OptionDict:

    >>> useropts = OptionDict(options)

Now, you can do several things. You can use useropts.usage() to display "usage
notes" for your program. But OptionDict is more than that--it also stores a
value for each option, and a simple way to get and set those values. To see a
complete list of options and their values:

    >>> useropts
    {'width': 8.5, 'height': 11.0}

Note that the default values have been filled in for you. To get and set
options individually, do this:

    >>> useropts['width']
    8.5
    >>> useropts['width'] = 5.0
    >>> useropts['width']
    5.0

Need to set a bunch of options at once? You can override values by giving a
string, list, or dictionary of options and values:

    >>> useropts.override('width 4.0 height 2.0')    # String of options
    >>> useropts
    {'width': 4.0, 'height': 2.0}
    >>> useropts.override({'width': 3.0})            # Dictionary of options
    >>> useropts
    {'width': 3.0, 'height': 2.0}

Any preceding '-'s before option names are ignored. To parse command-line
options given to your script, call update() with the list of arguments from
sys.argv[1:] (everything after the program name).
"""

__all__ = [\
    'Option',
    'OptionDict']

# From standard library
import re
from copy import copy
import textwrap
import doctest
# From libtovid
from libtovid.utils import trim, tokenize, pretty_dict
from libtovid import log

# TODO: Rethink this whole mess. Alias handling is a pain.

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

    def __init__(self, name, argformat='', default=None,
                 doc='Undocumented option', alias=None):
        """Create a new option definition with the given attributes.
        
            name:      Option name
            argformat: String describing format of expected arguments
                       (see is_valid() for examples)
            default:   Default value, if any
            doc:       Manual-page-style documentation of the option
            alias:     An ('option', 'value') equivalent for this option.

        """
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
        # Flag alias for another option
        if self.alias:
            return 0
        elif isinstance(self.default, bool):
            # Boolean: no argument
            return 0
        elif isinstance(self.default, list):
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
        if self.alias:
            usage = "-%s: Same as '-%s %s'\n" % \
                  (self.name, self.alias[0], self.alias[1])
        else:
            usage = "-%s %s (default: %s)\n" % \
                    (self.name, self.argformat, self.default)
            for line in textwrap.wrap(self.doc, 60):
                usage += '    ' + line + '\n'
        return usage

from libtovid.odict import Odict

class OptionDict(Odict):
    """An indexed collection (dictionary) of user-configurable options."""
    def __init__(self, options=None):
        """Create an option dictionary using the given list of Options."""
        Odict.__init__(self)
        # Keep a copy of the original Option definitions
        self.defdict = Odict()
        if options:
            for opt in options:
                print "Adding %s to defdict" % opt.name
                #self[opt.name] = copy(opt.default)
                self.defdict[opt.name] = opt

    def override(self, custom):
        """Override the option dictionary with custom options. options may be
        a string, a list of option/argument tokens, or a dictionary of
        option/value pairs."""
        # If custom is a string or list, turn it into a dictionary
        if custom.__class__ == str or custom.__class__ == list:
            custom = self._parse(custom)
        if custom:
            self.update(custom)

    def usage(self):
        """Return a string containing usage notes for all option definitions."""
        usage = ''
        for opt in self.defdict.values():
            usage += opt.usage()
        return usage

    def __getitem__(self, key):
        """Return the value indexed by key, or None if not present."""
        return Odict.get(self, key, None)

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
                # Is this option an alias (short-form) of another option?
                # (i.e., -vcd == -format vcd)
                if self.defdict[opt].alias:
                    key, value = self.defdict[opt].alias
                    custom[key] = value
                # No args; toggle a flag
                elif expected_args == 0:
                    custom[opt] = not custom[opt]
                # One arg; assign a value
                elif expected_args == 1:
                    arg = options.pop(0)
                    # Convert string, int, and float to proper type
                    argtype = self.defdict[opt].default.__class__
                    if argtype in [str, int, float]:
                        custom[opt] = argtype(arg)
                    else:
                        custom[opt] = arg
                # Comma-separated list of args
                elif expected_args < 0:
                    arglist = []
                    # Until next option keyword (or end of args), add to list
                    while options and options[0].lstrip('-') not in self.defdict:
                        next = options.pop(0)
                        # Ignore [ , ] in Python list syntax
                        if next not in "[,]":
                            arglist.append(next)
                    # Put the last token back if it was an option keyword
                    if next.lstrip('-') in self.defdict:
                        options.insert(0, next)
                    custom[opt] = arglist
        return custom
    
    def __str__(self):
        return pretty_dict(self)

if __name__ == '__main__':
    doctest.testmod(verbose=True)

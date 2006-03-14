#! /usr/bin/env python2.4
# opts.py

__doc__ =\
"""Provides command-line-style option definition, documentation, and parsing.
"""
__all__ = ['OptionDef', 'get_defaults', 'tokenize', 'parse']


import re
import sys
from copy import copy

from libtovid import utils
from libtovid.log import Log

log = Log('option.py')

class OptionDef:
    """A command-line-style option, expected argument formatting, default value,
    and notes on usage and purpose.
    
    For example:
        
        debug_opt = OptionDef(
            'debug',
            'none|some|all',
            'some',
            "Amount of debugging information to display"
           )

    This defines a 'debug' option, along with a human-readable string showing
    expected argument formatting, a default value, and a string documenting the
    option's purpose and/or usage information."""

    def __init__(self, name, argformat, default, doc='Undocumented option',
            alias=None):
        """Create a new option definition with the given attributes."""
        self.name = name
        self.argformat = argformat
        self.default = default
        self.doc = utils.trim(doc)
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

    def usage_string(self):
        """Return a string containing "usage notes" for this option."""
        usage = "-%s %s (default: %s)\n" % \
                (self.name, self.argformat, self.default)
        usage += "    %s\n" % self.doc
        return usage


def parse(options, optiondefs):
    """Parse a string or list of options, returning a dictionary of those that
    match optiondefs."""
    optiondict = {}
    # If options is a string, tokenize it before proceeding
    if options.__class__ == str:
        options = utils.tokenize(options)
    while len(options) > 0:
        opt = options.pop(0).lstrip('-')
        if opt not in optiondefs:
            log.error("Unrecognized option: %s. Ignoring." % opt)
        else:
            expected_args = optiondefs[opt].num_args()
            log.debug("%s expects %s args" % (opt, expected_args))
            # Is this option an alias (short-form) of another option?
            # (i.e., -vcd == -format vcd)
            if optiondefs[opt].alias:
                key, value = optiondefs[opt].alias
                optiondict[key] = value
            # No args
            elif expected_args == 0:
                optiondict[opt] = True
            # One arg
            elif expected_args == 1:
                arg = options.pop(0)
                optiondict[opt] = arg
            # Comma-separated list of args
            elif expected_args < 0:
                arglist = []
                next = options.pop(0)
                # If next is a keyword in optiondefs, print error
                if next in optiondefs:
                    log.error('"%s" option expects one or more arguments ' \
                            '(got keyword "%s")' % (opt, next))
                # Until the next keyword is reached, add to list
                while next and next.lstrip('-') not in optiondefs:
                    # Ignore any surrounding [ , , ]
                    arglist.append(next.lstrip('[').rstrip(',]'))
                    next = options.pop(0)
                # Put the last token back
                options.insert(0, next)
                optiondict[opt] = arglist
    return optiondict

class OptionDict(dict):
    """A custom dictionary of options."""
    def __init__(self, optiondefs):
        """Create an option dictionary using the given dictionary of OptionDefs."""
        dict.__init__(self)
        self.defs = optiondefs
        # Fill options from defaults
        for key, optdef in optiondefs.iteritems():
            self[key] = copy(optdef.default)

    def override(self, custom_options):
        """Update the option dictionary with custom options. options may be
        a string, a list of option/argument tokens, or a dictionary of
        option/value pairs."""
        if options.__class__ == str or options.__class__ == list:
            options = parse(options, self.defs)
        self.update(options)

    def usage(self):
        """Return a string containing usage notes for all option definitions."""
        usage = ''
        for opt in self.optiondefs.itervals():
            usage += opt.usage_string()
        return usage

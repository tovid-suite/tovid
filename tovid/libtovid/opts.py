#! /usr/bin/env python
# opts.py

# WARNING: This module is a hack in progress

__all__ = [
    'Option',
    'Usage',
    'parse',
    'validate',
]

### --------------------------------------------------------------------
import textwrap
from libtovid.odict import Odict
from libtovid.util import trim

class Option (object):
    """A command-line-style option, expected argument formatting, default value,
    and notes on usage and purpose.
    
    For example::
        
        debug_opt = Option(
            'debug',
            'none|some|all',
            'some',
            "Amount of debugging information to display"
           )

    This defines a 'debug' option, along with a human-readable string showing
    expected argument formatting, a default value, and a string documenting the
    option's purpose and/or usage information.
    """

    def __init__(self, name, argformat='', default=None,
                 doc='Undocumented option', alias=None,
                 required=False):
        """Create a new option definition with the given attributes.
        
            name
                Option name
            argformat
                String describing format of expected arguments
            default
                Default value, if any
            doc
                Manual-page-style documentation of the option
            alias
                An ('option', 'value') equivalent for this option

        """
        self.name = name
        self.argformat = argformat
        self.default = default
        self.doc = trim(doc)
        self.alias = alias
        self.required = required
        # If an alias was provided, generate documentation.
        # i.e., alias=('tvsys', 'ntsc') means this option is the same as
        # giving the 'tvsys' option with 'ntsc' as the argument.
        if self.alias:
            self.doc = 'Same as -%s %s.' % alias


    def num_args(self):
        """Return the number of arguments expected by this option,
        or -1 if unlimited.
        """
        # Flag alias for another option
        if self.alias:
            return 0
        # Boolean: no argument
        elif isinstance(self.default, bool):
            return 0
        # List: unlimited arguments
        elif isinstance(self.default, list):
            return -1
        # Unary: one argument
        else:
            return 1

    
    def __str__(self):
        """Return a string containing "usage notes" for this option.
        """
        if self.alias:
            usage = "-%s: Same as '-%s %s'\n" % \
                  (self.name, self.alias[0], self.alias[1])
        else:
            usage = "-%s %s " % (self.name, self.argformat)
            if self.required:
                usage += "(REQUIRED)\n"
            else:
                usage += "(default: %s)\n" % self.default
            for line in textwrap.wrap(self.doc, 60):
                usage += '    ' + line + '\n'
        return usage

### --------------------------------------------------------------------

class Usage (object):
    """Command-line usage definition."""
    def __init__(self, usage_string='program [options]', *options):
        """Define usage of a command-line program.
        
            usage_string
                Command-line syntax and required options
            options
                List of allowed Options

        Examples::

            usage = Usage('pytovid [options] -in FILENAME -out NAME',
                Option('in', 'FILENAME', None,
                    "Input video file, in any format."),
                Option('out', 'NAME', None,
                    "Output prefix or name."),
                Option('format', 'vcd|svcd|dvd|half-dvd|dvd-vcd', 'dvd',
                    "Make video compliant with the specified format")
            )
            print usage
            print usage.options['format']
        
        """
        self.usage_string = usage_string
        # Odict of options indexed by name
        names = [opt.name for opt in options]
        self.options = Odict(names, options)


    def __str__(self):
        """Return string-formatted usage notes.
        """
        result = "Usage: %s\n" % self.usage_string
        result += "Allowed options:\n"
        option_list = ['-' + opt.name for opt in self.options.values()]
        result += ', '.join(option_list)
        return result



### --------------------------------------------------------------------
from copy import copy

def parse(args):
    """Parse a list of arguments and return a dictionary of found options.

        args:    List of command-line arguments (such as from sys.argv)
    
    The argument list is interpreted in this way:
    
        * If it begins with '-', it's an option
        * Arguments that precede the first option are ignored
        * Anything following an option is an argument to that option
        * If there is no argument to an option, it's a flag (True if present)
        * If there's one argument to an option, it's a single string value
        * If there are multiple arguments to an option, it's a list of strings

    """
    args = copy(args)
    options = {}
    current = None
    while len(args) > 0:
        arg = args.pop(0)
        # New option
        if arg.startswith('-'):
            current = arg.lstrip('-')
            # Treat it as a flag unless we see arguments later
            options[current] = True
            
        # Argument to current option
        elif current:
            # Was a flag, now has a single value
            if options[current] is True:
                options[current] = arg
            # Was a single value, now a list
            elif type(options[current]) != list:
                options[current] = [options[current], arg]
            # Was a list, so append new value
            else:
                options[current].append(arg)
    return options


### --------------------------------------------------------------------
import re

def validate(option, arg):
    """Check whether an argument is valid for a given option.
    
        option: An Option to validate
        arg:    Candidate argument

    Expected/allowed values are inferred from the argformat string.
    
    argformat patterns to consider:
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
    if option.argformat == '':
        if arg in [True, False, '']:
            return True
        else:
            return False

    # Any alphanumeric word (any string)
    if re.compile('^\w+$').match(option.argformat):
        if arg.__class__ == str:
            return True
        else:
            return False

    # Square-bracketed values are ranges, i.e. [1-99]
    match = re.compile('^\[\d+-\d+\]$').match(option.argformat)
    if match:
        # Get min/max by stripping and splitting argformat
        limits = re.split('-', match.group().strip('[]'))
        option.min = int(limits[0])
        option.max = int(limits[1])
        if int(arg) >= option.min and int(arg) <= option.max:
            return True
        else:
            return False

    # Values separated by | are mutually-exclusive
    if re.compile('[-\w]+\|[-\w]+').match(option.argformat):
        if arg in option.argformat.split('|'):
            return True
        else:
            return False

    # For now, accept any unknown cases
    return True


import sys
if __name__ == '__main__':
    print "Option-parsing demo"

    print "You passed the following arguments:"
    print sys.argv[1:]

    print "Parsing..."
    options = parse(sys.argv[1:])

    print "Found the following options:"
    print options
    

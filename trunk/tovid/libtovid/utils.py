#! /usr/bin/env python
# utils.py
# Some short utility functions used by libtovid

__all__ = ['degunk', 'trim', 'ratio_to_float', 'subst']

import os
import sys
import string

def degunk(text):
    """Strip special characters from the given string (any that might
    cause problems when used in a filename)."""
    trans = string.maketrans(' :;?![]()\'\"','@@@@@@@@@@@')
    result = string.translate(text, trans)
    result = result.replace('@','')
    return result

def trim(text):
    """Strip leading indentation from a block of text.
    Borrowed from http://www.python.org/peps/pep-0257.html 
    """
    if not text:
        return ''
    # Split text into lines, converting tabs to spaces
    lines = text.expandtabs().splitlines()
    # Determine minimum indentation (except first line)
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special)
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            # Append line, minus indentation
            trimmed.append(line[indent:].rstrip())
    # Strip leading blank lines
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Strip trailing blank lines
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    # Return a string, rejoined with newlines
    return '\n'.join(trimmed)
    

def ratio_to_float(ratio):
    """Convert a string expressing a numeric ratio, with X and Y parts
    separated by a colon ':', into a floating-point value.
    
    For example:
        
        >>> ratio_to_float('4:3')
        1.33333
        >>>
    """
    values = ratio.split(':', 1)
    if len(values) == 2:
        return float(values[0]) / float(values[1])
    elif len(values) == 1:
        return float(values[0])
    else:
        raise Exception("ratio_to_float: too many values in ratio '%s'" % ratio)

def subst(command):
    """Do shell-style command substitution and return the output of command
    as a string (equivalent to bash `CMD` or $(CMD))."""
    output = os.popen(command, 'r').readlines()
    return ''.join(output).rstrip('\n')

def which(appname):
    """Return the full pathname of the given app, or empty string if not
    found (just like UNIX 'which')."""
    return subst('which %s' % appname)

def verify_app(self, appname):
    """Verify that the given appname is available; if not, log an error
    and exit."""
    app = which(appname)
    if not app:
        # TODO: A more friendly error message
        log.error("Cannot find '%s' in your path." % appname)
        log.error("You may need to (re)install it.")
        sys.exit()
    else:
        log.debug("Found %s" % app)


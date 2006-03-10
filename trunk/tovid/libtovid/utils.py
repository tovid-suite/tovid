#! /usr/bin/env python2.4
# utils.py
# Some short utility functions used by libtovid

__all__ = ['degunk', 'trim', 'ratio_to_float', 'subst']

import os
import sys
import string
from subprocess import *

from libtovid.log import Log

log = Log('utils.py')

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

def verify_app(appname):
    """Verify that the given appname is available; if not, log an error
    and exit."""
    app = subst('which %s' % appname)
    if not app:
        # TODO: A more friendly error message
        log.error("Cannot find '%s' in your path." % appname)
        log.error("You may need to (re)install it.")
        sys.exit()
    else:
        log.debug("Found %s" % app)


def pretty_dict(dict):
    """Return a pretty-printed dictionary, with one line for each key."""
    result = ''
    for key, value in dict.iteritems():
        # For boolean options, print Trues and omit Falses
        if value.__class__ == bool:
            if value == True:
                result += "    %s\n" % key
            else:
                pass
        # If value has spaces, quote it
        elif value.__class__ == str and ' ' in value:
            result += "    %s \"%s\"\n" % (key, value)
        # Otherwise, don't
        else:
            result += "    %s %s\n" % (key, value)
    return result


def run(command, wait=True):
    """Execute the given command, with proper stream redirection and
    verbosity. Wait for execution to finish if desired."""
    log.info("Running the following command:")
    log.info(command)
    process = Popen(command, shell=True, bufsize=1, \
            stdout=PIPE, stderr=PIPE, close_fds=True)
    if wait:
        for line in process.stdout.readlines():
            log.info(line.rstrip('\n'))
        for line in process.stderr.readlines():
            log.debug(line.rstrip('\n'))
        log.info("Waiting for process to terminate...")
        process.wait()

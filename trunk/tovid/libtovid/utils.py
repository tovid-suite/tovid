#! /usr/bin/env python2.4
# utils.py

# TODO: Categorize/reorganize these

__all__ = ['degunk', 'tokenize', 'trim', 'ratio_to_float',
    'pretty_dict', 'indent_level', 'get_code_lines', 'wait']

# From standard library
import os
import sys
import string
import shlex
from subprocess import Popen, PIPE


def degunk(text):
    """Strip special characters from the given string (any that might
    cause problems when used in a filename)."""
    trans = string.maketrans(' :;?![]()\'\"','@@@@@@@@@@@')
    result = string.translate(text, trans)
    result = result.replace('@','')
    return result

def tokenize(line):
    """Separate a text line into tokens, returning them in a list."""
    lexer = shlex.shlex(line, posix = True)
    # Rules for splitting tokens
    lexer.wordchars = lexer.wordchars + ".:-%()/"
    lexer.whitespace_split = False
    # Append all tokens to a list
    tokens = []
    while True:
        token = lexer.get_token()
        if not token:
            break
        else:
            tokens.append(token)
    return tokens

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
    separated by a colon ':', into a decimal number.
    
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

def float_to_ratio(number):
    """Convert a decimal number into an integer ratio string 'X:Y'.
    Keeps three digits of precision."""
    numerator = float(number) * 1000
    print numerator
    return "%g:1000" % numerator


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

def indent_level(line):
    """Return the number of leading whitespace characters in the line."""
    return len(line) - len(line.lstrip())

def get_code_lines(filename):
    """Return a list of all lines of code in the given file.
    Whitespace and #-style comments are ignored."""
    infile = open(filename, 'r')
    codelines = []
    for line in infile.readlines():
        if line.lstrip() and not line.lstrip().startswith('#'):
            codelines.append(line)
    infile.close()
    return codelines

def wait(seconds):
    """Print a message and pause for the given number of seconds."""
    print "Resuming in %s seconds..." % seconds
    os.system('sleep %ss' % seconds)

#! /usr/bin/env python

# ===========================================================
# tovid suite-wide constants
# ===========================================================

import re, string

def degunk(str):
    """Strip special characters from the given string (any that might
    cause problems when used in a filename)."""
    trans = string.maketrans(' :;?![]()\'\"','@@@@@@@@@@@')
    result = string.translate(str, trans)
    result = result.replace('@','')
    return result

def strip_indentation(block):
    """Strip leading indentation from a multi-line string literal.
    
    Stolen from Brett Levin:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/145672"""

    # Split block into lines
    lines = str(block).split('\n')
    if not lines: return block

    # If there's only one line, strip leading whitespace and return
    if len(lines) < 2:
        return block.lstrip(' \t')

    # Strip leading/trailing empty lines
    while not lines[0]: del lines[0]
    while not lines[-1]: del lines[-1]

    # Find first non-blank line after first line
    nonblank = 1
    while nonblank < len(lines) and not lines[nonblank]: nonblank += 1
    # Give all lines indentation relative to the first non-blank line
    ws = re.match( r'\s*',lines[nonblank]).group(0)
    if ws:
        lines = map( lambda x: x.replace(ws,'',1), lines )

    # Rejoin and return the block
    return '\n'.join(lines) + '\n'


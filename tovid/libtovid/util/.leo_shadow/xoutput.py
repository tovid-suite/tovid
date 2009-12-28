#@+leo-ver=4-thin
#@+node:eric.20090722212922.3401:@shadow output.py
"""This module does colored console output by calling color-named functions.
To use it, simply:

    >>> print(green("Looking good"))
    >>> print(red("Uh-oh..."))

It was stolen from an early version of a Gentoo module called output.py,
copyright 1998-2003 Daniel Robbins, Gentoo Technologies, Inc., distributed
under the GNU GPL v2:

# $Header: /home/cvsroot/gentoo-src/portage/pym/output.py,v 1.16 \
    2003/05/29 08:34:55 carpaski Exp $

Modified for inclusion in libtovid.
"""

__all__ = [
    'color',
    'ctext',
    'bold',
    'teal',
    'turquoise',
    'pink',
    'purple',
    'blue',
    'darkblue',
    'green',
    'darkgreen',
    'yellow',
    'brown',
    'red',
    'darkred']

codes = {
    'reset':     '\x1b[0m',
    'bold':      '\x1b[01m',
    'teal':      '\x1b[36;06m',
    'turquoise': '\x1b[36;01m',
    'pink':      '\x1b[35;01m',
    'purple':    '\x1b[35;06m',
    'blue':      '\x1b[34;01m',
    'darkblue':  '\x1b[34;06m',
    'green':     '\x1b[32;01m',
    'darkgreen': '\x1b[32;06m',
    'yellow':    '\x1b[33;01m',
    'brown':     '\x1b[33;06m',
    'red':       '\x1b[31;01m',
    'darkred':   '\x1b[31;06m'}

_do_color = True

#@+others
#@+node:eric.20090722212922.3403:color
def color(do_color):
    """Turn colored output on (True) or off (False).
    """
    global _do_color
    _do_color = do_color

#@-node:eric.20090722212922.3403:color
#@+node:eric.20090722212922.3404:ctext
def ctext(color, text):
    """Return a string containing text in the given color."""
    if _do_color:
        return codes[color] + text + codes['reset']
    else:
        return text

#@-node:eric.20090722212922.3404:ctext
#@+node:eric.20090722212922.3405:bold
def bold(text):
    return ctext('bold', text)

#@-node:eric.20090722212922.3405:bold
#@+node:eric.20090722212922.3406:teal
def teal(text):
    return ctext('teal', text)

#@-node:eric.20090722212922.3406:teal
#@+node:eric.20090722212922.3407:turquoise
def turquoise(text):
    return ctext('turquoise', text)

#@-node:eric.20090722212922.3407:turquoise
#@+node:eric.20090722212922.3408:pink
def pink(text):
    return ctext('pink', text)

#@-node:eric.20090722212922.3408:pink
#@+node:eric.20090722212922.3409:purple
def purple(text):
    return ctext('purple', text)

#@-node:eric.20090722212922.3409:purple
#@+node:eric.20090722212922.3410:blue
def blue(text):
    return ctext('blue', text)

#@-node:eric.20090722212922.3410:blue
#@+node:eric.20090722212922.3411:darkblue
def darkblue(text):
    return ctext('darkblue', text)

#@-node:eric.20090722212922.3411:darkblue
#@+node:eric.20090722212922.3412:green
def green(text):
    return ctext('green', text)

#@-node:eric.20090722212922.3412:green
#@+node:eric.20090722212922.3413:darkgreen
def darkgreen(text):
    return ctext('darkgreen', text)

#@-node:eric.20090722212922.3413:darkgreen
#@+node:eric.20090722212922.3414:yellow
def yellow(text):
    return ctext('yellow', text)

#@-node:eric.20090722212922.3414:yellow
#@+node:eric.20090722212922.3415:brown
def brown(text):
    return ctext('brown', text)

#@-node:eric.20090722212922.3415:brown
#@+node:eric.20090722212922.3416:red
def red(text):
    return ctext('red', text)

#@-node:eric.20090722212922.3416:red
#@+node:eric.20090722212922.3417:darkred
def darkred(text):
    return ctext('darkred', text)
#@-node:eric.20090722212922.3417:darkred
#@-others
#@-node:eric.20090722212922.3401:@shadow output.py
#@-leo

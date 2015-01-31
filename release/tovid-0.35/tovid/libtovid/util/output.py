"""This module does colored console output by calling color-named functions.
To use it, simply::

    print(green("Looking good"))
    print(red("Uh-oh..."))

It was stolen from an early version of a Gentoo module called ``output.py``,
copyright 1998-2003 Daniel Robbins, Gentoo Technologies, Inc., distributed
under the GNU GPL v2::

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
    'darkred',
]

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
    'darkred':   '\x1b[31;06m',
}

_do_color = True

def color(do_color):
    """Turn colored output on or off at a global level.
    
        do_color
            ``True`` to enable colored output, ``False`` to disable

    """
    global _do_color
    _do_color = do_color

def ctext(color, text):
    """Return a string containing text in the given color.
    """
    if _do_color:
        return codes[color] + text + codes['reset']
    else:
        return text

def bold(text):
    return ctext('bold', text)

def teal(text):
    return ctext('teal', text)

def turquoise(text):
    return ctext('turquoise', text)

def pink(text):
    return ctext('pink', text)

def purple(text):
    return ctext('purple', text)

def blue(text):
    return ctext('blue', text)

def darkblue(text):
    return ctext('darkblue', text)

def green(text):
    return ctext('green', text)

def darkgreen(text):
    return ctext('darkgreen', text)

def yellow(text):
    return ctext('yellow', text)

def brown(text):
    return ctext('brown', text)

def red(text):
    return ctext('red', text)

def darkred(text):
    return ctext('darkred', text)

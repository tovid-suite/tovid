#! /usr/bin/env python

__doc__ = \
"""This module defines functions for retrieving information about multimedia
standards. Any data about widely-published standards should be defined here,
for use by all libtovid modules."""

def get_resolution(format, tvsys):
    """Get the pixel resolution (x,y) for the given format and TV system."""
    width = match_std(std_widths, [format])
    height = match_std(std_heights, [format, tvsys])
    return (width, height)

def get_codec(format, tvsys):
    return match_std(std_codecs, [format])

def get_fps(format, tvsys):
    return match_std(std_fpss, [tvsys])


# Standard format/tvsystem definitions, indexed by value.  Each value
# corresponds to a list of matching standards (vcd/svcd/dvd) or TV systems
# (pal/ntsc) by keyword.
std_widths = {
    352: ['vcd', 'dvd-vcd', 'half-dvd'],
    480: ['pal', 'svcd'],
    720: ['dvd']
}
std_heights = {
    240: ['ntsc', 'vcd', 'dvd-vcd'],
    288: ['pal', 'vcd', 'dvd-vcd'],
    480: ['ntsc', 'half-dvd', 'svcd', 'dvd'],
    576: ['pal', 'half-dvd', 'svcd', 'dvd']
}
std_codecs = {
    'mpeg1': ['vcd'],
    'mpeg2': ['svcd', 'dvd-vcd', 'half-dvd', 'dvd']
}
std_fpss = {
    25.00: ['pal'],
    29.97: ['ntsc']
}


def match_std(defs, keywords):
    """Find values in defs by matching associated keywords."""
    for value in defs:
        # Make sure all keywords match
        match = True
        for key in keywords:
            # Unmatched keyword?
            if key not in defs[value]:
                match = False
                break
        # All keywords matched?
        if match:
            return value

    print "Couldn't match %s in %s" % (keywords, defs)
    return None




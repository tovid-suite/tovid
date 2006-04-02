#! /usr/bin/env python
# ffmpeg.py

__all__ = ['encode']

import logging

from libtovid.cli import Command
from libtovid.log import Log

log = logging.getLogger('libtovid.encoders.ffmpeg')

def encode(infile, options):
    """Encode infile (a MultimediaFile) with ffmpeg, using the given options."""
    cmd = Command('ffmpeg')
    cmd.append('-i "%s"' % infile.filename)
    if options['format'] in ['vcd', 'svcd', 'dvd']:
        cmd.append('-tvstd %s' % options['tvsys'])
        cmd.append('-target %s-%s' % (options['format'], options['tvsys']))
    cmd.append('-r %g' % options['fps'])
    cmd.append('-ar %s' % options['samprate'])

    # Convert scale/expand to ffmpeg's padding system
    if options['scale']:
        cmd.append('-s %sx%s' % options['scale'])
    if options['expand']:
        e_width, e_height = options['expand']
        s_width, s_height = options['scale']
        h_pad = (e_width - s_width) / 2
        v_pad = (e_height - s_height) / 2
        if h_pad > 0:
            cmd.append('-padleft %s -padright %s' % (h_pad, h_pad))
        if v_pad > 0:
            cmd.append('-padtop %s -padbottom %s' % (v_pad, v_pad))
    if options['widescreen']:
        cmd.append('-aspect 16:9')
    else:
        cmd.append('-aspect 4:3')

    cmd.append('-o "%s"' % options['out'])

    cmd.purpose = "Encoding " + infile.filename + " to " + options['format'] + \
        " " + options['tvsys'] + " format"

    cmd.run()

#! /usr/bin/env python
# ffmpeg.py

__all__ = ['get_script']

import logging

from libtovid.cli import Script

log = logging.getLogger('ffmpeg.py')

def get_script(infile, options):
    """Return a Script to encode infile (a MediaFile) with ffmpeg, using
    the given options (an OptionDict)."""

    script = Script('ffmpeg')

    # Build the ffmpeg command as a string
    cmd = 'ffmpeg'
    cmd += ' -i "%s"' % infile.filename
    if options['format'] in ['vcd', 'svcd', 'dvd']:
        cmd += ' -tvstd %s' % options['tvsys']
        cmd += ' -target %s-%s' % \
                (options['format'], options['tvsys'])
    cmd += ' -r %s' % options['fps']
    cmd += ' -ar %s' % options['samprate']
    # Convert scale/expand to ffmpeg's padding system
    if options['scale']:
        cmd += ' -s %sx%s' % options['scale']
    if options['expand']:
        e_width, e_height = options['expand']
        s_width, s_height = options['scale']
        h_pad = (e_width - s_width) / 2
        v_pad = (e_height - s_height) / 2
        if h_pad > 0:
            cmd += ' -padleft %s -padright %s' % (h_pad, h_pad)
        if v_pad > 0:
            cmd += ' -padtop %s -padbottom %s' % (v_pad, v_pad)
    if options['widescreen']:
        cmd += ' -aspect 16:9'
    else:
        cmd += ' -aspect 4:3'
    cmd += ' -o "%s"' % options['out']

    script.append(cmd)
    script.run()
    return script

#! /usr/bin/env python2.4
# ffmpeg.py

from libtovid.utils import verify_app, run

verify_app('ffmpeg')

def encode(infile, outfile, options):
    """Encode infile to outfile with ffmpeg, using the given options."""
    cmd = 'ffmpeg -i "%s" ' % infile
    if options['format'] in ['vcd', 'svcd', 'dvd']:
        cmd += ' -tvstd %s ' % options['tvsys']
        cmd += ' -target %s-%s ' % \
                (options['format'], options['tvsys'])
    cmd += ' -r %g ' % options['fps']
    cmd += ' -ar %s ' % options['samprate']

    # Convert scale/expand to ffmpeg's padding system
    if options['scale']:
        cmd += ' -s %sx%s ' % options['scale']
    if options['expand']:
        e_width, e_height = options['expand']
        s_width, s_height = options['scale']
        h_pad = (e_width - s_width) / 2
        v_pad = (e_height - s_height) / 2
        if h_pad > 0:
            cmd += ' -padleft %s -padright %s ' % (h_pad, h_pad)
        if v_pad > 0:
            cmd += ' -padtop %s -padbottom %s ' % (v_pad, v_pad)
    if options['widescreen']:
        cmd += ' -aspect 16:9 '
    else:
        cmd += ' -aspect 4:3 '

    run(cmd)

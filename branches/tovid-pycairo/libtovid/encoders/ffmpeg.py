#! /usr/bin/env python
# ffmpeg.py

__all__ = ['get_script']

from libtovid.cli import Script, Arg
from libtovid.log import Log

log = Log('libtovid.encoders.ffmpeg')

def get_script(infile, options):
    """Return a Script to encode infile (a MediaFile) with ffmpeg, using
    the given options (an OptionDict)."""

    script = Script('ffmpeg')

    # Build the ffmpeg command as a string
    cmd = Arg('ffmpeg')
    cmd.add('-i', infile.filename)
    if options['format'] in ['vcd', 'svcd', 'dvd']:
        cmd.add('-tvstd', options['tvsys'])
        cmd.add('-target', '%s-%s' % \
                (options['tvsys'], options['format']))
    
    cmd.add('-r', options['fps'])
    cmd.add('-ar', options['samprate'])
    # Convert scale/expand to ffmpeg's padding system
    if options['scale']:
        cmd.add('-s', '%sx%s' % options['scale'])
    if options['expand']:
        e_width, e_height = options['expand']
        s_width, s_height = options['scale']
        h_pad = (e_width - s_width) / 2
        v_pad = (e_height - s_height) / 2
        if h_pad > 0:
            cmd.add('-padleft', h_pad)
            cmd.add('-padright', h_pad)
        if v_pad > 0:
            cmd.add('-padtop', v_pad)
            cmd.add('-padbottom', v_pad)
    if options['widescreen']:
        cmd.add('-aspect', '16:9')
    else:
        cmd.add('-aspect', '4:3')
    
    cmd.add(options['out'])

    script.append(str(cmd))
    return script
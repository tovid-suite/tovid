#! /usr/bin/env python2.4
# mencoder.py

__all__ = ['encode']

from libtovid.cli import Command
from libtovid.log import Log

log = Log('mencoder.py')


def encode(infile, options):
    """Encode infile (a MultimediaFile) with mencoder, using the given options."""
    cmd = Command('mencoder')
    cmd.append('"%s" -o "%s"' % (infile.filename, options['out']))
    cmd.append('-oac lavc -ovc lavc -of mpeg')
    # Format
    if options['format'] in ['vcd', 'svcd']:
        cmd.append('-mpegopts format=x%s' % options['format'])
    else:
        cmd.append('-mpegopts format=dvd')
    
    # Audio settings
    # Adjust sampling rate
    # TODO: Don't resample unless needed
    cmd.append('-srate %s' % options['samprate'])
    cmd.append('-af lavcresample=%s' % options['samprate'])

    # Video codec
    if options['format'] == 'vcd':
        lavcopts = 'vcodec=mpeg1video'
    else:
        lavcopts = 'vcodec=mpeg2video'
    # Audio codec
    if options['format'] in ['vcd', 'svcd']:
        lavcopts += ':acodec=mp2'
    else:
        lavcopts += ':acodec=ac3'

    lavcopts += ':abitrate=%s:vbitrate=%s' % \
            (options['abitrate'], options['vbitrate'])
    # Maximum video bitrate
    lavcopts += ':vrc_maxrate=%s' % options['vbitrate']
    if options['format'] == 'vcd':
        lavcopts += ':vrc_buf_size=327'
    elif options['format'] == 'svcd':
        lavcopts += ':vrc_buf_size=917'
    else:
        lavcopts += ':vrc_buf_size=1835'
    # Set appropriate target aspect
    if options['widescreen']:
        lavcopts += ':aspect=16/9'
    else:
        lavcopts += ':aspect=4/3'
    # Put all lavcopts together
    cmd.append('-lavcopts %s' % lavcopts)

    # FPS
    if options['tvsys'] == 'pal':
        cmd.append('-ofps 25/1')
    elif options['tvsys'] == 'ntsc':
        cmd.append('-ofps 30000/1001') # ~= 29.97

    # Scale/expand to fit target frame
    if options['scale']:
        vfilter = 'scale=%s:%s' % options['scale']
        # Expand is not done unless also scaling
        if options['expand']:
            vfilter += ',expand=%s:%s' % options['expand']
        cmd.append('-vf ' + vfilter)

    cmd.purpose = "Encoding " + infile.filename + " to " + \
       options['format'] + " " + options['tvsys'] + " format"
    cmd.run()

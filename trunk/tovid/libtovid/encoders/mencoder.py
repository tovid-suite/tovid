#! /usr/bin/env python
# mencoder.py

__all__ = ['get_script']

from libtovid.cli import Script, Command
from libtovid import log

def get_script(infile, options):
    """Return a Script to encode infile (a MediaFile) with mencoder,
    using the given options (an OptionDict)."""

    script = Script('mencoder')

    # Build the mencoder command
    cmd = Command('mencoder')
    cmd.add(infile.filename,
            '-o', options['out'],
            '-oac', 'lavc',
            '-ovc', 'lavc',
            '-of', 'mpeg')
    # Format
    cmd.add('-mpegopts')
    
    if options['format'] in ['vcd', 'svcd']:
        cmd.add('format=x%s' % options['format'])
    else:
        cmd.add('format=dvd')
    
    # Audio settings
    # Adjust sampling rate
    # TODO: Don't resample unless needed
    cmd.add('-srate', options['samprate'],
            '-af', 'lavcresample=%s' % options['samprate'])

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
    cmd.add('-lavcopts', lavcopts)

    # FPS
    if options['tvsys'] == 'pal':
        cmd.add('-ofps', '25/1')
    elif options['tvsys'] == 'ntsc':
        cmd.add('-ofps', '30000/1001') # ~= 29.97

    # Scale/expand to fit target frame
    if options['scale']:
        vfilter = 'scale=%s:%s' % options['scale']
        # Expand is not done unless also scaling
        if options['expand']:
            vfilter += ',expand=%s:%s' % options['expand']
        cmd.add('-vf', vfilter)

    # Add the Command to the Script
    script.append(cmd)
    return script

#! /usr/bin/env python2.4
# mencoder.py

from libtovid.utils import verify_app, run

verify_app('mencoder')

def encode(infile, outfile, options):
    """Encode infile to outfile with mencoder, using the given options."""
    cmd = 'mencoder "%s" -o "%s"' % (infile, outfile)
    cmd += ' -oac lavc -ovc lavc -of mpeg '
    # Format
    if options['format'] in ['vcd', 'svcd']:
        cmd += ' -mpegopts format=x%s ' % options['format']
    else:
        cmd += ' -mpegopts format=dvd '
    
    # Audio settings
    # Adjust sampling rate
    # TODO: Don't resample unless needed
    cmd += ' -srate %s -af lavcresample=%s ' % \
            (options['samprate'], options['samprate'])

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
    cmd += ' -lavcopts %s ' % lavcopts

    # FPS
    if options['tvsys'] == 'pal':
        cmd += ' -ofps 25/1 '
    elif options['tvsys'] == 'ntsc':
        cmd += ' -ofps 30000/1001 ' # ~= 29.97

    # Scale/expand to fit target frame
    if options['scale']:
        cmd += ' -vf scale=%s:%s' % options['scale']
    if options['expand']:
        cmd += ',expand=%s:%s ' % options['expand']
    run(cmd)


        

#! /usr/bin/env python
# mpeg2enc.py

__all__ = ['get_script']

import os

from libtovid.cli import Script, Command, Pipe
from libtovid.utils import float_to_ratio
from libtovid import log
from libtovid.encoders.common import *
import libtovid.standards

"""options used by encoders:
format
tvsys
out
filters

fps
samprate
scale
expand
widescreen
abitrate
vbitrate
"""

def get_script(infile, options):
    """Return a Script to encode infile (a MediaFile) with mpeg2enc,
    using the given options (an OptionDict)."""
    log.warning("This encoder is very experimental, and may not work.")

    script = Script('mpeg2enc')

    outname = options['out']
    # YUV raw video FIFO, for piping video from mplayer to mpeg2enc
    yuvfile = '%s.yuv' % outname
    try:
        os.remove(yuvfile)
    except:
        pass
    os.mkfifo(yuvfile)
    
    # Filenames for intermediate streams (ac3/m2v etc.)
    # Appropriate suffix for audio stream
    # TODO: use standards
    if options['format'] in ['vcd', 'svcd']:
        audiofile = '%s.mpa' % outname
    else:
        audiofile = '%s.ac3' % outname
    # Appropriate suffix for video stream
    if options['format'] == 'vcd':
        videofile = '%s.m1v' % outname
    else:
        videofile = '%s.m2v' % outname
    # Do audio
    script.append(encode_audio(infile, audiofile, options))
    # Do video
    script.append(rip_video(infile, yuvfile, options))
    script.append(encode_video(infile, yuvfile, videofile, options))
    # Combine audio and video
    script.append(mplex_streams(videofile, audiofile, outname, options))
    return script
    
def rip_video(infile, yuvfile, options):
    """Rip input video to yuv4mpeg format, and write to yuvfile."""
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = Command('mplayer')
    cmd.add(infile.filename)
    cmd.add('-vo', 'yuv4mpeg:file=%s' % yuvfile)
    cmd.add('-nosound', '-benchmark', '-noframedrop')
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd.add('-noautosub')
    if options['scale']:
        cmd.add('-vf', 'scale=%s:%s' % options['scale'])
    if options['expand']:
        cmd.add('-vf-add', 'expand=%s:%s' % options['expand'])
    # Filters
    filters = options['filters']
    if 'denoise' in filters:
        cmd.add('-vf-add', 'hqdn3d')
    if 'contrast' in filters:
        cmd.add('-vf-add', 'pp=al:f')
    if 'deblock' in filters:
        cmd.add('-vf-add', 'pp=hb/vb')
    # Do ripping in background
    cmd.bg = True
    return cmd


def encode_video(infile, yuvfile, videofile, options):
    """Encode the yuv4mpeg stream to the given format and TV system."""
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    cat = Command('cat', yuvfile)
    mpeg2enc = Command('mpeg2enc')
    
    # TV system
    if options['tvsys'] == 'pal':
        mpeg2enc.add('-F', '3', '-n', 'p')
    elif options['tvsys'] == 'ntsc':
        mpeg2enc.add('-F', '4', '-n', 'n')

    # Format
    format = options['format']
    if format == 'vcd':
        mpeg2enc.add('-f', '1')
    elif format == 'svcd':
        mpeg2enc.add('-f', '4')
    elif 'dvd' in format:
        mpeg2enc.add('-f', '8')
        
    # Aspect ratio
    if options['widescreen']:
        mpeg2enc.add('-a', '3')
    else:
        mpeg2enc.add('-a', '2')
    mpeg2enc.add('-o', videofile)

    # Adjust framerate if necessary
    if infile.video.fps != options['fps']:
        log.info("Adjusting framerate")
        yuvfps = Command('yuvfps', '-r', float_to_ratio(options['fps']))
        return Pipe(cat, yuvfps, mpeg2enc)
    else:
        return Pipe(cat, mpeg2enc)

def mplex_streams(vstream, astream, outfile, options):
    """Multiplex the audio and video streams."""
    cmd = Command('mplex')
    format = options['format']
    if format == 'vcd':
        cmd.add('-f', '1')
    elif format == 'dvd-vcd':
        cmd.add('-V', '-f', '8')
    elif format == 'svcd':
        cmd.add('-V', '-f', '4', '-b', '230')
    elif format == 'half-dvd':
        cmd.add('-V', '-f', '8', '-b', '300')
    elif format == 'dvd':
        cmd.add('-V', '-f', '8', '-b', '400')
    # elif format == 'kvcd':
    #   cmd += ' -V -f 5 -b 350 -r 10800 '
    cmd.add(vstream, astream, '-o', outfile)
    return cmd

#! /usr/bin/env python
# mpeg2enc.py

__all__ = ['get_script']

import os

from libtovid.cli import Script
from libtovid.utils import float_to_ratio
from libtovid.log import Log

log = Log('libtovid.encoders.mpeg2enc')

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
    log.warn("This encoder is very experimental, and may not work.")

    script = Script('mpeg2enc', options)

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
    cmd = 'mplayer'
    cmd += ' "%s"' % infile.filename
    cmd += ' -vo yuv4mpeg:file=%s' % yuvfile
    cmd += ' -nosound -benchmark -noframedrop'
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd += ' -noautosub'
    if options['scale']:
        cmd += ' -vf scale=%s:%s' % options['scale']
    if options['expand']:
        cmd += ' -vf-add expand=%s:%s' % options['expand']
    # Filters
    filters = options['filters']
    if 'denoise' in filters:
        cmd += ' -vf-add hqdn3d'
    if 'contrast' in filters:
        cmd += ' -vf-add pp=al:f'
    if 'deblock' in filters:
        cmd += ' -vf-add pp=hb/vb'
    # Background ripping
    return cmd + ' &'


def encode_video(infile, yuvfile, videofile, options):
    """Encode the yuv4mpeg stream to the given format and TV system."""
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    
    cmd = 'mpeg2enc'
    # TV system
    if options['tvsys'] == 'pal':
        cmd += ' -F 3 -n p'
    elif options['tvsys'] == 'ntsc':
        cmd += ' -F 4 -n n'
    # Format
    format = options['format']
    if format == 'vcd':
        cmd += ' -f 1'
    elif format == 'svcd':
        cmd += ' -f 4'
    elif 'dvd' in format:
        cmd += ' -f 8'
    # Aspect ratio
    if options['widescreen']:
        cmd += ' -a 3'
    else:
        cmd += ' -a 2'
    cmd += ' -o "%s"' % videofile

    # Adjust framerate if necessary
    # FIXME: Can infile.video None?
    if infile.video != None:
        if infile.video.spec['fps'] != options['fps']:
            log.info("Adjusting framerate")
            yuvcmd = 'yuvfps -r %s' % float_to_ratio(options['fps'])
            cmd = yuvcmd + ' | ' + cmd
    else:
        pass
    
    # Pipe the .yuv file into mpeg2enc
    catcmd = 'cat "%s" | ' % yuvfile
    return catcmd + cmd

def encode_audio(infile, audiofile, options):
    """Encode the audio stream in infile to the target format."""
    if options['format'] in ['vcd', 'svcd']:
        acodec = 'mp2'
    else:
        acodec = 'ac3'
    cmd = 'ffmpeg '
    # If infile was provided, encode it
    if infile:
        cmd += ' -i "%s"' % infile.filename
    # Otherwise, generate 4-second silence
    else:
        cmd += ' -f s16le -i /dev/zero -t 4'
    cmd += ' -ac 2 -ab 224'
    cmd += ' -ar %s' % options['samprate']
    cmd += ' -acodec %s' % acodec
    cmd += ' -y "%s"' % audiofile
    return cmd

def mplex_streams(vstream, astream, outfile, options):
    """Multiplex the audio and video streams."""
    cmd = 'mplex'
    format = options['format']
    if format == 'vcd':
        cmd += ' -f 1'
    elif format == 'dvd-vcd':
        cmd += ' -V -f 8'
    elif format == 'svcd':
        cmd += ' -V -f 4 -b 230'
    elif format == 'half-dvd':
        cmd += ' -V -f 8 -b 300'
    elif format == 'dvd':
        cmd += ' -V -f 8 -b 400'
    # elif format == 'kvcd':
    #   cmd += ' -V -f 5 -b 350 -r 10800 '
    cmd += ' "%s" "%s" -o "%s"' % (vstream, astream, outfile)
    return cmd

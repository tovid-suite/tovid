#! /usr/bin/env python

# tools.py

# An interface to some external command-line tools for
# encoding/multiplexing video.

# Sort of a scratch-pad of functions at the moment

from Target import *

"""
Notes:


Command-line option variables:

# Filters
mplayer:
SUBTITLES
    -noautosub
    -sub FILE
YUV4MPEG_ILACE
    ''
    :interlaced
    :interlaced_bf
VF_PRE
    ''
    -vf-pre il=d:d

VID_SCALE
    ''
    -vf-add scale=$INNER_WIDTH:$INNER_HEIGHT
+   -vf-add expand=$TGT_WIDTH:$TGT_HEIGHT

VF_POST
    ''
    -vf-pre il=i:i
MPLAYER_OPTS
    (user-defined)

YUVDENOISE
    ''
    yuvdenoise |
ADJUST_FPS
    ''
    yuvfps -s $FORCE_FPSRATIO -r $TGT_FPSRATIO $VERBOSE |
    yuvfps -r $TGT_FPSRATIO $VERBOSE |


mpeg2enc
DISC_SIZE
    ''
    '4500'
    '700'
    (user-defined)

NONVIDEO_BITRATE
MTHREAD

MPEG2_FMT
+   !vcd: -b $VID_BITRATE

MPEG2_QUALITY
    vcd: -4 2 -2 1 -H
    other: -4 2 -2 1 -q $QUANT -H
"""

def get_mplayer_cmd(infile, format, tvsys, filters = []):
    """Get mplayer command-line for making a video compliant with the given
    format and tvsys, while applying named custom filters, writing output to
    stream.yuv.
    
    TODO: Custom mplayer options, subtitles, interlacing, safe area, corresp.
    to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE, etc.
    
    TODO: Determine aspect ratio and scale appropriately (in a separate
    function, preferably)."""


    cmd = 'mplayer -nosound -vo yuv4mpeg "%s" ' % infile
    # Get resolution
    tgt = Target(format, tvsys)
    cmd += '-vf scale=%s:%s ' % tgt.get_resolution()
    # Filters
    if 'denoise' in filters:
        cmd += '-vf-add hqdn3d '
    if 'contrast' in filters:
        cmd += '-vf-add pp=al:f '
    if 'deblock' in filters:
        cmd += '-vf-add pp=hb/vb '

    return cmd


def get_mpeg2enc_cmd(format, tvsys, aspect = '4:3'):
    """Get mpeg2enc command-line suitable for encoding a video stream to the
    given format and TV system, at the given aspect ratio (if the format
    supports it).
    
    TODO: Control over quality (bitrate/quantization) and disc split size,
    corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc."""

    cmd = 'cat stream.yuv | mpeg2enc '
    if tvsys == 'pal':
        cmd += '-F 3 -n p '
    elif tvsys == 'ntsc':
        cmd += '-F 4 -n n '

    if format == 'vcd':
        cmd += '-f 1 '
    elif format == 'svcd':
        cmd += '-f 4 '
    elif 'dvd' in format:
        cmd += '-f 8 '

    if aspect == '4:3':
        cmd += '-a 2 '
    elif aspect == '16:9':
        cmd += '-a 3 '

    return cmd


def get_mplex_cmd(format, tvsys):
    """Get mplex command-line suitable for muxing streams with the given format
    and TV system."""

    cmd = 'mplex '
    if format == 'vcd':
        cmd += '-f 1 '
    elif format == 'dvd-vcd':
        cmd += '-V -f 8 '
    elif format == 'svcd':
        cmd += '-V -f 4 -b 230 '
    elif format == 'half-dvd':
        cmd += '-V -f 8 -b 300 '
    elif format == 'dvd':
        cmd += '-V -f 8 -b 400 '
    # elif format == 'kvcd':
    #   cmd += '-V -f 5 -b 350 -r 10800 '

    return cmd



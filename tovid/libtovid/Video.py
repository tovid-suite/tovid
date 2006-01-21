#! /usr/bin/env python

# Video generator module

__doc__ = \
"""This module generates MPEG video files from TDL Video element definitions."""

def generate(video):
    """Generate a video element by encoding an input file to a target
    standard."""
    format = video.get('format')
    tvsys = video.get('tvsys')
    aspect = video.get('aspect')
    
    mplayer_cmd = get_mplayer_cmd(video.get('in'), format, tvsys)
    mpeg2enc_cmd = get_mpeg2enc_cmd(format, tvsys, aspect)
    mplex_cmd = get_mplex_cmd(format, tvsys)
    
    # TODO: Execute each command, with proper stream redirection and
    # other nonsense required for correct logging
    print "mplayer command:"
    print mplayer_cmd
    print "mpeg2enc command:"
    print mpeg2enc_cmd
    print "mplex command:"
    print mplex_cmd


# Standard format/tvsystem definitions, indexed by value.  Each value
# corresponds to a list of matching standards (vcd/svcd/dvd) or TV systems
# (pal/ntsc) by keyword.
std_widths = {
    352: ['vcd', 'dvd-vcd', 'half-dvd'],
    480: ['pal', 'svcd'],
    720: ['dvd']
}
std_heights = {
    240: ['ntsc', 'vcd', 'dvd-vcd'],
    288: ['pal', 'vcd', 'dvd-vcd'],
    480: ['ntsc', 'half-dvd', 'svcd', 'dvd'],
    576: ['pal', 'half-dvd', 'svcd', 'dvd']
}
std_codecs = {
    'mpeg1': ['vcd'],
    'mpeg2': ['svcd', 'dvd-vcd', 'half-dvd', 'dvd']
}
std_fpss = {
    25.00: ['pal'],
    29.97: ['ntsc']
}

def match_std(defs, keywords):
    """Find values in defs by matching associated keywords."""
    for value in defs:
        # Make sure all keywords match
        match = True
        for key in keywords:
            # Unmatched keyword?
            if key not in defs[value]:
                match = False
                break
        # All keywords matched?
        if match:
            return value

    print "Couldn't match %s in %s" % (keywords, defs)
    return None


def get_resolution(format, tvsys):
    """Get the pixel resolution (x,y) for the given format and TV system."""
    width = match_std(std_widths, [format])
    height = match_std(std_heights, [format, tvsys])
    return (width, height)

# codec = match_std(std_codecs, [format])
# fps = match_std(std_fpss, [tvsys])



def get_mplayer_cmd(infile, format, tvsys, filters = []):
    """Get mplayer command-line for making a video compliant with the given
    format and tvsys, while applying named custom filters, writing output to
    stream.yuv."""
    
    # TODO: Custom mplayer options, subtitles, interlacing, safe area, corresp.
    # to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE, etc.
    
    # TODO: Determine aspect ratio and scale appropriately (in a separate
    # function, preferably).

    cmd = 'mplayer -nosound -vo yuv4mpeg "%s" ' % infile
    # Get resolution
    cmd += '-vf scale=%s:%s ' % get_resolution(format, tvsys)
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
    supports it)."""
    
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.

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

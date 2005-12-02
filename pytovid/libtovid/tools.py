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

def get_mplayer_opts(format, tvsys, filters = []):

    opts = ''

    if 'denoise' in filters:
        opts += '-vf-add hqdn3d '
    if 'contrast' in filters:
        opts += '-vf-add pp=al:f '
    if 'deblock' in filters:
        opts += '-vf-add pp=hb/vb '


def get_mpeg2enc_opts(format, tvsys, aspect = '4:3'):
    """Get mpeg2enc command-line options suitable for encoding
    a video stream to the given format and TV system, at the given
    aspect ratio (if the format supports it).
    
    Not yet implemented: Control over quality (bitrate/quantization)
    and disc split size."""

    opts = ''
    if tvsys == 'pal':
        opts += '-F 3 -n p'
    elif tvsys == 'ntsc':
        opts += '-F 4 -n n'

    if format == 'vcd':
        opts += '-f 1 '
    elif format == 'svcd':
        opts += '-f 4 '
    elif 'dvd' in format:
        opts += '-f 8 '

    if aspect == '4:3':
        opts += '-a 2 '
    elif aspect == '16:9':
        opts += '-a 3 '

    return opts


def get_mplex_opts(format, tvsys):
    """Get mplex command-line options suitable for muxing
    streams with the given format and TV system."""

    opts = ''
    if format == 'vcd':
        opts += '-f 1 '
    elif format == 'dvd-vcd':
        opts += '-V -f 8 '
    elif format == 'svcd':
        opts += '-V -f 4 -b 230 '
    elif format == 'half-dvd':
        opts += '-V -f 8 -b 300 '
    elif format == 'dvd':
        opts += '-V -f 8 -b 400 '
    # elif format == 'kvcd':
    #   opts += '-V -f 5 -b 350 -r 10800 '

    return opts



#! /usr/bin/env python

# Video generator module

from libtovid.Option import OptionDef

# TODO: Eliminate some of the redundancy of this module; integrate related
# encoding/muxing functions into a class or other container, with the aim
# of making it as simple as possible to write alternative backends (easy
# access to data about standard targets, about input video specs, etc.)

__doc__ = \
"""This module generates MPEG video files from TDL Video element definitions."""


# Video TDL element definition
# Options pertaining to video format and postprocessing
optiondefs = {
    # New options to (eventually) replace -vcd, -pal etc.
    'format':
        OptionDef('format', 'vcd|svcd|dvd|half-dvd|dvd-vcd', 'dvd',
        """Make video compliant with the specified format"""),

    'tvsys':
        OptionDef('tvsys', 'ntsc|pal', 'ntsc',
        """Make the video compliant with the specified TV system"""),

    # Deprecated options. Need to find a way to
    # mark options as deprecated, so the parser can
    # warn the user.
    'vcd':
        OptionDef('vcd', '', False),
    'svcd':
        OptionDef('svcd', '', False),
    'dvd':
        OptionDef('dvd', '', False),
    'half-dvd':
        OptionDef('half-dvd', '', False),
    'dvd-vcd':
        OptionDef('dvd-vcd', '', False),
    'ntsc':
        OptionDef('ntsc', '', False),
    'ntscfilm':
        OptionDef('ntscfilm', '', False),
    'pal':
        OptionDef('pal', '', False),

    # Other options
    'in':           OptionDef('in', 'FILENAME', None),
    'out':          OptionDef('out', 'FILENAME', None),

    'aspect':       OptionDef('aspect', 'WIDTH:HEIGHT', "4:3",
        """Force the input video to be the given aspect ratio, where WIDTH
        and HEIGHT are integers."""),

    'quality':      OptionDef('quality', '[1-10]', 8,
        """Desired output quality, on a scale of 1 to 10, with 10 giving
        the best quality at the expense of a larger output file. Output
        size can vary by approximately a factor of 4 (that is, -quality 1
        output can be 25% the size of -quality 10 output). Your results may
        vary."""),
    
    'vbitrate':     OptionDef('vbitrate', '[0-9800]', 6000,
        """Maximum bitrate to use for video (in kbits/sec). Must be within
        allowable limits for the given format. Overrides default values.
        Ignored for VCD."""),

    'abitrate':     OptionDef('abitrate', '[0-1536]', 224,
        """Encode audio at NUM kilobits per second.  Reasonable values
        include 128, 224, and 384. The default is 224 kbits/sec, good
        enough for most encodings. The value must be within the allowable
        range for the chosen disc format; Ignored for VCD, which must be
        224."""),

    'safe':         OptionDef('safe', '[0-100]%', "100%",
        """Fit the video within a safe area defined by PERCENT. For
        example, '-safe 90%' will scale the video to 90% of the
        width/height of the output resolution, and pad the edges with a
        black border. Use this if some of the picture is cut off when
        played on your TV."""),

    'interlaced':   OptionDef('interlaced', '', False,
        """Do interlaced encoding of the input video. Use this option if
        your video is interlaced, and you want to preserve as much picture
        quality as possible. Ignored for VCD."""),

    'deinterlace':  OptionDef('deinterlace', '', False,
        """Use this option if your source video is interlaced. You can
        usually tell if you can see a bunch of horizontal lines when you
        pause the video during playback. If you have recorded a video from
        TV or your VCR, it may be interlaced. Use this option to convert to
        progressive (non-interlaced) video. This option is DEPRECATED, and
        will probably be ditched in favor of interlaced encoding, which is
        better in almost every way."""),

    'subtitles':    OptionDef('subtitles', 'FILE', None,
        """Get subtitles from FILE and encode them into the video.
        WARNING: This hard-codes the subtitles into the video, and you
        cannot turn them off while viewing the video. By default, no
        subtitles are loaded. If your video is already compliant with the
        chosen output format, it will be re-encoded to include the
        subtitles."""),

    'normalize':    OptionDef('normalize', '', False,
        """Normalize the volume of the audio. Useful if the audio is too
        quiet or too loud, or you want to make volume consistent for a
        bunch of videos."""),
    'chapters':     OptionDef('chapters', 'TIME [, TIME]', [],
        """Put chapter breaks at the specified times (HH:MM:SS).""")

}

    
def generate(video):
    """Generate a video element by encoding an input file to a target
    standard."""
    
    mplayer_cmd = get_mplayer_cmd(video)
    mpeg2enc_cmd = get_mpeg2enc_cmd(video)
    mplex_cmd = get_mplex_cmd(video)
    
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



def get_mplayer_cmd(video):
    """Get mplayer command-line for making a video compliant with the given
    format and tvsys, while applying named custom filters, writing output to
    stream.yuv."""
    infile = video.get('in')
    format = video.get('format')
    tvsys = video.get('tvsys')
    filters = video.get('filters')
    
    # TODO: Custom mplayer options, subtitles, interlacing, safe area, corresp.
    # to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE, etc.
    
    # TODO: Determine aspect ratio and scale appropriately (in a separate
    # function, preferably).

    cmd = 'mplayer "%s" ' % infile
    cmd += ' -vo yuv4mpeg -nosound -benchmark -noframedrop '
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd += ' -noautosub '
    # TODO: Avoid scaling unless necessary
    cmd += ' -vf scale=%s:%s ' % get_resolution(format, tvsys)
    # Filters
    if 'denoise' in filters:
        cmd += ' -vf-add hqdn3d '
    if 'contrast' in filters:
        cmd += ' -vf-add pp=al:f '
    if 'deblock' in filters:
        cmd += ' -vf-add pp=hb/vb '

    return cmd


def get_mpeg2enc_cmd(video):
    """Get mpeg2enc command-line suitable for encoding a video stream to the
    given format and TV system, at the given aspect ratio (if the format
    supports it)."""
    format = video.get('format')
    tvsys = video.get('tvsys')
    aspect = video.get('aspect')
    outfile = '%s.m2v' % video.get('out')

    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE

    cmd = 'cat stream.yuv | mpeg2enc '
    if tvsys == 'pal':
        cmd += ' -F 3 -n p '
    elif tvsys == 'ntsc':
        cmd += ' -F 4 -n n '

    if format == 'vcd':
        cmd += ' -f 1 '
    elif format == 'svcd':
        cmd += ' -f 4 '
    elif 'dvd' in format:
        cmd += ' -f 8 '

    if aspect == '4:3':
        cmd += ' -a 2 '
    elif aspect == '16:9':
        cmd += ' -a 3 '
    cmd += ' -o "%s"' % outfile

    return cmd


def get_mplex_cmd(video):
    """Get mplex command-line suitable for muxing streams with the given format
    and TV system."""
    format = video.get('format')

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


def ratio_to_float(ratio):
    """Convert a string expressing a numeric ratio, with X and Y parts
    separated by a colon ':', into a floating-point value.
    
    For example:
        
        >>> ratio_to_float('4:3')
        1.33333
        >>>
    """
    values = ratio.split(':', 1)
    if len(values) == 2:
        return float(values[0]) / float(values[1])
    elif len(values) == 1:
        return float(values[0])
    else:
        return 1.0

    
def get_mencoder_cmd(video):
    """Get mencoder command-line suitable for encoding the given video to
    its target format."""
    format = video.get('format')
    tvsys = video.get('tvsys')

    cmd = 'mplayer -oac lavc -ovc lavc -of mpeg '
    if format in ['vcd', 'svcd']:
        cmd += ' -mpegopts format=x%s ' % format
    else:
        cmd += ' -mpegopts format=dvd '

    # TODO: Move all aspect/scaling stuff into a separate
    # function, so all backends can benefit from it

    # Determine correct scaling and target aspect ratio
    src_aspect = ratio_to_float(video.get('aspect'))
    tgt_width, tgt_height = get_resolution(format, tvsys)
    
    # Use anamorphic widescreen for any video 16:9 or wider
    if src_aspect >= 1.7 and format == 'dvd':
        cmd += ' -vaspect=16/9 '
        tgt_aspect = 16.0/9.0
    else:
        cmd += ' -vaspect=4/3 '
        tgt_aspect = 4.0/3.0
    
    # If aspect matches target, no letterboxing is necessary
    # (Match within a tolerance of 0.05)
    if abs(src_aspect - tgt_aspect) < 0.05:
        inner_width = tgt_width
        inner_height = tgt_height
        letterbox = False
    # If aspect is wider than target, letterbox vertically
    elif src_aspect > tgt_aspect:
        inner_width = tgt_width
        inner_height = tgt_height * tgt_aspect / src_aspect
        letterbox = True
    # Otherwise (rare), letterbox horizontally
    else:
        inner_width = tgt_width * src_aspect / tgt_aspect
        inner_height = tgt_height
        letterbox = True
    
    # TODO: Implement safe area calculation

    if letterbox:
        cmd += ' -vf scale=%s:%s,expand=%s:%s ' % \
            (inner_width, inner_height, tgt_width, tgt_height)
    else:
        cmd += ' -vf scale=%s:%s ' % (inner_width, inner_height)

    # Audio settings
    if 'dvd' in format:
        cmd += ' -srate 48000 -af lavcresample=48000 '
    else:
        cmd += ' -srate 41000 -af lavcresample=41000 '


"""
For DVD:

Filtering: -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup

-lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:

mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg

"""

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


mencoder command-lines to build upon:

For DVD:

mencoder -oac lavc -ovc lavc -of mpeg -mpegopts format=dvd -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup -srate 48000 -af lavcresample=48000,equalizer=11:11:10:8:8:8:8:10:10:12 -lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:

mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg


"""

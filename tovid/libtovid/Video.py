#! /usr/bin/env python
# Video.py
# Video generator module

import sys
import libtovid
from libtovid.Option import OptionDef

log = libtovid.Log('Video')

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

    'filters':
        OptionDef('filters', 'denoise|contrast|deblock[, ...]', [],
        """Apply the given filters to the video before or during encoding."""),
        
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
    
    'vbitrate':     OptionDef('vbitrate', '[0-9800]', None,
        """Maximum bitrate to use for video (in kbits/sec). Must be within
        allowable limits for the given format. Overrides default values.
        Ignored for VCD."""),

    'abitrate':     OptionDef('abitrate', '[0-1536]', None,
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
        """Put chapter breaks at the specified times (HH:MM:SS)."""),
        
    'method':       OptionDef('method', 'mpeg2enc|mencoder|ffmpeg', 'mencoder',
        """Encode using the given tool. The mpeg2enc method uses mplayer
        to rip the audio and video, and mpeg2enc to encode the video. The
        mencoder and ffmpeg methods do all encoding with the respective tool.""")

}


from libtovid.VideoPlugins import *
    
def generate(video):
    """Generate a video element by encoding an input file to a target
    standard."""

    method = video.get('method')
    if method == 'mpeg2enc':
        encoder = Mpeg2encEncoder(video)
    elif method == 'mencoder':
        encoder = MencoderEncoder(video)
    elif method == 'ffmpeg':
        log.info("The ffmpeg encoding method is not yet implemented.")
        sys.exit()
    else:
        log.info("Encoding method '%s' is not yet supported by the backend" % method)
        log.info("Perhaps you'd like to write a backend for it? :-)")
        sys.exit()
    
    log.info("generate(): Encoding with the %s plugin..." % encoder.__class__)
    encoder.run()






    


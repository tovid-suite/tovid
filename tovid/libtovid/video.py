#! /usr/bin/env python2.4
# video.py

__doc__ = \
"""This module generates MPEG video files from TDL Video element definitions."""


# TODO: Eliminate some of the redundancy of this module; integrate related
# encoding/muxing functions into a class or other container, with the aim
# of making it as simple as possible to write alternative backends (easy
# access to data about standard targets, about input video specs, etc.)

import sys

import libtovid
from libtovid.options import OptionDef, OptionSet
from libtovid.log import Log
from libtovid.encoders import *

log = Log('video.py')


class Video(OptionSet):
    """A Video element with associated options.
    
    This dictionary defines the set of options that may be given to a
    command-line invocation of 'tovid', or which may be present in a
    TDL Video element declaration.
    
    A backend may implement these features by accessing the instantiated
    Video element using an index-style syntax, i.e.:
        
        if video['format'] == 'dvd' and video['tvsys'] == 'ntsc':
            ...
    
    By convention, all options are nonhyphenated lowercase English words
    or short phrases. There are no 'long' and 'short' forms; when invoked
    from the command-line, options may be preceded by a hyphen (though it's
    not required).
    """
    optiondefs = {
        # New options to (eventually) replace -vcd, -pal etc.
        'format': OptionDef('format', 'vcd|svcd|dvd|half-dvd|dvd-vcd', 'dvd',
            """Make video compliant with the specified format"""),
        'tvsys': OptionDef('tvsys', 'ntsc|pal', 'ntsc',
            """Make the video compliant with the specified TV system"""),
        'filters': OptionDef('filters', 'denoise|contrast|deblock[, ...]', [],
            """Apply the given filters to the video before or during
            encoding."""),
            
        # Deprecated options. Need to find a way to
        # mark options as deprecated, so the parser can
        # warn the user.
        'vcd': OptionDef('vcd', '', False, alias=('format', 'vcd')),
        'svcd': OptionDef('svcd', '', False, alias=('format', 'svcd')),
        'dvd': OptionDef('dvd', '', False, alias=('format', 'dvd')),
        'half-dvd': OptionDef('half-dvd', '', False, alias=('format', 'half-dvd')),
        'dvd-vcd': OptionDef('dvd-vcd', '', False, alias=('format', 'dvd-vcd')),
        'ntsc': OptionDef('ntsc', '', False, alias=('tvsys', 'ntsc')),
        'ntscfilm': OptionDef('ntscfilm', '', False),
        'pal': OptionDef('pal', '', False, alias=('tvsys', 'pal')),

        # Other options
        'in': OptionDef('in', 'FILENAME', None),
        'out': OptionDef('out', 'FILENAME', None),

        'aspect': OptionDef('aspect', 'WIDTH:HEIGHT', "4:3",
            """Force the input video to be the given aspect ratio, where WIDTH
            and HEIGHT are integers."""),

        'quality': OptionDef('quality', '[1-10]', 8,
            """Desired output quality, on a scale of 1 to 10, with 10 giving
            the best quality at the expense of a larger output file. Output
            size can vary by approximately a factor of 4 (that is, -quality 1
            output can be 25% the size of -quality 10 output). Your results may
            vary."""),
        
        'vbitrate': OptionDef('vbitrate', '[0-9800]', None,
            """Maximum bitrate to use for video (in kbits/sec). Must be within
            allowable limits for the given format. Overrides default values.
            Ignored for VCD."""),

        'abitrate': OptionDef('abitrate', '[0-1536]', None,
            """Encode audio at NUM kilobits per second.  Reasonable values
            include 128, 224, and 384. The default is 224 kbits/sec, good
            enough for most encodings. The value must be within the allowable
            range for the chosen disc format; Ignored for VCD, which must be
            224."""),

        'safe': OptionDef('safe', '[0-100]%', "100%",
            """Fit the video within a safe area defined by PERCENT. For
            example, '-safe 90%' will scale the video to 90% of the
            width/height of the output resolution, and pad the edges with a
            black border. Use this if some of the picture is cut off when
            played on your TV."""),

        'interlaced': OptionDef('interlaced', '', False,
            """Do interlaced encoding of the input video. Use this option if
            your video is interlaced, and you want to preserve as much picture
            quality as possible. Ignored for VCD."""),

        'deinterlace': OptionDef('deinterlace', '', False,
            """Use this option if your source video is interlaced. You can
            usually tell if you can see a bunch of horizontal lines when you
            pause the video during playback. If you have recorded a video from
            TV or your VCR, it may be interlaced. Use this option to convert to
            progressive (non-interlaced) video. This option is DEPRECATED, and
            will probably be ditched in favor of interlaced encoding, which is
            better in almost every way."""),

        'subtitles': OptionDef('subtitles', 'FILE', None,
            """Get subtitles from FILE and encode them into the video.
            WARNING: This hard-codes the subtitles into the video, and you
            cannot turn them off while viewing the video. By default, no
            subtitles are loaded. If your video is already compliant with the
            chosen output format, it will be re-encoded to include the
            subtitles."""),

        'normalize': OptionDef('normalize', '', False,
            """Normalize the volume of the audio. Useful if the audio is too
            quiet or too loud, or you want to make volume consistent for a
            bunch of videos."""),
        'chapters': OptionDef('chapters', 'TIME [, TIME]', [],
            """Put chapter breaks at the specified times (HH:MM:SS)."""),
            
        'method': OptionDef('method', 'mpeg2enc|mencoder|ffmpeg', 'mencoder',
            """Encode using the given tool. The mpeg2enc method uses mplayer to
            rip the audio and video, and mpeg2enc to encode the video. The
            mencoder and ffmpeg methods do all encoding with the respective
            tool.""")
    }

    def __init__(self, name='Untitled Video'):
        OptionSet.__init__(self, name, self.optiondefs)
        
    def generate(self):
        """Generate a video element by encoding an input file to a target
        standard."""

        method = self['method']
        if method == 'mpeg2enc':
            encoder = mpeg2enc.Mpeg2encEncoder(self)
        elif method == 'mencoder':
            encoder = mencoder.MencoderEncoder(self)
        elif method == 'ffmpeg':
            log.info("The ffmpeg encoding method is not yet implemented.")
            sys.exit()
        else:
            log.info("The '%s' encoder is not yet supported." % method)
            log.info("Perhaps you'd like to write a backend for it? :-)")
            sys.exit()
        
        log.info("generate(): Encoding with the %s plugin..." % encoder.__class__)
        encoder.encode()

    def to_string(self):
        """Return video and options, formatted as a string."""
        result = 'Video "%s"\n' % self.name
        result += OptionSet.to_string(self)
        return result
 


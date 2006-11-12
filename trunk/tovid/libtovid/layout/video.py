#! /usr/bin/env python
# video.py

__all__ = ['Video']

# From standard library
import sys
# From libtovid
from libtovid.opts import Option, OptionDict
from libtovid.standards import get_resolution
# TODO: Remove explicit dependency on encoder modules; generalize the
# encoder backend so the Video class doesn't have to know about specific
# encoders.
from libtovid.transcode import encode
from libtovid.media import MediaFile
from libtovid import log

class Video:
    """A video title for (optional) inclusion on a video disc.

    Encapsulates all user-configurable options, including the input file,
    target format and TV system, and any other argument that may be passed to
    the 'pytovid' command-line script.
    """
    # List of valid Video options with documentation
    optiondefs = [
        Option('in', 'FILENAME', None,
            """Input video file, in any format."""),
        Option('out', 'NAME', None,
            """Output prefix or name."""),

        # New options to (eventually) replace -vcd, -pal etc.
        Option('format', 'vcd|svcd|dvd|half-dvd|dvd-vcd', 'dvd',
            """Make video compliant with the specified format"""),
        Option('tvsys', 'ntsc|pal', 'ntsc',
            """Make the video compliant with the specified TV system"""),
        Option('filters', 'denoise|contrast|deblock[, ...]', [],
            """Apply the given filters to the video before or during
            encoding."""),
            
        Option('vcd', '', False, alias=('format', 'vcd')),
        Option('svcd', '', False, alias=('format', 'svcd')),
        Option('dvd', '', False, alias=('format', 'dvd')),
        Option('half-dvd', '', False, alias=('format', 'half-dvd')),
        Option('dvd-vcd', '', False, alias=('format', 'dvd-vcd')),
        Option('ntsc', '', False, alias=('tvsys', 'ntsc')),
        Option('ntscfilm', '', False),
        Option('pal', '', False, alias=('tvsys', 'pal')),

        Option('aspect', 'WIDTH:HEIGHT', "4:3",
            """Force the input video to be the given aspect ratio, where WIDTH
            and HEIGHT are integers."""),
        Option('quality', '[1-10]', 8,
            """Desired output quality, on a scale of 1 to 10, with 10 giving
            the best quality at the expense of a larger output file. Output
            size can vary by approximately a factor of 4 (that is, -quality 1
            output can be 25% the size of -quality 10 output). Your results may
            vary."""),
        Option('vbitrate', '[0-9800]', None,
            """Maximum bitrate to use for video (in kbits/sec). Must be within
            allowable limits for the given format. Overrides default values.
            Ignored for VCD."""),
        Option('abitrate', '[0-1536]', None,
            """Encode audio at NUM kilobits per second.  Reasonable values
            include 128, 224, and 384. The default is 224 kbits/sec, good
            enough for most encodings. The value must be within the allowable
            range for the chosen disc format; Ignored for VCD, which must be
            224."""),
        Option('safe', '[0-100]%', "100%",
            """Fit the video within a safe area defined by PERCENT. For
            example, '-safe 90%' will scale the video to 90% of the
            width/height of the output resolution, and pad the edges with a
            black border. Use this if some of the picture is cut off when
            played on your TV."""),
        Option('interlaced', '', False,
            """Do interlaced encoding of the input video. Use this option if
            your video is interlaced, and you want to preserve as much picture
            quality as possible. Ignored for VCD."""),
        Option('deinterlace', '', False,
            """Use this option if your source video is interlaced. You can
            usually tell if you can see a bunch of horizontal lines when you
            pause the video during playback. If you have recorded a video from
            TV or your VCR, it may be interlaced. Use this option to convert to
            progressive (non-interlaced) video. This option is DEPRECATED, and
            will probably be ditched in favor of interlaced encoding, which is
            better in almost every way."""),
        Option('subtitles', 'FILE', None,
            """Get subtitles from FILE and encode them into the video.
            WARNING: This hard-codes the subtitles into the video, and you
            cannot turn them off while viewing the video. By default, no
            subtitles are loaded. If your video is already compliant with the
            chosen output format, it will be re-encoded to include the
            subtitles."""),
        Option('normalize', '', False,
            """Normalize the volume of the audio. Useful if the audio is too
            quiet or too loud, or you want to make volume consistent for a
            bunch of videos."""),
        Option('method', 'mpeg2enc|mencoder|ffmpeg', 'mencoder',
            """Encode using the given tool. The mpeg2enc method uses mplayer to
            rip the audio and video, and mpeg2enc to encode the video. The
            mencoder and ffmpeg methods do all encoding with the respective
            tool.""")
    ]

    def __init__(self, custom_options=None):
        """Initialize Video with a string, list, or dictionary of options."""
        # TODO: Possibly eliminate code repetition w/ Disc & Menu by adding
        # a base class and inheriting
        self.options = OptionDict(self.optiondefs)
        self.options.override(custom_options)
        self.parent = None
        self.children = []

    def generate(self):
        """Generate a video element by encoding an input file to a target
        standard."""
        encode(self.options['in'], self.options['out'], \
               self.options['format'], self.options['tvsys'], \
               self.options['method'])

if __name__ == '__main__':
    vid = Video(sys.argv[1:])

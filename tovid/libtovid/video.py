#! /usr/bin/env python2.4
# video.py

__all__ = ['Video']

# From standard library
import sys
from copy import copy
# From libtovid
from opts import Option, OptionDict
from log import Log
from standards import get_resolution
from utils import ratio_to_float
from encoders import mencoder, ffmpeg, mpeg2enc
from filetypes import MultimediaFile

log = Log('video.py')

class Video:
    """A video title for (optional) inclusion on a video disc.

    Encapsulates all user-configurable options, including the input file,
    target format and TV system, and any other argument that may be passed to
    the 'pytovid' command-line script.
    """
    # Dictionary of valid options with documentation
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
            
        # Deprecated options. Need to find a way to
        # mark options as deprecated, so the parser can
        # warn the user.
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

    def __init__(self, custom_options=[]):
        """Initialize Video with a string, list, or dictionary of options."""
        # TODO: Possibly eliminate code repetition w/ Disc & Menu by adding
        # a base class and inheriting
        self.options = OptionDict(self.optiondefs)
        self.options.update(custom_options)
        self.parent = None
        self.children = []


    def preproc(self):
        """Do preprocessing common to all backends."""
        self.infile = MultimediaFile(self.options['in'])
        width, height = get_resolution(self.options['format'], self.options['tvsys'])
        # Convert aspect (ratio) to a floating-point value
        src_aspect = ratio_to_float(self.options['aspect'])
        # Use anamorphic widescreen for any video 16:9 or wider
        # (Only DVD supports this)
        if src_aspect >= 1.7 and self.options['format'] == 'dvd':
            target_aspect = 16.0/9.0
            widescreen = True
        else:
            target_aspect = 4.0/3.0
            widescreen = False
        # If aspect matches target, no letterboxing is necessary
        # (Match within a tolerance of 0.05)
        if abs(src_aspect - target_aspect) < 0.05:
            scale = (width, height)
            expand = False
        # If aspect is wider than target, letterbox vertically
        elif src_aspect > target_aspect:
            scale = (width, height * dvd_aspect / src_aspect)
            expand = (width, height)
        # Otherwise (rare), letterbox horizontally
        else:
            scale = (width * src_aspect / dvd_aspect, height)
            expand = (width, height)
        # If infile is already the correct size, don't scale
        if self.infile.video and self.infile.video.size == scale:
            scale = False
            log.debug('Infile resolution matches target resolution.')
            log.debug('No scaling will be done.')
        # TODO: Calculate safe area
        # Other commonly-used values
        if 'dvd' in self.options['format']:
            samprate = 48000
        else:
            samprate = 44100
        if self.options['tvsys'] == 'pal':
            fps = '25.0'
        elif self.options['tvsys'] == 'ntsc':
            fps = '29.97'
        
        # Set audio/video bitrates based on target format, quality, or
        # user-defined values (if given)
        vbitrate = self.options['vbitrate']
        abitrate = self.options['abitrate']
        # Audio and video bitrates
        if self.options['format'] == 'vcd':
            abitrate = 224
            vbitrate = 1152
        else:
            # If user didn't override, use reasonable defaults
            if not vbitrate:
                # TODO: Adjust bitrate based on -quality
                if self.options['format'] in ['svcd', 'dvd-vcd']:
                    vbitrate = 2600
                else:
                    vbitrate = 7000
            if not abitrate:
                abitrate = 224

        # Add .mpg to outfile if not already present
        if not self.options['out'].endswith('.mpg'):
            self.options['out'] += '.mpg'

        # Set options for use by the encoder backends
        self.options['abitrate'] = abitrate
        self.options['vbitrate'] = vbitrate
        self.options['scale'] = scale
        self.options['expand'] = expand
        self.options['samprate'] = samprate
        self.options['fps'] = fps
        self.options['widescreen'] = widescreen

    def generate(self):
        """Generate a video element by encoding an input file to a target
        standard."""
        self.preproc()
        method = self.options['method']
        if method == 'mpeg2enc':
            log.info("generate(): Encoding with mpeg2enc")
            mpeg2enc.encode(self.infile, self.options)
        elif method == 'mencoder':
            log.info("generate(): Encoding with mencoder")
            mencoder.encode(self.infile, self.options)
        elif method == 'ffmpeg':
            log.info("The ffmpeg encoding method is not yet implemented.")
            sys.exit()
        else:
            log.info("The '%s' encoder is not yet supported." % method)
            log.info("Perhaps you'd like to write a backend for it? :-)")
            sys.exit()

if __name__ == '__main__':
    vid = Video(sys.argv[1:])

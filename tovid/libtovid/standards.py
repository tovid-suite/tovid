#! /usr/bin/env python
# standards.py

"""This module defines functions for retrieving information about multimedia
standards. Any data about widely-published standards should be defined here,
for use by all libtovid modules.

   >>> standards.is_compliant('foo.mpg' 'dvd', 'ntsc')
   True
   >>> standards.compliance('foo.mpg')
   ['dvd', 'ntsc']
   
"""

__all__ = [\
    'get_resolution',
    'get_codec',
    'get_fps',
    'VideoStandard',
    'AudioStandard']

# TODO: This module needs major cleanup, ruthless code-culling and
# overall simplification.

import doctest
from libtovid.media import VideoStream, AudioStream

# Dictionaries of standard attributes for easy lookup
format_size = {\
    'vcd':
        {'pal': (352, 288), 'ntsc': (352, 240)},
    'dvd-vcd':
        {'pal': (352, 288), 'ntsc': (352, 240)},
    'svcd':
        {'pal': (480, 576), 'ntsc': (480, 480)},
    'half-dvd':
        {'pal': (352, 576), 'ntsc': (352, 480)},
    'dvd':
        {'pal': (720, 576), 'ntsc': (720, 480)}
    }
format_bitrate = {\
    'vcd': 1152,
    'svcd': (0, 2600),
    'dvd-vcd': (0, 9800),
    'half-dvd': (0, 9800),
    'dvd': (0, 9800)
    }
tvstd_fps = {\
    'pal': 25.00,
    'ntsc': 29.97,
    'ntscfilm': 23.976
    }

def get_resolution(format, tvsys):
    """Return the pixel resolution (x,y) for the given format and TV system.
    For example:

        >>> get_resolution('dvd', 'pal')
        (720, 576)
        >>> get_resolution('half-dvd', 'ntsc')
        (352, 480)
    """
    return valid_resolutions[format][tvsys]


def get_codec(format, tvsys):
    """Return the codec used by the given format and TV system. For example:
    
        >>> get_codec('vcd', 'ntsc')
        mpeg1
        >>> get_codec('svcd', 'ntsc')
        mpeg2
    """
    if format == 'vcd':
        return 'mpeg1'
    else:
        return 'mpeg2'
    

def get_fps(format, tvsys):
    """Return the number of frames per second for the given format and TV
    system. For example:
    
        >>> get_fps('dvd', 'ntsc')
        29.97
        >>> get_fps('dvd', 'pal')
        25.00
    """
    return tvstd_fps[tvsys]


def get_bitrate_range(format):
    """Return the range (min, max) of valid bitrates for the given format.
    For example:

        >>> get_bitrate_range('dvd')
        (0, 9800)
        >>> get_bitrate_range('vcd')
        (1152, 1152)
    """
    return format_bitrate[format]


def is_compliant(filename, format, tvsys):
    """Return True if the given file is compliant with the given format and
    TV system, False otherwise.
    """
    pass

def compliance(filename):
    """Return standards-compliance information about the given file, as a list
    of keywords."""
    pass


def validate_specs(video, audio):
    """Return a list of audio and video standards matched by the given specs."""
    assert isinstance(video, VideoStream)
    assert isinstance(audio, AudioStream)
    # Find any standards matching video's width and height
    width = video.width
    height = video.height
    if width in std_widths:
        if height in std_heights:
            # Find all formats matching both width and height
            formats = filter(lambda x:x not in std_widths[width],
                             std_heights[height])
            print "Matching %sx%s resolution:" % (width, height)
            print formats


def video_is_valid(vstream, vstandard):
    """Return True if the video stream is valid under the given standard."""
    if (vstream.width == vstandard.width and
         vstream.height == vstandard.height and
         vstream.fps == vstandard.fps and
         vstream.codec == vstandard.codec and
         vstream.bitrate >= vstandard.minBitrate and
         vstream.bitrate <= vstandard.maxBitrate):
        return True
    else:
        return False

def audio_is_valid(astream, astandard):
    """Return True if the audio stream is valid under the given standard."""
    if (astream.bitrate >= astandard.minBitrate and
         astream.bitrate <= astandard.maxBitrate and
         astream.codec == astandard.codec and
         astream.samprate == astandard.samprate):
        return True
    else:
        return False

# ===========================================================
# TODO: Merge stuff above with stuff below somehow...
# ===========================================================

class VideoStandard:
    def __init__(self, keywords = [], codec = "",
                  resolution = (0, 0), fps = 0, bitrateRange = (0, 0)):
        self.keywords = keywords 
        self.codec = codec
        self.width, self.height = resolution
        self.fps = fps
        self.minBitrate, self.maxBitrate = bitrateRange

    def display(self):
        print "=========== Video standard ============="
        print "Keywords: %s" % self.keywords
        print "Codec: %s" % self.codec
        print "Width: %s" % self.width
        print "Height: %s" % self.height
        print "FPS: %s" % self.fps
        print "Minimum bitrate: %s" % self.minBitrate
        print "Maximum bitrate: %s" % self.maxBitrate


class AudioStandard:
    def __init__(self, keywords = [], codec = "",
                  samprate = 0, channels = 0, bitrateRange = (0, 0)):
        self.keywords = keywords 
        self.codec = codec
        self.samprate = samprate
        self.channels = channels
        self.minBitrate, self.maxBitrate = bitrateRange

    def display(self):
        print "=========== Audio standard ============="
        print "Keywords: %s" % self.keywords
        print "Codec: %s" % self.codec
        print "Sampling rate: %s" % self.samprate
        print "Minimum bitrate: %s" % self.minBitrate
        print "Maximum bitrate: %s" % self.maxBitrate


VideoStandardList = [
    # VideoStandard([keywords], codec, (width, height), fps, (minBitrate, maxBitrate))

    # VCD standard formats
    VideoStandard(["vcd", "pal"], "mpeg1", (352, 288), 25.00, (1152, 1152)),
    VideoStandard(["vcd", "ntsc"], "mpeg1", (352, 240), 29.97, (1152, 1152)),
    VideoStandard(["vcd", "ntsc", "ntscfilm"], "mpeg1", (352, 240), 23.976, (1152, 1152)),

    # SVCD standard formats
    VideoStandard(["svcd" , "pal"], "mpeg2", (480, 576), 25.00, (0, 2600)),
    VideoStandard(["svcd" , "ntsc"], "mpeg2", (480, 480), 29.97, (0, 2600)),
    VideoStandard(["svcd" , "ntsc", "ntscfilm"], "mpeg2", (480, 480), 23.976, (0, 2600)),

    # DVD standard formats
    VideoStandard(["dvd", "pal"], "mpeg2", (720, 576), 25.00, (0, 9800)),
    VideoStandard(["dvd", "ntsc"], "mpeg2", (720, 480), 29.97, (0, 9800)),
    VideoStandard(["dvd", "ntsc", "ntscfilm"], "mpeg2", (720, 480), 23.976, (0, 9800)),

    VideoStandard(["half-dvd", "pal"], "mpeg2", (352, 576), 25.00, (0, 9800)),
    VideoStandard(["half-dvd", "ntsc"], "mpeg2", (352, 480), 29.97, (0, 9800)),
    VideoStandard(["half-dvd", "ntsc", "ntscfilm"], "mpeg2", (352, 480), 23.976, (0, 9800)),
    VideoStandard(["dvd-vcd", "pal"], "mpeg2", (352, 288), 25.00, (0, 9800)),
    VideoStandard(["dvd-vcd", "ntsc"], "mpeg2", (352, 240), 29.97, (0, 9800)),
    VideoStandard(["dvd-vcd", "ntsc", "ntscfilm"], "mpeg2", (352, 240), 23.976, (0, 9800)),

    # KVCDX3 standard formats
    VideoStandard(["kvcdx3", "pal"], "mpeg2", (528, 576), 25.00, (0, 9800)),
    VideoStandard(["kvcdx3", "ntsc"], "mpeg2", (528, 480), 29.97, (0, 9800)),
    VideoStandard(["kvcdx3", "ntsc", "ntscfilm"], "mpeg2", (528, 480), 23.976, (0, 9800))
] # End of VideoList

# ===========================================================
# List of defined audio standards
# ===========================================================
AudioStandardList = [
    # AudioStandard([keywords], codec, samprate, channels, (minBitrate, maxBitrate))

    # VCD standard formats
    AudioStandard(["vcd", "pal"], "mp2", 44100, 2, (224, 224)),
    AudioStandard(["vcd", "ntsc"], "mp2", 44100, 2, (224, 224)),

    # SVCD standard formats
    AudioStandard(["svcd", "pal"], "mp2", 44100, 2, (32, 1536)),
    AudioStandard(["svcd", "ntsc"], "mp2", 44100, 2, (32, 384)),

    # DVD standard formats
    AudioStandard(["dvd", "ac3"], "ac3", 48000, 2, (32, 1536)),
    AudioStandard(["dvd", "mp2"], "mp2", 48000, 2, (32, 1536)),
    AudioStandard(["dvd", "pcm"], "pcm", 48000, 2, (32, 1536))
    # 5.1-channel audio
    #AudioStandard(["dvd"], "ac3", 48000, 5.1, (32, 1536))
    #AudioStandard(["dvd"], "mp2", 48000, 5.1, (32, 1536)),
] # End of AudioList


if __name__ == '__main__':
    doctest.testmod(verbose=True)

#! /usr/bin/env python
# standards.py

"""This module defines functions for retrieving information about multimedia
standards, including functions for determining the appropriate resolution,
video and audio codec, fps, and bitrates for a given format.

Known formats include:
    vcd
    svcd
    dvd
    half-dvd
    dvd-vcd

"""

__all__ = [\
    'standard_profile',
    'get_resolution',
    'get_vcodec',
    'get_acodec',
    'get_fps',
    'get_fpsratio',
    'get_samprate',
    'Target',
    'VideoStandard',
    'AudioStandard']

import doctest
from os.path import abspath
from libtovid.media import MediaFile

def standard_profile(format, tvsys):
    """Return a MediaFile compliant with the given format and tvsys.
    """
    profile = MediaFile('', format, tvsys)
    # Set valid video attributes
    profile.vcodec = get_vcodec(format)
    profile.scale = get_resolution(format, tvsys)
    profile.fps = get_fps(tvsys)
    # Set valid audio attributes
    profile.acodec = get_acodec(format)
    profile.samprate = get_samprate(format)
    # TODO: How to handle default bitrates? These functions return a range.
    #profile.vbitrate = get_vbitrate(format)[1]
    #profile.abitrate = get_abitrate(format)[1]
    profile.abitrate = 224
    if format == 'vcd':
        profile.vbitrate = 1150
    elif format == 'svcd':
        profile.vbitrate = 2600
    else:
        profile.vbitrate = 6000
    return profile

def get_resolution(format, tvsys):
    """Return the pixel resolution (x,y) for the given format and TV system.
    For example:

        >>> get_resolution('dvd', 'pal')
        (720, 576)
        >>> get_resolution('half-dvd', 'ntsc')
        (352, 480)
    """
    # Valid resolutions, indexed by format and tvsys
    valid_size = {\
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
    return valid_size[format][tvsys]


def get_scaling(format, tvsys):
    """Return the (x,y) scaling factor for images to look right, for each
    aspect ratio. ?!

    TODO: Please update PAL values."""
    valid_scaling = {\
        'vcd':
            {'pal': (1.0, 1.0), 'ntsc': (352 / 320., 1.0)},
        'dvd-vcd':
            {'pal': (1.0, 1.0), 'ntsc': (352 / 320., 1.0)},
        'svcd':
            {'pal': (1.0, 1.0), 'ntsc': (480 / 640., 1.0)},
        'half-dvd':
            {'pal': (1.0, 1.0), 'ntsc': (352 / 640., 1.0)},
        'dvd':
            {'pal': (1.0, 1.0), 'ntsc': (720 / 640., 1.0)},
        }
    return valid_scaling[format][tvsys]

def get_vcodec(format):
    """Return the video codec used by the given format. For example:
    
        >>> get_vcodec('vcd')
        'mpeg1'
        >>> get_vcodec('svcd')
        'mpeg2'
    """
    if format == 'vcd':
        return 'mpeg1'
    else:
        return 'mpeg2'


def get_acodec(format):
    """Return the audio codec (or codecs) supported by the given format. For
    example:
    
        >>> get_acodec('vcd')
        'mp2'
        >>> get_acodec('dvd')
        ['ac3', 'mp2', 'pcm']
    """
    if format in ['vcd', 'svcd']:
        return 'mp2'
    else:
        return ['ac3', 'mp2', 'pcm']
    
def get_samprate(format):
    """Return the audio sampling rate used by the given format."""
    if format in ['vcd', 'svcd']:
        return 44100
    else:
        return 48000
    

def get_fps(tvsys):
    """Return the number of frames per second for the given TV system. For
    example:
    
        >>> get_fps('ntsc')
        29.969999999999999
        >>> get_fps('pal')
        25.0
    """
    # Valid frames per second, by TV system
    fps = {\
        'pal': 25.0,
        'ntsc': 29.97,
        'ntscfilm': 23.976,
        }
    return fps[tvsys]

def get_fpsratio(tvsys):
    """Return the number of frames per second for the given TV system, in the
    ratio form. For example:
    
        >>> get_fpsratio('ntsc')
        '30000:1001'
        >>> get_fpsratio('pal')
        '25:1'
    """
    # Valid frames per second, by TV system
    fps = {\
        'pal': '25:1',
        'ntsc': '30000:1001',
        'ntscfilm': '24000:1001',
        }
    return fps[tvsys]


def get_vbitrate(format):
    """Return the range (min, max) of valid video bitrates (in kilobits per
    second) for the given format. min and max are the same for constant-bitrate
    formats.
    """
    # Valid video bitrates, indexed by format
    valid_bitrates = {\
        'vcd': (1150, 1150),
        'svcd': (0, 2600),
        'dvd-vcd': (0, 9800),
        'half-dvd': (0, 9800),
        'dvd': (0, 9800)
        }
    return valid_bitrates[format]

def get_abitrate(format):
    """Return the range (min, max) of valid audio bitrates (in kilobits per
    second) for the given format. min and max are the same for constant-bitrate
    formats.
    """
    if format == 'vcd':
        return (224, 224)
    elif format == 'svcd':
        return (32, 384)
    else:
        return (32, 1536)
        




# Currently unused stuff...
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
    AudioStandard(["svcd", "pal"], "mp2", 44100, 2, (32, 384)),
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

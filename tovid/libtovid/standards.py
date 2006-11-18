#! /usr/bin/env python
# standards.py

"""This module defines functions for retrieving information about multimedia
standards, including functions for determining the appropriate resolution,
video and audio codec, fps, and bitrates for a given format.
"""

__all__ = [\
    'get_abitrate',
    'get_acodec',
    'get_fps',
    'get_fpsratio',
    'get_resolution',
    'get_samprate',
    'get_scaling',
    'get_vbitrate',
    'get_vcodec']

import doctest

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


if __name__ == '__main__':
    doctest.testmod(verbose=True)

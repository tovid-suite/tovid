#! /usr/bin/env python
# standard.py

"""This module defines functions for retrieving information about multimedia
standards, including functions for determining the appropriate resolution,
video and audio codec, fps, and bitrates for a given format.
"""

__all__ = [
    'abitrate',
    'acodec',
    'fps',
    'fps_ratio',
    'resolution',
    'samprate',
    'vbitrate',
    'vcodec',
]

import doctest

def resolution(format, tvsys):
    """Return the pixel resolution (x,y) for the given format and TV system.
    For example::

        >>> resolution('dvd', 'pal')
        (720, 576)
        >>> resolution('half-dvd', 'ntsc')
        (352, 480)
    """
    # Valid resolutions, indexed by format and tvsys
    valid_size = {
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


def vcodec(format):
    """Return the video codec used by the given format. For example::
    
        >>> vcodec('vcd')
        'mpeg1'
        >>> vcodec('svcd')
        'mpeg2'
    """
    if format == 'vcd':
        return 'mpeg1'
    else:
        return 'mpeg2'


def acodec(format):
    """Return the audio codec (or codecs) supported by the given format.
    For example::
    
        >>> acodec('vcd')
        'mp2'
        >>> acodec('dvd')
        'ac3'
    """
    if format in ['vcd', 'svcd']:
        return 'mp2'
    else:
        return 'ac3'


def samprate(format):
    """Return the audio sampling rate used by the given format.
    """
    if format in ['vcd', 'svcd']:
        return 44100
    else:
        return 48000
    

def fps(tvsys):
    """Return the number of frames per second for the given TV system.
    For example::
    
        >>> print fps('ntsc')
        29.97
        >>> print fps('pal')
        25.0
    """
    # Valid frames per second, by TV system
    _fps = {
        'pal': 25.0,
        'ntsc': 29.97,
        'ntscfilm': 23.976,
        }
    return _fps[tvsys]


def fps_ratio(tvsys):
    """Return the number of frames per second for the given TV system,
    in ratio form. For example::
    
        >>> fps_ratio('ntsc')
        '30000:1001'
        >>> fps_ratio('pal')
        '25:1'
    """
    # Valid frames per second, by TV system
    _fps = {
        'pal': '25:1',
        'ntsc': '30000:1001',
        'ntscfilm': '24000:1001',
        }
    return _fps[tvsys]


def vbitrate(format):
    """Return the range (min, max) of valid video bitrates (in kilobits per
    second) for the given format. min and max are the same for constant-bitrate
    formats.
    """
    # Valid video bitrates, indexed by format
    valid_bitrates = {
        'vcd': (1150, 1150),
        'svcd': (0, 2600),
        'dvd-vcd': (0, 9800),
        'half-dvd': (0, 9800),
        'dvd': (0, 9800)
        }
    return valid_bitrates[format]


def abitrate(format):
    """Return the range (min, max) of valid audio bitrates (in kilobits per
    second) for the given format. For constant-bitrate formats, min == max.
    """
    if format == 'vcd':
        return (224, 224)
    elif format == 'svcd':
        return (32, 384)
    else:
        return (32, 1536)


if __name__ == '__main__':
    doctest.testmod(verbose=True)

#! /usr/bin/env python
# media.py

"""This module provides a multimedia file class (MediaFile), for storing
a profile of attributes including resolution, audio and video codecs and
bitrates.

A function is also provided:

    standard_media(format, tvsys)
        Return a MediaFile profile matching the given format and TV system

These can be used for getting a target MediaFile for encoding via
one of the backends in libtovid.transcode.encode. For example:

    >>> dvd = standard_media('dvd', 'ntsc')
    >>> print dvd
    Filename:
    Format: DVD
    TVsys: NTSC
    Length: 0 seconds
    Video: 720x480 29.97fps 4:3 mpeg2 6000kbps
    Audio: ac3 224kbps 48000hz 2-channel

"""

__all__ = [
    'MediaFile',
    'standard_media',
    'correct_aspect',
]

import copy
from libtovid import log
from libtovid import standard
from libtovid.util import ratio_to_float

"""
Analysis of MediaFile attributes

acodec: ID, target
abitrate: ID, target
channels: ID
samprate: ID, source, target
vcodec: ID
vbitrate: ID, target
length: ID, source
scale: (ID), (source), target
expand: target
fps: ID, source, target
aspect: source
widescreen: target


Redundancies(?):
widescreen/aspect
scale/expand if aspect is known
"""

class MediaFile:
    """A multimedia video file, and its vital statistics.
    """
    def __init__(self, filename='', format='none', tvsys='none'):
        log.debug("MediaFile(%s, %s, %s)" % (filename, format, tvsys))
        # TODO: Set attributes to match given format and tvsys
        self.filename = filename
        self.format = format
        self.tvsys = tvsys
        self.length = 0
        # TODO: Support multiple audio and video tracks
        self.has_audio = False
        self.has_video = False
        # Audio attributes
        self.acodec = 'none'
        self.abitrate = 0
        self.channels = 0
        self.samprate = 0
        # Video attributes
        self.vcodec = 'none'
        # TODO: Better names for scale & expand, but not so long as
        # 'inner_resolution' and 'outer_resolution', or
        # 'picture_res' and 'frame_res'. Suggestions?
        self.scale = (0, 0)
        self.expand = (0, 0)
        self.vbitrate = 0
        self.fps = 0.0
        self.aspect = '0:0'
        self.widescreen = False


    def __str__(self):
        """Return a string representation of the MediaFile.
        """
        width, height = self.expand or self.scale
        # List of lines of output
        lines = [
            'Filename: %s' % self.filename,
            'Format: %s' % self.format,
            'TVsys: %s' % self.tvsys,
            'Length: %s seconds' % self.length,
            'Video: %sx%s %sfps %s %s %skbps' % \
            (width, height, self.fps, self.aspect, self.vcodec, self.vbitrate),
            'Audio: %s %skbps %shz %s-channel' % \
            (self.acodec, self.abitrate, self.samprate, self.channels)
            ]
        # Add newlines and return
        return '\n'.join(lines)


def standard_media(format, tvsys):
    """Return a MediaFile compliant with a standard format and TV system.
    
        format
            Standard format ('vcd', 'svcd', or 'dvd')
        tvsys
            TV system ('pal' or 'ntsc')

    """
    log.debug("standard_media(%s, %s)" % (format, tvsys))
    media = MediaFile('', format, tvsys)
    # Set valid video attributes
    media.vcodec = standard.vcodec(format)
    media.scale = standard.resolution(format, tvsys)
    media.expand = media.scale
    media.fps = standard.fps(tvsys)
    # Set valid audio attributes
    media.acodec = standard.acodec(format)
    media.samprate = standard.samprate(format)
    # TODO: How to handle default bitrates? These functions return a range.
    #media.vbitrate = standard.vbitrate(format)[1]
    #media.abitrate = standard.abitrate(format)[1]
    media.abitrate = 224
    if format == 'vcd':
        media.vbitrate = 1150
    elif format == 'svcd':
        media.vbitrate = 2600
    else:
        media.vbitrate = 6000
    return media


def correct_aspect(source, target, aspect='auto'):
    """Calculate the necessary scaling to fit source into target at a given
    aspect ratio, without distorting the picture.

        source
            Input MediaFile
        target
            Output MediaFile
        aspect
            Aspect ratio to assume for input file (e.g., '4:3', '16:9')
            or 'auto' to use autodetection

    Return a new target MediaFile with correct scaling, using letterboxing
    if appropriate, and anamorphic widescreen if available.
    """
    assert isinstance(source, MediaFile)
    assert isinstance(target, MediaFile)

    # Base new target on existing one
    target = copy.copy(target)
    
    # Convert aspect (ratio) to a floating-point value
    if aspect == 'auto':
        src_aspect = ratio_to_float(source.aspect)
    else:
        src_aspect = ratio_to_float(aspect)
    
    # Use anamorphic widescreen for any video ~16:9 or wider
    # (Only DVD supports this)
    if src_aspect >= 1.7 and target.format == 'dvd':
        target_aspect = 16.0/9.0
        widescreen = True
    else:
        target_aspect = 4.0/3.0
        widescreen = False

    width, height = target.scale
    # If aspect matches target, no letterboxing is necessary
    tolerance = 0.05
    if abs(src_aspect - target_aspect) < tolerance:
        scale = (width, height)
    # If aspect is wider than target, letterbox vertically
    elif src_aspect > target_aspect:
        scale = (width, int(height * target_aspect / src_aspect))
    # Otherwise (rare), letterbox horizontally
    else:
        scale = (int(width * src_aspect / target_aspect), height)
    expand = (width, height)

    # If input file is already the correct size, don't scale
    if scale == source.scale:
        scale = False

    # Final scaling/expansion for correct aspect ratio display
    target.scale = scale
    target.expand = expand
    target.widescreen = widescreen
    return target


# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    pass

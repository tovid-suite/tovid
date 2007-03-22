#! /usr/bin/env python
# media.py

"""This module provides a multimedia file class (MediaFile), for storing
a profile of attributes including resolution, audio and video codecs and
bitrates.

Two functions are also provided:

    load_media(filename)
        Return a MediaFile filled with attributes from the given file
    standard_media(format, tvsys)
        Return a MediaFile profile matching the given format and TV system

These can be used for getting source and target MediaFiles for encoding via
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

__all__ = [\
    'MediaFile',
    'load_media',
    'standard_media',
    'correct_aspect']

# From standard library
import os
import sys
import copy
# From libtovid
from libtovid import log
from libtovid.cli import Command
from libtovid import standard
from libtovid.utils import ratio_to_float

class MediaFile:
    """A multimedia video file, and its vital statistics.
    """
    def __init__(self, filename='', format='dvd', tvsys='ntsc'):
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
        self.acodec = 'ac3'
        self.abitrate = 224
        self.channels = 2
        self.samprate = 48000
        # Video attributes
        self.vcodec = 'mpeg2'
        # TODO: Better names for scale & expand, but not so long as
        # 'inner_resolution' and 'outer_resolution', or
        # 'picture_res' and 'frame_res'. Suggestions?
        self.scale = (720, 480)
        self.expand = (720, 480)
        self.vbitrate = 9800
        self.fps = 29.97
        self.aspect = '4:3'
        self.widescreen = False

    def __str__(self):
        """Return a string representation of the MediaFile suitable for
        printing.
        """
        width, height = self.expand
        # List of lines of output
        lines = [\
            'Filename: %s' % self.filename,
            'Format: %s' % self.format.upper(),
            'TVsys: %s' % self.tvsys.upper(),
            'Length: %s seconds' % self.length,
            'Video: %sx%s %sfps %s %s %skbps' % \
            (width, height, self.fps, self.aspect, self.vcodec, self.vbitrate),
            'Audio: %s %skbps %shz %s-channel' % \
            (self.acodec, self.abitrate, self.samprate, self.channels)
            ]
        # Add newlines and return
        return '\n'.join(lines)


def load_media(filename):
    """Return a MediaFile filled with attributes read from a file.
    
        filename:  Name of a multimedia video file
        
    """
    log.debug("load_media(%s)" % filename)
    # TODO: Raise an exception if the file couldn't be identified
    # TODO: Infer aspect ratio
    media = MediaFile(filename)
    mp_dict = {}
    # Use mplayer
    cmd = Command('mplayer',
                  '-identify',
                  '%s' % filename,
                  '-vo', 'null',
                  '-ao', 'null',
                  '-frames', '1',
                  '-channels', '6')
    cmd.run(capture=True)
    # Look for mplayer's "ID_..." lines and include each assignment in mp_dict
    for line in cmd.get_output().splitlines():
        if line.startswith("ID_"):
            left, right = line.split('=')
            mp_dict[left] = right.strip()
            
    # Check for existence of streams
    if 'ID_VIDEO_ID' in mp_dict:
        media.has_video = True
    else:
        media.has_video = False
    if 'ID_AUDIO_ID' in mp_dict:
        media.has_audio = True
    else:
        media.has_audio = False

    # Parse the dictionary and set appropriate values
    for left, right in mp_dict.iteritems():
        if left == "ID_VIDEO_WIDTH":
            media.scale = (int(right), media.scale[1])
        elif left == "ID_VIDEO_HEIGHT":
            media.scale = (media.scale[0], int(right))
        elif left == "ID_VIDEO_FPS":
            media.fps = float(right)
        elif left == "ID_VIDEO_FORMAT":
            media.vcodec = right
        elif left == "ID_VIDEO_BITRATE":
            media.vbitrate = int(right) / 1000
        elif left == "ID_AUDIO_CODEC":
            media.acodec = right
        elif left == "ID_AUDIO_FORMAT":
            audio_format = right
        elif left == "ID_AUDIO_BITRATE":
            media.abitrate = int(right) / 1000
        elif left == "ID_AUDIO_RATE":
            media.samprate = int(right)
        elif left == "ID_AUDIO_NCH":
            media.channels = right
        elif left == 'ID_LENGTH':
            media.length = float(right)
    media.expand = media.scale
    # Fix mplayer's audio codec naming for ac3 and mp2
    if media.acodec == "8192":
        media.acodec = "ac3"
    elif media.acodec == "80":
        media.acodec = "mp2"
    # Fix mplayer's video codec naming for mpeg1 and mpeg2
    if media.vcodec == "0x10000001":
        media.vcodec = "mpeg1"
    elif media.vcodec == "0x10000002":
        media.vcodec = "mpeg2"
    return media


def standard_media(format, tvsys):
    """Return a MediaFile compliant with a standard format and TV system.
    
        format:  Standard format ('vcd', 'svcd', or 'dvd')
        tvsys:   TV system ('pal' or 'ntsc')

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

        source:  Input MediaFile
        target:  Output MediaFile
        aspect:  Aspect ratio to assume for input file (e.g., '4:3', '16:9')
                 or 'auto' to use autodetection

    Return a new target (MediaFile) with correct scaling, using letterboxing
    if appropriate, and anamorphic widescreen if available.
    """
    assert isinstance(source, MediaFile)
    assert isinstance(target, MediaFile)
    # Make a copy of the provided Profile
    target = copy.copy(target)
    
    # Convert aspect (ratio) to a floating-point value
    src_aspect = ratio_to_float('4:3')
    if aspect is not 'auto':
        src_aspect = ratio_to_float(aspect)
    else:
        src_aspect = ratio_to_float(source.aspect)
    
    # Use anamorphic widescreen for any video 16:9 or wider
    # (Only DVD supports this)
    if src_aspect >= 1.7 and target.format == 'dvd':
        target_aspect = 16.0/9.0
        widescreen = True
    else:
        target_aspect = 4.0/3.0
        widescreen = False

    width, height = target.scale
    # If aspect matches target, no letterboxing is necessary
    # (Match within a tolerance of 0.05)
    if abs(src_aspect - target_aspect) < 0.05:
        scale = (width, height)
        expand = False
    # If aspect is wider than target, letterbox vertically
    elif src_aspect > target_aspect:
        scale = (width, int(height * target_aspect / src_aspect))
        expand = (width, height)
    # Otherwise (rare), letterbox horizontally
    else:
        scale = (int(width * src_aspect / target_aspect), height)
        expand = (width, height)

    # If input file is already the correct size, don't scale
    if scale == source.scale:
        scale = False
        log.debug('Infile resolution matches target resolution.')
        log.debug('No scaling will be done.')

    # Final scaling/expansion for correct aspect ratio display
    target.scale = scale
    target.expand = expand
    target.widescreen = widescreen
    return target


# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: media.py FILE"
    else:
        print "Creating a MediaFile object from file: %s" % sys.argv[1]
        infile = load_media(sys.argv[1])
        print "------------------------------"
        print infile
        print "------------------------------"



#! /usr/bin/env python
# media.py

"""This module provides classes and functions for retrieving and storing
information about video, audio, and multimedia files.

The primary intended interface is the MediaFile class. To use it, do like so:

    >>> infile = MediaFile()
    >>> infile.load("/pub/video/test/bb.avi")

The given file (bb.avi) is automatically identified with mplayer, and its
vital statistics stored in MediaFile attributes. The easiest way to see the
result is:

    >>> infile.display()

"""
__all__ = ['MediaFile']

# From standard library
import os
import sys
import commands
# From libtovid
from libtovid import log
from libtovid.cli import Command

    
class MediaFile(object):
    """A profile of a multimedia video file.
    """
    def __init__(self, filename='', format='dvd', tvsys='ntsc'):
        # TODO: Set attributes to match given format and tvsys
        self.filename = filename
        self.format = format
        self.tvsys = tvsys
        self.length = 0
        # Audio attributes
        self.acodec = 'ac3'
        self.abitrate = 224
        self.samprate = 48000
        self.channels = 2
        # Video attributes
        self.vcodec = 'mpeg2'
        self.scale = (720, 480)
        self.expand = None
        self.vbitrate = 9800
        self.fps = 29.97
        self.aspect = '4:3'
        self.widescreen = False

    def has_audio(self):
        """Return True if this profile contains audio."""
        # TODO
        return True


def load_profile(filename):
    """Identify the given file using mplayer, and return a MediaFile.
    """
    # TODO: Infer aspect ratio
    profile = MediaFile(filename)
    mp_dict = {}
    # Use mplayer
    cmd = Command('mplayer',
                  '-identify',
                  '%s' % filename,
                  '-vo', 'null',
                  '-ao', 'null',
                  '-frames', '1',
                  '-channels', '6')
    cmd.run()
    # Look for mplayer's "ID_..." lines and include each assignment in mp_dict
    for line in cmd.get_output().splitlines():
        if line.startswith("ID_"):
            left, right = line.split('=')
            mp_dict[left] = right.strip()
    # Check for existence of streams
    if 'ID_VIDEO_ID' in mp_dict:
        has_video = True
    if 'ID_AUDIO_ID' in mp_dict:
        has_audio = True
    # Parse the dictionary and set appropriate values
    for left, right in mp_dict.iteritems():
        log.debug('%s = %s' % (left, right))
        if left == "ID_VIDEO_WIDTH":
            width = int(right)
        elif left == "ID_VIDEO_HEIGHT":
            height = int(right)
        elif left == "ID_VIDEO_FPS":
            profile.fps = float(right)
        elif left == "ID_VIDEO_FORMAT":
            profile.vcodec = right
        elif left == "ID_VIDEO_BITRATE":
            profile.vbitrate = int(right) / 1000
        elif left == "ID_AUDIO_CODEC":
            profile.acodec = right
        elif left == "ID_AUDIO_FORMAT":
            audio_format = right
        elif left == "ID_AUDIO_BITRATE":
            profile.abitrate = int(right) / 1000
        elif left == "ID_AUDIO_RATE":
            profile.samprate = int(right)
        elif left == "ID_AUDIO_NCH":
            profile.channels = right
        elif left == 'ID_LENGTH':
            profile.length = float(right)
    # Set scaling
    profile.scale = (width or 0, height or 0)
    # Fix mplayer's audio codec naming for ac3 and mp2
    if audio_format == "8192":
        profile.acodec = "ac3"
    elif audio_format == "80":
        profile.acodec = "mp2"
    # Fix mplayer's video codec naming for mpeg1 and mpeg2
    if profile.vcodec == "0x10000001":
        profile.vcodec = "mpeg1"
    elif profile.vcodec == "0x10000002":
        profile.vcodec = "mpeg2"
    return profile




# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: media.py FILE"
    else:
        print "Creating a MediaFile object from file: %s" % sys.argv[1]
        infile = MediaFile()
        infile.load(sys.argv[1])
        infile.display()


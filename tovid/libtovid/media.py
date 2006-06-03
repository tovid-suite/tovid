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
__all__ = ['VideoStream', 'AudioStream', 'MediaFile', 'mplayer_identify']

# From standard library
import os
import sys
import logging
import commands
from os.path import abspath

log = logging.getLogger('libtovid.media')

class MediaFile:
    """Stores information about a file containing video and/or audio streams."""
    def __init__(self, filename=''):
        self.filename = abspath(filename)
        self.audio = None
        self.video = None

    def load(self, filename):
        """Load MediaFile attributes from given file."""
        self.filename = abspath(filename)
        # Make sure the file exists
        if os.path.exists(self.filename):
            self.audio, self.video = mplayer_identify(self.filename)
        else:
            log.error("Couldn't find file: %s" % filename)

    def display(self):
        print "=============================="
        print "MediaFile: %s" % self.filename
        print "=============================="
        # Print audio stream info
        if self.audio:
            self.audio.display()
        else:
            print "No audio stream"
        # Print video stream info
        if self.video:
            self.video.display()
        else:
            print "No video stream"


class AudioStream:
    """Stores information about an audio stream."""
    def __init__(self, filename=''):
        self.filename = abspath(filename)
        self.codec = ''
        self.bitrate = 0
        self.channels = 0
        self.samprate = 0

    def display(self):
        print "Audio stream in %s" % self.filename
        print "----------------------"
        print "        Codec: %s" % self.codec
        print "      Bitrate: %s" % self.bitrate
        print "     Channels: %s" % self.channels
        print "Sampling rate: %s" % self.samprate
        print "----------------------"


class VideoStream:
    """Stores information about a video stream."""
    def __init__(self, filename=''):
        self.filename = abspath(filename)
        self.codec = ''
        self.width = 0
        self.height = 0
        self.fps = 0
        self.bitrate = 0

    def display(self):
        print "Video stream in %s" % self.filename
        print "----------------------"
        print "      Codec: %s" % self.codec
        print "      Width: %s" % self.width
        print "     Height: %s" % self.height
        print "  Framerate: %s" % self.fps
        print "    Bitrate: %s" % self.bitrate
        print "----------------------"


def mplayer_identify(filename):
    """Identify the given video file using mplayer, and return a tuple
    (audio, video) of AudioStream and VideoStream. None is returned for
    nonexistent audio or video streams."""
    audio = None
    video = None
    mp_dict = {}
    # Use mplayer 
    cmd = 'mplayer "%s"' % filename
    cmd += ' -vo null -ao null -frames 1 -channels 6 -identify'
    output = commands.getoutput(cmd)
    # Look for mplayer's "ID_..." lines and append to mp_dict
    for line in output.splitlines():
        if line.startswith("ID_"):
            left, right = line.split('=')
            # Add entry to dictionary (stripping whitespace from argument)
            mp_dict[left] = right.strip()
    # Check for existence of streams
    if 'ID_VIDEO_ID' in mp_dict:
        video = VideoStream(filename)
    if 'ID_AUDIO_ID' in mp_dict:
        audio = AudioStream(filename)
    # Parse the dictionary and set appropriate values
    for left, right in mp_dict.iteritems():
        log.debug('%s = %s' % (left, right))
        if video:
            if left == "ID_VIDEO_WIDTH":
                video.width = int(right)
            elif left == "ID_VIDEO_HEIGHT":
                video.height = int(right)
            elif left == "ID_VIDEO_FPS":
                video.fps = float(right)
            elif left == "ID_VIDEO_FORMAT":
                video.codec = right
            elif left == "ID_VIDEO_BITRATE":
                video.bitrate = int(right) / 1000
        if audio:
            if left == "ID_AUDIO_CODEC":
                audio.codec = right
            elif left == "ID_AUDIO_FORMAT":
                audio.format = right
            elif left == "ID_AUDIO_BITRATE":
                audio.bitrate = int(right) / 1000
            elif left == "ID_AUDIO_RATE":
                audio.samprate = int(right)
            elif left == "ID_AUDIO_NCH":
                audio.channels = right
    # Fix mplayer's audio codec naming for ac3 and mp2
    if audio:
        if audio.format == "8192":
            audio.codec = "ac3"
        elif audio.format == "80":
            audio.codec = "mp2"
    # Fix mplayer's video codec naming for mpeg1 and mpeg2
    if video:
        if video.codec == "0x10000001":
            video.codec = "mpeg1"
        elif video.codec == "0x10000002":
            video.codec = "mpeg2"
    return (audio, video)


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


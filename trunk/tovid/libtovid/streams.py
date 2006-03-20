#! /usr/bin/env python2.4
# streams.py

__all__ = ['VideoStream', 'AudioStream']

# From libtovid
from standards import *

class VideoStream:
    def __init__(self):
        self.codec = None
        self.width, self.height = (0, 0)
        self.fps = 0
        self.aspect = 0
        self.numframes = 0
        self.bitrate = 0

    # Determine whether this video stream is valid
    # under the given standard
    def isValid(self, videoStd):
        if (self.width == videoStd.width and
             self.height == videoStd.height and
             self.fps == videoStd.fps and
             self.codec == videoStd.codec and
             self.bitrate >= videoStd.minBitrate and
             self.bitrate <= videoStd.maxBitrate):
            return True
        else:
            return False

    def display(self):
        print "Video:"
        print "      Codec: %s" % self.codec
        print "      Width: %s" % self.width
        print "     Height: %s" % self.height
        print "  Framerate: %s" % self.fps
        print "    Bitrate: %s" % self.bitrate

class AudioStream:
    def __init__(self):
        self.codec = None
        self.samprate = 0
        self.bitrate = 0
        self.channels = 0
        
    # Determine whether this audio stream is valid
    # under the given standard
    def isValid(self, audioStd):
        if (self.bitrate >= audioStd.minBitrate and
             self.bitrate <= audioStd.maxBitrate and
             self.codec == audioStd.codec and
             self.samprate == audioStd.samprate):
            return True
        else:
            return False

    def display(self):
        print "Audio:"
        print "          Codec: %s" % self.codec
        print "        Bitrate: %s" % self.bitrate
        print "       Channels: %s" % self.channels
        print "  Sampling rate: %s" % self.samprate

#! /usr/bin/env python
# streams.py

__all__ = ['VideoStream', 'AudioStream']

# From libtovid
from libtovid.standards import *

class VideoStream:
    def __init__(self):
        self.codec = ''
        self.width = 0
        self.height = 0
        self.fps = 0
        self.bitrate = 0

    def display(self):
        print "Video stream:"
        print "      Codec: %s" % self.codec
        print "      Width: %s" % self.width
        print "     Height: %s" % self.height
        print "  Framerate: %s" % self.fps
        print "    Bitrate: %s" % self.bitrate

class AudioStream:
    def __init__(self):
        self.codec = ''
        self.bitrate = 0
        self.channels = 0
        self.samprate = 0

    def display(self):
        print "Audio stream:"
        print "          Codec: %s" % self.codec
        print "        Bitrate: %s" % self.bitrate
        print "       Channels: %s" % self.channels
        print "  Sampling rate: %s" % self.samprate

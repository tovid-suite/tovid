#! /usr/bin/env python2.4
# streams.py

__all__ = ['VideoStream', 'AudioStream']

# From libtovid
from libtovid.standards import *

class VideoStream:
    def __init__(self):
        self.spec = {}

    def display(self):
        print "Video:"
        print "      Codec: %s" % self.spec['codec']
        print "      Width: %s" % self.spec['width']
        print "     Height: %s" % self.spec['height']
        print "  Framerate: %s" % self.spec['fps']
        print "    Bitrate: %s" % self.spec['bitrate']

class AudioStream:
    def __init__(self):
        self.spec = {}

    def display(self):
        print "Audio:"
        print "          Codec: %s" % self.spec['codec']
        print "        Bitrate: %s" % self.spec['bitrate']
        print "       Channels: %s" % self.spec['channels']
        print "  Sampling rate: %s" % self.spec['samprate']

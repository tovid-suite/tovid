#! /usr/bin/env python

# ===========================================================
# VideoStrea, AudioStream
# ===========================================================

from Standards import *

# ===========================================================
# Video stream
# ===========================================================
class VideoStream:
    filename = "" # String with full path to filename, if any
    codec = None
    width, height = ( 0, 0 )
    fps = 0
    aspect = 0
    numframes = 0
    bitrate = 0

    def __init__( self, filename, codec, resolution, fps, aspect, numframes, bitrate ):
        self.filename = filename
        self.codec = codec
        self.width, self.height = resolution
        self.fps = fps
        self.aspect = aspect
        self.numframes = numframes
        self.bitrate = bitrate

    # Determine whether this video stream is valid
    # under the given standard
    def isValid( self, videoStd ):
        if ( self.width == videoStd.width and
             self.height == videoStd.height and
             self.fps == videoStd.fps and
             self.codec == videoStd.codec and
             self.bitrate >= videoStd.minBitrate and
             self.bitrate <= videoStd.maxBitrate ):
            return True
        else:
            return False

    def display( self ):
        print "Video:"
        print "      Codec: %s" % self.codec
        print "      Width: %s" % self.width
        print "     Height: %s" % self.height
        print "  Framerate: %s" % self.fps
        print "    Bitrate: %s" % self.bitrate

# ===========================================================
# Audio stream
# ===========================================================
class AudioStream:
    filename = "" # String with full path to filename, if any
    codec = "NONE"
    samprate = 0
    bitrate = 0
    channels = 0

    def __init__( self, filename, codec, samprate, bitrate, channels ):
        self.filename = filename
        self.codec = codec
        self.samprate = samprate
        self.bitrate = bitrate
        self.channels = channels
        
    # Determine whether this audio stream is valid
    # under the given standard
    def isValid( self, audioStd ):
        if ( self.bitrate >= audioStd.minBitrate and
             self.bitrate <= audioStd.maxBitrate and
             self.codec == audioStd.codec and
             self.samprate == audioStd.samprate ):
            return True
        else:
            return False

    def display( self ):
        print "Audio:"
        print "          Codec: %s" % self.codec
        print "        Bitrate: %s" % self.bitrate
        print "       Channels: %s" % self.channels
        print "  Sampling rate: %s" % self.samprate

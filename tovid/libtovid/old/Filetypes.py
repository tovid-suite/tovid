#! /usr/bin/env python

import os
from Globals import *
from Streams import *

# ===========================================================
# Multimedia video/audio file
# Contains video and audio streams
# May eventually contain more than one of each stream, along
# with subtitles or other stuff
# ===========================================================
class MultimediaFile:
    "Describes a file containing video and/or audio"

    filename = "" # Full path to filename
    video = None
    audio = None

    def __init__( self, filename ):
        self.filename = filename
        # If the file exists, get specs from it
        if os.path.isfile( filename ):
            self.getSpecs( filename )

        self.validate()

    # Gather video/audio information from the given
    # file, and fill in VideoStream/AudioStream
    def getSpecs( self, filename ):
        # Use os.popen to grab info from mplayer
        cmd = "mplayer -vo null -ao null -frames 1 -channels 6 -identify %s 2>&1" % filename
        mpout = os.popen( cmd, 'r' )
        
        # No video/audio streams unless mplayer says there are
        hasVideo = False
        hasAudio = False
        for line in mpout.readlines():
            # If current line is mplayer identification info,
            # parse the line and set appropriate variables
            if line.startswith( "ID_" ):
                left, right = line.split( '=' )
                # Strip whitespace
                right = right.strip()
                
                if left == "ID_VIDEO_ID":
                    hasVideo = True
                elif left == "ID_AUDIO_ID":
                    hasAudio = True
                elif left == "ID_VIDEO_WIDTH":
                    width = int( right )
                elif left == "ID_VIDEO_HEIGHT":
                    height = int( right )
                elif left == "ID_VIDEO_FPS":
                    fps = float( right )
                elif left == "ID_VIDEO_FORMAT":
                    vcodec = right
                elif left == "ID_VIDEO_BITRATE":
                    vbitrate = int( right ) / 1000
                elif left == "ID_AUDIO_CODEC":
                    acodec = right
                elif left == "ID_AUDIO_FORMAT":
                    aformat = right
                elif left == "ID_AUDIO_BITRATE":
                    abitrate = int( right ) / 1000
                elif left == "ID_AUDIO_RATE":
                    samprate = int( right )
                elif left == "ID_AUDIO_NCH":
                    channels = right
        mpout.close()

        if hasAudio:
            # Fix mplayer identification quirks
            if aformat == "8192":
                acodec = "AC3"
            elif aformat == "80":
                acodec = "MP2"
            self.audio = AudioStream( "", acodec, samprate, abitrate, channels )

        if hasVideo:
            # Fix mplayer identification quirks
            if vcodec == "0x10000001":
                vcodec = "MPEG1"
            elif vcodec == "0x10000002":
                vcodec = "MPEG2"
            self.video = VideoStream( "", vcodec, ( width, height ), fps, 1.33, 100, vbitrate )


    def validate( self ):
        # If no video stream, don't bother validating
        if self.video is None:
            self.validVideo = []
        # Otherwise, compare with all known video standards
        else:
            # Keep a list of matching standards
            self.validVideo = []
            for vstd in VideoList:
                if self.video.isValid( vstd ):
                    self.validVideo.append( vstd )

        # If no audio stream, don't bother validating
        if self.audio is None:
            self.validAudio = []
        # Otherwise, compare with all known audio standards
        else:
            # Keep a list of matching standards
            self.validAudio = []
            for astd in AudioList:
                if self.audio.isValid( astd ):
                    self.validAudio.append( astd )


    def display( self ):
        print "File: %s" % self.filename
        # Print video stream info
        if self.video is None:
            print "No video stream"
        else:
            self.video.display()
        # Print audio stream info
        if self.audio is None:
            print "No audio stream"
        else:
            self.audio.display()
        # Print compliance info
        for vstd in self.validVideo:
            print "Matches video standard:"
            vstd.display()
        for astd in self.validAudio:
            print "Matches audio standard:"
            astd.display()
    

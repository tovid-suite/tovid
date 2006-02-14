#! /usr/bin/env python

import os, sys
from Globals import *
from Streams import *
from Standards import *

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

    def __init__(self, filename):
        self.filename = filename
        # If the file exists, get specs from it
        if os.path.isfile(filename):
            self.getSpecs(filename)
        self.validate()

    def getSpecs(self, filename):
        """Gather video/audio information from the given file, and fill in
        VideoStream/AudioStream."""
        # Use os.popen to grab info from mplayer
        cmd = "mplayer -vo null -ao null -frames 1 -channels 6 -identify %s 2>&1" % filename
        mpout = os.popen(cmd, 'r')
        mp_dict = {}
        video = None
        audio = None

        for line in mpout.readlines():
            # If current line is mplayer identification info, format and add an
            # entry to the mplayer stat-dictionary
            if line.startswith("ID_"):
                left, right = line.split('=')
                # Add entry to dictionary (stripping whitespace from argument)
                mp_dict[left] = right.strip()
        mpout.close()

        if 'ID_VIDEO_ID' in mp_dict:
            video = VideoStream()
            
        if 'ID_AUDIO_ID' in mp_dict:
            audio = AudioStream()

        # Parse the dictionary and set appropriate values
        for left, right in mp_dict.iteritems():
            # If there's a video stream, check for video attributes
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
            
            # If there's an audio stream, check for audio attributes
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

        # Fix mplayer identification quirks
        if audio and audio.format == "8192":
            audio.codec = "AC3"
        elif audio and audio.format == "80":
            audio.codec = "MP2"

        if video and video.codec == "0x10000001":
            video.codec = "MPEG1"
        elif video and video.codec == "0x10000002":
            video.codec = "MPEG2"
            
        # Keep local copies
        self.video = video
        self.audio = audio


    def validate(self):
        """Determine if the audio/video streams match a standard format."""
        
        # If video stream exists, compare with all known video standards
        if self.video:
            # Keep a list of matching standards
            self.validVideo = []
            for vstd in VideoStandardList:
                if self.video.isValid(vstd):
                    self.validVideo.append(vstd)
        # Otherwise, video doesn't match anything
        else:
            self.validVideo = []

        # If audio stream exists, compare with all known audio standards
        if self.audio:
            # Keep a list of matching standards
            self.validAudio = []
            for astd in AudioStandardList:
                if self.audio.isValid(astd):
                    self.validAudio.append(astd)
        # Otherwise, audio doesn't match anything
        else:
            self.validAudio = []


    def display(self):
        print "File: %s" % self.filename
        # Print video stream info
        if self.video:
            self.video.display()
        else:
            print "No video stream"
        # Print audio stream info
        if self.audio:
            self.audio.display()
        else:
            print "No audio stream"
        # Print compliance info
        for vstd in self.validVideo:
            print "Matches video standard:"
            vstd.display()
        for astd in self.validAudio:
            print "Matches audio standard:"
            astd.display()

# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: Filetypes.py FILE"
    else:
        print "Creating a MultimediaFile object from file: %s" % sys.argv[1]
        infile = MultimediaFile(sys.argv[1])
        infile.display()


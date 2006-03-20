#! /usr/bin/env python2.4
# filetypes.py

__all__ = ['MultimediaFile']

# From standard library
import os
import sys
# From libtovid
from log import Log
from streams import VideoStream, AudioStream
from utils import subst

log = Log('filetypes.py')

class MultimediaFile:
    "A file containing video and/or audio streams"
    def __init__(self, filename):
        self.filename = filename
        # If the file exists, get specs from it
        try:
            self.get_specs()
        except:
            log.debug('Could not get specs from file: %s' % filename)
            sys.exit()

    def display(self):
        log.info("File: %s" % self.filename)
        # Print video stream info
        if self.video:
            self.video.display()
        else:
            log.info("No video stream")
        # Print audio stream info
        if self.audio:
            self.audio.display()
        else:
            log.info("No audio stream")
        # Print compliance info
        for vstd in self.validVideo:
            log.info("Matches video standard:")
            vstd.display()
        for astd in self.validAudio:
            log.info("Matches audio standard:")
            astd.display()


    def get_specs(self):
        """Get information about the audio/video streams in the file."""
        # Use os.popen to grab info from mplayer
        cmd = 'mplayer -vo null -ao null -frames 1 -channels 6 -identify '
        cmd += ' "%s"' % filename
        log.debug('IDing video with this command: "%s"' % filename)
        log.debug(cmd)
        lines = subst(cmd)
        mp_dict = {}
        audio = None
        video = None
    
        # Look for mplayer's "ID_..." lines and append to mp_dict
        for line in lines():
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
        self.audio = audio
        self.video = video


# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: Filetypes.py FILE"
    else:
        print "Creating a MultimediaFile object from file: %s" % sys.argv[1]
        infile = MultimediaFile(sys.argv[1])
        infile.display()


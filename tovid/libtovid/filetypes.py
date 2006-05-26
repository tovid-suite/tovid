#! /usr/bin/env python
# filetypes.py

__all__ = ['MediaFile', 'mplayer_identify']

# From standard library
import os
import sys
import logging
import commands
# From libtovid
from libtovid.streams import VideoStream, AudioStream

log = logging.getLogger('libtovid.filetypes')

class MediaFile:
    "A file containing video and/or audio streams"
    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        # If the file exists, identify it
        if os.path.exists(self.filename):
            self.audio, self.video = mplayer_identify(self.filename)
        else:
            log.error("Couldn't find file: %s" % filename)

    def display(self):
        log.info("MediaFile: %s" % self.filename)
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
    return (audio, video)


# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: filetypes.py FILE"
    else:
        print "Creating a MediaFile object from file: %s" % sys.argv[1]
        infile = MediaFile(sys.argv[1])
        infile.display()


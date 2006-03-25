#! /usr/bin/env python2.4
# filetypes.py

__all__ = ['MultimediaFile']

# From standard library
import os
import sys
# From libtovid
from libtovid.log import Log
from libtovid.streams import VideoStream, AudioStream
from libtovid.cli import Command, subst

log = Log('filetypes.py')

class MultimediaFile:
    "A file containing video and/or audio streams"
    def __init__(self, filename):
        self.filename = filename
        # If the file exists, get specs from it
        self.get_specs()

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

    def get_specs(self):
        """Get information about the audio/video streams in the file."""
        self.audio, self.video = mplayer_identify(self.filename)


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
    output = subst(cmd)
    # Look for mplayer's "ID_..." lines and append to mp_dict
    for line in output.splitlines():
        if line.startswith("ID_"):
            print line
            left, right = line.split('=')
            # Add entry to dictionary (stripping whitespace from argument)
            mp_dict[left] = right.strip()
    # Check for existence of streams
    if 'ID_VIDEO_ID' in mp_dict:
        video = VideoStream()
        v_spec = video.spec
    if 'ID_AUDIO_ID' in mp_dict:
        audio = AudioStream()
        a_spec = audio.spec
    # Parse the dictionary and set appropriate values
    for left, right in mp_dict.iteritems():
        log.debug('%s = %s' % (left, right))
        if video:
            if left == "ID_VIDEO_WIDTH":
                v_spec['width'] = int(right)
            elif left == "ID_VIDEO_HEIGHT":
                v_spec['height'] = int(right)
            elif left == "ID_VIDEO_FPS":
                v_spec['fps'] = float(right)
            elif left == "ID_VIDEO_FORMAT":
                v_spec['codec'] = right
            elif left == "ID_VIDEO_BITRATE":
                v_spec['bitrate'] = int(right) / 1000
        if audio:
            if left == "ID_AUDIO_CODEC":
                a_spec['codec'] = right
            elif left == "ID_AUDIO_FORMAT":
                a_spec['format'] = right
            elif left == "ID_AUDIO_BITRATE":
                a_spec['bitrate'] = int(right) / 1000
            elif left == "ID_AUDIO_RATE":
                a_spec['samprate'] = int(right)
            elif left == "ID_AUDIO_NCH":
                a_spec['channels'] = right
    # Fix mplayer's audio codec naming for ac3 and mp2
    if audio:
        if a_spec['format'] == "8192":
            a_spec['codec'] = "ac3"
        elif a_spec['format'] == "80":
            a_spec['codec'] = "mp2"
    # Fix mplayer's video codec naming for mpeg1 and mpeg2
    if video:
        if v_spec['codec'] == "0x10000001":
            v_spec['codec'] = "mpeg1"
        elif v_spec['codec'] == "0x10000002":
            v_spec['codec'] = "mpeg2"
    return (audio, video)


# Self-test; executed when this file is run standalone
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: Filetypes.py FILE"
    else:
        print "Creating a MultimediaFile object from file: %s" % sys.argv[1]
        infile = MultimediaFile(sys.argv[1])
        infile.display()


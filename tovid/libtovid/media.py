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

def rip_frames(video_file, out_dir, frames='all', size=(0, 0)):
    """Convert a video file to a sequence of images, save them in the
    given output directory, and return a list of frame image files.
    Rips all frames, a selected frame, or a range:

    All frames (default):   frames='all'
    Frame 15 only:          frames=15
    Frames 30 through 90:   frames=[30, 90]

    If size is nonzero, images are saved at the specified resolution.
    """
    frame_files = []
    video_file = os.path.abspath(video_file)
    try:
        os.mkdir(out_dir)
    except:
        print "Temp directory: %s already exists. Overwriting." % out_dir

    # Use transcode to rip frames
    cmd = 'transcode -i "%s" ' % video_file
    # Resize
    if size != (0, 0):
        cmd += ' -Z %sx%s ' % size
    # Encode selected frames
    if frames == 'all':
        pass
    elif isinstance(frames, int):
        cmd += ' -c %s-%s ' % (frames, frames)
    elif isinstance(frames, list):
        cmd += ' -c %s-%s ' % (frames[0], frames[-1])
    cmd += ' -y jpg,null '
    cmd += ' -o %s/frame_' % out_dir
    print "Creating image sequence from %s" % video_file
    print cmd
    print commands.getoutput(cmd)
    # Remember ripped image filenames
    frame = start
    end_reached = False
    while not end_reached:
        framefile = '%s/frame_%06d.jpg' % (out_dir, frame)
        if os.path.exists(framefile):
            frame_files.append(framefile)
        else:
            end_reached = True #, apparently
        frame += 1
    return frame_files


class MediaFile:
    """Stores information about a file containing video and/or audio streams."""
    def __init__(self, filename=''):
        self.filename = abspath(filename)
        self.audio = None
        self.video = None
        self.frame_files = []
        # TODO: Replace hard-coded temp dir
        self.use_tempdir('/tmp')

    def use_tempdir(self, directory):
        """Use the given directory for storing temporary files (such as ripped
        video frames, video or audio streams, etc.) Directory is created if it
        doesn't already exist."""
        self.tempdir = os.path.abspath(directory)
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)

    def load(self, filename):
        """Load the given file and identify it."""
        self.filename = abspath(filename)
        # Make sure the file exists
        if os.path.exists(self.filename):
            self.audio, self.video = mplayer_identify(self.filename)
        else:
            log.error("Couldn't find file: %s" % filename)

    def add_frames(self, frame_files):
        """Add the given list of frame files to the current media file."""
        # For now, just add to end (support more controlled insertions later)
        self.frame_files.extend(frame_files)

    def rip_frames(self, frames='all', size=(0, 0)):
        """Rip video frames from the current file and save them as separate
        image files. Optionally specify which frames to rip, like so:

        All frames (default):   frames='all'
        Frame 15 only:          frames=15
        Frames 30 through 90:   frames=[30, 90]

        If size is nonzero, save images at the specified resolution.
        """
        self.frame_files = rip_frames(self.filename, self.tempdir, frames, size)


    def encode_frames(self, imagedir, outfile, format, tvsys):
        """Convert an image sequence in imagedir to an .m2v video compliant
        with the given format and tvsys.
    
        Currently supports only JPEG images; input images must already be at
        the desired target resolution.
        """
        # Use absolute path name
        imagedir = os.path.abspath(imagedir)
        print "Creating video stream from image sequence in %s" % imagedir
    
        # Use jpeg2yuv to stream images
        cmd = 'jpeg2yuv -I p '
        if tvsys == 'pal':
            cmd += ' -f 25.00 '
        else:
            cmd += ' -f 29.970 '
        cmd += ' -j "%s/%%08d.jpg"' % imagedir

        # TODO: Scale to correct target size using yuvscaler or similar
        
        # Pipe image stream into mpeg2enc to encode
        cmd += ' | mpeg2enc -v 0 -q 3 -o "%s"' % outfile
        if format == 'vcd':
            cmd += ' --format 1 '
        elif format == 'svcd':
            cmd += ' --format 4 '
        else:
            cmd += ' --format 8 '
    
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            print line

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


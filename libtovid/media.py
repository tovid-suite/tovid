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
__all__ = ['MediaFile', 'mplayer_identify', 'AudioStream', 'VideoStream']

# From standard library
import os
import sys
import commands
from os.path import abspath
# From libtovid
from libtovid.log import Log
from libtovid import standards

log = Log('libtovid.media')


class AudioStream:
    """Stores information about an audio stream."""
    def __init__(self, filename=''):
        self.filename = abspath(filename)
        self.codec = ''
        self.bitrate = 0
        self.channels = 0
        self.samprate = 0

    def display(self):
        print "Audio stream(s) in %s" % self.filename
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


class MediaFile:
    """Stores information about a file containing video and/or audio streams."""
    def __init__(self, filename=''):
        if filename is not '':
            self.filename = abspath(filename)
        else:
            self.filename = ''
        self.audio = None
        self.video = None
        self.length = 0.0
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

    def load(self, filename=''):
        """Load the given file and identify it. If filename is not provided,
        load self.filename."""
        if filename is not '':
            self.filename = abspath(filename)
        # Make sure the file exists
        if os.path.exists(self.filename):
            self.length, self.audio_num, self.audio, self.video = \
                         mplayer_identify(self.filename)
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
        self.frame_files = do_rip_frames(self.filename, self.tempdir, frames, size)

    def add_audio_to_video(self, video_file, audio_file=None):
        """Multiplex some audio to a specified video file.

        audio_file -- a filename. Silence will be added if None
        """

        return


    def encode_frames(self, imagedir, file_type, outfile, format, tvsys):
        """Convert an image sequence in imagedir to an .m2v video compliant
        with the given format and tvsys.
    
        Currently supports JPEG and PNG images; input images must already be
        at the desired target resolution.

        file_type -- one of 'jpg', 'png'
        """
        # Use absolute path name
        imagedir = os.path.abspath(imagedir)
        print "Creating video stream from image sequence in %s" % imagedir

        # TODO: transfer this job to Video() in video.py
        # it's encoding, and should use an encoding backend.
    
        # Use jpeg2yuv/png2yuv to stream images
        if file_type == 'jpg':
            cmd = 'jpeg2yuv '
            cmd += ' -Ip '
            cmd += ' -f %.3f ' % standards.get_fps(tvsys)
            cmd += ' -j "%s/%%08d.%s"' % (imagedir, file_type)
        elif file_type == 'png':
            cmd = 'ls %s/*.png | ' % imagedir
            cmd += 'xargs -n1 pngtopnm |'
            cmd = 'png2yuv -Ip -f %.3f ' % standards.get_fps(tvsys)
            cmd += ' -j "%s/%%08d.png"' % (imagedir)
#            cmd += 'pnmtoy4m -Ip -F %s %s/*.png' % standards.get_fpsratio(tvsys)
        else:
            raise ValueError, "File_type '%s' isn't currently supported to "\
                  "render video from still frames" % file_type

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
        print "Audio channels: %d" % self.audio_num
        print "Stream length: %f secs" % self.length
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


def mplayer_identify(filename):
    """Identify the given video file using mplayer, and return a tuple
    (audio, video) of AudioStream and VideoStream. None is returned for
    nonexistent audio or video streams."""
    audio = None
    audio_num = 0
    video = None
    length = 0.0
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
            if left == 'ID_AUDIO_ID':
                audio_num += 1
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
        if left == 'ID_LENGTH':
            length = float(right)
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
    return (length, audio_num, audio, video)


def do_rip_frames(filename, out_dir, frames='all', size=(0, 0)):
    """Extract frame images from a video file, saving in the given output
    directory, and return a list of frame image files. Rips all frames, a
    selected frame, or a range:

    All frames (default):   frames='all'
    Frame 15 only:          frames=15
    Frames 30 through 90:   frames=[30, 90]

    If size is nonzero, images are saved at the specified resolution.
    """
    frame_files = []
    video_file = os.path.abspath(filename)
    my_out_dir = out_dir + '/' + os.path.basename(filename) + '_media_rip'
    try:
        os.mkdir(my_out_dir)
    except:
        print "Temp directory: %s already exists. Overwriting." % my_out_dir
        os.system('rm -rf "%s"' % my_out_dir)
        os.mkdir(my_out_dir)

    # TODO: use tcdemux to generate a nav index, like:
    # tcdemux -f 29.970 -W -i "$FILE" > "$NAVFILE"
    
    # Use transcode to rip frames
    cmd = 'transcode -i "%s" ' % video_file
    # Resize
    if size != (0, 0):
        cmd += ' -Z %sx%s ' % size
    # Encode selected frames
    if frames == 'all':
        start = 0
    elif isinstance(frames, int):
        cmd += ' -c %s-%s ' % (frames, frames)
        start = frames
    elif isinstance(frames, list):
        start = frames[0]
        cmd += ' -c %s-%s ' % (frames[0], frames[-1])
    cmd += ' -y jpg,null '
    cmd += ' -o %s/frame_' % my_out_dir
    print "Creating image sequence from %s" % video_file
    print cmd
    print commands.getoutput(cmd)
    # Remember ripped image filenames
    frame = start
    end_reached = False
    while not end_reached:
        framefile = '%s/frame_%06d.jpg' % (my_out_dir, frame)
        if os.path.exists(framefile):
            frame_files.append(framefile)
        else:
            end_reached = True #, apparently
        frame += 1
    return frame_files


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


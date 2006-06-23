#! /usr/bin/env python
# VideoUtils.py

"""A collection of utilities for working with multimedia video files."""

__all__ = [\
    'video_to_images',
    'images_to_video',
    'label_images']

# From standard library
import os
import sys

def video_to_images(infile, start, end, scale=(320,240)):
    """Convert a video file to a sequence of images, starting and ending at the
    given times in seconds. Returns directory name where the images are saved.

    If end <= start, convert from start onwards.
    If scale is nonzero, resize.
    """
    
    outdir = '/tmp/%s_frames' % os.path.basename(infile)
    # Create output directory if it doesn't exist
    if not os.path.exists(outdir):
        print "Creating: %s" % outdir
        try:
            os.mkdir(outdir)
        except:
            print "Could not create: %s" % outdir
            sys.exit()
    # Use transcode to rip frames
    cmd = 'transcode -i "%s" ' % infile
    # Encode from start to end frames
    cmd += ' -c %s-%s ' % (start, end)
    cmd += ' -y jpg,null '
    cmd += ' -Z %sx%s ' % scale
    cmd += ' -o %s/frame_' % outdir
    print "Creating image sequence from %s" % infile
    print cmd
    for line in os.popen(cmd, 'r').readlines():
        print line

    return outdir


def images_to_video(imagedir, outfile, format, tvsys):
    """Convert an image sequence in imagedir to an .m2v video compliant
    with the given format and tvsys.

    Currently supports only JPEG images.
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

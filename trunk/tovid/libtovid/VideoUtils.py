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
import logging

log = logging.getLogger('libtovid.VideoUtils')

def video_to_images(infile, start=0, end=0, scale=(0,0)):
    """Convert a video file to a sequence of images, starting and ending at the
    given times in seconds. Returns directory name where the images are saved.

    If end <= start, convert from start onwards.
    If scale is nonzero, resize.
    """
    
    outdir = os.path.expanduser('~/tmp/%s_images' % infile)
    # Create output directory if it doesn't exist
    if not os.path.exists(outdir):
        log.info("Creating: %s" % outdir)
        try:
            os.mkdir(outdir)
        except:
            log.error("Could not create: %s" % outdir)
            sys.exit()
    # Use mplayer to rip images
    cmd = 'mplayer "%s" ' % infile
    # From start to end (if given)
    cmd += ' -ss %s ' % start
    if end > start:
        cmd += ' -endpos %s ' % end - start
    # Scale if requested
    if scale != (0, 0):
        cmd += ' -zoom -x %s -y %s ' % scale
    cmd += ' -vo jpeg:outdir="%s" -ao null ' % outdir

    log.info("Creating image sequence from %s" % infile)
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
    log.info("Creating video stream from image sequence in %s" % imagedir)

    # Use jpeg2yuv to stream images
    cmd = 'jpeg2yuv -v 0 -I p '
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
        log.debug(line)

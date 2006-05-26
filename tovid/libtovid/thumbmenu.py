#! /usr/bin/env python
# thumbmenu.py

__all__ = ['generate']

import os
import glob
import string
import logging

import libtovid
from libtovid.cli import Script, verify_app

log = logging.getLogger('libtovid.thumbmenu')

# TODO: Eliminate this:
FRAMES=90

def generate(options):
    """Generate a menu with selectable thumbnail previews."""
    for app in ['convert', 'jpeg2yuv', 'mplayer']:
        verify_app(app)
    ThumbMenu(options)

class ThumbMenu:
    """Menu of video thumbnails"""
    def __init__(self, options):
        """Create a thumbnail menu from the given Menu."""
        self.options = options
        self.thumbs = []
        self.outdir = os.path.abspath('menu_%s' % self.options['out'])
        print "\n\nself.outdir: %s\n\n" % self.outdir
        # Find out how many thumbnails are needed
        self.numthumbs = len(self.options['thumbnails'])
        # Arrange thumbs in a grid
        # TODO: Support more than 12 (generalize)
        if self.numthumbs > 12:
            print "Sorry, can't do more than 12 thumbnails on a menu (yet)."
            sys.exit()
        thumbsize = (120, 90)
        index = 0
        for videofile in self.options['thumbnails']:
            # TODO: Pass video title (options['titles'][n]) to Thumbnail
            thumb = Thumbnail(videofile, thumbsize, thumb_slots[index])
            print "Appending video '%s' to thumbnails" % videofile
            self.thumbs.append(thumb)
            index += 1
        self.generate()
            
    def generate(self):
        for thumb in self.thumbs:
            thumb.generate()
            # Apply effects
            if 'label' in self.options['effects']:
                thumb.label()

        if not os.path.exists(self.outdir):
            print "\n\nCreating scratch dir: %s\n\n" % self.outdir
            os.mkdir(self.outdir)

        # Composite thumbs over background
        for frame in range(FRAMES):
            cmd = 'convert -size 720x480 '
            if self.options['background']:
                cmd += ' %s' % self.options['background']
            else:
                cmd += ' gradient:blue-black'
            for thumb in self.thumbs:
                cmd += ' -page +%s+%s' % thumb.loc
                cmd += ' -label "%s"' % thumb.videofile
                cmd += ' %s/%s.jpg' % (thumb.outdir, string.zfill(frame, 8))
            cmd += ' -mosaic %s/%s.jpg' % (self.outdir, string.zfill(frame, 8))
            run(cmd)
            
        # Generate video stream of composite images
        self.outfile = os.path.abspath("%s.m2v" % self.options['out'])
        cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
        cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % self.outdir
        cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o "%s"' % self.outfile
        run(cmd)


# ===========================================================
# Supporting variables and classes for thumbnail menu


# List of top-left coordinates and size for default menu
# thumbnails (for now, a 4x3 grid)
thumb_slots = [
    (72, 48),   (224, 48),   (376, 48),   (528, 48),
    (72, 192),  (224, 192),  (376, 192),  (528, 192),
    (72, 342),  (224, 342),  (376, 342),  (528, 342)
]
    

class ImageSequence:
    """A collection of images comprising a video sequence."""

    def __init__(self, outdir, size):
        """Create an image sequence in the given directory, at the given
        size (x,y)."""
        self.outdir = outdir
        self.size = size

        
    def generate(self, videofile):
        """Create an image sequence from the given video file."""
        # Create work directory if it doesn't exist
        if not os.path.exists(self.outdir):
            print "Creating thumbnail directory: %s" % self.outdir
            os.mkdir(self.outdir)
        cmd = 'mplayer "%s" ' % videofile
        cmd += ' -vf scale=%s:%s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.outdir
        cmd += ' -frames %s ' % FRAMES
        run(cmd)

    def label(self, text):
        for image in glob.glob('%s/*.jpg' % self.outdir):
            cmd = 'convert "%s"' % image
            cmd += ' -gravity south'
            cmd += ' -stroke "#0004" -strokewidth 1'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' -stroke none -fill white'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' "%s"' % image
            run(cmd)


class Thumbnail:
    """Video thumbnail, a small preview of a video, with effects"""
    def __init__(self, videofile, size = (120,90), loc = (0,0)):
        """Create a thumbnail from the given Video."""
        self.videofile = videofile
        self.size = size
        self.loc = loc
        self.outdir = os.path.abspath('thumb_%s' % self.videofile)
        self.imageseq = ImageSequence(self.outdir, self.size)

    def generate(self):
        print "Generating ImageSeqence for thumbnail '%s'" % self.videofile
        self.imageseq.generate(self.videofile)

    def label(self):
        print "Labeling thumbnail '%s'" % self.videofile
        self.imageseq.label(self.videofile)


def generate_highlight_png(coords):
    """Generate a transparent highlight .png for the menu, with
    cursor positions near the given coordinates.
    """
    outfile = 'high.png'
    cmd = 'convert -size 720x480 xc:none +antialias'
    cmd += ' -fill "#20FF40"'
    for rect in coords:
        x0, y0, x1, y1 = rect
        cmd += ' -draw "rectangle %s,%s %s,%s"' % \
            (x0, y1+4, x1, y1+10)
    cmd += ' -type Palette -colors 3 png8:%s' % outfile
    run(cmd)
    return outfile


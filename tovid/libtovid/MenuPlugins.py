#! /usr/bin/env python
# MenuPlugins.py

from Globals import degunk

__doc__=\
"""This module implements several backends for generating MPEG menus
from a list of video titles."""

class MenuPlugin:
    """Base plugin class; all menu-generators inherit from this."""
    def __init__(self, menu):
        self.menu = menu


class TextMenu (MenuPlugin):
    """Simple menu with selectable text titles"""
    def __init__(self, menu):
        MenuPlugin.__init__(self, menu)



# ===========================================================
# Supporting variables and classes for thumbnail menu

FRAMES=90

# List of top-left coordinates and size for default menu
# thumbnails (for now, a 4x3 grid)
thumb_slots = [
    (72, 48),   (224, 48),   (376, 48),   (528, 48),
    (72, 192),  (224, 192),  (376, 192),  (528, 192),
    (72, 342),  (224, 342),  (376, 342),  (528, 342)
]
    
# TODO: Generalize globals into a shared-state class in an imported module
WORK_DIR='~/tmp'

class ImageSequence:
    """A collection of images comprising a video sequence."""

    def __init__(self, outdir, size):
        """Create an image sequence in the given directory, at the given
        size (x,y)."""
        self.outdir = outdir
        self.size = size

        
    def generate(self, video):
        """Create an image sequence from the given Video element."""
        # Create work directory if it doesn't exist
        if not os.path.exists(self.outdir):
            print "Creating thumbnail directory: %s" % self.outdir
            os.mkdir(self.outdir)

        cmd = 'mplayer "%s" ' % video.get('in')

        x, y = self.size

        cmd += ' -zoom -x %s -y %s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.outdir
        cmd += ' -ss 05:00 -frames %s ' % FRAMES

        print "Creating image sequence from %s" % video.get('in')
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            #print line
            pass



    def label(self, text):
        for image in glob.glob('%s/*.jpg' % self.outdir):
            cmd = 'convert "%s"' % image
            cmd += ' -gravity south'
            cmd += ' -stroke "#0004" -strokewidth 1'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' -stroke none -fill white'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' "%s"' % image

            print 'Labeling "%s" with command:' % image
            print cmd
            for line in os.popen(cmd, 'r').readlines():
                print line


class Thumbnail:
    """Video thumbnail, a small preview of a video, with effects"""
    def __init__(self, video, size = (120,90), loc = (0,0)):
        """Create a thumbnail from the given Video element."""
        self.video = video
        self.size = size
        self.loc = loc
        self.outdir = os.path.abspath('thumb_%s' % degunk(self.video.name))
        self.imageseq = ImageSequence(self.outdir, self.size)

    def generate(self):
        print "Generating ImageSeqence for thumbnail '%s'" % self.video.name
        self.imageseq.generate(self.video)

    def label(self):
        print "Labeling thumbnail '%s'" % self.video.name
        self.imageseq.label(self.video.name)

        
class ThumbMenu (MenuPlugin):
    """Menu of video thumbnails"""
    def __init__(self, menu):
        """Create a thumbnail menu from the given Menu element."""
        self.menu = menu
        self.thumbs = []
        self.outdir = os.path.abspath('menu_%s' % degunk(self.menu.name))
        print "\n\nself.outdir: %s\n\n" % self.outdir
        # Find out how many thumbnails are needed
        self.numthumbs = len(menu.children)
        # Arrange thumbs in a grid
        # TODO: Support more than 12 (generalize)
        if self.numthumbs > 12:
            print "Sorry, can't do more than 12 thumbnails on a menu (yet)."
            sys.exit()
        thumbsize = (120, 90)
        index = 0
        for video in self.menu.children:
            thumb = Thumbnail(video, thumbsize, thumb_slots[index])
            print "Appending video '%s' to thumbnails" % video.name
            self.thumbs.append(thumb)
            index += 1
        self.generate()
            
    def generate(self):
        for thumb in self.thumbs:
            thumb.generate()
            # Apply effects
            if 'label' in self.menu.get('effects'):
                thumb.label()

        if not os.path.exists(self.outdir):
            print "\n\nCreating scratch dir: %s\n\n" % self.outdir
            os.mkdir(self.outdir)

        # Composite thumbs over background
        for frame in range(FRAMES):
            cmd = 'convert -size 720x480 %s' % self.menu.get('background')
            for thumb in self.thumbs:
                cmd += ' -page +%s+%s' % thumb.loc
                cmd += ' -label "%s"' % thumb.video.name
                cmd += ' %s/%s.jpg' % (thumb.outdir, string.zfill(frame, 8))
            cmd += ' -mosaic %s/%s.jpg' % (self.outdir, string.zfill(frame, 8))
            print cmd
            os.popen(cmd, 'r')
            
        # Generate video stream of composite images
        self.outfile = os.path.abspath("%s.m2v" % degunk(self.menu.name))
        cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
        cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % self.outdir
        cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o "%s"' % self.outfile
        print "Generating video stream with command:"
        print cmd
        for line in os.popen(cmd, 'r'):
            print line


def generate_highlight_png(coords):
    """Generate a transparent highlight .png for the menu, with
    cursor positions near the given coordinates."""
    outfile = 'high.png'
    cmd = 'convert -size 720x480 xc:none +antialias'
    cmd += ' -fill "#20FF40"'
    for rect in coords:
        x0, y0, x1, y1 = rect
        cmd += ' -draw "rectangle %s,%s %s,%s"' % \
            (x0, y1+4, x1, y1+10)
    cmd += ' -type Palette -colors 3 png8:%s' % outfile
    print cmd
    for line in os.popen(cmd, 'r').readlines():
        print line
    return outfile

  
    



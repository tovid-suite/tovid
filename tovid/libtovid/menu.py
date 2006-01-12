#! /usr/bin/env python

import string, sys, os, glob
from libtovid import Project
from Globals import degunk

"""Generate Menu elements for a tovid project."""

"""Conceptual steps in generating a menu:

    - convert/generate background (image or video)
    - convert audio
    - generate link content (titles and/or thumbnails)
    - generate link navigation (spumux)
    - composite links/thumbnails over background
    - convert image sequence into video stream
    - mux video/audio streams
    - mux link highlight/select subtitles

Interfaces:

    - Convert video to image sequence
    - Convert image sequence to video
    - Composite two or more image sequences together
    - Alter an image sequence (decoration, labeling, etc.)

Data structures:

    - Image sequence
        - Name/title
        - Resolution
        - Filesystem location (directory name)
    - Thumbnail (a specialized image sequence)


Desired end result:

    - Generalized video stream combination interface
        - For streaming multiple videos into a single video
        - For applying effects and visual widgets to a video
        - For adding customized subtitle streams
"""


FRAMES=30

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

    def __init__(self, video, outdir, size):
        """Create an image sequence of the given video element, at the given
        size (x,y)."""
        self.video = video
        self.outdir = outdir
        self.size = size

        
    def generate(self):
        """Create an image sequence from the given Video element."""
        # Create work directory if it doesn't exist
        if not os.path.exists(self.outdir):
            print "Creating thumbnail directory: %s" % self.outdir
            os.mkdir(self.outdir)

        cmd = 'mplayer "%s" ' % self.video.get('in')

        x, y = self.size

        cmd += ' -zoom -x %s -y %s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.outdir
        cmd += ' -ss 05:00 -frames %s ' % FRAMES

        print "Creating image sequence from %s" % self.video.get('in')
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            #print line
            pass


    def to_video(self):
        """Create a video stream from the image sequence."""
        outfile = os.path.abspath("%s.m2v" % degunk(self.video.name))
        cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
        cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % self.outdir
        cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o "%s"' % outfile
        print "Generating video stream with command:"
        print cmd
        for line in os.popen(cmd, 'r'):
            print line
        return outfile


    def decorate(self, effects):
        """Apply the given filters and decorations to the image sequence."""

        # For all .jpg images in self.outdir, add decoration
        for image in glob.glob('%s/*.jpg' % self.outdir):
            cmd = 'convert "%s"' % image

            if 'label' in effects:
                cmd += ' -gravity south'
                cmd += ' -stroke "#0004" -strokewidth 1'
                cmd += ' -annotate 0 "%s"' % self.video.name
                cmd += ' -stroke none -fill white'
                cmd += ' -annotate 0 "%s"' % self.video.name

            if 'shadow' in effects:
                cmd += ''

            # TODO: Convert these mplayer effects to IM equivalents
            """
            if 'border' in effects:
                cmd += ' -vf expand=%s:%s:2:2 ' % (x+2, y+2)

            if 'glass' in effects:
                cmd += ' -vf '
                cmd += 'rectangle=%s:%s,' % (x, y)
                cmd += 'rectangle=%s:%s,' % (x-2, y-2)
                cmd += 'rectangle=%s:%s,' % (x-4, y-4)
                cmd += 'rectangle=%s:%s' % (x-6, y-6)
            """

            # Write output back to the original image
            cmd += ' "%s"' % image

            print 'Decorating "%s" with command:' % image
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
        self.imageseq = ImageSequence(self.video, self.outdir, self.size)

    def generate(self):
        print "Generating ImageSeqence for thumbnail '%s'" % self.video.name
        self.imageseq.generate()

        
class ThumbMenu:
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




def generate_project_menus(project):
    """Create an MPEG menu for each Menu in the given project."""
    for menu in project.get_elements('Menu'):
        if menu.get('format') == 'dvd':
            generate_dvd_menu(menu)
        elif disc.get('format') in ['vcd', 'svcd']:
            generate_vcd_menu(menu)


def generate_dvd_menu(menu):
    """Generate a DVD MPEG menu, saving to the file specified by the menu's
    'out' option."""

    # TODO:
    # Convert audio to compliant format

    foo = ThumbMenu(menu)

    """
    outdir = os.path.abspath('composite')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    background = menu.get('background')
    generate_highlight_png(coords[:index])
    composite_thumbs(background, thumbs, outdir)
    """

    # TODO:
    # Create a subtitle stream with "button" regions over each thumbnail
    # Multiplex video, audio, and subtitles, output in menu.get('out')



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

  
    
def generate_vcd_menu(menu):
    """Generate an (S)VCD MPEG menu, saving to the file specified by the menu's
    'out' option."""
    # TODO
    pass




if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    generate_project_menus(proj)

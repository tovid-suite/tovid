#! /usr/bin/env python

# Menu generator module

import string, sys, os, glob
import libtovid
from libtovid.Option import OptionDef
from libtovid.Globals import degunk

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

# Menu TDL element definition
# Options pertaining to generating a video disc menu
optiondefs = {
    'format': OptionDef('format', 'vcd|svcd|dvd', 'dvd',
        """Generate a menu compliant with the specified disc format"""),
    'tvsys': OptionDef('tvsys', 'pal|ntsc', 'ntsc',
        """Make the menu for the specified TV system"""),
    'linksto': OptionDef('linksto', '"TITLE" [, "TITLE"]', [],
        """Comma-separated list of quoted titles; these are the
        titles that will be displayed (and linked) from the menu."""),
    'background': OptionDef('background', 'IMAGE', None,
        """Use IMAGE (in most any graphic format) as a background."""),
    'audio': OptionDef('audio', 'AUDIOFILE', None,
        """Use AUDIOFILE for background music while the menu plays."""),
    'font':
        OptionDef('font', 'FONTNAME', 'Helvetica',
        """Use FONTNAME for the menu text."""),
    'fontsize':
        OptionDef('fontsize', 'NUM', '24',
        """Use a font size of NUM pixels."""),
    'alignment':
        OptionDef('alignment', 'left|center|right', 'left'),
    'textcolor':
        OptionDef('textcolor', 'COLOR' 'white',
        """Color of menu text. COLOR may be a hexadecimal triplet
        (#RRGGBB or #RGB), or a color name from 'convert -list color'."""),
    'highlightcolor':
        OptionDef('highlightcolor', 'COLOR', 'red',
        """Color of menu highlights."""),
    'selectcolor':
        OptionDef('selectcolor', 'COLOR', 'green',
        """Color of menu selections."""),
    'out':
        OptionDef('out', 'FILE', None),
    # Thumbnail menus and effects
    'choices':
        OptionDef('choices', '[list|thumbnails]', 'list',
            """Display links as a list of titles, or as a grid
            of labeled thumbnail videos."""),
    'border':
        OptionDef('border', 'NUM', '0',
            """Add a border of NUM pixels around thumbnails."""),
    'effects':
        OptionDef('effects', 'shadow|round|glass [, ...]', [],
            """Add the listed effects to the thumbnails.""")
}


def generate(menu):
    """Generate the given menu element, and return the filename of the
    resulting menu."""
    # TODO: Raise exceptions

    # Generate a menu of the appropriate format
    if menu.get('format') == 'dvd':
        generate_dvd_menu(menu)
    elif disc.get('format') in ['vcd', 'svcd']:
        generate_vcd_menu(menu)


def generate_vcd_menu(menu):
    """Generate an (S)VCD MPEG menu, saving to the file specified by the menu's
    'out' option."""
    # TODO
    pass


def generate_dvd_menu(menu):
    """Generate a DVD MPEG menu, saving to the file specified by the menu's
    'out' option."""

    foo = ThumbMenu(menu)

    # TODO:
    # Write this TODO

    

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

  
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()


    generate_project_menus(proj)

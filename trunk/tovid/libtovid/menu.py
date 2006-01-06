#! /usr/bin/env python

import string, sys, os, glob
from libtovid import Project

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

"""


FRAMES=30

class ImageSequence:
    """A collection of images comprising a video sequence."""
    def __init__(self, dir, size):
        """Create an image sequence in the given directory, using
        any existing image files there. Images must be at the given
        size (x,y)."""
        self.dir = os.path.abspath(dir)
        self.size = size
        # Create directory if it doesn't exist
        if not self.dir:
            os.mkdir(self.dir)

        
    def from_video(self, video):
        """Create an image sequence from the given Video element."""
        cmd = 'mplayer "%s" ' % video.get('in')

        x, y = self.size

        cmd += ' -zoom -x %s -y %s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.dir
        cmd += ' -ss 05:00 -frames %s ' % FRAMES

        print "Creating image sequence from %s" % video.get('in')
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            #print line
            pass


    def to_video(self):
        """Create a video stream from the image sequence."""
        outfile = os.path.abspath("%s.m2v" % self.name)
        cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
        cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % self.dir
        cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o "%s"' % outfile
        print "Generating video stream with command:"
        print cmd
        for line in os.popen(cmd, 'r'):
            print line
        return outfile


    def decorate(self, effects):
        """Apply the given filters and decorations to the image sequence."""

        # For all .jpg images in self.dir, add decoration
        for image in glob.glob('%s/*.jpg' % self.dir):
            cmd = 'convert "%s"' % image

            if 'label' in effects:
                cmd += ' -gravity south'
                cmd += ' -stroke "#0004" -strokewidth 1'
                cmd += ' -annotate 0 "%s"' % self.name
                cmd += ' -stroke none -fill white'
                cmd += ' -annotate 0 "%s"' % self.name

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


    def composite(self, imgseq):
        """Composite the given image sequence over this one."""
        # (Maybe better to put this at a higher level)
        pass



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

    effects = menu.get('effects')
    coords = grid_coordinates(720, 480, 3, 2)
    index = 0
    thumbs = []
    for video in menu.children:
        print "video: "
        print video
        thumbs.append(Thumb(index, video, coords[index], effects))
        thumbs[-1].generate()
        thumbs[-1].decorate()
        index += 1
    
    outdir = os.path.abspath('composite')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    background = menu.get('background')
    generate_highlight_png(coords[:index])
    composite_thumbs(background, thumbs, outdir)

    # TODO:
    # Create a subtitle stream with "button" regions over each thumbnail
    # Multiplex video, audio, and subtitles, output in menu.get('out')


def composite_thumbs(background, thumbs, outdir):
    for frame in range(FRAMES):
        cmd = 'convert -size 720x480 %s' % background
        for thumb in thumbs:
            x0, y0, x1, y1 = thumb.coords
            cmd += ' -page +%s+%s' % (x0, y0)
            cmd += ' -label "%s"' % thumb.video.name
            cmd += ' %s/%s.jpg' % (thumb.outdir, string.zfill(frame, 8))
        cmd += ' -mosaic %s/%s.jpg' % (outdir, string.zfill(frame, 8))
        print cmd
        os.popen(cmd, 'r')


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


def grid_coordinates(width, height, cols, rows):
    """Return a list of coordinates for rectangular cells (cols x rows)
    in a space (width x height) pixels."""
    # TODO: Cleanup, simplify, and/or optimize math
    left = 0.1 * width
    right = 0.9 * width
    top = 0.1 * height
    bottom = 0.9 * height
    x_inc = (right - left) / cols
    y_inc = (bottom - top) / rows
    aspect = 1.0 * width / height
    d_x = 0.5 * x_inc - 4
    d_y = d_x / aspect
    coords = []
    for y in range(rows):
        for x in range(cols):
            x_center = left + (x + 0.5) * x_inc
            y_center = top + (y + 0.5) * y_inc
            coords.append((int(x_center - d_x), int(y_center - d_y),
                           int(x_center + d_x), int(y_center + d_y)))
    return coords


def rect_size(coords):
    """Return the size (w,h) of the rectangle defined by the given
    coordinates."""
    x0, y0, x1, y1 = coords
    return (x1-x0, y1-y0)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    generate_project_menus(proj)

#! /usr/bin/env python

import string, sys, os
from libtovid import Project

"""Generate Menu elements for a tovid project."""

FRAMES=60

class Thumb:
    """Video thumbnail, for use in thumbnail menus.
    Stores everything needed for making a thumbnail of an existing
    video."""
    def __init__(self, id, video, coords, effects=[]):
        """Create a Thumb with the given unique ID, from the given video."""
        self.id = id
        self.video = video
        self.coords = coords
        self.size = rect_size(coords)
        self.effects = effects

    def generate(self):
        """Generate .jpg thumbnail images of the video using mplayer, and
        return the full pathname of the directory where the images are
        saved."""
        self.outdir = os.path.abspath('thumb%s' % self.id)
        cmd = 'mplayer "%s" ' % self.video.get('in')

        x, y = self.size
        if 'border' in self.effects:
            cmd += ' -vf expand=%s:%s:2:2 ' % (x+2, y+2)

        if 'glass' in self.effects:
            cmd += ' -vf '
            cmd += 'rectangle=%s:%s,' % (x, y)
            cmd += 'rectangle=%s:%s,' % (x-2, y-2)
            cmd += 'rectangle=%s:%s,' % (x-4, y-4)
            cmd += 'rectangle=%s:%s' % (x-6, y-6)

        cmd += ' -zoom -x %s -y %s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.outdir
        cmd += ' -ss 05:00 -frames %s ' % FRAMES

        print "Generating thumbnails for video %s with command:" % \
                self.video.get('in')
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            #print line
            pass
        return self.outdir


    def decorate(self, label = '', border = 0):
        """Decorate the thumbnail with a text label or black border."""
        if not self.outdir:
            self.generate()
        # For all images in outdir, add decoration
        for image in os.listdir(self.outdir):
            cmd = 'convert %s/%s -gravity south' % (self.outdir, image)
            if label:
                cmd += ' -stroke "#0004" -strokewidth 1'
                cmd += ' -annotate 0 "%s"' % label
                cmd += ' -stroke none -fill white -annotate 0 "%s"' % label
            if border > 0:
                pass
            # Write output back to the original image
            cmd += ' %s/%s' % (self.outdir, image)

            print "Adding label with command:"
            print cmd
            for line in os.popen(cmd, 'r').readlines():
                print line



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
        thumbs[-1].decorate(video.name)
        index += 1
    
    composite_thumbs(thumbs)
    generate_video('composite')

    # TODO:
    # Create a subtitle stream with "button" regions over each thumbnail
    # Multiplex video, audio, and subtitles, output in menu.get('out')


def composite_thumbs(thumbs):
    outdir = 'composite'
    for frame in range(FRAMES):
        cmd = 'convert -size 720x480 xc:skyblue '
        for thumb in thumbs:
            x0, y0, x1, y1 = thumb.coords
            cmd += ' -page +%s+%s' % (x0, y0)
            cmd += ' -label "%s"' % thumb.video.name
            #cmd += ' -frame 6x6+2+2'
            cmd += ' %s/%s.jpg' % (thumb.outdir, string.zfill(frame, 8))
        cmd += ' -mosaic %s/%s.jpg' % (outdir, string.zfill(frame, 8))
        print cmd
        os.popen(cmd, 'r')
  
def generate_video(framedir):
    """Generate a video stream from numbered images in framedir."""
    cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
    cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % framedir
    cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o %s.m2v' % framedir
    print "Generating video stream with command:"
    print cmd
    for line in os.popen(cmd, 'r'):
        print line

    
def generate_vcd_menu(menu):
    """Generate an (S)VCD MPEG menu, saving to the file specified by the menu's
    'out' option."""
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

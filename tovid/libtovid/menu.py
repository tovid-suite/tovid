#! /usr/bin/env python

import string, sys, os
from libtovid import Project

"""Generate Menu elements for a tovid project."""

FRAMES=60

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

    coords = grid_coordinates(720, 480, 3, 2)
    print "coords:"
    print coords
    x0, y0, x1, y1 = coords[0]
    size = rect_size(x0, y0, x1, y1)
    thumbnum = 1
    thumbdirs = []
    for video in menu.children:
        generate_thumbs(video.get('in'), size, "thumbs_%s" % thumbnum)
        thumbdirs.append("thumbs_%s" % thumbnum)
        thumbnum += 1
    
    composite_thumbs(thumbdirs, coords)

    # TODO:
    # Create a video stream of the composite images
    # Create a subtitle stream with "button" regions over each thumbnail
    # Multiplex video, audio, and subtitles, output in menu.get('out')


def composite_thumbs(thumbdirs, coords):
    outdir = 'composite'
    for frame in range(FRAMES):
        cmd = 'convert -size 720x480 xc:skyblue '
        thumbnum = 0
        for dir in thumbdirs:
            x0, y0, x1, y1 = coords[thumbnum]
            thumbnum += 1
            cmd += ' -page +%s+%s' % (x0, y0)
            cmd += ' %s/%s.jpg' % (dir, string.zfill(frame, 8))
        cmd += ' -mosaic %s/%s.jpg' % (outdir, string.zfill(frame, 8))

        os.popen(cmd, 'r')

    
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


def rect_size(x0, y0, x1, y1):
    """Return the size (w,h) of the rectangle defined by the given
    coordinates."""
    return (x1-x0, y1-y0)


def generate_thumbs(video, size, outdir):
    """Generate thumbnail images of a video."""
    # TODO: Solve outdir problem
    print "size: "
    print size
    cmd = 'mplayer "%s" ' % video
    cmd += ' -zoom -x %s -y %s ' % size
    cmd += ' -vo jpeg:outdir="%s" -ao null ' % outdir
    cmd += ' -ss 02:00 -frames %s ' % FRAMES
    print "Generating thumbnails for video " + video + " with command:"
    print cmd
    for line in os.popen(cmd, 'r').readlines():
        #print line
        pass



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply the name of a .tdl file."
        sys.exit()

    proj = Project.Project()
    proj.load_file(sys.argv[1])

    generate_project_menus(proj)

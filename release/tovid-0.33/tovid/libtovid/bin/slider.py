#!/usr/bin/python
# -=- encoding: utf-8 -=-
#
# GPL - Copyright 2007 - Alexandre Bourget
#
# Final credits generator. Generic image scroller, pan-scanner..
# Generated an .mpg/.vob from a single .jpg/.png/...
#
# Now libtovid has interlacing support.
#

from libtovid.render import effect,animation,layer,flipbook
from libtovid.render.animation import Keyframe
import sys
import Image
import optparse

##
# Options parser
##

parser = optparse.OptionParser()

parser.add_option('-s', dest="seconds", type="float", default=5.0,
                  help="Sets the length of the video produced.")
parser.add_option('-t', dest="tvsys", type="string", default='ntsc',
                  help="tvsys supported by libtovid (ntsc, pal, etc)")
parser.add_option('-f', dest="format", type="string", default='dvd',
                  help="format supported by libtovid (dvd, vcd, dvd-vcd, half-dvd)")
parser.add_option('-a', dest="aspect", type="string", default='4:3',
                  help="Aspect ratio, 4:3 or 16:9")
parser.add_option('-i', dest="interlaced", action="store_true", default=False,
                  help="Enable interlaced rendering (experimental)")

parser.add_option('-d', dest="direction", type="int", default=1,
                  help="Scan direction:\n\t1 = top to bottom\n\t2 = bottom to top\n\t3 = left to right\n\t4 = right to left")

parser.add_option('-c', dest="clear", action="store_true", default=False,
                  help="Start with blank image, and scroll from under the screen.\nIf this option is not specified, then the first frame will be filled with\n the first part of the image.")

#parser.set_epilog('Use this program to generate a .vob/.mpg file that slides an image (final credits, pan-scan of an image, etc..')

(opts, args) = parser.parse_args()

if (not len(args)):
    print "ERROR: image list required"
    parser.print_help()
    sys.exit()

if (opts.direction not in [1,2,3,4]):
    print "Direction must be one of: 1, 2, 3, 4.\nSee --help for details."
    sys.exit();

image = args[0]

# Longueur: 155.155, etc... 640x480 dvd..
f = flipbook.Flipbook(opts.seconds, opts.format, opts.tvsys, opts.aspect, interlaced=False)


im = Image.open(image)

im_x = im.size[0]
im_y = im.size[1]

if (opts.direction in [1,2]):
    scale_factor = float(f.w) / float(im_x)
else:
    scale_factor = float(f.h) / float(im_y)

print "Size: %sx%s" % (im_x, im_y)
print "SCALE: %s" % scale_factor
new_x = int(im_x * scale_factor)
new_y = int(im_y * scale_factor)


if (opts.direction == 1):
    p1 = (0, (int(opts.clear) * f.h))
    p2 = (0, - new_y + (int(not opts.clear) * f.h))
elif (opts.direction == 2):
    p1 = (0, - new_y + (int(not opts.clear) * f.h))
    p2 = (0, (int(opts.clear) * f.h))
elif (opts.direction == 3):
    p1 = ((int(not opts.clear) * f.w), 0)
    p2 = (- new_x + (int(opts.clear) * f.w), 0)
elif (opts.direction == 4):
    p1 = (- new_x + (int(not opts.clear) * f.w), 0)
    p2 = ((int(opts.clear) * f.w), 0)


print "SIZE: %sx%s" % (new_x, new_y)
print "p1: %s, %s" % p1
print "p2: %s, %s" % p2

#sys.exit()

# Dimensions de l'image...
l1 = layer.Background('black');
l2 = layer.Image(image,
                 p1,
                 (new_x, new_y))
f.add(l1)
f.add(l2)

# Go translate...

e = effect.Translate(0, f.frames, (p2[0] - p1[0], p2[1] - p1[1]))
l2.add_effect(e)


f.render_video("%s.mpg" % (image.split('.')[0]))

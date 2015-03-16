#!/usr/bin/python
# -=- encoding: utf-8 -=-
#
# GPL - Copyright 2007 - Alexandre Bourget
#
# Still image to .mpg video.
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
#parser.add_option('-u', dest="fullframe", action="store_true", default=False,
#                  help="Specified image is a full frame (no pan-scan nor letterboxing)")


(opts, args) = parser.parse_args()

if (len(args) != 1):
    print "ERROR: One image filename required."
    parser.print_help()
    sys.exit()

image = args[0]

# Longueur: 155.155, etc... 640x480 dvd..
f = flipbook.Flipbook(opts.seconds, opts.format, opts.tvsys, opts.aspect, interlaced=False)


im = Image.open(image)

im_x = im.size[0]
im_y = im.size[1]

print "SIZE: %d %d" % (im_x, im_y)
print "FLIPBOOK: %d %d" % (f.w, f.h)

#sys.exit()

# Dimensions de l'image...
l1 = layer.Background('black');
l2 = layer.Image(image,
                 (0, 0),
                 (f.w, f.h))
f.add(l1)
f.add(l2)

f.render_video("%s.mpg" % (image.split('.')[0]))

#if (opts.direction in [1,2]):
#    scale_factor = float(f.w) / float(im_x)
#else:
#    scale_factor = float(f.h) / float(im_y)

#print "Size: %sx%s" % (im_x, im_y)
#print "SCALE: %s" % scale_factor
#new_x = int(im_x * scale_factor)
#new_y = int(im_y * scale_factor)


#if (opts.direction == 1):
#    p1 = (0, (int(opts.clear) * f.h))
#    p2 = (0, - new_y + (int(not opts.clear) * f.h))
#elif (opts.direction == 2):
#    p1 = (0, - new_y + (int(not opts.clear) * f.h))
#    p2 = (0, (int(opts.clear) * f.h))
#elif (opts.direction == 3):
#    p1 = ((int(not opts.clear) * f.w), 0)
#    p2 = (- new_x + (int(opts.clear) * f.w), 0)
#elif (opts.direction == 4):
#    p1 = (- new_x + (int(not opts.clear) * f.w), 0)
#    p2 = ((int(opts.clear) * f.w), 0)


#print "SIZE: %sx%s" % (new_x, new_y)
#print "p1: %s, %s" % p1
#print "p2: %s, %s" % p2


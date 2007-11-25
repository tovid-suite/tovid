#!/usr/bin/python
# -=- encoding: utf-8 -=-
#
# GPL - Copyright 2007 - Alexandre Bourget
#
# PhotoZoom animator
# Give it a .jpg/.png/... and it'll output a .vob/.mpg showing the image
# zoomed in gracefully and moving a little bit around.
#
# Ideal for slideshow generation, and Cinelerra manipulation (music montage)
#


import os
import sys
import Image # for im.size, etc..
import optparse
from libtovid.render import *
from libtovid.transcode import *

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
parser.add_option('-m', dest="move", action='store_true', default=False,
                  help="Enable move/zoom")

(opts, args) = parser.parse_args()


if (not len(args)):
    print "ERROR: image list required"
    parser.print_help()
    sys.exit()

images = args


##
# Setup the layers, effects
##

print "Processing:"
print images

fb = flipbook.Flipbook(opts.seconds, opts.format, opts.tvsys, opts.aspect)

# add black background.
fb.add(layer.Background())

im = Image.open(images[0]) # for im.size

k = [animation.Keyframe(0, 0.0),
     animation.Keyframe(fb.frames, 1.0)]
photozoom = effect.PhotoZoom(k)

f1 = float(fb.w) / float(im.size[0])
f2 = float(fb.h) / float(im.size[1])
print "Factor 1 and 2: %f and %f" % (f1, f2)

if (f1 <= f2):
    nw = f1 * im.size[0]
    nh = f1 * im.size[1]
else:
    nw = f2 * im.size[0]
    nh = f2 * im.size[1]
    
p1 = (fb.w - nw) / 2
p2 = (fb.h - nh) / 2

print "Size     WxH: %d x %d" % (nw, nh)
print "Position X,Y: %d , %d" % (p1, p2)

l = layer.Image(images[0], (p1,p2), (nw, nh))

# Only if we want to move..
if (opts.move):
    l.add_effect(photozoom)

fb.add(l)

##
# Process
##


fb.render_video('./%s.mpg' % (images[0].split('.')[0]))


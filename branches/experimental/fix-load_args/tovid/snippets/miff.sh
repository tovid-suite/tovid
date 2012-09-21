#!/bin/bash


# 3 pipes using miff:- , mpr: and no files on disk
convert magick:rose -write mpr:rose +delete \
-background grey \
-label "Pete Rose"   mpr:rose -label  "Feels thorny" mpr:rose -label "is a rose ..." mpr:rose \
miff:- | \
montage - -background none  -tile x4   -fill black  -pointsize 16 -geometry '96x64' \
miff:- | \
convert magick:rose -resize 432x288! -write mpr:rosey +delete \
xc:grey -size 720x480 -resize 720x480! -write mpr:bg +delete \
mpr:bg -gravity south -pointsize 40 -fill black -draw 'text 0,20 "Nice pipes !"' \
-page +68+118 -  -page +210+100  mpr:rosey -mosaic  -resize 720x480! \
miff:- | display -


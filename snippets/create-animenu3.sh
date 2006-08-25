#!/bin/sh
#
# by grepper on irc.freenode.net
#
# Currently this script is for NTSC DVD mpeg-2 video
#
# First, outside of this script, you must create a directory 
# of your mpegs that will be used in the thumbnails. Use 4 videos, 
# named 1.mpg, 2.mpg, 3.mpg and 4.mpg
# as well as bg.mpg which will be the largest cip - 
# it should probably be some kind of intro though it will
# show at the same time as the other clips in the menu.
# These may also be symlinks to the real files.
#
# Also if you want to use your own background you must have a jpeg  
# in this root directory.  If you do use your own background file,  
# change the variable BACKGROUND_PIC below to the name of your file. 
#
# So at the moment you have just  /mpg  in the current directory.
# The script will create a pics/ directory that will look like this:  
# 1/ 2/ 3/ 4/ intro/  background/ 
#
# Right now the script is set to process only 300 frames as a test
# -  about 10 seconds of video at ntsc framerate (29.970 fps)
# Change the FRAMES= variable to however long you want the menu to be.
# Your video clips must all be long enough for the time you choose.
#
# Let the script do the rest !
#######################################################################

# The 1st 5 vars are for the text overlay - I couldn't figure out how 
# to do spaces so just used single words:
# "convert" didn't like any kind of escaping I did.

TITLE=""
CLIP1=""
CLIP2=""
CLIP3=""
CLIP4=""

FRAMES=$1
FRAMERATE=29.970
TIME=`awk 'BEGIN { printf("'"$FRAMES"'" /"'"$FRAMERATE"'")"\n" ; exit  }'`
BACKGROUND_PIC=template.jpg
QUALITY=100   # jpeg compression level - 75 is fine - use 100 is you have space
INTRO_BORDER=10x10
BORDER_COLOUR="#111011"       
INTRO_RAISE="-raise 4x4"  #this may also be +raise which gives a different effect
CLIP_BORDER=5x5
CLIP_RAISE="-raise 3x3"

echo -e "\nWe will be creating a menu of $TIME seconds length\n"

echo -e "\nCreating the directory structure\n"

# create directories
mkdir -p pics/{1,2,3,4,intro,background}

# use mplayer to make jpegs of the intro clip in the /intro dir

echo -e "\nCreating jpegs of the intro clip in the intro/ directory\n"

mplayer -vo jpeg:quality=$QUALITY:outdir=pics/intro/ -ao null -zoom -x 432 -y 288  -ss 0:0:01 -frames $FRAMES  mpeg/bg.mpg > /dev/null 2>&1

# use convert to create a background template
echo -e "\nCreating the background images in background/ - this will take some time\n"

# a few options I tried for creating bg with only ImageMagick
#convert  -size 720x480 xc:black template.jpg 
#convert  -size 720x480 pattern:bricks -fill "#8B7D6B" -colorize "150" template.jpg 
convert  magick:GRANITE -size 240x240 -resize 240x240  -fill "#8B7D6B" -colorize "150" -implode 2  temp.jpg
convert -size 720x480 tile:temp.jpg template.jpg


# experiment to see if I can draw some labels and title: not sure how to
# script this for changing layouts and geometries 

echo -e "just for giggles try drawing some labels\n"


convert -font helvetica   -fill "#080707" -pointsize 20    -draw 'text 66,157 '$CLIP1'' -draw 'text 66,253 '$CLIP2''  -draw 'text 66,349 '$CLIP3''   -draw 'text 66,445 '$CLIP4'' -pointsize 50 -gravity "North" -draw 'text 0,20 '$TITLE'' $BACKGROUND_PIC $BACKGROUND_PIC


# copy the BACKGROUND_PIC to pics/background/

echo -e "\nMaking $FRAMES copies of the finalized $BACKGROUND_PIC in pics/background/\n" 

for i in `find pics/intro -name \*.jpg -exec basename {} \;`;do cp $BACKGROUND_PIC pics/background/$i;done


# start making some more  jpegs with mplayer

echo -e "\nCreating jpegs of clips 1 to 4 in directories 1/ 2/ 3/ and 4/ \n "

mplayer -vo jpeg:quality=$QUALITY:outdir=pics/1 -ao null -zoom -x 96 -y 64  -ss 0:0:01 -frames $FRAMES  mpeg/1.mpg >/dev/null 2>&1
mplayer -vo jpeg:quality=$QUALITY:outdir=pics/2 -ao null -zoom -x 96 -y 64  -ss 0:0:01 -frames $FRAMES  mpeg/2.mpg >/dev/null 2>&1
mplayer -vo jpeg:quality=$QUALITY:outdir=pics/3 -ao null -zoom -x 96 -y 64  -ss 0:0:01 -frames $FRAMES  mpeg/3.mpg >/dev/null 2>&1
mplayer -vo jpeg:quality=$QUALITY:outdir=pics/4 -ao null -zoom -x 96 -y 64  -ss 0:0:01 -frames $FRAMES  mpeg/4.mpg >/dev/null 2>&1

# use convert on each jpeg to make prettier frames

echo -e "\nCreating borders for all pictures - please be patient\n"
for i in pics/intro/*.jpg;do convert -border $INTRO_BORDER -bordercolor $BORDER_COLOUR $INTRO_RAISE $i $i;done &
#for i in pics/{1,2,3,4}/*.jpg;do mogrify -border 2x2 -bordercolor $BORDER_COLOUR $i;done
for i in pics/{1,2,3,4}/*.jpg;do convert -border $CLIP_BORDER -bordercolor black $CLIP_RAISE $i $i;done


echo -e "\nUsing imagemagick to overlay clip images onto background images\n"
echo -e "\nThis will take some time, please be patient\n"


# use convert -mosaic rather than composite as its waay faster

for i in `find pics/background  -name \*.jpg -exec basename {} \;`;do convert  -size 720x480 pics/background/$i  -page +68+66 pics/1/$i -page +68+162 pics/2/$i -page +68+258 pics/3/$i -page +68+354 pics/4/$i -page +210+100 pics/intro/$i -mosaic pics/background/$i;done


echo -e "\nPictures are complete !  - now creating video stream with jpeg2yuv and encoding to mpg\n"

# create a yuv stream from the jpegs in /background which we pipe to mpeg2enc

jpeg2yuv -v 0 -f 29.970 -I p -L 1 -b1 -j pics/background/%08d.jpg | mpeg2enc -v 0 -q 3 -f 8 -o animenu.mpg

echo -e "\nEncoding complete !  Your menu should be ready in the file $PWD/animenu.m2v\n"

# clean up
#rm -fr pics/
#rm -f template.jpg temp.jpg intro-frame.jpg clips-frame.jpg

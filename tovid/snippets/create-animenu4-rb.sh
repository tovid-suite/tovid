#!/bin/sh

########## here follows my script to create a rounded intro menu ##########
# by grepper on irc.freenode.net

TITLE="Smallville"
CLIP1="Arrival"
CLIP2="Mortal"
CLIP3="Hidden"
CLIP4="Aqua"
LABEL=""
FRAMES=$1       # comment out "usage" block if you change this
FRAMERATE=29.970
TIME=`awk 'BEGIN { printf("'"$FRAMES"'" /"'"$FRAMERATE"'")"\n" ; exit  }'`
BACKGROUND_PIC=template.jpg
JPG_QUALITY=75   # jpeg compression level- 75 is fine
PNG_COMPRESS=6    # huge no matter what level you use :P 
INTRO_BORDER=10x10
BORDER_COLOUR="#111011"
INTRO_RAISE="-raise 4x4"  #this may also be +raise which gives a different effect
CLIP_BORDER=5x5 # unused
CLIP_RAISE="-raise 3x3"  #unused
XxYSIZE=96x64
TITLE_POINTSIZE=40


################## Functions #######################


# round function

#########################

# the rounding function below shamelessly borrowed from 
# someone calling himself Astarna,  kind enough to post his solution
# to a problem on the magic-users  mailing list 
# http://studio.imagemagick.org/pipermail/magick-users/2004-September/013557.html

round()
{
IMG="$1"
OUTFILE="$2"
DIM=`identify -format %wx%h $IMG`
DIM2=`identify -format %w,%h $IMG`
# create the mask for the image
# 10,10 is the position... 0,0 would be centered
# 220,200 is the size of the circle
convert -size $DIM xc:black \
        -fill white \
        -draw "RoundRectangle 10,10 220,220, 105,105" \
        +matte \
        -compose CopyOpacity \
        mask.png

# create the shadow
# need to change the position, and expand it.
# #999999 is the shade... and set the gaussian 7x7
convert -size $DIM xc:white \
        -fill "#999999" \
        -draw "RoundRectangle 20,20 235,235, 105,105" \
        -blur 7x7 \
        -fill white \
        -matte \
        mask_shadow.png

# implement the mask.. once mask is created underlay the shadow
composite -compose CopyOpacity \
        mask.png -background white $IMG $OUTFILE
# add the shadow
convert $OUTFILE -background none  \
        mask_shadow.png \
        -compose Dst_Over tmp.png
}

################################################

# mkround function

# the mkround function calls mplayer, the round function and converts, adds text
# and moves the mpeg to the proper temp directory
# hm, guess I should rename it

mkround()
{

# usage mkround INMPEG OUTDIR

INMPEG=$1
OUTDIR=$2


# help mkround identify which infile its currently processing

if [ "$1" = "mpeg/1.mpg" ]; then
LABEL="$CLIP1"
elif [ "$1" = "mpeg/2.mpg" ]; then 
LABEL="$CLIP2"
elif [ "$1" = "mpeg/3.mpg" ]; then 
LABEL="$CLIP3"
elif [ "$1" = "mpeg/4.mpg" ]; then 
LABEL="$CLIP4"
fi


# create the pngs from the original mpeg

echo -e "\nCreating pngs of clip $i then running the round function on each\n"


mplayer -vo png:z=$PNG_COMPRESS  \
-ao null -zoom -x 232 -y 232  \
-ss 0:0:01 \
-frames $FRAMES $INMPEG >/dev/null 2>&1

# run round function on each

for i in *.png; do 
round $i $i
done

# resize the images back to 720x480
# this is wasteful and an extra step
# . . . if only I could convert round.sh to do various sized images
# oops . just figured this out - add to next script :)


echo -e "\nResizing images, applying the label \"$LABEL\" to them, and moving them to $1\n"

for i in 000*.png; do
convert -size $XxYSIZE  \
-resize $XxYSIZE!  \
-background none \
-font helvetica \
-pointsize 20 \
-gravity "South" \
-splice 0x20 \
-fill "#000000" \
-annotate 0x0 "$LABEL" \
$i pics/$OUTDIR/$i
done

# better remove the pngs so the next run will not have to overwrite them

rm -f 000*.png

}


#################### End of functions ###########################

# now lets get started


# check if we were called with a "number of frames argument"
# just for testing speed etc

if [ -z "$1" ]
then
        echo "usage: $0 <number of frames to process>"
exit
fi


echo -e "\nWe will be creating a menu of $TIME seconds length\n"

# create the directory structure

mkdir -p pics/{1,2,3,4,intro,background}

# run mplayer to create framed jpegs in pics/intro
# which is the one clip we will leave rectangular

echo -e "\nMaking images from the intro clip in clips/intro\n"

mplayer -vo jpeg:quality=$JPG_QUALITY:outdir=pics/intro/ \
-vf expand=-20:-20 \
-ao null \
-zoom -x 432 -y 288  \
-ss 0:0:01 \
-frames $FRAMES \
mpeg/bg.mpg > /dev/null 2>&1


# run the mkround() function on each file 
# which  will invoke mplayer then the round() function creating the effect
  
echo -e "\nThis creates $FRAMES frames in current dir at png size (big) so be wary of space\n"

for i in 1 2 3 4; do
mkround mpeg/$i.mpg $i
done


# make a background template with ImageMagick


convert  magick:GRANITE \
-size 240x240 \
-resize 240x240  \
-fill "#8B7D6B" \
-colorize "150" \
-implode 2  \
temp.jpg
convert -size 720x480 tile:temp.jpg $BACKGROUND_PIC

#convert  -size 720x480 xc:black $BACKGROUND_PIC    <- nice effect with round buttons

# draw text on the template

convert -font helvetica   \
-fill "#080707"  \
-pointsize $TITLE_POINTSIZE \
-gravity "North" \
-draw 'text 0,20 '$TITLE'' $BACKGROUND_PIC $BACKGROUND_PIC



# copy templates to pics/background

for i in `find pics/intro -name \*.jpg -exec basename {} \;`; do
cp $BACKGROUND_PIC pics/background/$i
done


# overlay them onto the background images in /background

echo -e "\nUsing imagemagick to overlay clip images onto background images\n"
echo -e "This will take some time, please be patient\n"


# use convert rather than composite as its waay faster


for i in `find pics/1  -name \*.png -exec basename {} \;`; do
convert  -size 720x480 pics/background/`echo $i|sed 's/.png/.jpg/'` \
-page +68+66 pics/1/$i \
-page +68+162 pics/2/$i \
-page +68+258 pics/3/$i \
-page +68+354 pics/4/$i \
-page +210+100 pics/intro/`echo $i|sed 's/.png/.jpg/'` \
-mosaic pics/background/`echo $i|sed 's/.png/.jpg/'` 
done


# create m2v

echo -e "\nCreating a stream with jpeg2yuv and piping it to mpeg2enc\n"

jpeg2yuv -v 0 -f 29.970 -I p -n $FRAMES -L 1 -b1 \
-j pics/background/%08d.jpg | mpeg2enc -v 0 -q 3 -f 8 -o animenu.m2v


echo -e "\nThe menu is ready and is at `pwd`/animenu.m2v"

# clean up
#rm -fr pics
#rm -f template.jpg temp.jpg intro-frame.jpg clips-frame.jpg

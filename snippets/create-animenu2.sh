#!/bin/sh
#
# by grepper on irc.freenode.net
#
# Currently this script is for NTSC DVD mpeg-2 video
#
# First, outside of this script, you must create a directory of your mpegs
# that will be used in the thumbnails. Use 4 videos, named 1.mpg, 2.mpg, 3.mpg and 4.mpg
# as well as bg.mpg which will be the largest cip - it should probably be some kind of intro
# though it will show at the same time as the other clips in the menu.
# These may also be symlinks to the real files residing somewhere else.
#
# Also if you want to use your own background you must have a jpeg named bg.jpg 
# in this root directory.  If you do use your own background file,  uncomment the line
# that copies the bg.jpg (line 33) and comment out the following line containing 
# "convert  -size 720x480 pattern:bricks"
#
# So at the moment you have just  /mpg  and perhaps bg.jpg in the current directory.
# Below the script will create a pics/ directory that will look like this:  
# 1/ 2/ 3/ 4/ intro/  background/ 
#
# Right now the script is set to process only about 300 frames as a kind of test
# -  about 10 seconds of video at ntsc framerate (29.970 fps)
# Change the FRAMES= variable in the 1st line to however long you want the menu to be.
# Of course your video clips must all be long enough for the time you choose.
#
# Let the script do the rest ! Your menu will be called "animenu.mpg" when its done
#
FRAMES=600
FRAMERATE=29.970
TIME=`awk 'BEGIN { printf("'"$FRAMES"'" /"'"$FRAMERATE"'")"\n" ; exit  }'`
#
echo -e "\nWe will be creating a menu of $TIME seconds length\n"
echo -e "\nCreating the directory structure\n"
mkdir -p pics/{1,2,3,4,intro,background}
echo -e "\nCreating jpegs of the intro clip in the intro/ directory\n"
mplayer -vo jpeg:outdir=pics/intro/ -vf expand=-20:-20 -ao null -zoom -x 432 -y 288  -ss 0:0:01 -frames $FRAMES  mpeg/bg.mpg > /dev/null 2>&1
#for i in `find pics/intro -name \*.jpg -exec basename {} \;`;do cp bg.jpg pics/background/$i;done
echo -e "\nCreating the background images in background/ - this will take some time\n"
#for i in `find pics/intro -name \*.jpg -exec basename {} \;`;do convert  -size 720x480 pattern:bricks -fill "#8B7D6B" -colorize "150"  pics/background/$i;done
convert  -size 720x480 pattern:bricks -fill "#8B7D6B" -colorize "150" template.jpg
for i in `find pics/intro -name \*.jpg -exec basename {} \;`;do cp template.jpg  pics/background/$i;done
echo -e "\nCreating jpegs of clips 1 to 4 in directories 1/ 2/ 3/ and 4/ \n "
mplayer -vo jpeg:outdir=pics/1 -vf expand=-8:-8 -ao null -zoom -x 96 -y 64  -ss 0:0:00 -frames $FRAMES  mpeg/1.mpg  >/dev/null 2>&1
mplayer -vo jpeg:outdir=pics/2 -vf expand=-8:-8 -ao null -zoom -x 96 -y 64  -ss 0:0:00 -frames $FRAMES  mpeg/2.mpg  >/dev/null 2>&1
mplayer -vo jpeg:outdir=pics/3 -vf expand=-8:-8 -ao null -zoom -x 96 -y 64  -ss 0:0:00 -frames $FRAMES  mpeg/3.mpg >/dev/null 2>&1
mplayer -vo jpeg:outdir=pics/4 -vf expand=-8:-8 -ao null -zoom -x 96 -y 64  -ss 0:0:00 -frames $FRAMES  mpeg/4.mpg >/dev/null 2>&1
#for i in pics/intro/*.jpg;do mogrify -border 8x8 -bordercolor black $i;done
#echo -e "\nCreating borders for all pictures - please be patient\n"
#for i in pics/intro/*.jpg;do convert -border 6x6 -bordercolor black -raise 3x3 $i $i;done
#for i in pics/{1,2,3,4}/*.jpg;do mogrify -border 2x2 -bordercolor black $i;done
#for i in pics/{1,2,3,4}/*.jpg;do convert -border 3x3 -bordercolor black -raise 2x2 $i $i;done
echo -e "\nUsing imagemagick's composite to overlay clip images onto the background images\n"
echo -e "\nThis will take some time, please be patient\n"
for i in `find pics/intro -name \*.jpg -exec basename {} \;`;do composite  -compose over  -geometry +210+100 pics/intro/$i pics/background/$i pics/background/$i;done 
for i in `find pics/1/ -name \*.jpg -exec basename {} \;`;do composite  -compose over  -geometry +68+66 pics/1/$i pics/background/$i pics/background/$i;done 
for i in `find pics/2/ -name \*.jpg -exec basename {} \;`;do composite  -compose over  -geometry +68+162 pics/2/$i pics/background/$i pics/background/$i;done 
for i in `find pics/3/ -name \*.jpg -exec basename {} \;`;do composite  -compose over  -geometry +68+258  pics/3/$i pics/background/$i pics/background/$i;done 
for i in `find pics/4/ -name \*.jpg -exec basename {} \;`;do composite  -compose over  -geometry +68+354  pics/4/$i pics/background/$i pics/background/$i;done
sleep 5
echo -e "\nPictures are complete !  - now creating video stream with jpeg2yuv and encoding to mpg\n"
jpeg2yuv -v0 -f 29.970 -I p -L 1 -b1 -j pics/background/%08d.jpg | mpeg2enc -v0 -q 3 -f 8 -o animenu.mpg
echo -e "\nEncoding complete !  Your menu should be ready in the file $PWD/animenu.mpg\n"

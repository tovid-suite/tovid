#!/bin/sh
# by grepper on irc.freenode.net

TITLE="Smallville Season 5"
CLIP1="Arrival"
CLIP2="Mortal"
CLIP3="Hidden"
CLIP4="Aqua"
LABEL=""
FRAMES=$2       # comment out "usage" block if you change this
FRAMERATE=29.970
TIME=`awk 'BEGIN { printf("'"$FRAMES"'" /"'"$FRAMERATE"'")"\n" ; exit  }'`
JPG_QUALITY=75   # jpeg compression level- 75 is fine
PNG_COMPRESS=1    # huge no matter what level you use :P

# make sure it is called with the right # of arguments
if [ ! $# == 3 ]; then
echo "usage: $0 <infile>  <frames (number of)>  <outfile basename (no extension> "
  exit
fi

# create pics/ dir

mkdir -p pics/background

# make a conf file for mencoder for subs
# Note: add -freetype to the mencoder line if not specifying a font= in the conf file

 echo -e "
# font=/home/robert/.fonts/Candice.ttf
 ffactor="10" #black outline
 sub-bg-alpha="0" #background color ala closed captions
 sub-bg-color="0" #black to white
 subfont-text-scale="4.7" #truetype font scaling
 subfont-blur="1" #Slight blur
 subpos="90"
" >$1.conf

# make a subtitle file

SUBTIME=$[$FRAMES / 30 + 1]
echo -e "1
00:00:00,000 --> 00:00:$SUBTIME,000
$TITLE" > $1.srt


# extract png's  - without z=0 (default) files are much smaller
# high compression is too great a load on processor though
# and doesn't make that much diff in size

echo -e "\nExtracting images from the video\n"
mplayer -vo png:z=$PNG_COMPRESS \
-ao null \
-vf expand=-288:-192,rectangle=432:288,rectangle=430:286,rectangle=428:284,rectangle=426:282  \
-zoom -x 432 -y 288  -ss 0:0:01 -frames $FRAMES $1 >/dev/null 2>&1


echo -e "\nMoving the images to pics/background\n"
mv 000*.png pics/background
echo -e "\nEncoding the pngs to a stream with png2yuv and mpeg2enc\n"

png2yuv -v 0 -f 29.970 -I p -b 1 -n $FRAMES \
-j  pics/background/%08d.png|mpeg2enc -a 2 -v 0 -q 3 -f 8  -o $3.m2v 

echo -e "\nCreating $TIME seconds of silence for background in $3.ac3\n"

ffmpeg -v 0 -t $TIME -y \
-f s16le -ac 2 -ar 48000 -i /dev/zero -ab 224 -acodec ac3 $3.ac3 > /dev/null 2>&1
echo -e "\nmplexing $3.m2v with $3.ac3\n"
mplex -v 0 -V -f 8 -b 1000 -o $3.mpg  $3.m2v  $3.ac3


echo -e "\nAdding a title with mencoder\n"
mencoder  -fontconfig -ovc lavc -lavcopts vcodec=mpeg2video:vme=4:mbd=1 -oac copy -sub `pwd`/bg.mpg.srt  -include `pwd`/bg.mpg.conf $3.mpg  -o $3-final.mpg >/dev/null 2>&1

echo -e "\nYour video is ready and is located at `pwd`/$3-final.mpg\n"

# clean up

# rm -fr pics

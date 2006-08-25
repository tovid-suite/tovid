#!/bin/bash
# Author: corpix64

QUIET=1

BITRATE=2000
ABITRATE=128
QUAL=6
DVDDEV="/dev/hdd"
TEST="-endpos 10M"
TEST=""

#[ "$QUIET" == "1" ] && $QUIET=">/dev/null 2>&1"

get_args(){
 while test $# -gt 0; do
         case "$1" in
         "-b")
         shift
         BITRATE="$1" # in kbit per sec of <16000
         ;;
         "-dvddev")
         shift
         DVDDEV="$1" # in kbit per sec of <16000
         ;;


         "-a")
         shift
         ABITRATE="$1" # in kbit per sec
         ;;
         "-q")
         shift
         QUAL="$1" # 0-10 default=6
         ;;


         "--delete")
         DELETE=1
         ;;
         "-dvd")
          DVD=1
          ;;
        # Null option; ignored.
         "-" )
         ;;
          "-in" )
          shift
          # symlink, if FILE has whitespaces
#         FILE="$1"
#         echo "$FILE" | grep -q " " && ln -s "$FILE" $(echo `basename "$i"` | tr " " "_") && FILE=$(echo `basename "$i"` | tr " " "_") && echo "symlink = $1"
          while ! [ "$1" == "" ]; do
          if  [ "$IN_FILES" == "" ];
             then IN_FILES="$1"
             else IN_FILES="${IN_FILES} $1"
          fi
          shift
          done
          # Get a full pathname for the infile
    #      pushd `dirname "$IN_FILE"` >/dev/null
    #      IN_DIR=${PWD}
    #      popd >/dev/null
    #      IN_FILE=${IN_DIR}/`basename "$IN_FILE"`

          ;; 
          esac
     # Get next argument
        shift
    done 
  
}

XVIDOPTS="me_quality=$QUAL:chroma_me:chroma_opt:trellis:max_key_interval=300:vhq=4:autoaspect"
#INTERMATRIX=quant_intra_matrix=18,18,18,18,19,21,23,27,18,18,18,18,19,21,24,29,18,18,19,20,22,24,28,32,18,18,20,24,27,30,35,40,19,19,22,27,33,39,46,53,21,21,24,30,39,50,61,73,23,24,28,35,46,61,79,98,27,29,32,40,53,73,98,129:intra_matrix=8,16,16,16,17,18,21,24,16,16,16,16,17,19,22,25,16,16,17,18,20,22,25,29,16,16,18,21,24,27,31,36,17,17,20,24,30,35,41,47,18,19,22,27,35,44,54,65,21,22,25,31,41,54,70,88,24,25,29,36,47,65,88,115

midentify(){
        echo "probing for video info ..."
        mplayer -vo null -ao null -frames 0 -identify "$@" 2>/dev/null |  grep "^ID" | sed -e 's/[`\\!$"]/\\&/g' | sed -e '/^ID_FILENAME/ { s/^ID_FILENAME=\(.*\)/ID_FILENAME="\1"/g; }'
}

get_args "$@"
echo $BITRATE
echo $IN_FILES


#mencoder dvd:// -dvd-device "$dvd" -ovc copy  -oac copy -o `basename "$dvd"`.avi

if [ "$DVD" == "1" ];
then
 DVD_IN="-dvd-device $DVDDEV dvd://1"
 IN_FILES="$(dvdbackup -i $DVDDEV -I | grep "DVD-Video information" | awk '{print $8}')" # only used for output!
fi
for i in $IN_FILES
do

echo "SOURCE FILE =  $i"
[ "$DVD" == "1" ] || [ -f "$i" ] || { echo "file does NOT exist" ;  exit;}

if [ "$DVD" == "1" ]
then
ID_VIDEO_WIDTH=720
ID_VIDEO_HEIGHT=576
else
    eval `midentify "$i" | grep ID_VIDEO`
fi
#ID_VIDEO_WIDTH=720
#ID_VIDEO_HEIGHT=576

POSTFIX=xvid_${ID_VIDEO_WIDTH}x${ID_VIDEO_HEIGHT}
echo "using RES: $ID_VIDEO_WIDTH : $ID_VIDEO_HEIGHT"
echo "converting "$i" into xvid,bitrate=$BITRATE,2-pass,mp3@$ABITRATE kbps,$ID_VIDEO_WIDTH x $ID_VIDEO_HEIGHT"
echo "Pass 1 ..."
PASS1="mencoder $TEST $TIME -quiet -nosound -ovc xvid -xvidencopts turbo:stats:${XVIDOPTS}:pass=1 -o /dev/null "
if [ "$DVD" == "1" ]
    then
    PASS1="$PASS1  $DVD_IN"
    time $PASS1  >/dev/null 2>&1
    else
    PASS1="$PASS1   $i"
    time $PASS1 >/dev/null 2>&1
fi

#exit
echo "Pass 2 ..."

SCALE="aspect=16:9,cropdetect,scale=$ID_VIDEO_WIDTH:$ID_VIDEO_HEIGHT:1,"
#SCALE="scale=$ID_VIDEO_WIDTH:$ID_VIDEO_HEIGHT:1,"
SCALE=""
[ "$DVD" == "1"  ] && SCALE="" # dont rescale for dvds
echo $SCALE
PASS2="mencoder $TEST  -af volnorm=1:hrtf -sws 9 -ovc xvid -xvidencopts $XVIDOPTS:pass=2:bitrate=$BITRATE -oac mp3lame -vf-add ${SCALE}kerndeint -lameopts br=$ABITRATE:abr -o `basename "$i" .avi`_$POSTFIX.avi"
if [ "$DVD" == "1" ]
    then
    PASS2="$PASS2  -noautosub -alang de -noautosub $DVD_IN"
    time $PASS2 >/dev/null 2>&1
    else
    PASS2="$PASS2 $i"
    $PASS2 >/dev/null 2>&1
    time $PASS2  && [ "$DELETE" == "1" ] && echo "deleting source video.." "$i"
fi

done

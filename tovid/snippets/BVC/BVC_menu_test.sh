#!/bin/bash

ARGS=("$@")
WORK_DIR=$HOME/tmp/BVC
BVC_LOG=$WORK_DIR/BVC.log
TOTAL_PNGS=101
INTRO_VIDEO="$WORK_DIR/intro.avi"
MAX_ANI_LENGTH=150
TARGET=DVD
LINE=$(for ((i=1; i<=79; i++));do echo -n =;done)
TITLE_PAGE=animated
VID_SIZE_OPT=720x480
FRAME_STYLE=fancy
FRAME_CMD=fancy
TITLE_PG_TITLE="My Video Collection"
DATA_DIR=$HOME/.BVC/data/
SPUMUX_XML=$WORK_DIR/spumux.xml
DVDAUTHOR_XML=$WORK_DIR/dvdauthor.xml
SUB_MENU="false" # set to anything but true if submenu not wanted

##############################################################################
#                                 Functions                                  #
##############################################################################

function cleanlog()
# process $BVC_LOG.tmp variously - eg. ffmpeg's output is ugly without this
{
FOLD="fold -bs"
NO_CR="tr -d '\r'"
RELINE="{s/$SED_VAR/\n$SED_VAR/g}"
TMP_LOG="$BVC_LOG.tmp"
NOSPACE="tr -s ' '"


case "$1" in
    1 )
        $FOLD $TMP_LOG >> $BVC_LOG
        echo >> $BVC_LOG
        ;;
    2 )
        $NO_CR < $TMP_LOG | $FOLD >> $BVC_LOG
        echo >> $BVC_LOG
        ;;
    3 )
        $NO_CR < $TMP_LOG | sed $RELINE | $FOLD >> $BVC_LOG
        echo >> $BVC_LOG
        ;;
    4 )
        $NOSPACE < $TMP_LOG | $FOLD >> $BVC_LOG
        ;;
esac

rm -f $BVC_LOG.tmp
}

function sorry_msg()
{
echo -e "Oops . . .Something went wrong.\nThere was a problem \
creating the $OUTPUT. \
\nPlease check the log at $BVC_LOG"
}

function usage()
{
echo -e "Usage: `basename $0` -S (SVCD)|-D (DVD)
        Other options: \n \
        -d <cdrom or dvd device> Default: /dev/cdrom and /dev/dvd respectively \n \
        -f <fade audio in/out in secs. eg. 1.0 or 0.5> \n \
            Default: -f 1    For no fade use -f 0 \n \
        -b <frame border style> fancy, steel, or none. \n \
            Default: kdialog prompt  \n \
        -a <title page style> none, animated, or plain. \n \
            Default: kdialog prompt"

}

function usage2()
{
    echo -e "\nError: option requires an argument.\n \
    For -b use either 'fancy', 'steel', or 'none'. \n \
    For -f give fade-in/fade-out time in seconds, ie. 1.0 or 0.6\n \
    For -d give device name: Default /dev/dvd for DVD or /dev/cdrom for SVCD\n \
    For -a give either 'none', 'plain', or 'animated'\n"

}

function vid_length()
{
mencoder "$1" -quiet \
-ovc copy -oac pcm -o /dev/null |grep "Video stream"|awk '{print $10}'
}

function static_fade()
# this is suitable for fades for static images, not animated sequences
# usage: static_fade type <string discribing fade type for progress bar
{
# check args
if [[ -n $2 && $2 = "-fo" ]]; then

:
else
    # use -dissolve to create fade effect
    S=100
    for ((X=0; X<50; X++)) ; do
        composite -dissolve $S $WORK_DIR/black.png \
        "${FADIN_PNGS[X]}" "${FADIN_PNGS[X]}"
        S=$((S-2))
    done
fi

# do fade-outs
S=0
for ((Y=0; Y<50; Y++)) ; do
    composite -dissolve $S $WORK_DIR/black.png \
    "${FADEOUT_PNGS[Y]}" "${FADEOUT_PNGS[Y]}"
    S=$((S+2))
done
}

function format_seconds()
{
awk '{
hr=($1/3600); hd=(sprintf("%02d", hr))
mr=((hr-hd)*60); md=(sprintf("%02d", mr))
s=((mr-md)*60); sd=(sprintf("%02d", s))
t=(sprintf("%02d:%02d:%06.3f" ,hd,md,s)); print t}' <<< $1
}


function fancy()
# thanks to Anthony Thyssen http://www.cit.gu.edu.au/~anthony/graphics/imagick6
# for this function: the pngs used are copies of his example gifs
# usage: fancy infile <infile dimension (XxY)> <outfile>
{

DIM=`identify -format %wx%h $1`
NEW_DIM=$2
for i in $1; do
    convert -size $DIM $1 \
    -thumbnail "$NEW_DIM>" \
    -matte  -compose Copy \
    -bordercolor Black -border 2 -bordercolor Sienna4 -border 3 \
    -bordercolor Black -border 1 -bordercolor none -border 2 \
    -bordercolor Black -border 2 -bordercolor Sienna4 -border 3 \
    -bordercolor Black -border 1 \
    -compose Over \
    \( $DATA_DIR/fancy_add.png \) -gravity NorthWest -composite \
    \( $DATA_DIR/fancy_add.png -flip       \) -gravity SouthWest -composite \
    \( $DATA_DIR/fancy_add.png       -flop \) -gravity NorthEast -composite \
    \( $DATA_DIR/fancy_add.png -flip -flop \) -gravity SouthEast -composite \
    -compose DstOut \
    \( $DATA_DIR/fancy_sub.png \)             -gravity NorthWest -composite \
    \( $DATA_DIR/fancy_sub.png -flip       \) -gravity SouthWest -composite \
    \( $DATA_DIR/fancy_sub.png       -flop \) -gravity NorthEast -composite \
    \( $DATA_DIR/fancy_sub.png -flip -flop \) -gravity SouthEast -composite \
    $3
done

}

function steel()
# this creates a steel frame instead of a fancy frame
{
convert -size $2 -border 4x4 -bordercolor "#444744" -raise 2x2 "$1" "$3"
}

function cleanup()
{
exit 1
}

##############################################################################
#                          	End of functions                                 #
##############################################################################

trap cleanup 0 2 15
# create a user's tmp dir if it doesn't exist
# if it exists, move it to a new name
if [ -d $WORK_DIR ]; then
    mv $WORK_DIR $WORK_DIR-`date "+%s"`
    mkdir -p $WORK_DIR
    else
    mkdir -p  $WORK_DIR
fi
cd $WORK_DIR
# video array starts at 0, title array starts at 1
for ((i=0; i<${#ARGS[@]}; i=$(($i + 2)))); do
VID_ARRAY=( "${VID_ARRAY[@]}" "${ARGS[i]}" )
done
for ((i=1; i<=${#ARGS[@]}; i=$(($i + 2)))); do
TITLES=( "${TITLES[@]}" "${ARGS[i]}" )
done

# make sure titles have no more than 12 characters
wlen=( $(for i in "${!TITLES[@]}"; do echo ${#TITLES[i]};done) )
for val in "${wlen[@]}"; do
    [ -z "$MAX_VAL" ] || ((val > MAX_VAL)) && MAX_VAL=$val
done
echo -e "the longest value is " "$MAX_VAL"

if [ $MAX_VAL -gt 14 ]; then
    echo -e "Sorry, the maximum number of characters you can use for a title is 14"
    exit 1
fi

echo -e "files are "${VID_ARRAY[@]}""
echo -e "file 1 is "${VID_ARRAY[0]}""
echo -e "titles are "${TITLES[@]}""
echo -e "title 1 is \""${TITLES[0]}"\""

SVCD_VID_SIZE_OPT="480x480"
DVD_VID_SIZE_OPT="720x480"
DVD_AUDIO_EXT=ac3
SVCD_AUDIO_EXT=mp2
DVD_SAMPLERATE="48000"
SVCD_SAMPLERATE="44100"
DVD_AUDIO_OPTS="-ab 224 -ar 48000 -ac 2 -acodec $DVD_AUDIO_EXT"
SVCD_AUDIO_OPTS="-ab 224 -ar 44100 -ac 2 -acodec $SVCD_AUDIO_EXT"
SVCD_FFMPEG_TARGET="ntsc-svcd"
DVD_FFMPEG_TARGET="ntsc-dvd"
SVCD_FFMPEG_OPTS="-b 2200 -minrate 2200 -maxrate 2200 -bufsize 230 -aspect 4:3"
DVD_FFMPEG_OPTS="-b 8000  -maxrate 9000 -bufsize 230  -aspect 4:3"
SVCD_INTRO_SIZE="240x240"
DVD_INTRO_SIZE="360x240"
SVCD_MPLEX_FORMAT=4
DVD_MPLEX_FORMAT=8
SVCD_TITLE_FONT_SIZE=32
DVD_TITLE_FONT_SIZE=36
PTSIZE=(30 36 42 42 42 42 48 48 48 48 48 48 54 54 54 54 54 54 54 54 \
54 54 54 54 54 54 54 54 54 54)
CHOP=(42 48 54 54 54 54 60 60 60 60 60 60 60 60 60 60 60 60 60 60
60 60 60 60 60 60 60 60 60 60) 
DVD_GEO_ARRAY=(360x240 270x180 192x128 192x128 180x120 180x120 120x80 120x80 \
144x96 120x80 120x80 120x80 96x64 96x64 96x64 96x64 96x64 96x64 96x64 96x64 \
72x48 72x48 72x48 72x48 72x48 72x48 72x48 72x48 72x48 72x48)
SVCD_GEO_ARRAY=(240x240 180x180 120x120 120x120 120x120 120x120 96x96 96x96 \
96x96 80x80 80x80 80x80 64x64 64x64 64x64 64x64 64x64 64x64 64x64 64x64 \
48x48 48x48 48x48 48x48 48x48 48x48 48x48 48x48 48x48 48x48)
TILE_ARRAY=(1x1 2x1 2x2 2x2 3x2 3x2 3x3 3x3 3x3 4x3 4x3 4x3 4x4 4x4 4x4
4x4 5x4 5x4 5x4 5x4 5x5 5x5 5x5 5x5 5x5 6x5 6x5 6x5 6x5 6x5)
WITH_CHAPT_TILE=(1x1 2x1 2x2 2x2 3x2 3x2 4x2 4x2 3x3 4x3 4x3 4x3 4x4 4x4 4x4 \
4x4 5x4 5x4 5x4 5x4 5x5 5x5 5x5 5x5 5x5 6x5 6x5 6x5 6x5 6x5)

V_ARRAY_TOTAL=${#VID_ARRAY[@]}
A_ARRAY_TOTAL=${#TITLES[@]}
FILES=$(($V_ARRAY_TOTAL - 1))
echo -e "VID_ARRAY total is ${#VID_ARRAY[@]}"
echo -e "V_ARRAY_TOTAL is $V_ARRAY_TOTAL"
echo -e "FILES are $FILES"

# test if BVC is installed or running from current dir
if [ -d $DATA_DIR ]; then
    DATA_DIR=$DATA_DIR
else
    DATA_DIR=`pwd`/data
fi


# set up our log file
PATTERN=$(for ((i=1; i<=79; i++));do echo -n \*;done)
printf "%s\n%s\n%s\n\n\n" "$PATTERN" \
"Ben's video Converter (BVC) - log for `date`" \
"$PATTERN" >> $BVC_LOG


# create_dirs
for ((i=0; i<=FILES; i++)) ; do
    mkdir -p  $WORK_DIR/pics/$i/video_fadeout
done

if [ $TITLE_PAGE = "animated" ]; then
    mkdir $WORK_DIR/{animenu,fade}
elif [ $TITLE_PAGE = "plain" ]; then
    mkdir $WORK_DIR/fade
fi

# create black png for dissolve
convert  -size $VID_SIZE_OPT xc:black $WORK_DIR/black.png



if  [ $TARGET = "DVD" ]; then
        VID_SIZE_OPT=$DVD_VID_SIZE_OPT
        AUDIO_OPTS=$DVD_AUDIO_OPTS
        SAMPLERATE=$DVD_SAMPLERATE
        AUDIO_EXT=$DVD_AUDIO_EXT
        FFMPEG_TARGET=$DVD_FFMPEG_TARGET
        INTRO_SIZE=$DVD_INTRO_SIZE
        FFMPEG_OPTS=$DVD_FFMPEG_OPTS
        MPLEX_FORMAT=$DVD_MPLEX_FORMAT
        TITLE_FONT_SIZE=$DVD_TITLE_FONT_SIZE
        GEO_ARRAY=("${DVD_GEO_ARRAY[@]}")
fi

# create a default if user doesn't specify DEVICE or if called from BVC*.desktop
if [ ! "$DEVICE" ]; then
    if [ "$TARGET" = "DVD" ]; then
        if [ -b /dev/dvdrw ]; then
            DEVICE=/dev/dvdrw
        elif [ -b /dev/dvd ]; then
            DEVICE=/dev/dvdrw
        else
            echo -e "Sorry, no dvdrw device found \
            \nPlease symlink your device to /dev/dvdrw or /dev/dvd"
            exit 1
         fi
    fi
fi

###############################################################################
#                       process original video and audio                      #
###############################################################################

# get information about videos and store in an array
for i in ${!VID_ARRAY[@]}; do
    mencoder_stats=( "${mencoder_stats[@]}" "$(mencoder "${VID_ARRAY[i]}" \
    -oac pcm -ovc copy \
    -o /dev/null)" )
done

# put in the log file in case anyone is interested
for i in ${!VID_ARRAY[@]}; do
    VCODEC="$(awk '/VIDEO:/ {gsub(/\[|\]/, ""); print $2}' \
    <<< "${mencoder_stats[i]}")"
    V_BR="$(awk '/Video stream:/{print $3}'<<<"${mencoder_stats[i]}")"
    ACODEC="$(awk  '/Selected audio codec/ {gsub(/\[|\]/, ""); print $4}' \
    <<< "${mencoder_stats[0]}")"
    A_BR="$(awk  '/AUDIO:/ {print $7}' <<< "${mencoder_stats[i]}")"
    if [ -z "$A_BR" ]; then
        A_BR="No audio found"
    fi
    ID_LENGTH="$(awk '/Video stream:/{print $10}'<<<"${mencoder_stats[i]}")"
    printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
    echo -e "Stats for" "${VID_ARRAY[i]}" "\n" \
    "video codec:   " \
    "$VCODEC" "\n" \
    "video bitrate: " "$V_BR" "kbps" "\n" \
    "audio codec:   " \
    "$ACODEC" "\n" \
    "audio bitrate: " \
    "$A_BR" " kbps" "\n" \
    "clip length:   " \
    "$ID_LENGTH" " seconds" "\n" >> $BVC_LOG
done


for i in ${!mencoder_stats[@]}; do
    VID_LEN=( ${VID_LEN[@]}  "$(awk '/Video stream:/{print $10}' \
    <<<"${mencoder_stats[i]}")" )
done
for i in ${!VID_LEN[@]}; do
    NEW_LENGTH=( ${NEW_LENGTH[@]}   ${VID_LEN[i]%.*} )
done

for val in ${NEW_LENGTH[@]}; do
    [ -z "$MAX_VAL" ] || ((val > MAX_VAL)) && MAX_VAL=$val
done
echo -e "NEW_LENGTH is "${NEW_LENGTH[@]}""
MAX_VAL_FRAMES="$(($MAX_VAL * 30))"
if [ $MAX_VAL_FRAMES -lt $MAX_ANI_LENGTH ]; then
    MAX_ANI_LENGTH=$MAX_VAL_FRAMES
fi
ANI_FRAMES=$(($MAX_ANI_LENGTH - 90))

# create high bitrate xvid avi's of our video clips

echo -e "VID_ARRAY is ${VID_ARRAY[@]}"
for ((i=0; i<=FILES; i++)) ; do

    CURRENT_CLIP=${VID_ARRAY[$i]}
    FFMPEG_ENC_CMD=(ffmpeg -i "$CURRENT_CLIP" -f avi -an -vcodec mpeg4 -b 3000 \
    -r 29.970 -s $VID_SIZE_OPT -aspect 4:3 $WORK_DIR/pics/$i/$i.avi)
    printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
    echo -e "\nRunning: ${FFMPEG_ENC_CMD[@]}" |fold -bs |tr -s ' ' >> $BVC_LOG

    SED_VAR="frame="
    if "${FFMPEG_ENC_CMD[@]}" >> $BVC_LOG.tmp 2>&1; then
        cleanlog 3
    else
        cleanlog 3
        OUTPUT="clips from your videos"
        sorry_msg
        exit 1
    fi

done
set +x
# put avi clips into an array
for ((i=0; i<=FILES; i++)) ; do
    VID=( ${VID[@]} $(find $WORK_DIR/pics -name $i.avi) )
    VID_LENGTH=( ${VID_LENGTH[@]} $(vid_length ${VID[$i]}) )
    NEW_LENGTH=( ${NEW_LENGTH[@]}   ${VID_LENGTH[i]%.*} )
done
echo -e "VID is ${VID[@]}"

# extract audio from files, or if none, create silence
for ((i=0; i<=FILES; i++)) ; do
    CURRENT_CLIP=${VID_ARRAY[$i]}
    if ! mplayer -identify -frames 0 -vo null -ao null "$CURRENT_CLIP" |
    grep "no sound"; then
        ffmpeg -i "$CURRENT_CLIP" -ar 44100 -ac 2 -acodec pcm_s16le -y \
        $WORK_DIR/pics/$i/$i.wav
    else
        TIME=${VID_LENGTH[$i]}
        cat /dev/zero | nice -n 0 sox -t raw -c 2 -r 48000 -w \
        -s - $WORK_DIR/pics/$i/$i.wav  trim 0 $TIME
    fi
done

# get exact length of the wav's with sox, and put in an array (of course !)
for ((i=0; i<=FILES; i++)); do
    WAVS=( ${WAVS[@]} $(find $WORK_DIR/pics/$i/$i.wav) )
    WAV_TIME=( ${WAV_TIME[@]} \
    $(awk '/Length/{print $3}'<<<"$(sox ${WAVS[i]} -e stat 2>&1)" ) )
    echo -e "WAV_TIME is is ${WAV_TIME[@]}"
    echo -e "WAV_TIME of $i.wav is ${WAV_TIME[i]}"
done
#create fade effect on the extracted wavs
#if [ $DO_FADE = "false" ]; then
#    FADE=0
if [ -z $FADE ]; then
    FADE=1
else
    FADE=$FADE
fi

if [ $FADE != 0 ]; then
    for ((i=0; i<=FILES; i++)) ; do

        echo -e "Running sox $WORK_DIR/pics/$i/$i.wav \
        $WORK_DIR/pics/$i/$i-processed.wav fade t \
        $FADE ${WAV_TIME[i]} $FADE" >> $BVC_LOG.tmp
        cleanlog 1

        sox $WORK_DIR/pics/$i/$i.wav \
        $WORK_DIR/pics/$i/$i-processed.wav fade t $FADE ${WAV_TIME[i]} $FADE
    done

    # convert faded wav to ac3 or mp2
    for ((i=0; i<=FILES; i++)) ; do
        ffmpeg -i $WORK_DIR/pics/$i/$i-processed.wav \
        $AUDIO_OPTS -y $WORK_DIR/pics/$i/$i.$AUDIO_EXT
    done

elif [[ $FADE = "0" || $FADE = "0.0" ]]; then
    for ((i=0; i<=FILES; i++)) ; do
        ffmpeg -i $WORK_DIR/pics/$i/$i.wav \
        $AUDIO_OPTS -y $WORK_DIR/pics/$i/$i.$AUDIO_EXT
    done
fi

###############################################################################
#             end of processing original video and audio                      #
###############################################################################

###############################################################################
#                       work on the clip title images                         #
###############################################################################


# create the pngs for background image and move to proper pics/ dir
for ((i=0; i<=FILES; i++)) ; do
    CREATE_PNG_CMD=(ffmpeg -i "${VID_ARRAY[$i]}" -vframes $ANI_FRAMES \
    -s "$INTRO_SIZE" "$WORK_DIR/pics/$i/%d.png")
#    CREATE_PNG_CMD=(mplayer -vo png:z=$PNG_COMPRESS -ao null \
#    -vf expand=-288:-192,rectangle=432:288,rectangle=430:286,rectangle=428:284,rectangle=426:282  \
#    -zoom -x 360 -y 240  -ss 0:0:01 -frames $FRAMES $ANI_FRAMES >/dev/null 2>&1
    printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
    echo -e "\nRunning: ${CREATE_PNG_CMD[@]}\n" | fold -bs >> $BVC_LOG

    SED_VAR="frame="
    if "${CREATE_PNG_CMD[@]}" >> $BVC_LOG.tmp 2>&1;then
        cleanlog 3
    else
        cleanlog 3
        OUTPUT="There was a problem creating pngs from the video.\n \
        Please see the output of $BVC_LOG"
        SORRY_MSG=$OUTPUT
        sorry_msg
        exit 1
    fi
cp $WORK_DIR/pics/$i/59.png $WORK_DIR/pics/$i/intro.png
done

#  create black background
BG_PIC="$WORK_DIR/pics/template.png"
convert  -size $VID_SIZE_OPT xc:"#1E1E1E" $BG_PIC

FRAME_FONT="$DATA_DIR/Candice.ttf"
# font to use for our plain title text - fall back on Candice if no helvetica

if [[ $FRAME_STYLE != "fancy" ]]; then
    if convert -font Helvetica -draw "text 0,0 'test'" $BG_PIC /dev/null; then
        FRAME_FONT="Helvetica"
    elif
        convert -font helvetica -draw "text 0,0 'test'" $BG_PIC /dev/null; then
            FRAME_FONT="helvetica"
    else
        FRAME_FONT=$FRAME_FONT
    fi
fi

for ((f=0; f<=FILES; f++)) ; do

    GRADIENT="aqua_gradient.png"

    #  create a transparant png with the title on it
    TITLE="\"${TITLES[$f]}\""
    convert -font $FRAME_FONT -pointsize $TITLE_FONT_SIZE -size 420x \
    -gravity Center caption:"$TITLE"  -negate  \( +clone -blur 0x8 \
    -shade 110x45 -normalize \
    $DATA_DIR/$GRADIENT  -fx 'v.p{g*v.w,0}' \)  +matte +swap \
    -compose CopyOpacity -composite  $WORK_DIR/pics/$f/title_txt.png

    if [ $FRAME_STYLE = "none" ]; then
        printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
        echo -e "Running: convert -size $INTRO_SIZE \
        $WORK_DIR/pics/$f/intro.png $WORK_DIR/pics/$f/title.png" >>$BVC_LOG.tmp
        cleanlog 1
        convert -size $INTRO_SIZE $WORK_DIR/pics/$f/intro.png \
        $WORK_DIR/pics/$f/title.png >> $BVC_LOG 2>&1
    else
        #  create a frame around our title picture
        printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
        echo -e "Running: $FRAME_CMD $WORK_DIR/pics/$f/intro.png \
        $INTRO_SIZE $WORK_DIR/pics/$f/title.png" >> $BVC_LOG.tmp
        cleanlog 1

        $FRAME_CMD $WORK_DIR/pics/$f/intro.png $INTRO_SIZE \
        $WORK_DIR/pics/$f/title.png

    #  paint the title and the title picture onto the black background
    convert   $WORK_DIR/pics/template.png $WORK_DIR/pics/$f/title_txt.png \
    -gravity south -geometry +0+65 -composite $WORK_DIR/pics/$f/title.png \
    -gravity north -composite  $WORK_DIR/pics/$f/background.png
    fi
done

# end of title png loop

###############################################################################
#                      end of clip title image stuff                          #
###############################################################################

###############################################################################
#               create introductory video ("menu") if called for              #
###############################################################################

#  create a transparant png with the title on it
#    TITLE="My Video Collection"
convert -font $FRAME_FONT -pointsize $TITLE_FONT_SIZE -size 420x \
-gravity Center caption:"\"$TITLE_PG_TITLE\""  -negate  \( +clone -blur 0x8 \
-shade 110x45 -normalize \
$DATA_DIR/$GRADIENT  -fx 'v.p{g*v.w,0}' \)  +matte +swap \
-compose CopyOpacity -composite  $WORK_DIR/intro_txt.png

# check if we are using static or animated images, and using submenu or not
if [ $SUB_MENU = "true" ]; then 
    DVD_TILE_ARRAY=${WITH_CHAPT_TILE[@]}
fi
if [ $TITLE_PAGE = "plain" ]; then
    TITLE_PNGS=( "$(find $WORK_DIR -name intro.png)" )
    montage ${TITLE_PNGS[@]} -tile ${TILE_ARRAY[FILES]} \
    -geometry ${GEO_ARRAY[FILES]}+5+5 -background "#1E1E1E" -frame 4 \
    -bordercolor "#343634" miff:- |
    convert -size $VID_SIZE_OPT xc:"#1E1E1E" $WORK_DIR/intro_txt.png \
    -gravity south -geometry +0+55 -composite \
    - -gravity north -geometry +0+55 -composite \
    $WORK_DIR/title_page.png

       # create a fade-in and fade-out effect
        # copy enough pngs for the fade
        for ((i=0; i<=230; i++)); do
            cp $WORK_DIR/title_page.png $WORK_DIR/fade/title_page$i.png
        done

        # run the fade on the pngs
        # identify our target pngs
        for ((i=0; i<50; i++)); do
            FADIN_PNGS=( ${FADIN_PNGS[@]} $(find  $WORK_DIR/fade \
            -name title_page$i.png) )
        done

        for ((i=181; i<=230; i++)); do
            FADEOUT_PNGS=( ${FADEOUT_PNGS[@]} $(find $WORK_DIR/fade \
            -name title_page$i.png) )
        done
    # run the static_fade() function
        static_fade
        unset FADIN_PNGS FADEOUT_PNGS



    png2yuv -f 29.970 -I p -b 1 -n 100 -j $WORK_DIR/fade/title_page%0d.png |
    ffmpeg -f yuv4mpegpipe -i -  -an -vcodec mpeg4 -r 29.970 -b 2000 \
    -s $VID_SIZE_OPT -aspect 4:3 -y $INTRO_VIDEO
    rm -f $WORK_DIR/fade/*.png

elif [ $TITLE_PAGE = "animated" ]; then
    for ((i=0; i<=FILES; i++)); do
        PNGS=( "${PNGS[@]}" $(find $WORK_DIR/pics/$i -maxdepth 1 -name '*[0-9]*.png') )
        for png in "${PNGS[@]}"; do
            montage -geometry +0+0 -font BitstreamVeraSansB -background none \
            -fill '#C6C6C6' -pointsize 22 -title "${TITLES[i]}"  $png miff:- |
            convert -gravity South  -chop   0x${CHOP[FILES]}  - miff:- |
            convert -background none -frame 5x5+0+0 \
            -bordercolor none -mattecolor "#444744" - miff:- |
            convert -resize $INTRO_SIZE! - $png
        done
            #-pointsize ${PTSIZE[FILES]} -title "${TITLES[i]}"  $png miff:- |

        last_png="$((${#PNGS[@]} - 1))"
        next_png=$(($last_png + 1))
        if [ $last_png -ge $MAX_ANI_LENGTH ]; then
            :
        else
            for ((l=$next_png; l<=$MAX_ANI_LENGTH; l++)); do
                cp $WORK_DIR/pics/$i/$last_png.png $WORK_DIR/pics/$i/$l.png
            done
        fi
        unset PNGS last_png next_png
    done

    for (( count=0; count < $MAX_ANI_LENGTH; count++)); do
        ANI_PICS=$(find $WORK_DIR/pics/*[0-9]* -maxdepth 1 -name $count.png)

        # make montages and composite onto grey background with title
        IM_CMD=(montage ${ANI_PICS[@]} -tile ${TILE_ARRAY[FILES]} \
        -geometry ${GEO_ARRAY[FILES]}+5+5 -background none miff:-)
        IM_CMD2=(convert $WORK_DIR/pics/template.png \
        $WORK_DIR/intro_txt.png  -gravity south -geometry +0+55 -composite \
        -  -gravity north -geometry +0+55 -composite \
        $WORK_DIR/animenu/$count.png)
        echo -e "Running ${IM_CMD[@]} | ${IM_CMD2[@]}" >> $BVC_LOG.tmp
        cleanlog 1
        "${IM_CMD[@]}" | "${IM_CMD2[@]}" >> $BVC_LOG.tmp
        cleanlog 1
    done
    # convert pngs to video stream

    png2yuv  -f 29.970 -I p -b 3 -n $MAX_ANI_LENGTH -j  \
    $WORK_DIR/animenu/%0d.png |
    ffmpeg -f yuv4mpegpipe -i -  -an -vcodec mpeg4 -r 29.970 -b 2000 \
    -s $VID_SIZE_OPT -aspect 4:3 -y $INTRO_VIDEO
    # convert to proper video format
    ENC_CMD=(ffmpeg -i $INTRO_VIDEO -f mpeg2video \
    -tvstd ntsc $FFMPEG_OPTS -s $VID_SIZE_OPT -y $WORK_DIR/intro.m2v)
    if "${ENC_CMD[@]}" >> $BVC_LOG.tmp 2>&1; then
        cleanlog 1
    else
        cleanlog 1
        sorry_msg
        exit 1
    fi
fi

TIME=`vid_length "$INTRO_VIDEO"`
cat /dev/zero | nice -n 0 sox -t raw -c 2 -r 48000 -w \
-s - $WORK_DIR/intro.wav  trim 0 $TIME

# convert to proper audio format
ffmpeg -i $WORK_DIR/intro.wav \
$AUDIO_OPTS -y $WORK_DIR/intro.$AUDIO_EXT
        
# mplex intro audio and video together
INTRO_MPLEX_CMD="mplex -V -f $MPLEX_FORMAT -b 230 -o $WORK_DIR/intro.mpg \
$WORK_DIR/intro.$AUDIO_EXT $WORK_DIR/intro.m2v"
echo -e "\nRunning: $INTRO_MPLEX_CMD\n" >> $BVC_LOG.tmp 
cleanlog 1
if ${INTRO_MPLEX_CMD[@]} >> $BVC_LOG.tmp 2>&1; then
    cleanlog 1
else
    cleanlog 1
    sorry_msg
    exit 1
fi


###############################################################################
#                       work on the title lead-ins                            #
###############################################################################



# copy enough background.png's to destination for a lead-{in,out}
for ((i=0; i<=FILES; i++)) ; do
        for ((a=0; a<=$TOTAL_PNGS; a++)) ; do
        cp $WORK_DIR/pics/$i/background.png $WORK_DIR/pics/$i/$a.png
    done
done


# finish the leadin operations, like identifying the target
# pngs, dissolving, and making a video stream of them

for ((i=0; i<=FILES; i++)) ; do
    CLIP_CNT=$(($i + 1))
    for ((PIC=0; PIC<50; PIC++)); do
        FADIN_PNGS=( ${FADIN_PNGS[@]} $(find  $WORK_DIR/pics/$i \
        -maxdepth 1 -name $PIC.png) )
    done

for ((PIC=51; PIC<=100; PIC++)); do
        FADEOUT_PNGS=( ${FADEOUT_PNGS[@]} $(find $WORK_DIR/pics/$i \
        -maxdepth 1 -name $PIC.png) )
    done
    static_fade title
    unset FADIN_PNGS FADEOUT_PNGS

    # use png2yuv to convert to an mpeg stream
    png2yuv  -f 29.970 -I p -b 1 -n $TOTAL_PNGS -j  $WORK_DIR/pics/$i/%0d.png |
    ffmpeg -f yuv4mpegpipe -i -  -an -vcodec mpeg4 -r 29.970 -b 2000 \
    -s $VID_SIZE_OPT -aspect 4:3 -y "$WORK_DIR/pics/$i/$i-leadin.avi"


    # remove pngs to save disk space
    find $WORK_DIR/pics/$i -name '[0-9]*.png'  -exec rm -f {} \;

    # create silence for leadin/leadout
    TIME=`vid_length $WORK_DIR/pics/$i/$i-leadin.avi`
    ffmpeg -t $TIME $AUDIO_OPTS \
    $WORK_DIR/pics/$i/$i-leadin.$AUDIO_EXT
done


###############################################################################
#                       end of title lead-in stuff                            #
###############################################################################

###############################################################################
#                       begin work on video fades                             #
###############################################################################

# create the pngs for the video fadeout from our new mpeg-4's
#and move to proper fadeout dir
for ((i=0; i<=FILES; i++)) ; do
    unset VID_LENGTH
    VID_LENGTH=`vid_length $WORK_DIR/pics/$i/$i.avi`
    ROUND_VID_LENGTH=`echo $VID_LENGTH|cut -f1 -d.`
    CUT_TIME=$[$ROUND_VID_LENGTH - 1]  # FIXME
    ffmpeg  -ss $CUT_TIME -i $WORK_DIR/pics/$i/$i.avi -s $VID_SIZE_OPT \
    $WORK_DIR/%d.png

    VIDEO_FADEOUT_PNG=$(find $WORK_DIR -maxdepth 1 \
    -name '[0-9]*.png'|tail -n 2|head -n 1)

    # just in case the png is corrupt, then use solid background
        if [ ! $(identify $VIDEO_FADEOUT_PNG |awk '{print $2}') = "PNG" ]; then
            VIDEO_FADEOUT_PNG="$WORK_DIR/pics/template.png"
        fi

    cp $VIDEO_FADEOUT_PNG $WORK_DIR/pics/$i/video_fadeout.png
    rm -f $WORK_DIR/[0-9]*.png
    # copy enough video_fadeout.png's to create a fade
    for ((a=0; a<=60; a++)) ; do
        cp $WORK_DIR/pics/$i/video_fadeout.png \
        $WORK_DIR/pics/$i/video_fadeout/$a.png
    done
done


# do the leadin operations on the video clip

for ((i=0; i<=FILES; i++)) ; do
    CLIP_CNT=$(($i + 1))

    S=40
    for ((Y=0; Y<=60; Y++)); do
        FADEOUT_PNGS=( ${FADEOUT_PNGS[@]} \
        $(find  $WORK_DIR/pics/$i/video_fadeout -name $Y.png) )

        # do the fadeout on each video
        composite -dissolve $S $WORK_DIR/black.png \
        "${FADEOUT_PNGS[Y]}" "${FADEOUT_PNGS[Y]}"
        S=$((S+1))
    done
    unset FADEOUT_PNGS

    # convert to video stream

    PNG2YUV_CMD="png2yuv  -f 29.970 -I p -b 1 -j \
    $WORK_DIR/pics/$i/video_fadeout/%0d.png"
    FFMPEG_CMD="ffmpeg -f yuv4mpegpipe -i - -an -vcodec mpeg4 -r 29.970 -s \
    $VID_SIZE_OPT -aspect 4:3 -b 2000 -y $WORK_DIR/pics/$i/$i-video_fadeout.avi"

    printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
    echo -e "\nRunning: $PNG2YUV_CMD | $FFMPEG_CMD\n" >> $BVC_LOG.tmp
    cleanlog 4

    SED_VAR="frame="
    if { $PNG2YUV_CMD | $FFMPEG_CMD ;}  >> $BVC_LOG.tmp 2>&1; then
        cleanlog 3
    else
        cleanlog 3
        OUTPUT="There was a problem converting the pngs to video. \
        Please see the output of $BVC_LOG"
        $KDIALOG --msgbox "$OUTPUT"
        dcop $dcopRef close
        exit 1
    fi

    # create silence for video fadeout
    TIME=`vid_length $WORK_DIR/pics/$i/$i-video_fadeout.avi`

    ffmpeg -t $TIME $AUDIO_OPTS \
    $WORK_DIR/pics/$i/$i-video_fadeout.$AUDIO_EXT

    # remove pngs to save space
    rm -f $WORK_DIR/pics/$i/video_fadeout/*.png

done

###############################################################################
#                      end of video fade stuff                                #
###############################################################################


###############################################################################
#       join the files into one video and audio file, then mplex them         #
###############################################################################

# put everything together into m2v and mp2,then mplex them together

for ((a=0; a<$V_ARRAY_TOTAL; a++)); do
    JOINED_AUDIOS=("${JOINED_AUDIOS[@]}" "$WORK_DIR/pics/$a/$a-leadin.$AUDIO_EXT" \
    "$WORK_DIR/pics/$a/$a.$AUDIO_EXT" \
    "$WORK_DIR/pics/$a/$a-video_fadeout.$AUDIO_EXT")
done

#JOINED_AUDIOS=("${JOINED_AUDIOS[@]}" $WORK_DIR/intro.$AUDIO_EXT" \
#"${CLIP_AUDIOS[@]}")

for ((i=0; i<$V_ARRAY_TOTAL; i++)); do
    JOINED_VIDEO=("${JOINED_VIDEO[@]}" "$WORK_DIR/pics/$i/$i-leadin.avi" \
    "$WORK_DIR/pics/$i/$i.avi" "$WORK_DIR/pics/$i/$i-video_fadeout.avi")
done

#JOINED_VIDEO=("${JOINED_VIDEO[@]}" "${CLIP_VIDEOS[@]}")

OUTPUT="joined video"
COPY_CMD=(mencoder -quiet -oac copy -ovc copy ${JOINED_VIDEO[@]} \
-o $WORK_DIR/joined-tmp.avi)

printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
echo -e "\nRunning:" "${COPY_CMD[@]}" "\n"  >> $BVC_LOG.tmp
cleanlog 4

if "${COPY_CMD[@]}" >> $BVC_LOG.tmp 2>&1; then
    cleanlog 1
else
    cleanlog 1
    sorry_msg
    exit 1
fi

OUTPUT="final joined svcd video"
JOIN_CMD=(ffmpeg -i $WORK_DIR/joined-tmp.avi -f mpeg2video \
-tvstd ntsc $FFMPEG_OPTS -s $VID_SIZE_OPT -y $WORK_DIR/joined.m2v)

printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
echo -e "\nRunning ${JOIN_CMD[@]}\n"  >> $BVC_LOG.tmp
cleanlog 4

SED_VAR="frame="
if "${JOIN_CMD[@]}" >> $BVC_LOG.tmp 2>&1; then
    cleanlog 3
else
    cleanlog 3
    sorry_msg
    exit 1
fi

# use cat to join the finished individual audio files
cat "${JOINED_AUDIOS[@]}" > $WORK_DIR/joined.$AUDIO_EXT


OUTPUT="mplexed final video (audio plus video)"
MPLEX_CMD="mplex -V -f $MPLEX_FORMAT -b 230 -o $WORK_DIR/final.mpg \
$WORK_DIR/joined.m2v $WORK_DIR/joined.$AUDIO_EXT"

printf "%s\n\n" "$LINE" "$LINE" >> $BVC_LOG
echo -e "\nRunning: $MPLEX_CMD\n" >> $BVC_LOG.tmp
cleanlog 4
if $MPLEX_CMD >> $BVC_LOG.tmp 2>&1; then
    cleanlog 1
    echo "Exit code is $?" >> $BVC_LOG
else
    cleanlog 1
    echo "Exit code is $?" >> $BVC_LOG
    sorry_msg
    exit 1
fi

##############################################################################
#                      spumux and friends                                    #
##############################################################################

# create the Highlight png
GEO="${GEO_ARRAY[FILES]/x/,}"
SELECT_CMD="-size "${GEO_ARRAY[FILES]}+5+5" xc:none -fill none +antialias \
-stroke '#DE7F7C' -strokewidth 4 -draw 'rectangle 0,0 $GEO'"
HIGHLIGHT_CMD="-size "${GEO_ARRAY[FILES]}+5+5" xc:none -fill none +antialias \
-stroke '#188DF6' -strokewidth 4 -draw 'rectangle 0,0 $GEO'"
eval convert "$SELECT_CMD" -colors 3 "$WORK_DIR/Selectx1.png"
eval convert "$HIGHLIGHT_CMD" -colors 3 "$WORK_DIR/Highlightx1.png"

for ((i=0; i<=FILES; i++)); do 
    cp $WORK_DIR/Selectx1.png $WORK_DIR/$i-Select.png
    cp $WORK_DIR/Highlightx1.png $WORK_DIR/$i-Highlight.png
done

montage -background none "$WORK_DIR/*-Select.png" -tile ${TILE_ARRAY[FILES]} \
-geometry ${GEO_ARRAY[FILES]}+5+5 -bordercolor none -mattecolor transparent miff:- |
convert  -colors 3 -size 720x480 xc:none  - -gravity north -geometry +0+55  \
-composite  "$WORK_DIR/Select.png"

montage -background none "$WORK_DIR/*-Highlight.png" -tile ${TILE_ARRAY[FILES]} \
-geometry ${GEO_ARRAY[FILES]}+5+5 -bordercolor none -mattecolor transparent  miff:- |
convert  -size 720x480 xc:none  - -gravity north -geometry +0+55  \
-composite  "$WORK_DIR/Highlight.png"

# get array of fadein+clip+fadeout length for each clip
VIDS=( ${VIDS[@]} $(find $WORK_DIR/pics/[0-9]* -maxdepth 1 -name '*.avi') )
echo -e "VIDS are ${VIDS[@]}"
Y=$((${#VIDS[@]} -1))
echo -e "Y is $Y"
for i in ${VIDS[@]}; do
    VIDS_LEN=( ${VIDS_LEN[@]} $(vid_length "$i") )
done
echo -e "VIDS_LENS is ${VIDS_LEN[@]}"


for ((i=0; i<$Y; i=$i+3)); do
    NEW_ARRAY=( ${NEW_ARRAY[@]} \
    $(echo "${VIDS_LEN[i]} + ${VIDS_LEN[i+1]} + ${VIDS_LEN[i+2]}" | bc) )
done
echo -e "NEW_ARRAY is ${NEW_ARRAY[@]}"
# try to get chapter into the xml file
# IFS=$'\n'; echo "${NEW_ARRAY[*]}"; unset IFS
TIMES=($(for ((x=0; x<${#NEW_ARRAY[@]}; x++)); do echo  "${NEW_ARRAY[x]}";done |
awk -v column_number="$column_number" '
   { total += $column_number
     print total
   }
   END {
   }'))

#TIMES=( $(for ((x=0;x<${#NEW_ARRAY[@]};x++)); do \
#echo $((y=y+${NEW_ARRAY[x]})); done) )
CHAPTERS=$(for i in ${TIMES[@]}; do echo -n "$(format_seconds $i),";done)
echo -e "CHAPTERS are $CHAPTERS"
DVD_CHAPTERS="0,${CHAPTERS[@]%,}"
echo -e "DVD_CHAPTERS are $DVD_CHAPTERS"


# make xml files, and run dvdauthor and spumux
(
    cat <<EOF
<subpictures>
   <stream>
     <spu start="00:00:00.0" end="00:00:00.0"
          highlight="$WORK_DIR/Highlight.png"
          select="$WORK_DIR/Select.png"
          autooutline="infer"
          autoorder="rows"/>
   </stream>
 </subpictures>
EOF
)  > "$SPUMUX_XML"

spumux "$SPUMUX_XML" < $WORK_DIR/intro.mpg > $WORK_DIR/menu.mpg

(
cat <<EOF
<?xml version="1.0" encoding="utf-8"?>
<dvdauthor dest="$WORK_DIR/DVD" jumppad="1">
  <vmgm>
    <menus>
      <pgc>
        <post>jump titleset 1 menu;</post>
      </pgc>
    </menus>
  </vmgm>
  <titleset>
    <menus>
      <pgc>
EOF
) > "$DVDAUTHOR_XML"

for ((i=1; i<=$V_ARRAY_TOTAL; i++)); do
    echo -e "<button name=\"$i\">jump title 1 chapter $i;</button>\n"
done >> "$DVDAUTHOR_XML"

(
cat <<EOF
<vob file="$WORK_DIR/menu.mpg" pause="inf"/>
      </pgc>
    </menus>
    <titles>
      <pgc>
        <vob file="$WORK_DIR/final.mpg" chapters="$DVD_CHAPTERS"/>
        <post>call vmgm menu 1;</post>
      </pgc>
    </titles>
  </titleset>
</dvdauthor>
EOF
) >> "$DVDAUTHOR_XML"

mkdir $WORK_DIR/DVD
dvdauthor -x "$DVDAUTHOR_XML"

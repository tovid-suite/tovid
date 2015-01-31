#!/bin/bash

#############
# variables #
#############

WORK_DIR=$(readlink -f todisc_work)
LOG_FILE=$(readlink -f makemix)
FRAME_RATE=29.970
ASPECT_RATIO="4:3"
MENU_LENGTH=20
SLICE_PER_VID=3
FRAME_SIZE="720x480"
SHOWCASE_MIX=false
FFMPEG_PREFIX=$(which ffmpeg)
FFMPEG_PREFIX=$(sed 's/bin\/ffmpeg//g' <<< "$FFMPEG_PREFIX")
IMLIB2_VHOOK="$FFMPEG_PREFIX/lib/vhook/imlib2.so"
CLIP_SIZE="medium"
TV_STD="ntsc"

#############
# functions #
#############

vid_length()
{
    mencoder -nosound -mc 0 -oac pcm -ovc copy -o /dev/null "$1" 2>/dev/null |
    awk 'END{print $(NF-3)}'
}

runtime_error()
{
    # Uncomment if needed later
    #killsubprocs
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "makecollage.sh encountered an error:"
    echo "    $@"
    echo "Check the contents of $LOG_FILE to see what went wrong."
    echo "See the tovid website ($TOVID_HOME_PAGE) for what to do next."
    echo "Sorry for the inconvenience!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
}

make_slice()
{
    FILE_IN="$1"
    slice=$2
    index=$3
     [[ -s "$FILE_IN.nav_log" ]] && NAVSEEK="-nav_seek" && NAVLOG="$FILE_IN.nav_log"
    if $SHOWCASE_MIX; then
        :
#        FFMPEG_CMD=(ffmpeg -i "$FILE_IN" -ss $slice -t $slice_size \
#        -s 318x212 -an -padtop 104 -padbottom 164 -padleft 262 -padright 140 \
#        -f mpeg2video -r $FRAME_RATE -tvstd ntsc -b 12000k -maxrate 15000k \
#        -bufsize 230KiB -aspect $ASPECT_RATIO \
#        -y  "$WORK_DIR/slice${index}_tmp.m2v")
    else
        SLICE_CMD=(transcode -i "$FILE_IN" $NAVSEEK "$NAVLOG" -c $slice \
        -Z $CLIP_SIZE --export_fps $FRAME_RATE -w 8000  -y ffmpeg,null \
        --export_asr $AR -F mpeg2video $DO_PADDING -o  "$WORK_DIR/slice${index}_tmp")
        echo "Running: ${SLICE_CMD[@]}"|fold -bs >> "$LOG_FILE.log" 2>&1
        "${SLICE_CMD[@]}" >>"$LOG_FILE.log" 2>&1
#        FFMPEG_CMD=(ffmpeg -i "$FILE_IN" -ss $slice -t $slice_size \
#        -s $FRAME_SIZE -an -f mpeg2video -r $FRAME_RATE -tvstd ntsc \
#        -b 8000k -maxrate 9000k -bufsize 230KiB -aspect $ASPECT_RATIO \
#        -y  "$WORK_DIR/slice${index}_tmp.m2v")
    fi
}

cleanup()
{
    exit 1
}

tempdir()
{
    NUM=0
    BASENAME="$1"
    CREATE=:
    TEMPDIR="$BASENAME.$NUM"
    [[  -n $2  && $2 = "nocreate" ]] && CREATE=false
    while test -d "$BASENAME.$NUM"; do
        ((NUM++))
    done
    $CREATE && mkdir "$BASENAME.$NUM"
    echo "$BASENAME.$NUM"
}

bc_math()
# usage: bc_math "expression" [int]
{
    bc_out=$(bc <<< "scale=3;$1" 2>/dev/null)
    [[ -n $2 && $2 = "int" ]] && bc_out=${bc_out%.*}
    echo "$bc_out"
}

get_listargs()
{
    unset x ARGS_ARRAY
    # Hackish list-parsing
    while test $# -gt 0 && test x"${1:0:1}" != x"-"; do
        ARGS_ARRAY[x++]="$1"
        shift
    done
    # Do not skip past the next argument
    if test $# -gt 0 && test x"${1:0:1}" = x"-";then
        DO_SHIFT=false
    fi
}

# usage: test_is_number INPUT
function test_is_number()
{
    [[ $1 && $1 =~ ^[-+]?[0-9]*\(\.[0-9]+\)?$ ]]
}


if [[ -z "$@" ]]; then
    echo "Usage: makemix.sh -files FILES -menu-length SECONDS -slices-per-video N"
    exit 1
fi

########################
#  get script options  #
########################


while [ $# -gt 0 ]; do
    case "$1" in
        "-files" | "-in" )
            shift
            get_listargs "$@"
            for f in  ${!ARGS_ARRAY[@]}; do
                FILES[f]=$(readlink -f "${ARGS_ARRAY[f]}")
            done
            ;;
        "-slices-per-video" | "-ns" )
            shift
            SLICE_PER_VID=$1
            ;;
        "-menu-length" | "-ml" )
            shift
            MENU_LENGTH=$1
            ;;
        "-showcase" | "-sc" )
            SHOWCASE_MIX=:
            ;;           
        "-keep-files" | "-kf" )
            KEEP_FILES=:
            ;;           
        "-size" | "-s" )
            shift
            CLIP_SIZE="$1"
            ;;
        "-ntsc" )
            TV_STD="ntsc"
            ;;
        "-pal" )
            TV_STD="pal"
            ;;
        "-aspect" | "-s" )
            shift
            ASPECT_RATIO="$1"
            [[ $ASPECT_RATIO = "4:3" ]] && AR=2
            [[ $ASPECT_RATIO = "16:9" ]] && AR=3
            ;;
        "-out" | "-kf" )
            shift
            OUT_FILE=$(readlink -f "$1")
            ;;           
    esac
    shift
done

#########################
# execution starts here #
#########################

trap 'cleanup; exit 13' TERM INT

# checks and balances
! [[ -s "$IMLIB2_VHOOK" ]] && runtime_error "Can't find your ffmpeg's vhook's"

# set OUT_FILE name
OUT_FILE=$(tempdir "$OUT_FILE" nocreate)

# create the working directory
WORK_DIR=$(tempdir "$WORK_DIR")
cd "$WORK_DIR"

# set LOG_FILE name then create it

LOG_FILE=$(tempdir $LOG_FILE nocreate)
rm -f "$LOG_FILE.log"

# tv standard options
if [[ $TV_STD = "ntsc" ]]; then
    FRAME_SIZE=720x480
    FRAME_RATE=29.970
elif [[ $TV_STD="pal" ]]; then
    FRAME_SIZE=720x576
    FRAME_RATE=25
fi
# what size clips are we making
if [[ $CLIP_SIZE = "full" ]]; then
    CLIP_SIZE=$FRAME_SIZE
elif [[ $CLIP_SIZE = "small" ]]; then 
    CLIP_SIZE=288x216
elif [[ $CLIP_SIZE = "medium" ]]; then
    CLIP_SIZE=384x256
    TOPPAD=110
    LEFTPAD=240
fi
if [[ $CLIP_SIZE != $FRAME_SIZE ]]; then
    BOTTOMPAD=$(( ${FRAME_SIZE##*x} - $TOPPAD - ${CLIP_SIZE##*x} ))
    RIGHTPAD=$(( ${FRAME_SIZE%%x*} - $LEFTPAD - ${CLIP_SIZE%%x*} ))
    DO_PADDING="-Y -${TOPPAD},-${LEFTPAD},-${BOTTOMPAD},-${RIGHTPAD}"
fi

# get menu length in frames
MENU_LENGTH=$(bc_math "$MENU_LENGTH * $FRAME_RATE" int)

echo
echo "Getting video lengths"
echo

unset y
for v in ${!FILES[@]}; do
    echo "Getting stats on ${FILES[v]}"
    stats[v]=$(idvid "${FILES[v]}")
    file_len[v]=$(awk '/Frames:/ {print $2}' <<< "${stats[v]}")
done

for i in ${!FILES[@]}; do
    echo "${FILES[i]##*/}:"
    echo "Length:  ${file_len[i]} seconds"
    echo
done
echo

# get the size (seconds) of each slice
slice_size=$(bc_math "(($MENU_LENGTH / ${#FILES[@]}) / $SLICE_PER_VID)" )

# array of slices for each vid (add 1 to -n VALUE so we skip end credits)
for i in ${!file_len[@]}; do
    SEEK[i]=$(bc_math "${file_len[i]} / ($SLICE_PER_VID + 1)")
done

# make the individual slices, outputting high bitrate m2v
z=1
for ind in ${!FILES[@]}; do
    echo
    echo "Working on ${FILES[ind]}"
    for ((s=0; s<SLICE_PER_VID; s++)); do
        sliceseek=$( bc_math "${SEEK[ind]} * ($s + 1)" int)
        slice_end=$(bc_math "$sliceseek + $slice_size" int)
        make_slice "${FILES[ind]}" ${sliceseek}-${slice_end} ${ind}-${s}
    done
done

# cat the m2v's together in random order to produce the final 'mix'
for f in *.m2v; do
    a=$RANDOM
    while [[ ${m2v_files[a]} ]]; do
        a=$RANDOM
    done
    m2v_files[a]="$f"
done
cat "${m2v_files[@]}" > "${OUT_FILE}.m2v"

echo
echo "Your file is ready: ${OUT_FILE}.m2v"
echo

! $KEEP_FILES && rm -fr "$WORK_DIR"

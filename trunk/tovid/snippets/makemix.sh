#!/bin/bash

#############
# variables #
#############

WORK_DIR=$(readlink -f todisc_work)
LOG_FILE="makemix"
FRAME_RATE=29.970
ASPECT_RATIO="4:3"
MENU_LENGTH=20
FRAME_SIZE="720x480"
QUICK_MENU_SHOWCASE=false
FFMPEG_PREFIX=$(which ffmpeg)
FFMPEG_PREFIX=$(sed 's/bin\/ffmpeg//g' <<< "$FFMPEG_PREFIX")
IMLIB2_VHOOK="$FFMPEG_PREFIX/lib/vhook/imlib2.so"

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
    if $QUICK_MENU_SHOWCASE; then
        FFMPEG_CMD=(ffmpeg -i "$FILE_IN" -ss $slice -t $slice_size \
        -s 318x212 -an -padtop 104 -padbottom 164 -padleft 262 -padright 140 \
        -f mpeg2video -r $FRAME_RATE -tvstd ntsc -b 12000k -maxrate 15000k \
        -bufsize 230KiB -aspect $ASPECT_RATIO \
        -y  "$WORK_DIR/slice${index}_tmp.m2v")
    else
        FFMPEG_CMD=(ffmpeg -i "$FILE_IN" -ss $slice -t $slice_size \
        -s $FRAME_SIZE -an -f mpeg2video -r $FRAME_RATE -tvstd ntsc \
        -b 8000k -maxrate 9000k -bufsize 230KiB -aspect $ASPECT_RATIO \
        -y  "$WORK_DIR/slice${index}_tmp.m2v")
    fi

    "${FFMPEG_CMD[@]}" >/dev/null 2>&1
}

cleanup()
{
    exit 1
}

function tempdir()
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

function bc_math()
{
    echo "scale=2; $1" | bc -l
}

function get_listargs()
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
        "-quick-menu" | "-qm" )
            QUICK_MENU_SHOWCASE=:
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
OUT_FILE=$(tempdir mix nocreate)
OUT_FILE=$(readlink -f ${OUT_FILE/./})

# create the working directory
WORK_DIR=$(tempdir "$WORK_DIR")
cd "$WORK_DIR"

# set LOG_FILE name then create it or zero out existing log

LOG_FILE=$(tempdir $LOG_FILE nocreate)
> "$LOG_FILE.log"


echo
echo "Getting video lengths"
echo

for v in ${!FILES[@]}; do
    file_len[v]=$(vid_length "${FILES[v]}")
done

for i in ${!FILES[@]}; do
    echo "${FILES[i]##*/}:"
    echo "Length:  ${file_len[i]} seconds"
    echo
done
echo

# get the size of each slice
slice_size=$(bc_math "$MENU_LENGTH / (${#FILES[@]} * $SLICE_PER_VID)" )

# array of slices for each vid (add 1 to -n VALUE so we skip end credits)
for i in ${!file_len[@]}; do
    slice_seek[i]=$(bc_math "${file_len[i]} / ($SLICE_PER_VID + 1)")
done

# make the individual slices, outputting high bitrate m2v
z=1
for ind in ${!FILES[@]}; do
    echo
    echo "Working on ${FILES[ind]}"
    sliceseek=${slice_seek[ind]}
    for ((i=0; i<SLICE_PER_VID; i++)); do
        make_slice "${FILES[ind]}" $( bc_math "$sliceseek * ($i + 1)" ) ${ind}-${i}
        echo "slice $((z++)) of $((SLICE_PER_VID * ${#FILES[@]}))  done"
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

rm -fr "$WORK_DIR"

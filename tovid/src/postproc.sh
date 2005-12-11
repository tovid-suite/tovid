# -* sh *-
. tovid-init

# postproc
# Part of the tovid suite
# ==============
# A bash script for doing post-encoding processing on
# MPEG video files. Can requantize (shrink) video and
# adjust A/V sync.
#
# Project homepage: http://tovid.sourceforge.net/
#
# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

SCRIPT_NAME=`cat << EOF
--------------------------------
postproc video postprocessing script
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------
EOF`

USAGE=`cat << EOF
Usage: postproc [OPTIONS] <input file> <output file>

OPTIONS may be any of the following:

  -audiodelay [NUM]
      Delay the audio stream by [NUM] milliseconds. Use this if
      your final output has audio that is not synced with the
      video. For example, if the audio comes 2 seconds sooner than
      the video, use "-audiodelay 2000". Use a negative number for
      audio that comes later than the video.
  -shrink [NUM]
      Shrink the video stream by a factor of [NUM]. May be a decimal
      value. A value of 1.0 means the video will be the same size;
      larger values cause more reduction in size. Beyond 2.0, the
      returns are diminishing.
  -parallel
      Run all processes in parallel and pipe into multiplexer should
      increase speed significantly.
  -debug
      Save output in a temporary file, for later viewing if
      something goes wrong.

EOF`

SEPARATOR="========================================================="

# Default values
TMP_FILE="postproc.fileinfo.$PPID"
AUDIO_DELAY=""
SHRINK_FACTOR=""
DO_SHRINK=false
MUX_OPTS=""
DEBUG=false
# File to use for saving postprocessing statistics
STAT_DIR=$HOME/.tovid
STAT_FILE="$STAT_DIR/stats.postproc"
SHRINK_PERCENT="0"
PARALLEL=false
# Video format in use
VIDEO_FORMAT="DVD"
BACKGR=""

# Print script name, usage notes, and optional error message, then exit.
# Args: $1 == text string containing error message
usage_error ()
{
  echo $"$USAGE"
  echo "$SEPARATOR"
  echo $@
  exit 1
}

# ***********************************
# EXECUTION BEGINS HERE
# ***********************************

echo $"$SCRIPT_NAME"

while [[ ${1:0:1} == "-" ]]; do
    case "$1" in
        "-audiodelay" )
            shift
            AUDIO_DELAY="-O ${1}ms"
            ;;
        "-shrink" )
            shift
            DO_SHRINK=:
            SHRINK_FACTOR="$1"
            ;;
        "-parallel" )
            PARALLEL=:
            mkfifo video_dump
            mkfifo audio_dump
            mkfifo video_shrink
            BACKGR="&"
            ;;
        "-debug" )
            DEBUG=:
            ;;
    esac

    # Get next argument
    shift
done

# Make sure at least two arguments remain (infile and outfile)
if test $# -lt 2; then
  usage_error "Error: Please provide an input filename and an output filename."
fi

IN_FILE="$1"
shift
OUT_FILE="$1"

echo $SEPARATOR

# Figure out what format it is. 44.1khz audio can be VCD or SVCD,
# 48khz audio is DVD.
mplayer -vo null -ao null -frames 0 -identify "$IN_FILE" 2>/dev/null | \
  grep "^ID_" > $TMP_FILE
AUD_SAMPRATE=$( grep 'ID_AUDIO_RATE' $TMP_FILE | sed -e 's/ID_AUDIO_RATE=//' )
VID_WIDTH=$( grep 'ID_VIDEO_WIDTH' $TMP_FILE | sed -e 's/ID_VIDEO_WIDTH=//' )

if test $AUD_SAMPRATE -eq "48000"; then
    MUX_OPTS="-V -f 8"
    VIDEO_FORMAT="DVD"
elif test $AUD_SAMPRATE -eq "44100"; then
    # VCD is 352 wide, SVCD is 480 wide
    if test $VID_WIDTH -eq "352"; then
        MUX_OPTS="-f 1"
        VIDEO_FORMAT="VCD"
    elif test $VID_WIDTH -eq "480"; then
        MUX_OPTS="-V -f 4"
        VIDEO_FORMAT="SVCD"
    fi
fi

echo "Dumping audio and video streams with the following commands:"

# Dump audio and video
AUDIO_DUMP="mplayer \"$IN_FILE\" -quiet -dumpaudio -dumpfile audio_dump"
VIDEO_DUMP="mplayer \"$IN_FILE\" -quiet -dumpvideo -dumpfile video_dump"

echo "$AUDIO_DUMP"
echo "$VIDEO_DUMP"
# Should always be safe to put audio decode in the background
eval $AUDIO_DUMP > $TMP_FILE 2>&1 &
eval $VIDEO_DUMP > $TMP_FILE 2>&1 $BACKGR

# Let the audio process finish if not in parallel mode (should always finish 
# before video, so this is just precautionary)
$PARALLEL && wait

# Shrink, if requested
if $DO_SHRINK; then
    # Can't shrink VCD
    if test $VIDEO_FORMAT = "VCD"; then
        echo $SEPARATOR
        echo "This file appears to be in VCD format. Unfortunately, the"
        echo "VCD specification does not allow shrinking (requantization)."
        echo "Shrinking will be skipped."
        echo $SEPARATOR
    else
        START_SIZE=$( ls -l video_dump | awk '{print $5}' )
        echo $SEPARATOR
        echo "Shrinking video stream by a factor of $SHRINK_FACTOR"
        SHRINK_CMD="tcrequant -i video_dump -o video_shrink -f $SHRINK_FACTOR"
        echo "$SHRINK_CMD"
        eval $SHRINK_CMD $BACKGR
        if $PARALLEL; then
            :
        else
            wait
            SHRINK_SIZE=$( ls -l video_shrink | awk '{print $5}' )
            mv video_shrink video_dump
            SHRINK_PERCENT=`100 \- \( 100 \* $SHRINK_SIZE \/ $START_SIZE \)`
            echo "Video stream was shrunk by $SHRINK_PERCENT%"
        fi
    fi
fi

echo $SEPARATOR


# Multiplex audio and video back together
echo "Multiplexing audio and video streams with the following command:"
MPLEX_CMD="mplex video_dump audio_dump -o \"$OUT_FILE\" $MUX_OPTS $AUDIO_DELAY"
echo "$MPLEX_CMD"
eval $MPLEX_CMD > $TMP_FILE 2>&1

# For parallel, compare infile and outfile sizes
if $PARALLEL; then
    START_SIZE=$( ls -l "$IN_FILE" | awk '{print $5}' )
    SHRINK_SIZE=$( ls -l "$OUT_FILE" | awk '{print $5}' )
    SHRINK_PERCENT=`expr 100 \- \( 100 \* $SHRINK_SIZE \/ $START_SIZE \)`
    echo "Video stream was shrunk by $SHRINK_PERCENT%"
fi  
  
echo $SEPARATOR

echo "Cleaning up..."
rm -fv video_dump audio_dump

# Create stats directory and save video statistics
mkdir -p $STAT_DIR
FINAL_STATS=`cat << EOF
postproc $TOVID_VERSION
File: $OUT_FILE
Shrink factor: $SHRINK_FACTOR
Shrunk by: $SHRINK_PERCENT%
EOF`
echo $"$FINAL_STATS" >> $STAT_FILE

# If doing debugging, keep log and print message
if $DEBUG; then
  echo "All output has been saved in the file: $TMP_FILE."
else
  rm $TMP_FILE
fi

echo "Done. Thanks for using postproc!"

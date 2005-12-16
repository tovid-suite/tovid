# -* sh *-
ME="[idvid]:"
. tovid-init

# idvid
# Part of the tovid suite
# =======================
# A bash script for identifying arbitrary video files and
# testing for VCD, SVCD, DVD or other video disc compliance.
#
# Project homepage: http://www.tovid.org
#
#
# Copyright (C) 2005 tovid.org <http://www.tovid.org>
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA. Or see:
#
#           http://www.gnu.org/licenses/gpl.txt

SCRIPT_NAME=`cat << EOF
--------------------------------
idvid 
Video identification script
Part of the tovid suite, version $TOVID_VERSION
http://www.tovid.org
--------------------------------
EOF`

USAGE=`cat << 'EOF'
Usage: idvid [OPTIONS] <file list>

OPTIONS may be any of the following:

  -terse
    Print information in a terse format suitable for
    parsing by other scripts
EOF`

NON_COMPLIANT=`cat << EOF
This video does not seem to be compliant with (S)VCD or DVD
standards. If you burn it to a video disc, it may not work.
EOF`

# ***********************************
# DEFAULTS AND FUNCTION DEFINITIONS
# ***********************************

# Do not use terse output by default
TERSE=false
TMP_DIR=`mktemp -d idvid-temp.XXXXXX`
SCRATCH_FILE="$TMP_DIR/idvid.scratch"
STAT_DIR=$TOVID_HOME
STAT_FILE="$STAT_DIR/stats.idvid"
NTSC_FPS=""
NTSC_FILM_FPS=""
PAL_FPS=""
A_NONCOMPLIANT=""
V_NONCOMPLIANT=""
A_NONE=""
V_TV=""
mkdir -p "$STAT_DIR"
touch "$STAT_FILE"

# Print usage notes and optional error message, then exit.
# Args: $@ == text string containing error message
usage_error ()
{
  printf "%s\n" "$USAGE"
  echo "$SEPARATOR"
  echo $@
  exit 1
}

# Get video information from available utilities
# Args: $1 = filename to identify
get_info ()
{
    # Start with a clean scratch file
    rm -f "$SCRATCH_FILE"

    INFILE="$1"

    if $TERSE; then :;
    else
        printf "%s\n" "$SCRIPT_NAME"
        echo "Gathering video information. This may take several minutes,"
        echo "so please be patient..."
        echo $SEPARATOR
    fi

    # Identify video using mplayer
    if test -n "$MPLAYER"; then
    mplayer -vo null -ao null -frames 1 -channels 6 -identify \
        "$INFILE" > "$SCRATCH_FILE" 2>&1
    fi
    # Identify video using ffmpeg
    if test -n "$FFMPEG"; then
        # ffmpeg puts its output on standard error
        ffmpeg -i "$INFILE" >> "$SCRATCH_FILE" 2>&1
    fi
    # Identify video using tcprobe
    if test -n "$TCPROBE"; then
        tcprobe -i "$INFILE" >> "$SCRATCH_FILE" 2>/dev/null
    fi

    # Exit if the file couldn't be identified
    if grep -q "^ID_" "$SCRATCH_FILE"; then :;
    else
        if $TERSE; then
            echo "CANT_IDENTIFY=:"
        else
            echo "Could not identify file: $INFILE"
        fi
        rm -rf "$TMP_DIR"
        exit 1
    fi

    # Defaults. Many of these values may be overridden by
    # mplayer's output in the 'eval' statement to follow
    ID_VIDEO_WIDTH="0"
    ID_VIDEO_HEIGHT="0"
    ID_VIDEO_FPS="0"
    ID_VIDEO_FORMAT="Unknown"
    ID_AUDIO_CODEC="Unknown"
    ID_AUDIO_FORMAT="Unknown"
    ID_VIDEO_BITRATE="0"
    ID_AUDIO_BITRATE="0"
    ID_AUDIO_RATE="0"
    ID_AUDIO_NCH="0"
    V_ASPECT_RATIO="1:1"
    ID_LENGTH="0"

    # Source mplayer's output to set relevant variables
    # (ID_V(ideo), ID_A(udio), and ID_L(ength))
    eval `cat "$SCRATCH_FILE" | grep "^ID_[VAL]"`
    
    ID_VIDEO_FRAMES=`grep 'length:' "$SCRATCH_FILE" | \
        awk -F ' ' '{print $2}'`
    test -z $ID_VIDEO_FRAMES && ID_VIDEO_FRAMES="0"

    # Infer aspect ratio by what mplayer uses for playback
    MPLAYER_RES=`grep '^VO:' "$SCRATCH_FILE" | \
        sed -e "s/..*=> *//g" -e "s/ .*$//g"`
    PLAY_WIDTH=`echo $MPLAYER_RES | awk -F 'x' '{print $1}'`
    PLAY_HEIGHT=`echo $MPLAYER_RES | awk -F 'x' '{print $2}'`
    # Fix nulls
    if test -z "$PLAY_WIDTH" || test -z "$PLAY_HEIGHT"; then
        PLAY_WIDTH="100"
        PLAY_HEIGHT="100"
    fi

    V_ASPECT_WIDTH=`expr $PLAY_WIDTH \* 100 \/ $PLAY_HEIGHT`
    V_ASPECT_RATIO=`echo $V_ASPECT_WIDTH | \
        sed -r -e 's/([0-9]*)([0-9][0-9])/\1.\2:1/g'`

    # Truncate floating-point values to integer
    ID_LENGTH=`echo $ID_LENGTH | sed 's/\.[0-9]*//'`
    
    # If mplayer reported a non-zero length, assume it's correct
    if test $ID_LENGTH -gt 0; then
        V_DURATION=$ID_LENGTH
    else
        # A time-consuming alternative: determine duration by playing the video
        # into /dev/null
        V_DURATION="`LC_ALL=C mencoder -ovc frameno -oac copy -noskiplimit \"$INFILE\" \
            -o /dev/null 2>/dev/null | tr '\r' '\n' | grep \"^Pos:\" | tail -n 1 | \
            sed s/\"Pos:\"// | awk -- '{print $1}' | sed s/[.][0-9]s//`"
    fi
    test -z $V_DURATION && V_DURATION=0

    # Mplayer reports ac3 and mp2 incorrectly, so refer to numeric codes
    test "$ID_AUDIO_FORMAT" = "8192" && ID_AUDIO_CODEC="ac3"
    test "$ID_AUDIO_FORMAT" = "80" && ID_AUDIO_CODEC="mp2"

    # For known formats reported in hex codes, convert to plain English
    test "$ID_VIDEO_FORMAT" = "0x10000001" && ID_VIDEO_FORMAT="MPEG1"
    test "$ID_VIDEO_FORMAT" = "0x10000002" && ID_VIDEO_FORMAT="MPEG2"
}

# Main idvid function. Calls get_info to gather video information
# about a file passed as the argument, and prints everything out
# in terse or human-readable form
idvid_main ()
{
    if test -e "$1"; then
        get_info "$1"
    else
        echo "Could not find file: $1"
        exit 1
    fi

    # Set some frequently-used variables
    # Frames per second
    case "$ID_VIDEO_FPS" in
        "29.970" | "29.97" )
            ID_VIDEO_FPS="29.970"
            NTSC_FPS="29.970"
            ;;
        "23.976" )
            NTSC_FILM_FPS="23.976"
            ;;
        "25.000" | "25.00" | "25.0" | "25" )
            ID_VIDEO_FPS="25.000"
            PAL_FPS="25.000"
            ;;
    esac

    # Print out identifying information, either in terse form
    # or in human-readable form
    if $TERSE; then
        echo "ID_VIDEO_WIDTH=$ID_VIDEO_WIDTH"
        echo "ID_VIDEO_HEIGHT=$ID_VIDEO_HEIGHT"
        echo "V_DURATION=$V_DURATION"
        echo "ID_VIDEO_FPS=$ID_VIDEO_FPS"
        echo "ID_VIDEO_FORMAT=$ID_VIDEO_FORMAT"
        echo "ID_AUDIO_CODEC=$ID_AUDIO_CODEC"
        echo "ID_VIDEO_BITRATE=$ID_VIDEO_BITRATE"
        echo "ID_AUDIO_BITRATE=$ID_AUDIO_BITRATE"
        echo "ID_AUDIO_NCH=$ID_AUDIO_NCH"
        echo "ID_AUDIO_RATE=$ID_AUDIO_RATE"
        echo "V_ASPECT_WIDTH=$V_ASPECT_WIDTH"
        echo "ID_VIDEO_FRAMES=$ID_VIDEO_FRAMES"
    else
        echo "               File: $INFILE"
        echo "              Width: $ID_VIDEO_WIDTH pixels"
        echo "             Height: $ID_VIDEO_HEIGHT pixels"
        echo "       Aspect ratio: $V_ASPECT_RATIO"
        echo "             Frames: $ID_VIDEO_FRAMES"
        echo "           Duration: `format_time $V_DURATION` hours/mins/secs"
        echo "          Framerate: $ID_VIDEO_FPS frames per second"
        echo "       Video format: $ID_VIDEO_FORMAT"
        echo "       Audio format: $ID_AUDIO_CODEC"
        echo "      Video bitrate: $ID_VIDEO_BITRATE bits per second"
        echo "      Audio bitrate: $ID_AUDIO_BITRATE bits per second"
        echo "     Audio channels: $ID_AUDIO_NCH channels"
        echo "Audio sampling rate: $ID_AUDIO_RATE Hz"
        echo $SEPARATOR
    fi
    
    # Separate flags for each audio profile (there may be multiple matches)
    A_VCD1=""
    A_VCD2=""
    A_SVCD=""
    A_DVD=""

    # Find matching audio profile(s)
    # DVD audio must be 48khz, 32-1536 kbps
    if test "$ID_AUDIO_RATE" = "48000" && \
      test "$ID_AUDIO_BITRATE" -ge "32000" && \
      test "$ID_AUDIO_BITRATE" -le "1536000"; then
        case "$ID_AUDIO_CODEC" in
            "ac3" )
                A_DVD="$ID_AUDIO_BITRATE bps 48khz AC3 DVD (Dolby Digital)"
                ;;
            "mp2" )
                A_DVD="$ID_AUDIO_BITRATE bps 48khz MP2 DVD (MPEG audio)"
                ;;
        esac

    # VCD/SVCD must be 44.1khz mp2
    elif test "$ID_AUDIO_RATE" = "44100" && test "$ID_AUDIO_CODEC" = "mp2"; then
        # SVCD can be 32-384 bps, 1-4 channels
        if test "$ID_AUDIO_NCH" -le "4" && \
          test "$ID_AUDIO_BITRATE" -ge "32000" && \
          test "$ID_AUDIO_BITRATE" -le "384000"; then
            A_SVCD="$ID_AUDIO_NCH-channel $ID_AUDIO_BITRATE bps SVCD"
        fi
        # VCD must be 224 bps, 2 channels
        if test "$ID_AUDIO_NCH" = "2" && \
          test "$ID_AUDIO_BITRATE" = "224000"; then
            A_VCD1="VCD 1.1"
            A_VCD2="VCD 2.0"
        fi
    fi

    # Check for missing audio stream (0 channels, 0 Hz)
    if test "$ID_AUDIO_NCH" -eq "0" && test "$ID_AUDIO_RATE" -eq "0"; then
        A_NONE="No audio stream present"
    fi
     
    # Separate flags for each video profile (there may be multiple matches)
    V_VCD=""
    V_SVCD=""
    V_DVD=""
    V_RES=""
  
    # Resolution
    case "$ID_VIDEO_WIDTH" in
        "352" )
            case "$ID_VIDEO_HEIGHT" in
                "240" ) V_RES="NTSC_VCD" ;;
                "288" ) V_RES="PAL_VCD" ;;
                "480" ) V_RES="NTSC_HALF" ;;
                "576" ) V_RES="PAL_HALF" ;;
            esac
            ;;
        "480" )
            case "$ID_VIDEO_HEIGHT" in
                "480" ) V_RES="NTSC_SVCD";;
                "576" ) V_RES="PAL_SVCD" ;;
            esac
            ;;
        "528" )
            case "$ID_VIDEO_HEIGHT" in
                "480" ) V_RES="NTSC_KVCDX3";; 
                "576" ) V_RES="PAL_KVCDX3" ;;
            esac
            ;;
        "544" )
            case "$ID_VIDEO_HEIGHT" in
                "480" ) V_RES="NTSC_KVCDX3A" ;;
                "576" ) V_RES="PAL_KVCDX3A" ;;
            esac
            ;;
        "704" | "720" )
            case "$ID_VIDEO_HEIGHT" in
                "480" ) V_RES="NTSC_DVD" ;;
                "576" ) V_RES="PAL_DVD" ;;
            esac
            ;;
    esac
  
    # Find matching video profile(s)
    # Test for VCD/DVD-VCD MPEG1 compliance
    if test "$ID_VIDEO_FORMAT" = "MPEG1" && test "$ID_VIDEO_BITRATE" -le "1856000"; then
        # VCD compliance
        if test "$ID_VIDEO_BITRATE" = "1152000"; then
            # NTSC
            if test "$V_RES" = "NTSC_VCD"; then
                V_TV="NTSC"
                if test -n "$NTSC_FPS"; then
                  V_VCD="$NTSC_FPS fps NTSC VCD 1.1/2.0"
                elif test -n "$NTSC_FILM_FPS"; then
                  V_VCD="$NTSC_FILM_FPS fps film NTSC VCD 1.1/2.0"
                fi
            # PAL
            elif test "$V_RES" = "PAL_VCD" && test -n "$PAL_FPS"; then
                V_TV="PAL"
                V_VCD="$PAL_FPS fps PAL VCD 2.0"
            fi
        fi

        # DVD-VCD MPEG1 compliance
        # NTSC
        if test "$V_RES" = "NTSC_VCD"; then
            V_TV="NTSC"
            if test -n "$NTSC_FPS"; then
                V_DVD="$NTSC_FPS fps $ID_VIDEO_FORMAT NTSC DVD-VCD"
            elif test -n "$NTSC_FILM_FPS"; then
                V_DVD="$NTSC_FILM_FPS fps with 3:2 pulldown $ID_VIDEO_FORMAT NTSC DVD-VCD"
            fi
        # PAL
        elif test "$V_RES" = "PAL_VCD" && test-n "$PAL_FPS"; then
            V_TV="PAL"
            V_DVD="$PAL_FPS fps $ID_VIDEO_FORMAT PAL DVD-VCD"
        fi

    # Test for SVCD/DVD MPEG2 compliance
    elif test "$ID_VIDEO_FORMAT" = "MPEG2" && test "$ID_VIDEO_BITRATE" -le "9800000"; then
        # *********************
        # NTSC
        # *********************
        if test -n "$NTSC_FPS" || test -n "$NTSC_FILM_FPS"; then
            V_TV="NTSC"
            case "$V_RES" in
            # DVD-VCD
            "NTSC_VCD" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT NTSC DVD-VCD"
                ;;
            # SVCD
            "NTSC_SVCD" )
                # Ensure valid bitrate
                test "$ID_VIDEO_BITRATE" -le "2600000" && \
                    V_SVCD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT NTSC SVCD"
                ;;
            # Half-D1
            "NTSC_HALF" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT NTSC Half-D1"
                ;;
            # DVD
            "NTSC_DVD" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT NTSC DVD"
                ;;
            esac
        # *********************
        # PAL
        # *********************
        elif test -n "$PAL_FPS"; then
            V_TV="PAL"
            case "$V_RES" in
            # DVD-VCD
            "PAL_VCD" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT PAL DVD-VCD"
                ;;
            # SVCD
            "PAL_SVCD" )
                    # Ensure valid bitrate
                test "$ID_VIDEO_BITRATE" -le "2600000" && \
                    V_SVCD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT PAL SVCD"
                ;;
            # Half-D1
            "PAL_HALF" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT PAL Half-D1"
                ;;
            # DVD
            "PAL_DVD" )
                V_DVD="$ID_VIDEO_BITRATE bps $ID_VIDEO_FPS fps $ID_VIDEO_FORMAT PAL DVD"
                ;;
            esac
        fi
    fi # Video profile (MPEG-1/2)

    # See if audio is not compliant with anything
    if test -z "$A_VCD1" && test -z "$A_VCD2" && test -z "$A_SVCD" \
        && test -z "$A_DVD" && test -z "$A_DVD"; then
        A_NONCOMPLIANT="Not compliant with (S)VCD or DVD"
    fi
    if test -z "$V_VCD" && test -z "$V_SVCD" && test -z "$V_DVD"; then
        V_NONCOMPLIANT="Not compliant with (S)VCD or DVD"
    fi


    # Print out compliance information
    if $TERSE; then
        test -n "$A_VCD1" && echo "A_VCD1_OK=:"
        test -n "$A_VCD2" && echo "A_VCD2_OK=:"
        test -n "$A_SVCD" && echo "A_SVCD_OK=:"
        test -n "$A_DVD" && echo "A_DVD_OK=:"
        test -n "$A_NONE" && echo "A_NOAUDIO=:"
        test -n "$V_VCD" && echo "V_VCD_OK=:"
        test -n "$V_SVCD" && echo "V_SVCD_OK=:"
        test -n "$V_DVD" && echo "V_DVD_OK=:"
        test -n "$V_RES" && echo "V_RES=$V_RES"
        test -n "$V_TV" && echo "V_TV=$V_TV"
    else
        echo "Audio is compliant with the following formats:"
        test -n "$A_VCD1" && echo "  $A_VCD1"
        test -n "$A_VCD2" && echo "  $A_VCD2"
        test -n "$A_SVCD" && echo "  $A_SVCD"
        test -n "$A_DVD" && echo "  $A_DVD"
        test -n "$A_NONCOMPLIANT" && echo "  $A_NONCOMPLIANT"
        test -n "$A_NONE" && echo "  $A_NONE"
        echo "Video is compliant with the following formats:"
        test -n "$V_VCD" && echo "  $V_VCD"
        test -n "$V_SVCD" && echo "  $V_SVCD"
        test -n "$V_DVD" && echo "  $V_DVD"
        test -n "$V_NONCOMPLIANT" && echo "  $V_NONCOMPLIANT"
        # Print out what discs this video can be burned to
        # PAL
        if test x"$V_TV" = x"PAL"; then
            if test -n "$A_VCD1" || test -n "$A_VCD2"; then
                if test -n "$V_VCD"; then
                    echo "You can burn this video to PAL VCD"
                fi
            elif test -n "$A_SVCD" && test -n "$V_SVCD"; then
                echo "You can burn this video to PAL SVCD"
            elif test -n "$A_DVD" && test -n "$V_DVD"; then
                echo "You can burn this video to PAL DVD"
            else
                printf "%s\n" "$NON_COMPLIANT"
            fi
        # NTSC
        elif test x"$V_TV" = x"NTSC"; then
            if test -n "$A_VCD1" || test -n "$A_VCD2"; then
                if test -n "$V_VCD"; then
                    echo "You can burn this video to NTSC VCD"
                fi
            elif test -n "$A_SVCD" && test -n "$V_SVCD"; then
                echo "You can burn this video to NTSC SVCD"
            elif test -n "$A_DVD" && test -n "$V_DVD"; then
                echo "You can burn this video to NTSC DVD"
            else
                printf "%s\n" "$NON_COMPLIANT"
            fi
        else
            printf "%s\n" "$NON_COMPLIANT"
        fi

        echo $SEPARATOR
    fi

    # Write stats to stat file
    FINAL_STATS_FORMATTED=`cat << EOF
"$TOVID_VERSION", "$INFILE", "$ID_VIDEO_WIDTH", "$ID_VIDEO_HEIGHT", "$V_DURATION", "$ID_VIDEO_FPS", "$ID_VIDEO_FORMAT", "$ID_AUDIO_CODEC", "$ID_VIDEO_BITRATE", "$ID_AUDIO_BITRATE", "$ID_AUDIO_NCH", "$ID_AUDIO_RATE", "$V_ASPECT_WIDTH"
EOF`
    touch "$STAT_FILE"
    printf "%s\n" "$FINAL_STATS_FORMATTED" >> "$STAT_FILE"
  
}

# ===========================
# EXECUTION BEGINS HERE
# ===========================

# See what programs are available for doing identification
MPLAYER=`type -p mplayer`
FFMPEG=`type -p ffmpeg`
TCPROBE=`type -p tcprobe`

while test $# -gt 0; do
    case "$1" in
        "-terse" ) TERSE=: ;;
        * )
            idvid_main "$1"
            ;;
    esac
    shift
done

rm -rf "$TMP_DIR"

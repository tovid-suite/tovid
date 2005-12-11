#!/bin/bash
. tovid-init

# tovid-batch
# Part of the tovid suite
# ==============
# A bash script for batch video conversion.
#
# Project homepage: http://tovid.sourceforge.net/
#
# Convert any video/audio stream that mplayer can play
# into VCD, SVCD, or DVD-compatible Mpeg output file.
# Run this script without any options to see usage information.
#
# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

SCRIPT_NAME=`cat << EOF
--------------------------------
tovid-batch
A batch conversion script using tovid
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------
EOF`

USAGE=`cat << 'EOF'
Usage: tovid-batch [OPTIONS] -infiles <input files>

OPTIONS may be any options that tovid accepts. Run 'tovid'
without any options to see what it expects.

You can provide any number of input files; the output
files will be named INPUT_FILENAME.tovid_encoded.mpg
EOF`

SEPARATOR="========================================================="

# No tovid arguments to start with
TOVID_ARGS=""

# ***********************************
# EXECUTION BEGINS HERE
# ***********************************

printf "%s\n" "$SCRIPT_NAME"

# Get all arguments up to -infiles
while test $# -gt 0; do
    if test "$1" = "-infiles"; then
        shift
        break
    else
        TOVID_ARGS="$TOVID_ARGS $1"
    fi
    
    # Get next argument
    shift
done

# If no infiles, print usage notes
if test $# -le 0; then
    printf "%s\n" "$USAGE"
    printf "%s\n" "$SEPARATOR"
    echo "Please provide a list of files to encode using -infiles"
    exit 1
fi

# For every input filename provided, run tovid with the given options
for FILE in "$@"; do
    TOVID_CMD="tovid $TOVID_ARGS -in \"$FILE\" -out \"$FILE.tovid_encoded\""
    echo $TOVID_CMD
    eval $TOVID_CMD
done

# -* sh *-
ME="[tovid-test]:"
. tovid-init

# tovid-test
# Part of the tovid suite
# =======================
# A bash script for testing the tovid suite.
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

# ******************************************************************************
# ******************************************************************************
#
#
# DEFAULTS AND GLOBALS
#
#
# ******************************************************************************
# ******************************************************************************

SEPARATOR="========================================================="

# An identifying string to be printed before all console/log output
ME="[tovid-test]:"
ERRORS=0

SCRIPT_NAME=`cat << EOF
--------------------------------
tovid-test
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------
EOF`

USAGE=`cat << EOF
Usage: tovid-test [OPTIONS] {input file}

OPTIONS may be any of the following:

    (no options currently implemented)

The input file may be any video file. Output
and logging go into a temporary directory
with a name like "tovid-test.3peFka".
EOF`


# Options to test
# Lists of mutually-exclusive options for each script

# tovid
# -normalize
# -lowquality?
# -deinterlace?
# -vbitrate
# -abitrate
# -overwrite

ALL_FORMATS="-dvd -half-dvd -svcd -dvd-vcd -vcd -kvcd -ksvcd -kdvd"
BASIC_FORMATS="-dvd -svcd -vcd"
TVSYSTEMS="-pal -ntsc -ntscfilm"
ASPECTS="-full -wide -panavision"
MISC_OPTS="-interlaced -normalize -parallel"

KEEP_OUTPUT=false
TMP_DIR=`mktemp -d tovid-test.XXXXXX`
LOG_FILE="$TMP_DIR/tovid-test.log"
DEFAULT_OUTFILE="$TMP_DIR/outfile.default"

# makemenu
# -aspect [left|center|right]
# -topmenu
# -menu
# -background
# -audio
# -textcolor
# -highlightcolor
# -selectcolor
# -font

# ******************************************************************************
# Y-echo: echo to two places at once (stdout and logfile)
# Output is preceded by the script name that produced it
# Args: $@ == any text string
# If no args are given, echo a separator bar
# Why echo when you can yecho?
# ******************************************************************************
yecho()
{
    if test $# -eq 0; then
        printf "\n%s\n\n" "$SEPARATOR"
        # If logfile exists, copy output to it (with pretty formatting)
        test -e "$LOG_FILE" && \
            printf "%s\n%s %s\n%s" "$ME" "$ME" "$SEPARATOR" "$ME" >> "$LOG_FILE"
    else
        echo "$@"
        test -e "$LOG_FILE" && \
            printf "%s %s" "$ME" "$@" >> "$LOG_FILE"
    fi
}

# ******************************************************************************
# Print usage notes and optional error message, then exit.
# Args: $@ == text string containing error message
# ******************************************************************************
usage_error()
{
    echo $"$USAGE"
    echo "$SEPARATOR"
    echo $@
    exit 1
}

# ******************************************************************************
# Test the tovid script with the given options and infile
# Args: $@ = all options (including -in) to test
#   -out filename will be ignored if provided
# ******************************************************************************
test_tovid()
{
    # If we're keeping every output file, generate a unique name
    if $KEEP_OUTPUT; then
        OUTFILE_UNIQUE=`echo $@ | sed 's/ //g'`
        OUTFILE="outfile.opts.$OUTFILE_UNIQUE"
    else
        OUTFILE="$DEFAULT_OUTFILE"
    fi
    CMD="tovid $@ -overwrite -out \"$OUTFILE\" >> \"$LOG_FILE\""
    yecho $CMD
    echo $CMD >> "$LOG_FILE"

#:<< EOF
    if eval $CMD; then
        # Report success
        echo "--------"
        echo "Success!"
        echo "$ME Detected a successful encoding" >> $LOG_FILE
        echo $SEPARATOR
    else
        # Count and log error
        let "ERRORS=$ERRORS + 1"
        echo "$ME Detected an encoding failure" >> $LOG_FILE
        # Report failure
        echo "----------------"
        echo "*** Failure! ***"
        echo "Please see $LOG_FILE for error messages."
        # Report error
        echo $SEPARATOR
    fi
#EOF

}

# ******************************************************************************
# Execution begins here
# ******************************************************************************
INFILE="$1"
if [[ -z "$INFILE" ]]; then
    usage_error "Please provide the name of a video file to use as input."
fi

# Remove any existing log file
[[ -f "$LOG_FILE" ]] && rm "$LOG_FILE"

# Test tovid with the most basic command-line options
# NOTE TO DEVELOPERS:
# This whole quick-and-dirty approach has to go. This
# test script should offer the option to test with
# varying intensity and thoroughness.
for MISC_OPT in $MISC_OPTS; do
    test_tovid -in $INFILE $MISC_OPT
done
for FORMAT in $ALL_FORMATS; do
    test_tovid -in $INFILE $FORMAT
done
for TVSYS in $TVSYSTEMS; do
    test_tovid -in $INFILE $TVSYS
done
for ASPECT in $ASPECTS; do
    test_tovid -in $INFILE $ASPECT
done


echo "There were $ERRORS errors. Please see $LOG_FILE for a complete report."
echo "Done. Thanks for using tovid-test."

exit 0

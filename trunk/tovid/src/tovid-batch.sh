# -* sh *-
ME="[tovid-batch]:"
. tovid-init

# tovid-batch
# Part of the tovid suite
# =======================
# A bash script for batch video conversion.
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

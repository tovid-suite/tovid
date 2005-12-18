# -* sh *-
ME="[makedvd]:"
. tovid-init

# makedvd
# Part of the tovid suite
# =======================
# A bash script for creating a DVD VIDEO_TS/VOB structure and
# burning it to a recordable DVD.
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

SCRIPTNAME=`cat << EOF
--------------------------------
makedvd
A script to create a DVD-Video file structure and burn it to DVD
Part of the tovid suite, version $TOVID_VERSION
http://www.tovid.org
--------------------------------
EOF`

USAGE=`cat << 'EOF'
Usage: makedvd {OPTIONS} FILE.xml

Where OPTIONS may be any of the following:

  -author
  -image
  -burn
  -device DEVFS_NAME (default /dev/dvd)
  -speed NUM (default 1)
  -label DISC_LABEL

FILE.xml is a
See the makedvd manual page ('man makedvd') for additional documentation.

EOF`

# Print script name, usage notes, and optional error message, then exit.
# Args: $1 == text string containing error message
usage_error ()
{
  echo $"$USAGE"
  echo $SEPARATOR
  echo $"$@"
  exit 1
}

# Print out a runtime error specified as an argument, and exit
runtime_error ()
{
    #killsubprocs
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "makedvd encountered an error during the DVD creation process:"
    echo $@
    echo "See if anything in the above output helps you diagnose the"
    echo "problem, and please file a bug report containing the above"
    echo "output. Sorry for the inconvenience!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
}

# Defaults
# Create the DVD filesystem hierarchy?
DO_AUTHOR=""
# Create an ISO image?
DO_IMAGE=""
# Burn the image to disc?
DO_BURN=""

DVDRW_DEVICE="/dev/dvd"
BURN_SPEED=1
OUT_DIR="makedvd_out"
DISC_LABEL=""
DO_IMAGE=""

# ==========================================================
# EXECUTION BEGINS HERE
echo $"$SCRIPTNAME"

while [[ ${1:0:1} == "-" ]]; do
    if [[ $1 == "-author" ]]; then
        DO_AUTHOR="y"
    elif [[ $1 == "-image" ]]; then
        DO_IMAGE="y"
    elif [[ $1 == "-burn" ]]; then
        DO_BURN="y"
    elif [[ $1 == "-device" ]]; then
        # Get device name
        shift
        DVDRW_DEVICE="$1"
    elif [[ $1 == "-speed" ]]; then
        shift
        BURN_SPEED=$1
    elif [[ $1 == "-label" ]]; then
        shift
        DISC_LABEL="$1"
    fi

    # Get next argument
    shift
done

# Make sure there's one more argument (XML file)
if test $# -gt 0; then
    DVDAUTHOR_XML="$1"
    # Set disc title and output directory based on XML filename
    # (without .xml, space to underscore)
    [[ -z $DISC_LABEL ]] && DISC_LABEL=$( echo "$DVDAUTHOR_XML" | sed -e "s/\.xml//g" | tr ' ' '_')
    # And, just in case that failed...
    [[ -z $DISC_LABEL ]] && DISC_LABEL="UNTITLED_DVD"
    OUT_DIR=`grep 'dest=' $DVDAUTHOR_XML | cut -d= -f2 | tr -d '">'`
else
    usage_error "Please provide the name of a dvdauthor-style XML file to use."
fi

# Make sure the file exists
if [[ ! -f "$DVDAUTHOR_XML" ]]; then
    echo "Could not open file: $DVDAUTHOR_XML"
    exit 1
else
    echo "Authoring disc from file: $DVDAUTHOR_XML"
fi

# Remind user to insert a DVD
if [[ -n $DO_BURN ]]; then
    echo "Please insert a blank DVD+/-R(W) disc into your DVD-recorder"
    echo "($DVDRW_DEVICE) if you have not already done so."
fi

# Sanity check: Make sure given device is valid (somehow)
# before creating the image. Give option to proceed anyway?
# (i.e., could there be any point to proceeding?)


# TODO:
# Warn if there isn't enough space to make the image

# See if target directory already exists.
if [[ -d $OUT_DIR ]]; then
    echo "Authoring directory $OUT_DIR already exists."

    # If target directory exists, it may be due to a prior
    # attempt at encoding. Skip authoring unless -author
    # was specified.
    if [[ -z $DO_AUTHOR ]]; then
        echo $SEPARATOR
        echo "Skipping authoring; to force, use the -author option."
        echo $SEPARATOR
    # Remove existing directory, and author from scratch
    else
        echo "Deleting contents of directory: $OUT_DIR"
        rm -rf "$OUT_DIR"
    fi
else
    # DVD Tree doesn't exist, so create it
    DO_AUTHOR="y"
fi

if [[ ! -z $DO_AUTHOR ]]; then
    # Create disc structure
    DVDAUTHOR_CMD="dvdauthor -x \"$DVDAUTHOR_XML\""
    echo $SEPARATOR
    echo "Creating DVD-Video disc structure with the following command:"
    echo $DVDAUTHOR_CMD
    SUCCESS=false
    eval "$DVDAUTHOR_CMD" 2>&1 && SUCCESS=:

    # Confirm that authoring worked
    if $SUCCESS; then
        echo $SEPARATOR
        echo "Disc structure successfully created in $OUT_DIR."
        echo $SEPARATOR
    else
        runtime_error "Could not create the DVD-Video disc structure in $OUT_DIR. Leaving $OUT_DIR for inspection."
    fi
fi


# See if target disc image exists
if [[ -f $DISC_LABEL.iso && -s $DISC_LABEL.iso ]]; then
    if [[ -z $DO_IMAGE ]]; then 
        echo "Disc image $DISC_LABEL.iso already exists."
        echo "Skipping image (.iso) creation; To force, use the -image option."
    # Otherwise, proceed with image creation
    else
        rm $DISC_LABEL.iso
    fi
else
    # Image doesn't exist, so create it
    DO_IMAGE="y"
fi

if [[ ! -z $DO_IMAGE ]]; then
    # Create ISO image
    VOLID=`echo "$DISC_LABEL" | tr a-z A-Z`
    # Make sure we have a valid VOLID at this point...can't be too long
    VALID_VOLID=`echo $VOLID | awk '{ print substr($0, 0, 32) }'`
    if [ $VOLID != $VALID_VOLID ]; then
        echo "Disk Label is too long. Truncating to $VALID_VOLID"
        VOLID=$VALID_VOLID
    fi
    ISO_CMD="mkisofs -dvd-video -V $VOLID -o $DISC_LABEL.iso $OUT_DIR"
    echo $SEPARATOR
    echo "Creating DVD filesystem ISO image with the following command:"
    echo $ISO_CMD
    echo $SEPARATOR
    SUCCESS=false
    eval "$ISO_CMD" 2>&1 && SUCCESS=:

    # Confirm that the ISO command was successful
    if $SUCCESS; then
        echo $SEPARATOR
        echo "ISO image $DISC_LABEL.iso successfully created."
        echo $SEPARATOR
    else
        runtime_error "Could not create ISO image $DISC_LABEL.iso"
    fi
fi
    
# Burn the disc, if requested
if [[ -n $DO_BURN ]]; then
    BURN_CMD="growisofs -dvd-compat -speed=$BURN_SPEED -Z $DVDRW_DEVICE=$DISC_LABEL.iso"
    echo $SEPARATOR
    echo "Burning ISO to DVD with the following command:"
    echo $BURN_CMD
    echo $SEPARATOR
    SUCCESS=false
    eval "$BURN_CMD" 2>&1 && SUCCESS=:

    if $SUCCESS; then
        echo $SEPARATOR
        echo "Done. You should now have a working DVD. Please visit"
        echo "the tovid homepage: http://tovid.sourceforge.net/"
        echo $SEPARATOR
    else
        runtime_error "Could not burn the disc to $DVDRW_DEVICE at speed $BURN_SPEED"
    fi

fi

echo "Thanks for using makedvd!"

exit 0



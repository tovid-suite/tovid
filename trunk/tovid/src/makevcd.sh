#!/bin/bash
. tovid-init

# makevcd 
# Part of the tovid suite
# ==============
# A bash script for creating a VCD cue/bin set and burning it
# to a recordable CD.
#
# Project homepage: http://tovid.sourceforge.net/
#
# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#     http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

SCRIPTNAME=`cat << EOF
--------------------------------
makevcd
A script to create cue/bin files for a (S)VCD and burn them to a CD
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------
EOF`

USAGE=`cat << 'EOF'
Usage: makevcd {OPTIONS} VCDIMAGER_XML

Where OPTIONS may be any of the following:

  -overwrite
      Overwrite existing ISO image, and re-create the image.
      By default, no existing files are overwritten.
  -burn
      Burn the disc after creating the ISO file. Default is off.
  -device [DEVICE] (default /dev/cdrw)
      Use DEVICE as the Linux device filesystem name of your
      CD-recorder. Common examples might be /dev/cdrw, /dev/scd0,
      and /dev/hdc. You can also use a bus/id/lun triple such as
      ATAPI:0,1,0
  -speed [NUM] (default 12)
      Burn disc at speed NUM.
  -noburn
      Author the disc image only; do not burn it to disc.

And:

  VCDIMAGER_XML is the name of a file containing a VCDImager XML
      description (For XML format, see http://www.vcdimager.org/).
      If you use(d) 'makexml' to create the XML file, you can use
      that as input here.

Please insert a blank CD before running the script.

The output cue/bin file is created in the current directory, so
please run it from a directory that has at least 1.5GB of free
space (~700MB .bin and ~700MB .iso), if you are burning a full disc.

Please note that if you are using a 2.6.x Linux kernel without
SCSI emulation (and cdrdao is not suid root), then this script
will likely fail to burn a disc from a normal user account. In
that situation, please run 'makevcd' from a root account, or
setuid root on the 'makevcd' script.
EOF`

SEPARATOR="=========================================="

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
    killsubprocs
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "makevcd encountered an error during the VCD creation process:"
    echo $@
    echo "See if anything in the above output helps you diagnose the"
    echo "problem, and please send a bug report containing the above"
    echo "output to wapcaplet99@yahoo.com. Sorry for the inconvenience!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
}
# Defaults
CDRW_DEVICE="/dev/cdrw"
BURN_SPEED=12

# ==========================================================
# EXECUTION BEGINS HERE
echo $"$SCRIPTNAME"

while [[ ${1:0:1} == "-" ]]; do
    if [[ $1 == "-device" ]]; then
        # Get device name
        shift
        CDRW_DEVICE="$1"
    elif [[ $1 == "-speed" ]]; then
        shift
        BURN_SPEED=$1
    fi

    # Get next argument
    shift
done

if [[ $# -ne 1 ]]; then
    usage_error "Please provide the name of a VCDimager XML file \
containing the (S)VCD description."
else
    # XML input is last argument
    VCDIMAGER_XML="$1"
fi

# Remind user to insert a CD
echo "Please insert a blank CD-R(W) disc into your CD-recorder"
echo "($CDRW_DEVICE) if you have not already done so."

# Sanity check: Make sure given device is valid (somehow)
# before creating the cue/bin. Give option to proceed anyway?
# (i.e., could there be any point to proceeding?)

# Create cue/bin
# Warn if there isn't enough space to make cue/bin
VCDIMAGER_CMD="vcdxbuild -c \"$VCDIMAGER_XML.cue\" -b \
    \"$VCDIMAGER_XML.bin\" \"$VCDIMAGER_XML\""
echo $SEPARATOR
echo "Creating cue/bin disc image with the following command:"
echo $VCDIMAGER_CMD
( eval $VCDIMAGER_CMD )

# Burn the disc
CDRDAO_CMD="cdrdao write --device $CDRW_DEVICE --driver generic-mmc \
    --speed $BURN_SPEED \"$VCDIMAGER_XML.cue\""
echo $SEPARATOR
echo "Burning cue/bin image to $CDRW_DEVICE with the following command:"
echo $CDRDAO_CMD
( eval $CDRDAO_CMD )

if [[ ! $? ]]; then
    runtime_error "Could not burn the disc to $CDRW_DEVICE at speed $BURN_SPEED"
else
    echo "Done. You should now have a working VCD or SVCD. Please report"
    echo "any problems you might have to wapcaplet99@yahoo.com."
fi
exit 0

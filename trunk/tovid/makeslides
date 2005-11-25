#!/bin/bash
. tovid-init

# makeslides
# Part of the tovid suite
# ==============
# This script converts one or more still images in
# nearly any format into still-image MPEG video
# files for use as a VCD or SVCD slideshow.
#
# Project homepage: http://tovid.sourceforge.net/
#
# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

SCRIPTNAME=`cat << EOF
--------------------------------
makeslides
A script to create MPEG stills from provided images
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------
`

USAGE=`cat << 'EOF'
Usage: makeslides [FORMAT] [IMAGES]

Where:
  FORMAT is one or more of the following:

  -ntsc (default)
  -ntscfilm
    Generate NTSC (704x480) output
  -pal
    Generate PAL (704x576) output

  IMAGES is a single image or list of images to be
    converted to still MPEGs. The output names will
    be the same as the input name, with a .mpg extension.
`
# ***********************************
# DEFAULTS AND FUNCTION DEFINITIONS
# ***********************************

SEPARATOR="========================================================="

# Set defaults
HEIGHT="480"
MPEG2ENC_FMT="-a 2 -f 6 -T 120"
PPM_OPTS="-S 420mpeg2 -A 10:11 -F 30000:1001"

# Print usage notes and optional error message, then exit.
# Args: $@ == text string containing error message
usage_error ()
{
  echo $"$USAGE"
  echo "$SEPARATOR"
  echo $@
  exit 1
}

echo $"$SCRIPTNAME"

while [[ ${1:0:1} == "-" ]]; do
  # PAL or NTSC
  if [[ $1 == "-pal" ]]; then
    HEIGHT="576"
    PPM_OPTS="-S 420mpeg2 -A 59:54 -F 25:1"
  elif [[ $1 == "-ntsc" ]]; then
    HEIGHT="480"
    PPM_OPTS="-S 420mpeg2 -A 10:11 -F 30000:1001"
  else
    usage_error "Error: Unrecognized command-line option $1"
  fi

  # Get next argument
  shift
done

# Create a black background to composite each image over
# Use unusual filename to prevent overwriting anything important
BLACK_BG="makeslides.$PPID.black.png"
convert -size 704x$HEIGHT xc:black $BLACK_BG

# Process remaining arguments as image filenames
while [[ $# -gt 0 ]]; do
  CUR_IMAGE=$1
  echo "Processing image: $CUR_IMAGE"
  composite -resize 704x$HEIGHT -gravity center \
    "$CUR_IMAGE" $BLACK_BG -depth 8 "$CUR_IMAGE.ppm"
  ppmtoy4m -n 1 $PPM_OPTS "$CUR_IMAGE.ppm" | \
    mpeg2enc $MPEG2ENC_FMT -o "$CUR_IMAGE.mpg"
  rm "$CUR_IMAGE.ppm"
  shift
done

rm $BLACK_BG
echo "Done"
exit 0

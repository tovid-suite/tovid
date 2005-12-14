# -* sh *-
ME="[tovid-interactive]:"
. tovid-init

# tovid-interactive
# Part of the tovid suite
# =======================
# A bash script with an interactive frontend to the tovid
# script. This script prompts the user for all options, and
# then runs the tovid script with the selected options.
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

WELCOME=`cat << EOF
--------------------------------
tovid-interactive
Part of the tovid suite, version $TOVID_VERSION
http://tovid.sourceforge.net/
--------------------------------

Welcome to the tovid-interactive script. This script is an interactive
front-end for the tovid video conversion script. I will ask you several
questions about the video you want to encode, and then run the tovid
script with the options you choose.

EOF`

SEPARATOR="========================================================="

echo $"$WELCOME"
echo $SEPARATOR

# Make sure tovid is in the path
if [[ ! $( type -p tovid ) ]]; then
  echo "Oops! I can't find tovid in your path. Before you use this script,"
  echo "please install the tovid suite by running the 'configure' script"
  echo "from the directory where you unzipped tovid."
  exit 1
fi

# Ask for input file unless it was already provided
if [[ $# -eq 0 ]]; then
  echo "What video file do you want to encode? Please use the full path"
  echo "name if the file is not in the current directory. Hint: if you"
  echo "don't know the full name of the file, you can press [control]-C"
  echo "now, and run tovid-interactive followed by the name of the file."
  echo -n "filename: "
  read INFILE
  echo $SEPARATOR
else
  INFILE=$1
  echo "Encoding the filename provided on the command-line:"
  echo "$1"
  echo $SEPARATOR
fi
# Ask for format
echo "You can encode this video to one of the following formats:"
echo "For burning onto DVD:"
echo "   dvd       DVD format             720x480 NTSC, 720x576 PAL"
echo "   half-dvd  Half-DVD format        352x480 NTSC, 352x576 PAL"
echo "   dvd-vcd   VCD-on-DVD format      352x240 NTSC, 352x288 PAL"
echo "For burning onto CD:"
echo "   vcd       Video CD format        352x240 NTSC, 352x288 PAL"
echo "   svcd      Super Video CD format  480x480 NTSC, 480x576 PAL"
echo "Please enter one of the formats above (vcd, half-dvd, dvd-vcd, vcd, svcd)."
echo -n "format: "
read VIDFORMAT
echo $SEPARATOR
# Ask for NTSC or PAL
echo "Do you want the video to be NTSC or PAL? If you live in the Americas"
echo "or Japan, you probably want NTSC; if you live in Europe, you probably"
echo "want PAL. Please use lowercase (ntsc, pal)."
echo -n "ntsc or pal: "
read TVSYS
echo $SEPARATOR
# Ask for aspect ratio
echo "You can encode to three different screen formats:"
echo "   full        If your video is full-screen (4:3 aspect ratio)"
echo "   wide        If your video is wide-screen (16:9 aspect ratio)"
echo "   panavision  If your video is theatrical wide-screen (2.35:1 aspect ratio)"
echo "If you choose wide or panavision, the video will be 'letterboxed' to fit"
echo "a standard TV screen. Most TV programs are 'full'; many movies are 'wide',"
echo "and some movies are 'panavision' (if they look very wide and skinny)."
echo "Please enter one of the screen formats listed above (full, wide, panavision)."
echo -n "screen format: "
read ASPECT
echo $SEPARATOR
# Normalize audio?
echo "In some videos, the volume may be too quiet or too loud. You can"
echo "fix this by normalizing the audio."
echo -n "normalize audio (default yes) [y/n]? "
read NORMALIZE
if [[ $NORMALIZE == "n" || $NORMALIZE == "N" ]]; then
  NORMALIZE=""
else
  NORMALIZE="-normalize"
fi
echo $SEPARATOR
# Get output prefix
echo "You are almost ready to encode your video. All I need now is the name"
echo "you want to use for the output file. You don't need to give a filename"
echo "extension (like .mpg); just type a name like 'MyVideo1'."
echo -n "output name: "
read OUT_PREFIX
echo $SEPARATOR
# Print last message and call tovid
echo "Great! I will now start tovid with the options you chose. Here is the"
echo "command that will be executed:"
TOVID_CMD="tovid $NORMALIZE -$VIDFORMAT -$TVSYS -$ASPECT \
    -in \"$INFILE\" -out \"$OUT_PREFIX\""
echo $SEPARATOR
echo $TOVID_CMD
echo $SEPARATOR
echo "Starting tovid in 5 seconds..."
for COUNTER in 5 4 3 2 1; do
  sleep 1s
  echo -n "$COUNTER "
done
echo "Here goes!"
eval $TOVID_CMD
exit 0

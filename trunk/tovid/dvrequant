#! /bin/bash

# DVrequant script   

# Will rip a DVD-9 disc with the  title and audio of your
# choice and requantize it to fit on a DVD-R 4.7
# Copyright Jean-François Ouellette (Steel_J)  2005-08-12

# Further coding, concept analysis and alpha testing and also set to read 
# from config file and work hands free by Daniel Patterson (KillFire) 2005-04-23
# Additional code for chaptering and error checking from Eric Pierce (WapCaplet) 2005-03-04
# Special thanks to SK545 (Khurram Ahmed) for is beta testing efforts and precious feedback 2005-06-07
# Without these guys this script would'nt have been the same.

# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

# Requirement: mplayer / libdvdcss / transcode / mjpegtools / dvdauhtor 0.6.10 / cdrecord (mkisofs) / lsdvd 

#===========================================================================
# DEFAULTS VARIABLES AND FUNCTION DEFINITIONS
# Configuration file
CONFIG_FILE=~/.dvrequant_config
# DVD content log
NFO_LOG=~/.dvrequant_nfo
# Process log file
PROCESS_LOG=~/.dvrequant_process.log
# Hands-free operation? (empty == no)
NOHANDS=""
# Have libdvdread? (assume no until it's found)
HAVE_READ=""
# Have libdvdcss? (assume no until it's found)
HAVE_CSS=""
# Name for video output and shrunk files
VIDEO_OUTPUT="video_out.m2v"
VIDEO_SHRUNK="video_shrunk.m2v"

# Take an integer number of seconds and format it as hours:minutes:seconds
# Echoes result to stdout, so in order to use the output as a "return value",
# call the function like this:
#   RETURN_VALUE=$( format_time $NUM_SECONDS )
format_time ()
{
  let "HMS_HOURS=$1 / 3600"
  let "HMS_MINS=( $1 % 3600 ) / 60"
  let "HMS_SECS=$1 % 3600 % 60"

  [[ $HMS_HOURS -lt 10 ]] && HMS_HOURS="0${HMS_HOURS}"
  [[ $HMS_MINS -lt 10 ]] && HMS_MINS="0${HMS_MINS}"
  [[ $HMS_SECS -lt 10 ]] && HMS_SECS="0${HMS_SECS}"

  echo "${HMS_HOURS}:${HMS_MINS}:${HMS_SECS}"
}

# Take a string containing a time (like "02:15:25.3") and
# format it as an integer number of seconds. Fractional seconds
# are truncated. Result is echoed to stdout, so to use the output
# as a "return value", call the function like this:
#   RETURN_VALUE=$( unformat_time $TIME_STRING )
unformat_time ()
{
  HMS_HOURS=$( echo $1 | sed -r -e 's/0?([0-9]+):0?([0-9]+):0?([0-9]+)(\.[0-9])?/\1/' )
  HMS_MINS=$( echo $1 | sed -r -e 's/0?([0-9]+):0?([0-9]+):0?([0-9]+)(\.[0-9])?/\2/' )
  HMS_SECS=$( echo $1 | sed -r -e 's/0?([0-9]+):0?([0-9]+):0?([0-9]+)(\.[0-9])?/\3/' )
  let "TOT_SECONDS=$HMS_HOURS * 3600 + $HMS_MINS * 60 + $HMS_SECS"
  echo $TOT_SECONDS
}

# Retrieve the chapter breaks from the specified track on the DVD.
# Echoes a string to stdout with a list of chapter-start times
# (i.e., "0, 1:53, 15:26, 1:23:15" etc.)
# To use output as a "return value", call the function like this:
#   CHAPTER_START_TIMES=$( get_chapters $TITLE )
get_chapters ()
{
  CH_LIST=$( lsdvd -c -t $1 2>&1 | grep "Chapter:" | \
      sed -r -e 's/^.* Length: ([^,]+).*$/\1/' )
  
  # Assemble the list
  echo -n "0"
  TOTAL_SECS=0
  for CUR_CHAP in $CH_LIST; do
    CUR_SECS=$( unformat_time $CUR_CHAP )
    # Don't insert markers for 0-second chapters
    if [[ $CUR_SECS -gt 0 ]]; then
      let "TOTAL_SECS=$TOTAL_SECS + $CUR_SECS"
      CUR_TIME=$( format_time $TOTAL_SECS )
      echo -n ",$CUR_TIME"
    fi
  done
}

#========================================================================
# Presentation
clear
VERSION=0.182b
echo -e "* DVRequant v${VERSION} *" 2> $PROCESS_LOG 1> $PROCESS_LOG
echo -e "* DVRequant v${VERSION} *"
echo "Requires: mplayer / libdvdcss / libdvdread / transcode / mjpegtools / dvdauhtor 0.6.10 / cdrecord (mkisofs)  / lsdvd / slocate "
echo " "
echo "**dvdauthor must be version 0.6.10 and upward** "
echo "--You may modify the config file default values in $CONFIG_FILE"
echo "--growisofs or K3B are optional but recommended"
echo " "

#============================================================================
# Checking for needed software
if ! which slocate >/dev/null ; then
  echo " "
  echo "slocate is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p mplayer ) ]]; then
  echo " "
  echo "mplayer is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p transcode ) ]]; then
  echo " " 
  echo "transcode is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p mpeg2enc ) ]]; then
  echo " "
  echo "mjpegtools is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p dvdauthor ) ]]; then
  echo " "
  echo "dvdauthor is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p mkisofs ) ]]; then
  echo " "
  echo "cdrecord (mkisofs) is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

if [[ -z $( type -p lsdvd ) ]]; then
  echo " "
  echo "lsdvd is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

# Try to find libdvdread.so.3, looking first in the most obvious places
if [[ $( type -p /usr/lib/libdvdread.so.3 ) ]]; then HAVE_READ="y"
elif [[ $( type -p /usr/local/lib/libdvdread.so.3 ) ]]; then HAVE_READ="y"
elif [[ $( slocate libdvdread.so.3 | head -n 1 ) ]]; then HAVE_READ="y"
fi

if [[ -z $HAVE_READ ]]; then
  echo " "
  echo "libdvdread is not detected";
  echo "you need it installed. Exiting...";
  false; exit;
fi

# Try to find libdvdcss.so.2, looking first in the most obvious places
if [[ $( type -p /usr/lib/libdvdcss.so.2 ) ]]; then HAVE_CSS="y"
elif [[ $( type -p /usr/local/lib/libdvdcss.so.2 ) ]]; then HAVE_CSS="y"
elif [[ $( slocate libdvdcss.so.2 | head -n 1 ) ]]; then HAVE_CSS="y"
fi

if [[ -z $HAVE_CSS ]]; then
  echo " "
  echo "*************************************************************** "
  echo "libdvdcss is not detected, you need it to complete the process.";
  echo "*************************************************************** "
  echo " "
  echo "******************************************************************************** "
  echo "The script will keep going but may exit with errors when trying to read the DVD. "
  echo "******************************************************************************** "
  echo " "
fi

#==========================================================================
# Read config file
echo "Reading from the config file..."
echo " "
# If config file doesn't exist, create it
if [[ ! -e "$CONFIG_FILE" ]]; then
echo "DVD_DEVICE_DEVICE /dev/dvd" > "$CONFIG_FILE"
echo "WORKING_DIR /home/$USER" >> "$CONFIG_FILE"
fi

WORKING_DIR=$( eval "echo `cat "$CONFIG_FILE" | grep "^WORKING_DIR" | cut -d \" \" -f 2`" )

if [[ ! -d $WORKING_DIR ]]; then
	mkdir $WORKING_DIR 2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

DVD_DEVICE=`cat $CONFIG_FILE | grep "^DVD_DEVICE" | cut -d " " -f 2`

echo "DONE!  "
echo "Press ENTER."
read KEY

#===========================================================================
# Create project folder and choose preferences

DISK_TITLE=`lsdvd $DVD_DEVICE -q | grep Disc | cut -d " " -f 3`

if [[ ! -d $DISK_TITLE ]]; then
mkdir $WORKING_DIR/$DISK_TITLE 2>> $PROCESS_LOG 1>> $PROCESS_LOG
else
echo "Directory $WORKING_DIR/$DISK_TITLE already exists. Continuing." 
fi

#==========================================================================
# Video stream sub-section
# Read and display info about DVD video titles (dvdnfo)

SPACE=" "

VIDEO_DISPLAY=`lsdvd -qt $DVD_DEVICE | grep Title | cut -d " " -f 1,2,3,4`

TITLE_PLAY=`lsdvd $DVD_DEVICE | grep Longest | cut -c 16-17` 

TITLE_LENGTH=`lsdvd $DVD_DEVICE -q -t $TITLE_PLAY | grep Length: | cut -c 20-40`
                                
AUDIO_DISPLAY=`mplayer  -nojoystick -nolirc -dvd-device $DVD_DEVICE dvd://$TITLE_PLAY -vo null -ao null -frames 0 -v | grep aid | cut -d " " -f 2,3,4,5,6,7,8,9,10,11,12`

echo "$VIDEO_DISPLAY" > "$NFO_LOG" 
echo "$SPACE " >> "$NFO_LOG" 

echo "The longest title is $TITLE_PLAY  and is  $TITLE_LENGTH long"  >> "$NFO_LOG" 
echo "$SPACE " >> "$NFO_LOG" 

echo "$AUDIO_DISPLAY"  >> "$NFO_LOG"
echo "$SPACE " >> "$NFO_LOG" 

# Feed NFO Logfile
cat $NFO_LOG 2>> $PROCESS_LOG 1>> $PROCESS_LOG

#Display content of DVD to console
clear
echo -e "DVRequant v${VERSION}"
echo -e "You may modify $CONFIG_FILE as needed"
echo "DVD content is:"
echo " "
cat $NFO_LOG
echo " " 

#Clear content from log file
echo "$SPACE"  > "$NFO_LOG"

# Ask user what title he wants to rip
echo -n "WHAT TITLE DO YOU WANT TO RIP? (Default is title $TITLE_PLAY)>"
     
read -e TITLE_NUM
if [[ -z $TITLE_NUM  ]]; then  TITLE_NUM=$TITLE_PLAY  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to title $TITLE_PLAY"
fi
if [ $TITLE_NUM -lt "0"  ]; then  TITLE_NUM=$TITLE_PLAY  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to title $TITLE_PLAY"
fi
 
#audio stream sub-section
echo -n "HOW MANY AUDIO TRACKS DO YOU WANT ?(Max.2, default is 1)>"
read AUD_NUMBER
#Default
if [[ -z $AUD_NUMBER ]]; then  AUD_NUMBER="1"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to 1 audio track"
fi
if [ $AUD_NUMBER -gt "2"  ]; then  AUD_NUMBER="1"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to 1 audio track"
fi
 
CHAPTER_START_TIMES=$( get_chapters $TITLE_NUM )
 
#Rip selected audio tracks and then video stream
echo     
echo -n "AID code for track #1 (Default 128)>"
read -e TRACKA
if [[ -z $TRACKA  ]]; then  TRACKA="128"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to AID 128"
fi
if [ $TRACKA -lt "128"  ]; then  TRACKA="128"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to AID 128"
fi

#To prevent use of old files
if [ "$AUD_NUMBER" = "1" ]; then rm $WORKING_DIR/$DISK_TITLE/langb.ac3  2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi
#Choice of 2 tracks
if [ "$AUD_NUMBER" = "2" ]; then 
echo -n  "AID code for track #2 (Default 129)>"
read -e TRACKB
if [[ -z $TRACKB  ]]; then  TRACKB="129"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to AID 129"
fi
if [ $TRACKB -lt "128"  ]; then  TRACKB="129"  2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "Defaulting to AID 129"
fi

echo "Ripping audio AID $TRACKB...Wait..."
mplayer -dvd-device $DVD_DEVICE dvd://$TITLE_NUM -dumpaudio -aid $TRACKB -dumpfile $WORKING_DIR/$DISK_TITLE/langb.ac3  2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

echo "Ripping audio AID $TRACKA...Wait..."

mplayer -dvd-device $DVD_DEVICE dvd://$TITLE_NUM -dumpaudio -aid $TRACKA -dumpfile $WORKING_DIR/$DISK_TITLE/langa.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG

echo " "
echo "Title $TITLE_NUM now being ripped...Wait..."
echo " "

mplayer -dvd-device $DVD_DEVICE dvd://$TITLE_NUM -dumpvideo -dumpfile $WORKING_DIR/$DISK_TITLE/$VIDEO_OUTPUT 2>> $PROCESS_LOG 1>> $PROCESS_LOG

# Calculate requant factor      
#requant_factor = (video_size / (4700000000 - audio_size)) * 1.04

# If you are including more than one audio stream or a subtitle stream, those   
# filesizes must also be subtracted from the maximum dvd image size.
echo "Calculating factor..."
echo "The closer to 1.00 the better"
echo " "

#Move to work folder
cd $WORKING_DIR/$DISK_TITLE

VIDEO_SIZE=`du -b $VIDEO_OUTPUT  | cut -c 1-10`  2>> $PROCESS_LOG 1>> $PROCESS_LOG
AUDIOA=`du -b langa.ac3 | cut -c 1-9` 2>> $PROCESS_LOG 1>> $PROCESS_LOG

if [ "$AUD_NUMBER" = "2" ]; then 
AUDIOB=`du -b langb.ac3 | cut -c 1-9` 2>> $PROCESS_LOG 1>> $PROCESS_LOG
SPACE_AVAILABLE=$((4700000000-($AUDIOA+$AUDIOB))) 2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

if [ "$AUD_NUMBER" = "1" ]; then
SPACE_AVAILABLE=$((4700000000-$AUDIOA)) 2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi
 
RATIO=$(echo "scale=2; $VIDEO_SIZE/$SPACE_AVAILABLE" | bc) 2>> $PROCESS_LOG 1>> $PROCESS_LOG

QUANT_FACTOR=$(echo "scale=2; $RATIO*1.05" | bc) 2>> $PROCESS_LOG 1>> $PROCESS_LOG

echo "Requant factor :"  "$QUANT_FACTOR"
echo " "

#========================================================================    
# Requantize it, if necessary:

if [[ $( echo "$QUANT_FACTOR > 1.00" | bc ) == "1" ]]; then

echo "Requantizing..."
echo " "
tcrequant -d2 -i $VIDEO_OUTPUT  -o $VIDEO_SHRUNK -f $QUANT_FACTOR 2>> $PROCESS_LOG 1>> $PROCESS_LOG

# Cleaning....  
rm $VIDEO_OUTPUT 
else
echo "No requantization necessary. Skipping."
mv $VIDEO_OUTPUT  $VIDEO_SHRUNK
fi

#========================================================================
# Remultiplex:
# *** If you experience problems with mplex splitting ouput files, uncomment the tcmplex commands below and comment out the mplex ones.
echo "Multiplexing..."
echo " "

if [ "$AUD_NUMBER" = "" ]; then
mplex -f 8 -o final.mpg $VIDEO_SHRUNK langa.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG
#tcmplex -o final.mpg -i $VIDEO_SHRUNK -p langa.ac3 -m d 2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

if [ "$AUD_NUMBER" = "1" ]; then
mplex -f 8 -o final.mpg $VIDEO_SHRUNK langa.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG
#tcmplex -o final.mpg -i $VIDEO_SHRUNK -p langa.ac3 -m d 2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

if [ "$AUD_NUMBER" = "2" ]; then
mplex -f 8 -o final.mpg $VIDEO_SHRUNK langa.ac3 langb.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG
#tcmplex -o final.mpg -i $VIDEO_SHRUNK -p langa.ac3 -s langb.ac3 -m d  2>> $PROCESS_LOG 1>> $PROCESS_LOG
fi

# Cleaning up  *** If you want to keep the audio and video streams comment out the 3 lines below.
rm langa.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG
rm langb.ac3 2>> $PROCESS_LOG 1>> $PROCESS_LOG
rm $VIDEO_SHRUNK  2>> $PROCESS_LOG 1>> $PROCESS_LOG

#To prevent use of old files
rm *.iso 2>> $PROCESS_LOG 1>> $PROCESS_LOG
rmdir dv_dvd 2>> $PROCESS_LOG 1>> $PROCESS_LOG

#========================================================================     
# Re-author it
# This will create a folder named "dv_dvd" and generate inside it
# a dvd structure -- VIDEO_TS and AUDIO_TS

echo "FINALIZING:"
echo -n "Authoring dvd: "
# Populate filesystem
dvdauthor  -t  -o  dv_dvd  -c $CHAPTER_START_TIMES final.mpg 2>> $PROCESS_LOG 1>> $PROCESS_LOG
	   
# Create IFO files
dvdauthor -o dv_dvd -T 2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "DONE!  "

#futher cleaning
rm final.mpg 2>> $PROCESS_LOG 1>> $PROCESS_LOG

cd $WORKING_DIR/$DISK_TITLE
echo -n "Making .iso: "   
# Create DVD Video compliant ISO image
mkisofs -dvd-video -udf -V $DISK_TITLE -o $DISK_TITLE.iso "$WORKING_DIR/$DISK_TITLE/dv_dvd" 2>> $PROCESS_LOG 1>> $PROCESS_LOG
echo "DONE!  "
#Copy the process log over to work folder
cp $PROCESS_LOG $WORKING_DIR/$DISK_TITLE/dvrequant_process.log

#========================================================================       
# End messages

echo "You may consult the log file:$PROCESS_LOG"
echo " "
echo "BURNING:"
echo "Use to burn image: growisofs -dvd-compat -Z $DVD_DEVICE=$DISK_TITLE.iso "
echo "Insert blank dvd and press ENTER"
read BURN
cd $WORKING_DIR/$DISK_TITLE
growisofs -dvd-compat -Z $DVD_DEVICE=$DISK_TITLE.iso 

exit



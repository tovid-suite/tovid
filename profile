#!/bin/sh
 
# profile
# A script that profiles a given input video with mpeg2enc. Multiple tests
# are run with different encoder flags and statistics on output file size 
# and encoding times are taken.
#
# Hard coded variables allow the output files to be kept or a specific
# frame to be captured from the output files, or both! Also, the Peak
# Signal to Noise Ratio may be calculated. Please set up your profile
# by changing the values of the variables under VARIABLES (not CONSTANTS).
#
# Please see the discussion on the tovid forums for further details:
# http://www.createphpbb.com/phpbb/viewtopic.php?p=462&mforum=tovid#462
#
# Usage:
#
# $ profile video.avi
#
# Pass profile a video file, and go get some coffee (and maybe a good book).
#
# TO-DO:
# (1) Adapt for long movies: allow inpoints and outpoints

# Copyright (C) 2005 Joe Friedrichsen <pengi.films@gmail.com>
# Original script pieces by Eric Pierce.
# Modified on 2005 September 23.
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 
 
# ******************************************************************************
# ******************************************************************************
#
#
# CONSTANTS
#
#
# ******************************************************************************
# ******************************************************************************
 
# Base format: 4:3 29.97fps NTSC DVD
MP2_FIXED="-a 2 -n n -f 8 -F 4"
 
PROFILE_HOME=$HOME/.tovid
LOGFILE=$PROFILE_HOME/profile.stats
ERROR_LOG=$PROFILE_HOME/profile.err
ENC_LOG=/dev/null

MPLAYER_OPTS="-benchmark -nosound -noframedrop -noautosub -vo yuv4mpeg -vf scale=720:480"
 
# A counter for data points collected during the test. Initialize.
DATA_POINTS=0

# Flags for data processing the control test (see post_test)
VARIABLE_TEST=0
CONTROL_TEST=1

# Count how many times the control test has happened
CONTROL_ITER=0

# List of PIDS to kill on exit
PIDS=""

 
 
 
# ******************************************************************************
# ******************************************************************************
#
#
# VARIABLES
#
#
# ******************************************************************************
# ******************************************************************************
 
# If an option has a range, the syntax is:
# [option] [min] [max] [step]
# [step] may be a decimal as long as [max] has the same number of decimal points
#        eg "-N 0 2.0 0.4" is OK, while
#           "-N 0 2   0.4" is not.
# Comment out a test to not run that test.
TEST_R="-R 0 2 1"
TEST_E="-E -40 40 5"
TEST_r="-r 8 32 8"
TEST_D="-D 9 10 1"
TEST_bq="-b 800 9800 500 -q 1 18 1"
TEST_42="-4 1 4 1 -2 1 4 1"
TEST_QX="-Q 0 5 1 -X 0 1000 100"
TEST_H="-H"
TEST_s="-s"
TEST_p="-p"
TEST_c="-c"
TEST_Gg="-G 2 24 2 -g 2 24 2"
TEST_N="-N 0 2.0 0.4"
 
# How many frames should mplayer send to mpeg2enc?
# To encode the entire input file, comment these lines, or set the the number of
# frames to more than the frames in the input file.
# 450 frames play just longer than 15sec (NTSC) or 18sec (PAL)
LAST_FRAME=450
MPLAYER_FRAMES="-frames $LAST_FRAME"

# Keep the movies mpeg2enc creates? [:|false]
# The script leaves the movies in the same directory from which it was called.
KEEP_OUTFILES=false
 
# Take a frame from each test? [:|false]
# If so, which one? (be sure it's less than either the number of frames mplayer sends
#   to mpeg2enc, above, or the amount of frames in the entire input file).
# The script leaves the snap shots in the same directory from which it was called.
TAKE_SNAP=false
FRAME=400

# Find the Peak Signal to Noise Ratio? [:|false]
# If so, where should frames (in ppm format) be dropped? (they will be removed at the end)
#        where should the frame-by-frame PSNR log be dropped?
#        how many frames should be compared? (comment for all. NOTE: each frame is about 1MB)
FIND_PSNR=false
PSNR_CONT_DIR=$PROFILE_HOME/psnr-control
PSNR_COMP_DIR=$PROFILE_HOME/psnr-compare
PSNR_FRAME_LOG=$PROFILE_HOME/profile.psnr
PSNR_FRAMES="-frames 60"

# Set-up mplayer output format for PSNR
CONT_PNM="pnm:outdir=$PSNR_CONT_DIR"
COMP_PNM="pnm:outdir=$PSNR_COMP_DIR"
 
 
 

# ******************************************************************************
# ******************************************************************************
#
#
# FUNCTIONS
#
#
# ******************************************************************************
# ******************************************************************************

# Trap Ctrl-C and TERM to clean up child processes
trap 'killsubprocs; exit 13' TERM INT
 
# ******************************************************************************
# Kill child processes
# ******************************************************************************
killsubprocs()
{
    echo
    echo "Profile stopped, killing all sub-processes"
    eval "kill $PIDS"
    rm_output
    clean_up
}    

# ******************************************************************************
# Set up the profile
# Args: $@ = command line arguments
# ******************************************************************************
set_up()
{
    # Basic sanity checks
    # One and only one input argument ok
    if test $# -ne 1; then
       echo "Usage: profile [infile]"
       echo "e.g.   profile render.avi"
       exit 1
    fi
 
    INFILE="$1"

    # Does the file exist?
    if test -e "$INFILE"; then
       :
    else
       echo "Could not find infile: $INFILE. Exiting."
       exit 1
    fi
 
    SCRIPT_START=`date +%c`
 
    # Gather input video file information
    FILE_ID=`md5sum $INFILE`
    PIDS="$PIDS $!"
    
    VID_SPECS=`mplayer -vo null -ao null -frames 1 -identify "$INFILE" 2>$ERROR_LOG | grep -A 12 ID_FILENAME`     
    
    # Find the length of the video to test    
    if test -z $LAST_FRAME; then
       DURATION=`echo "$VID_SPECS" | grep "LENGTH" | awk -F '=' '{ print $2 }'`
    else
       FPS=`echo "$VID_SPECS" | grep "FPS" | awk -F '=' '{ print $2 }'`
       DURATION=`echo "scale=2; $LAST_FRAME/$FPS" | bc -l`
    fi
    
    echo "md5sum:            $FILE_ID"
    echo "Video Duration:    $DURATION sec"
    echo "mpeg2enc baseline: $MP2_FIXED"
    echo
    
    # Put a new header in the data log
    touch "$LOGFILE"
    echo "\"Profile time:\",       \"$SCRIPT_START\""  >> "$LOGFILE"
    echo "\"md5sum:\",             \"$FILE_ID\"" >> "$LOGFILE"
    echo "\"Test baseline:\",      \"mpeg2enc $MP2_FIXED\"" >> "$LOGFILE"
    echo  >> "$LOGFILE"
    echo "\"Profile Parameters:\"" >> "$LOGFILE"
    echo "                    \"$TEST_R\"" >> "$LOGFILE"
    echo "                    \"$TEST_E\"" >> "$LOGFILE"
    echo "                    \"$TEST_r\"" >> "$LOGFILE"
    echo "                    \"$TEST_D\"" >> "$LOGFILE"
    echo "                    \"$TEST_bq\"" >> "$LOGFILE"
    echo "                    \"$TEST_42\"" >> "$LOGFILE"
    echo "                    \"$TEST_QX\"" >> "$LOGFILE"
    echo "                    \"$TEST_H\"" >> "$LOGFILE"
    echo "                    \"$TEST_s\"" >> "$LOGFILE"
    echo "                    \"$TEST_p\"" >> "$LOGFILE"
    echo "                    \"$TEST_c\"" >> "$LOGFILE"
    echo "                    \"$TEST_Gg\"" >> "$LOGFILE"
    echo "                    \"$TEST_N\"" >> "$LOGFILE"
    echo >> "$LOGFILE"
            
    # Logfile headers for data columns
    echo "\"Option 1\", \"Option 1 Value\", \"Option 2\", \"Option 2 Value\", \"Video Duration (s)\", \"Encoding time (s)\", \"Output size (kB)\", \"Time Multiplier\", \"Output Bitrate (kbps)\", \"Normalized Time (%)\", \"Normalized Bitrate (%)\", \"PSNR (dB)\"" >> "$LOGFILE"
    # Put a new header in the error log
    touch "$ERROR_LOG"
    echo "Profile time:       $SCRIPT_START"  >> "$ERROR_LOG"
    echo "md5sum:             $FILE_ID" >> "$ERROR_LOG"
    echo "Test baseline:      mpeg2enc $MP2_FIXED" >> "$ERROR_LOG"
    echo  >> "$ERROR_LOG"  
    
    # Put a new header in the encoding log
    touch "$ENC_LOG"
    echo "Profile time:       $SCRIPT_START"  >> "$ENC_LOG"
    echo "md5sum:             $FILE_ID" >> "$ENC_LOG"
    echo "Test baseline:      mpeg2enc $MP2_FIXED" >> "$ENC_LOG"
    echo  >> "$ENC_LOG"  
    
    # Prepare for PSNR
    if $FIND_PSNR; then
       mkdir $PSNR_CONT_DIR
       mkdir $PSNR_COMP_DIR
    fi
}
 
# ******************************************************************************
# Run the control test, only the base parameters
# Args: $1 is the unique output file name identifier for the control file
# ******************************************************************************
control()
{
  CONTROL_ID="$1"
  CONTROL_ITER=`expr $CONTROL_ITER + 1`
  CONTROL_PSNR="CONTROL $CONTROL_ITER"
 
  pre_test
    
  OUTFILE="control_${CONTROL_ID}"
  CMD="$MP2_FIXED -o $OUTFILE.mpg"
  
  encode
  
  # Things to do on first control test only:
  # Find the base control figures (bitrate and encoding time)
  if test $CONTROL_ITER -eq 1; then
     post_test $CONTROL_TEST
     
       # Make frames if finding the PSNR
       if $FIND_PSNR; then
          mplayer -nosound -benchmark -noframedrop -noautosub $PSNR_FRAMES -vo $CONT_PNM "$OUTFILE.mpg" >> "$ENC_LOG" 2>&1
       fi
  else 
     post_test $VARIABLE_TEST
     CONTROL_PSNR=`calc_psnr`
  fi
  
  snap_shot    
  rm_output
  
  echo "\"CONTROL $CONTROL_ITER\", \"CONTROL $CONTROL_ITER\", \"CONTROL $CONTROL_ITER\", \"CONTROL $CONTROL_ITER\", \"$DURATION\", \"$TOT_TIME\", \"$FINAL_SIZE\", \"$TIME_MULT\", \"$BITRATE\", \"$NORM_TIME\", \"$NORM_BITR\", \"$CONTROL_PSNR\"" >> "$LOGFILE"
}
 
# ******************************************************************************
# Run a test on an option that takes an integer value
# Args: $1 $2 $3 $4 = [option] [min] [max] [step]
# ******************************************************************************
range_test()
{
  TEST_OPT=$1
  VAR=$2
  TEST_MAX=$3
  STEP=$4
 
  while :
  do
    pre_test
    
    OUTFILE="profiler_${TEST_OPT}_${VAR}"
    CMD="$MP2_FIXED $TEST_OPT $VAR -o $OUTFILE.mpg"
    
    encode
    post_test $VARIABLE_TEST
    PSNR=`calc_psnr`
    snap_shot
    rm_output
 
    echo "\"null\", \"null\", \"$TEST_OPT\", \"$VAR\", \"$DURATION\", \"$TOT_TIME\", \"$FINAL_SIZE\", \"$TIME_MULT\", \"$BITRATE\", \"$NORM_TIME\", \"$NORM_BITR\", \"$PSNR\"" >> "$LOGFILE"
    
    if test $VAR = $TEST_MAX; then
       break
    fi

    VAR=`echo "$VAR + $STEP" | bc -l`
  done
}
 
# ******************************************************************************
# Run a test on two options that take integer values
# Args: $1 $2 $3 $4 \ = [option1] [min1] [max1] [step1] \
#       $5 $6 $7 $8   = [option2] [min2] [max2] [step2]
# ******************************************************************************
dual_range()
{
  TEST_OPT1=$1
  TEST_MIN1=$2
  TEST_MAX1=$3
  STEP1=$4
  
  TEST_OPT2=$5
  TEST_MIN2=$6
  TEST_MAX2=$7
  STEP2=$8
  
  VAR1=$TEST_MIN1
  VAR2=$TEST_MIN2
  
  while :
  do
    
    while :
    do
      pre_test
      
      OUTFILE="profiler_${TEST_OPT1}_${VAR1}_${TEST_OPT2}_${VAR2}"
      CMD="$MP2_FIXED $TEST_OPT1 $VAR1 $TEST_OPT2 $VAR2 -o $OUTFILE.mpg"
      
      encode
      post_test $VARIABLE_TEST
      PSNR=`calc_psnr`
      snap_shot
      rm_output
      
      echo "\"$TEST_OPT1\", \"$VAR1\", \"$TEST_OPT2\", \"$VAR2\", \"$DURATION\", \"$TOT_TIME\", \"$FINAL_SIZE\", \"$TIME_MULT\", \"$BITRATE\", \"$NORM_TIME\", \"$NORM_BITR\", \"$PSNR\"" >> "$LOGFILE"
     
      if test $VAR2 = $TEST_MAX2; then
         break
      fi
      
      VAR2=`echo "$VAR2 + $STEP2" | bc -l`
    done
      
    VAR2=$TEST_MIN2
    
    if test $VAR1 = $TEST_MAX1; then
       break
    fi
    
    VAR1=`echo "$VAR1 + $STEP1" | bc -l`
  done
}
 
# ******************************************************************************
# Run a test on an option that is only a flag (takes no value)
# Args: $1 = [option]
# ******************************************************************************
flag_test()
{
  FLAG=$1
 
  pre_test
  
  OUTFILE="profiler_${FLAG}"
  CMD="$MP2_FIXED $FLAG -o $OUTFILE.mpg"
  
  encode
  post_test $VARIABLE_TEST
  PSNR=`calc_psnr`
  snap_shot
  rm_output
 
  echo "\"null\", \"null\", \"$FLAG\", \"null\", \"$DURATION\", \"$TOT_TIME\", \"$FINAL_SIZE\", \"$TIME_MULT\", \"$BITRATE\", \"$NORM_TIME\", \"$NORM_BITR\", \"$PSNR\"" >> "$LOGFILE"
}
 
# ******************************************************************************
# Run a test on two options that take integer values, and where one option must
# always be greater than or equal to the other
# Args: $1 $2 $3 $4 \ = [option1] [min1] [max1] [step1] \
#       $5 $6 $7 $8     [option2] [min2] [max2] [step2]
# In this function, option1 >= option2 (G >= g).
# ******************************************************************************
G_g_test()
{
  TEST_OPT1=$1
  TEST_MIN1=$2
  TEST_MAX1=$3
  STEP1=$4
  
  TEST_OPT2=$5
  TEST_MIN2=$6
  TEST_MAX2=$7
  STEP2=$8
  
  VAR1=$TEST_MIN1
  VAR2=$TEST_MIN2
 
  while test $VAR1 -le $TEST_MAX1; do
    
    while test $VAR2 -le $VAR1; do
      pre_test
      
      OUTFILE="profiler_${TEST_OPT1}_${VAR1}_${TEST_OPT2}_${VAR2}"
      CMD="$MP2_FIXED $TEST_OPT1 $VAR1 $TEST_OPT2 $VAR2 -o $OUTFILE.mpg"
      
      encode
      post_test $VARIABLE_TEST
      PSNR=`calc_psnr`
      snap_shot
      rm_output
      
      echo "\"$TEST_OPT1\", \"$VAR1\",  \"$TEST_OPT2\", \"$VAR2\", \"$DURATION\", \"$TOT_TIME\", \"$FINAL_SIZE\", \"$TIME_MULT\", \"$BITRATE\", \"$NORM_TIME\", \"$NORM_BITR\", \"$PSNR\"" >> "$LOGFILE"
 
      VAR2=`expr $VAR2 + $STEP2`
    done
    
    VAR2=$TEST_MIN2
    VAR1=`expr $VAR1 + $STEP1`
  done
}
 

# ******************************************************************************
# Clean up the profile
# 
# ******************************************************************************
clean_up()
{
  # Remove frames (and directories) if finding the PSNR
  if $FIND_PSNR; then
     rm -f $PSNR_CONT_DIR/*.ppm
     rmdir $PSNR_CONT_DIR
     rm -f $PSNR_COMP_DIR/*.ppm
     rmdir $PSNR_COMP_DIR
  fi

  rm -f stream.yuv
  echo  >> "$LOGFILE"
  echo  >> "$LOGFILE"
  
  echo  >> "$ERROR_LOG"
  echo  >> "$ERROR_LOG"
  
  echo  >> "$ENC_LOG"
  echo  >> "$ENC_LOG"
}  
  
# ******************************************************************************
# Print a summary of the profile
# 
# ******************************************************************************
print_summary()
{
  SCRIPT_END=`date +%c`
  echo
  echo
  echo "All finished profiling $INFILE with mpeg2enc."
  echo "You have $DATA_POINTS new data points!"
  if $KEEP_OUTFILES; then
  echo "And output movies!"
  fi
  if $TAKE_SNAP; then
  echo "And output stills!"
  fi
  echo "I started on       $SCRIPT_START"
  echo "and finished on    $SCRIPT_END."
  echo
}
 
# ******************************************************************************
# Clean up before running an encoding test.
# Make note of the start time.
# ******************************************************************************
pre_test()
{
  rm -f stream.yuv >> "$ERROR_LOG" 2>&1
  mkfifo stream.yuv >> "$ERROR_LOG" 2>&1

  START_TIME=`date +%s`
}
 
# ******************************************************************************
# Encode the video.
# 
# ******************************************************************************
encode()
{
  printf '%-80s\r' "Testing $CMD"
  mplayer $MPLAYER_OPTS $MPLAYER_FRAMES "$INFILE" >> "$ENC_LOG" 2>&1 &
  PIDS="$PIDS $!"
  cat stream.yuv | mpeg2enc $CMD >> "$ENC_LOG" 2>&1
  PIDS="$PIDS $!"
  wait
}
 
# ******************************************************************************
# Clean up after running an encoding test.
# Make note of the encoding time and output file's size.
# ******************************************************************************
post_test()
{
  # Prepare output stats for the log
  END_TIME=`date +%s`
  TOT_TIME=`echo "scale=2; $END_TIME-$START_TIME" | bc -l`
  FINAL_SIZE=`du -k "$OUTFILE.mpg" | awk '{print $1}'`
  TIME_MULT=`echo "scale=2; $TOT_TIME/$DURATION" | bc -l`
  BITRATE=`echo "scale=0; 8*$FINAL_SIZE/$DURATION" | bc -l`

  if test $1 -eq $CONTROL_TEST
  then
    CONT_TIME=$TOT_TIME
    CONT_BITR=$BITRATE
  fi    
  
  NORM_TIME=`echo "scale=2; ((100*$TOT_TIME/$CONT_TIME)-100)" | bc -l`
  NORM_BITR=`echo "scale=2; ((100*$BITRATE/$CONT_BITR)-100)" | bc -l`
  
  DATA_POINTS=`expr $DATA_POINTS + 1`
}
 
# ******************************************************************************
# Take a snap-shot of a movie.
# 
# ******************************************************************************
snap_shot()
{
  if $TAKE_SNAP; then
      mplayer -vo png -frames `expr $FRAME + 1` "$OUTFILE.mpg" >> "$ENC_LOG" 2>&1
      PIDS="$PIDS $!"
      sleep 2
      mv 0*$FRAME.png "frame-$FRAME-$OUTFILE.png" >> "$ERROR_LOG" 2>&1
      rm -f 0*.png >> "$ERROR_LOG" 2>&1
  fi
}
 
# ******************************************************************************
# Take a snap-shot of a movie.
# 
# ******************************************************************************
calc_psnr()
{
  if $FIND_PSNR; then
     mplayer -nosound -benchmark -noframedrop -noautosub $PSNR_FRAMES -vo $COMP_PNM "$OUTFILE.mpg" >> "$ENC_LOG" 2>&1
     PIDS="$PIDS $!"
     echo "`psnrcore \"$PSNR_CONT_DIR\" \"$PSNR_COMP_DIR\" \"$PSNR_FRAME_LOG\"`"
     PIDS="$PIDS $!"
  else
     echo "not measured"
  fi
}

# ******************************************************************************
# Clean up the encoded movie.
# 
# ******************************************************************************
rm_output()
{
  if $KEEP_OUTFILES; then
      :
  else
      rm -f "$OUTFILE.mpg" >> "$ERROR_LOG" 2>&1
  fi
}
 
 
 
 
# ******************************************************************************
# ******************************************************************************
#
#
# MAIN
#
#
# ******************************************************************************
# ******************************************************************************
 
set_up "$@"
control start
if test -n "$TEST_R";  then range_test $TEST_R;  fi
if test -n "$TEST_E";  then range_test $TEST_E;  fi
if test -n "$TEST_r";  then range_test $TEST_r;  fi
if test -n "$TEST_D";  then range_test $TEST_D;  fi
if test -n "$TEST_bp"; then dual_range $TEST_bq; fi
if test -n "$TEST_42"; then dual_range $TEST_42; fi
if test -n "$TEST_QX"; then dual_range $TEST_QX; fi
if test -n "$TEST_H";  then flag_test  $TEST_H;  fi
if test -n "$TEST_s";  then flag_test  $TEST_s;  fi
if test -n "$TEST_p";  then flag_test  $TEST_p;  fi
if test -n "$TEST_c";  then flag_test  $TEST_c;  fi
if test -n "$TEST_Gg"; then G_g_test   $TEST_Gg; fi
if test -n "$TEST_N";  then range_test $TEST_N;  fi
control end
clean_up
print_summary
 
exit 0

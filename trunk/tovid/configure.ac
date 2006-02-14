# Process this file with autoconf to produce a configure script.
# Autoconf documentation:
#     http://www.gnu.org/software/autoconf/manual/index.html

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
# INIT
#
#
# ******************************************************************************
# ******************************************************************************

# The first arugment sets the package name, the second sets the package version.
# eg [tovid], [0.40] would yield a tovid-0.40.tar.gz after "$ make dist"
#                    the version number is also substituted into tovid-init.sh.in
#                    and into setup.py.in
AC_INIT([tovid], [0.25])
AC_CONFIG_SRCDIR([src/tovid])

AM_INIT_AUTOMAKE




# ******************************************************************************
# ******************************************************************************
#
#
# CHECK FOR DEPENDENCIES 
#
#
# ******************************************************************************
# ******************************************************************************

# ******************************************************************************
# Required Dependencies 
# ******************************************************************************
# How to add a dependency called foo: 
#  (1) append another line to the AC_CHECK_PROG block to check for foo:
#         AC_CHECK_PROG(FOO, [foo], [ok], [MISSING])
#  (2) add another msg called foo_msg to the *_msg block 
#  (3) add another name/variable pair to REQ_DEP_LIST: foo=$FOO

AC_MSG_NOTICE([Checking for required core dependencies...])
AC_CHECK_PROG(GREP, [grep], [ok], [MISSING])
AC_CHECK_PROG(SED, [sed], [ok], [MISSING])
AC_CHECK_PROG(MD5SUM, [md5sum], [ok], [MISSING])
AC_CHECK_PROG(MPLAYER, [mplayer], [ok], [MISSING])
AC_CHECK_PROG(MENCODER, [mencoder], [ok], [MISSING])
AC_CHECK_PROG(MPLEX, [mplex], [ok], [MISSING])
AC_CHECK_PROG(MPEG2ENC, [mpeg2enc], [ok], [MISSING])
AC_CHECK_PROG(YUVFPS, [yuvfps], [ok], [MISSING])
AC_CHECK_PROG(YUVDENOISE, [yuvdenoise], [ok], [MISSING])
AC_CHECK_PROG(PPMTOY4M, [ppmtoy4m], [ok], [MISSING])
AC_CHECK_PROG(MP2ENC, [mp2enc], [ok], [MISSING])
AC_CHECK_PROG(FFMPEG, [ffmpeg], [ok], [MISSING])
AC_CHECK_PROG(SOX, [sox], [ok], [MISSING])

# ------------------------------------------------------------------------------
# Complain about missing required dependencies. If some are missing, list all
# missing ones and their _msg before failing and exiting.

grep_msg="a GNU utility (www.gnu.org/software/grep)"
sed_msg="a GNU utility (directory.fsf.org/GNU/sed.html)"
md5sum_msg="a GNU utility (www.gnu.org/software/coreutils)"
mplayer_msg="part of mplayer (www.mplayerhq.hu)"
mencoder_msg="$mplayer_msg"
mplex_msg="part of mjpegtools (mjpeg.sf.net}"
mpeg2enc_msg="$mplex_msg"
yuvfps_msg="$mplex_msg"
yuvdenoise_msg="$mplex_msg"
ppmtoy4m_msg="mplex_msg"
mp2enc_msg="mplex_msg"
ffmpeg_msg="a video encoding utility (ffmpeg.sf.net)"
sox_msg="a CLI sound utility (sox.sf.net)"

# Sneaky make-do array. 
REQ_DEP_LIST="grep=$GREP sed=$SED md5sum=$MD5SUM mplayer=$MPLAYER mencoder=$MENCODER mplex=$MPLEX mpeg2enc=$MPEG2ENC yuvfps=$YUVFPS yuvdenoise=$YUVDENOISE ppmtoy4m=$PPMTOY4M mp2enc=$MP2ENC ffmpeg=$FFMPEG sox=$SOX"

# Build a list of missing dependencies
# We can use gawk with confidence because the above
# initiation macros look for it and will exit if gawk isn't found.
FAIL=false
for DEP in $REQ_DEP_LIST; do
   NAME=`echo $DEP | gawk -F '=' '{ print $1 }'`
   FOUND=`echo $DEP | gawk -F '=' '{ print $2 }'`
   if test "x$FOUND" = "xMISSING"; then
     FAIL=:
     ERR_MSG=$`eval echo ${NAME}_msg`
     ERR_MSG=`eval echo $ERR_MSG`
     MISSING_DEPS=`echo "$MISSING_DEPS"; printf "    %-10s %s\n" "$NAME" "$ERR_MSG"`
   fi
done

# ******************************************************************************
# Optional Dependencies 
# ******************************************************************************
# Optional dependencies are grouped according to the functionality they bring
# to tovid: menu creation, DVD creation, (S)VCD creation, and post-processing.
# Each catagory is broken into three steps. 
# To add a new catagory, follow this pattern:
#  (1) test for the dependency
#  (2) define a message given to the user when a specific dep isn't found
#  (3) set the build option if all deps in the catagory were found, else warn.

# To add a new depedency called bar inside a catagory:
#  (1) append another line to the AC_CHECK_PROG block to check for bar:
#         AC_CHECK_PROG(BAR, [bar], [ok], [MISSING])
#  (2) add another msg called bar_msg to the *_msg block 
#  (3) add another test to the catagory's build option:
#         test "x$FOO" = "xok"
#  (4) add another name/variable pair to OPT_DEP_LIST: bar=$BAR

AC_MSG_NOTICE([Checking for optional dependencies...])

# ------------------------------------------------------------------------------
# ImageMagick components
AC_MSG_NOTICE([Checking for ImageMagick...])
AC_CHECK_PROG(COMPOSITE, [composite], [ok], [MISSING])
AC_CHECK_PROG(CONVERT, [convert], [ok], [MISSING])

# Disabled messages given to user in the FINAL SUMMARY when a dependency cannot
# be found.
composite_msg="part of ImageMagick (www.imagemagick.org)"
convert_msg="$composite_msg"

# Set the build option if all dependencies were found
if test "x$COMPOSITE" = "xok" && \
   test "x$CONVERT" = "xok"
then
   HAVE_MAGICK="magick"
else
   HAVE_MAGICK=""
   AC_MSG_WARN([Cannot find ImageMagick! You cannot use makemenu or makeslides.])
fi

# ------------------------------------------------------------------------------
# dvdauthor compononets
# (note: growisofs and mkisofs are NOT distributed with dvdauthor, but for tovid's
# purposes, it fits in the same catagory, as it burns DVDs!)
AC_MSG_NOTICE([Checking for dvd tools...])
AC_CHECK_PROG(SPUMUX, [spumux], [ok], [MISSING])
AC_CHECK_PROG(DVDAUTHOR, [dvdauthor], [ok], [MISSING])
AC_CHECK_PROG(GROWISOFS, [growisofs], [ok], [MISSING])
AC_CHECK_PROG(MKISOFS, [mkisofs], [ok], [MISSING])

spumux_msg="part of dvdauthor (dvdauthor.sf.net)"
dvdauthor_msg="$spumux_msg"
growisofs_msg="part of dvd+rw-tools: (fy.chalmers.se/~appro/linux/DVD+RW)"
mkisofs_msg="part of cdrecord (cdrecord.berlios.de)"

if test "x$SPUMUX" = "xok" && \
   test "x$DVDAUTHOR" = "xok" && \
   test "x$GROWISOFS" = "xok" && \
   test "x$MKISOFS" = "xok"
then
   HAVE_DVD="dvd"
else
   HAVE_DVD=""
   AC_MSG_WARN([Cannot find dvd authoring tools! You cannot burn DVDs.])
fi

# ------------------------------------------------------------------------------
# vcdimager components
# (note: cdrdao is NOT distributed with vcdimager, but for tovid's
# purposes, it fits in the same catagory, as it burns (S)VCDs!)
AC_MSG_NOTICE([Checking for vcd tools...])
AC_CHECK_PROG(VCDXBUILD, [vcdxbuild], [ok], [MISSING])
AC_CHECK_PROG(CDRDAO, [cdrdao], [ok], [MISSING])

vcdxbuild_msg="part of vcdimager (www.vcdimager.org)"
cdrdao_msg="$mkisofs_msg"

if test "x$VCDXBUILD" = "xok" && \
   test "x$CDRDAO" = "xok"
then
   HAVE_VCD="vcd"
else
   HAVE_VCD=""
   AC_MSG_WARN([Cannot find vcdimager! You cannot burn (S)VCDs.])
fi

# ------------------------------------------------------------------------------
# transcode components
AC_MSG_NOTICE([Checking for transcode...])
AC_CHECK_PROG(TCPROBE, [tcprobe], [ok], [MISSING])
AC_CHECK_PROG(TCREQUANT, [tcrequant], [ok], [MISSING])

tcprobe_msg="part of transcode (www.transcoding.org)"
tcrequant_msg="$tcprobe_msg"

if test "x$TCPROBE" = "xok" && \
   test "x$TCREQUANT" = "xok"
then   
   HAVE_TRANSCODE="transcode"
else
   HAVE_TRANSCODE=""
   AC_MSG_WARN([Cannot find transcode! You cannot use postproc.])
fi

if test x$HAVE_MAGICK = "xmagick" && \
   test x$HAVE_DVD = "xdvd" && \
   test x$HAVE_VCD = "xvcd" && \
   test x$HAVE_TRANSCODE = "xtranscode"
then
   OPT_DEPENDENCIES="ALL FOUND"
else
   OPT_DEPENDENCIES="SOME MISSING"
fi

# ------------------------------------------------------------------------------
############### TEMP ##################
##### For now, all dependencies are required, later these will be optional and
##### this test will be removed.

# Another sneaky make-do array. 
OPT_DEP_LIST="composite=$COMPOSITE convert=$CONVERT spumux=$SPUMUX dvdauthor=$DVDAUTHOR growisofs=$GROWISOFS mkisofs=$MKISOFS vcdxbuild=$VCDXBUILD cdrdao=$CDRDAO tcprobe=$TCPROBE tcrequant=$TCREQUANT"

# Build the rest of the list of missing dependencies
for DEP in $OPT_DEP_LIST
do
   NAME=`echo $DEP | gawk -F '=' '{ print $1 }'`
   FOUND=`echo $DEP | gawk -F '=' '{ print $2 }'`
   if test "x$FOUND" = "xMISSING"; then
     FAIL=:
     ERR_MSG=$`eval echo ${NAME}_msg`
     ERR_MSG=`eval echo $ERR_MSG`
     MISSING_DEPS=`echo "$MISSING_DEPS"; printf "    %-10s %s\n" "$NAME" "$ERR_MSG"`
   else
     unset ${NAME}_msg
   fi
done

##### This belongs up with the required options when optional deps are turned on
if $FAIL; then
 AC_MSG_ERROR([

  Could not find these REQUIRED dependencies:
$MISSING_DEPS
 
  Please install the missing dependencies and ./configure again.
  Go to http://tovid.org for more help.
])
fi
############## END TEMP #################


# Build the build options string for substitution into tovid-init.sh.in
BUILD_OPTS=""
for OPT in $HAVE_DVD $HAVE_VCD $HAVE_MAGICK $HAVE_TRANSCODE
do
  if test -z $OPT; then :
  else
     BUILD_OPTS=" $OPT$BUILD_OPTS"
  fi
done
BUILD_OPTS="core$BUILD_OPTS"

# AC_SUBST(VARIABLE, [VALUE]) 
# Make VARIABLE .in file substitutable. @VARIABLE@ found inside .in files will 
# be replaced with VALUE
AC_SUBST(BUILD_OPTS)


AC_CONFIG_FILES([Makefile src/Makefile src/tovid-init.sh])
AC_OUTPUT


# ******************************************************************************
# ******************************************************************************
#
# PRETTY SUMMARY
#
# ******************************************************************************
# ******************************************************************************

AC_MSG_NOTICE([

FINAL SUMMARY

Required dependencies   ALL FOUND

Other dependencies      $OPT_DEPENDENCIES
  
  magick (needed to make menus and slideshows)
    composite:    $COMPOSITE $composite_msg
    convert:      $CONVERT $convert_msg
  
  dvd (needed to make DVD menus and burn DVDs)
    spumux:       $SPUMUX $spumux_msg
    dvdauthor:    $DVDAUTHOR $dvdauthor_msg
    growisofs:    $GROWISOFS $growisofs_msg
    mkisofs:      $MKISOFS $mkisofs_msg
    
  vcd (needed to burn (S)VCDs)
    vcdxbuild:    $VCDXBUILD $vcdxbuild_msg
    cdrdao:       $CDRDAO $cdrdao_msg
    
  transcode (needed to compress encode videos)
    tcprobe:      $TCPROBE $tcprobe_msg
    tcrequant:    $TCREQUANT $tcrequant_msg

 You may now type 'make && su -c "make install"' to compile and install tovid.
 ])

############ POST-TEMP #################
##### This message belongs in the FINAL SUMMARY once optional dependencies
##### are turned on.
# If optional dependencies are missing (MISSING), some features of the 
# tovid suite will be disabled. Please install any missing dependencies 
# and ./configure again. See www.tovid.org for links. 
 

# Process this file with autoconf to produce a configure script.

# Copyright (C) 2005 Joe Friedrichsen <friedrij@users.berlios.de>
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
# INIT
#
#
# ******************************************************************************
# ******************************************************************************

# The first arugment sets the package name, the second sets the package version.
# eg [tovid], [0.40] would yield a tovid-0.40.tar.gz after "$ make dist"
#                    the version number is also substituted into tovid-init.sh.in
AC_INIT([tovid], [svn])
AC_CONFIG_SRCDIR([src/tovid.sh])

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

# AC_MSG_CHECKING(feature-description)
# AC_MSG_RESULT(result-description)
# AC_PATH_PROG(variable, prog-to-check-for, [value-if-not-found])
# AC_CHECK_PROG(variable, prog-to-check-for, value-if-found, 
#               [value-if-not-found], [path-to-search], [reject])
# AC_MSG_WARN([problem-description])

# ******************************************************************************
# Required Dependencies 
# ******************************************************************************
AC_MSG_NOTICE([Checking for required core dependencies... (: means found)])
AC_CHECK_PROG(GREP, [grep], [:], [false])
AC_CHECK_PROG(SED, [sed], [:], [false])
AC_CHECK_PROG(MD5SUM, [md5sum], [:], [false])
AC_CHECK_PROG(MPLAYER, [mplayer], [:], [false])
AC_CHECK_PROG(MENCODER, [mencoder], [:], [false])
AC_CHECK_PROG(MPLEX, [mplex], [:], [false])
AC_CHECK_PROG(MPEG2ENC, [mpeg2enc], [:], [false])
AC_CHECK_PROG(YUVFPS, [yuvfps], [:], [false])
AC_CHECK_PROG(YUVDENOISE, [yuvdenoise], [:], [false])
AC_CHECK_PROG(PPMTOY4M, [ppmtoy4m], [:], [false])
AC_CHECK_PROG(MP2ENC, [mp2enc], [:], [false])
AC_CHECK_PROG(FFMPEG, [ffmpeg], [:], [false])
AC_CHECK_PROG(SOX, [sox], [:], [false])

################# PRE-TEMP#################
##### Un-comment this section when optional dependencies are turned on.
# Sneaky make-do array. 
#DEP_LIST="grep=$GREP sed=$SED md5sum=$MD5SUM mplayer=$MPLAYER mencoder=$MENCODER mplex=$MPLEX #mpeg2enc=$MPEG2ENC yuvfps=$YUVFPS yuvdenoise=$YUVDENOISE ppmtoy4m=$PPMTOY4M mp2enc=$MP2ENC #ffmpeg=$FFMPEG sox=$SOX"

# We can use gawk with confidence because the above
# initiation macros look for it and will exit if gawk isn't found.
#FAIL=false
#for DEP in $DEP_LIST
#do
#  NAME=`echo $DEP | gawk -F '=' '{ print $1 }'`
#  FOUND=`echo $DEP | gawk -F '=' '{ print $2 }'`
#  if $FOUND; then :
#  else
#    AC_MSG_WARN([Cannot find REQUIRED dependency: $NAME])
#    FAIL=:
#  fi
#done

#if $FAIL; then
# AC_MSG_ERROR([
#
# Could not find the above REQUIRED dependencies.
# Please install the missing dependencies and ./configure again.
# See www.tovid.org for links.
#])
#fi

# ******************************************************************************
# Optional Dependencies 
# ******************************************************************************

AC_MSG_NOTICE([Checking for optional dependencies...])

# ImageMagick components
AC_MSG_NOTICE([Checking for ImageMagick... (: means found)])
AC_CHECK_PROG(HAVE_COMPOSITE, [composite], [:], [false])
AC_CHECK_PROG(HAVE_CONVERT, [convert], [:], [false])

if $HAVE_COMPOSITE && $HAVE_CONVERT; then
   HAVE_MAGICK="magick"
   HAVE_COMPOSITE="ok"
   HAVE_CONVERT="ok"
else
   HAVE_MAGICK=""
   if $HAVE_COMPOSITE; then HAVE_COMPOSITE="ok"; else HAVE_COMPOSITE="MISSING"; fi
   if $HAVE_CONVERT; then HAVE_CONVERT="ok"; else HAVE_CONVERT="MISSING"; fi
   AC_MSG_WARN([Cannot find ImageMagick! You cannot use makemenu or mkslides.])
fi

# dvdauthor compononets
# (note: growisofs and mkisofs are NOT distributed with dvdauthor, but for tovid's
# purposes, it fits in the same catagory, as it burns DVDs!)
AC_MSG_NOTICE([Checking for dvd tools... (: means found)])
AC_CHECK_PROG(HAVE_SPUMUX, [spumux], [:], [false])
AC_CHECK_PROG(HAVE_DVDAUTHOR, [dvdauthor], [:], [false])
AC_CHECK_PROG(HAVE_GROWISOFS, [growisofs], [:], [false])
AC_CHECK_PROG(HAVE_MKISOFS, [mkisofs], [:], [false])

if $HAVE_SPUMUX && $HAVE_DVDAUTHOR && $HAVE_GROWISOFS && $HAVE_MKISOFS; then
   HAVE_DVD="dvd"
   HAVE_SPUMUX="ok"
   HAVE_DVDAUTHOR="ok"
   HAVE_GROWISOFS="ok"
   HAVE_MKISOFS="ok"
else
   HAVE_DVD=""
   if $HAVE_SPUMUX; then HAVE_SPUMUX="ok"; else HAVE_SPUMUX="MISSING"; fi
   if $HAVE_DVDAUTHOR; then HAVE_DVDAUTHOR="ok"; else HAVE_DVDAUTHOR="MISSING"; fi
   if $HAVE_GROWISOFS; then HAVE_GROWISOFS="ok"; else HAVE_GROWISOFS="MISSING"; fi
   if $HAVE_MKISOFS; then HAVE_MKISOFS="ok"; else HAVE_MKISOFS="MISSING"; fi
   AC_MSG_WARN([Cannot find dvd authoring tools! You cannot burn DVDs.])
fi

# vcdimager components
# (note: cdrdao is NOT distributed with vcdimager, but for tovid's
# purposes, it fits in the same catagory, as it burns (S)VCDs!)
AC_MSG_NOTICE([Checking for vcd tools...] (: means found))
AC_CHECK_PROG(HAVE_VCDXBUILD, [vcdxbuild], [:], [false])
AC_CHECK_PROG(HAVE_CDRDAO, [cdrdao], [:], [false])

if $HAVE_VCDXBUILD && $HAVE_CDRDAO; then
   HAVE_VCD="vcd"
   HAVE_VCDXBUILD="ok"
   HAVE_CDRDAO="ok"
else
   HAVE_VCD=""
   if $HAVE_VCDXBUILD; then HAVE_VCDXBUILD="ok"; else HAVE_VCDXBUILD="MISSING"; fi
   if $HAVE_CDRDAO; then HAVE_CDRDAO="ok"; else HAVE_CDRDAO="MISSING"; fi
   AC_MSG_WARN([Cannot find vcdimager! You cannot burn (S)VCDs.])
fi

# transcode components
AC_MSG_NOTICE([Checking for transcode... (: means found)])
AC_CHECK_PROG(HAVE_TCPROBE, [tcprobe], [:], [false])
AC_CHECK_PROG(HAVE_TCREQUANT, [tcrequant], [:], [false])

if $HAVE_TCPROBE && $HAVE_TCREQUANT; then
   HAVE_TRANSCODE="transcode"
   HAVE_TCPROBE="ok"
   HAVE_TCREQUANT="ok"
else
   HAVE_TRANSCODE=""
   if $HAVE_TCPROBE; then HAVE_TCPROBE="ok"; else HAVE_TCPROBE="MISSING"; fi
   if $HAVE_TCREQUANT; then HAVE_TCREQUANT="ok"; else HAVE_TCREQUANT="MISSING"; fi
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

############### TEMP ##################
##### For now, all dependencies are required, later these will be optional

# Sneaky make-do array. 
DEP_LIST="grep=$GREP sed=$SED md5sum=$MD5SUM mplayer=$MPLAYER mencoder=$MENCODER mplex=$MPLEX mpeg2enc=$MPEG2ENC yuvfps=$YUVFPS yuvdenoise=$YUVDENOISE ppmtoy4m=$PPMTOY4M mp2enc=$MP2ENC ffmpeg=$FFMPEG sox=$SOX"

FAIL=false
for DEP in $DEP_LIST
do
  NAME=`echo $DEP | gawk -F '=' '{ print $1 }'`
  FOUND=`echo $DEP | gawk -F '=' '{ print $2 }'`
  if $FOUND; then :
  else
    AC_MSG_WARN([Cannot find REQUIRED dependency: $NAME])
    FAIL=:
  fi
done

# Another sneaky make-do array. 
DEP_LIST="composite=$HAVE_COMPOSITE convert=$HAVE_CONVERT spumux=$HAVE_SPUMUX dvdauthor=$HAVE_DVDAUTHOR growisofs=$HAVE_GROWISOFS mkisofs=$HAVE_MKISOFS vcdxbuild=$HAVE_VCDXBUILD cdrdao=$HAVE_CDRDAO tcprobe=$HAVE_TCPROBE tcrequant=$HAVE_TCREQUANT"

##### Un-comment when optional dependencies are turned on
#FAIL=false
for DEP in $DEP_LIST
do
  NAME=`echo $DEP | gawk -F '=' '{ print $1 }'`
  FOUND=`echo $DEP | gawk -F '=' '{ print $2 }'`
  if test x$FOUND = "xok"; then :
  else
    AC_MSG_WARN([Cannot find REQUIRED dependency: $NAME])
    FAIL=:
  fi
done

if $FAIL; then
 AC_MSG_ERROR([

 Could not find the above REQUIRED dependencies.
 Please install the missing dependencies and ./configure again.
 See www.tovid.org for links.
])
fi
############## END TEMP #################


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
    composite:          $HAVE_COMPOSITE
    convert:            $HAVE_CONVERT
  
  dvd (needed to make DVD menus and burn DVDs)
    spumux:             $HAVE_SPUMUX
    dvdauthor:          $HAVE_DVDAUTHOR
    growisofs:          $HAVE_GROWISOFS
    mkisofs:            $HAVE_MKISOFS
    
  vcd (needed to burn (S)VCDs)
    vcdxbuild:          $HAVE_VCDXBUILD
    cdrdao:             $HAVE_CDRDAO
    
  transcode (needed to compress encoded videos)
    tcprobe:            $HAVE_TCPROBE
    tcrequant:          $HAVE_TCREQUANT

 You may now type 'su -c make install' to compile and install tovid.
 ])

############ POST-TEMP #################
##### This message belongs in the FINAL SUMMARY once optional dependencies
##### are turned on.
# If optional dependencies are missing (MISSING), some features of the 
# tovid suite will be disabled. Please install any missing dependencies 
# and ./configure again. See www.tovid.org for links. 
 
AC_CONFIG_FILES([Makefile src/Makefile src/tovid-init.sh])
AC_OUTPUT
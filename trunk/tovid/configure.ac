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
AC_MSG_NOTICE([Checking for required core dependencies...])
AC_PATH_PROG(GREP, [grep], [NOT FOUND])
AC_PATH_PROG(AWK, [awk], [NOT FOUND])
AC_PATH_PROG(SED, [sed], [NOT FOUND])
AC_PATH_PROG(MD5SUM, [md5sum], [NOT FOUND])
AC_PATH_PROG(MPLAYER, [mplayer], [NOT FOUND])
AC_PATH_PROG(MENCODER, [mencoder], [NOT FOUND])
AC_PATH_PROG(MPLEX, [mplex], [NOT FOUND])
AC_PATH_PROG(MPEG2ENC, [mpeg2enc], [NOT FOUND])
AC_PATH_PROG(YUVFPS, [yuvfps], [NOT FOUND])
AC_PATH_PROG(YUVDENOISE, [yuvdenoise], [NOT FOUND])
AC_PATH_PROG(PPMTOY4M, [ppmtoy4m], [NOT FOUND])
AC_PATH_PROG(MP2ENC, [mp2enc], [NOT FOUND])
AC_PATH_PROG(FFMPEG, [ffmpeg], [NOT FOUND])
AC_PATH_PROG(SOX, [sox], [NOT FOUND])

if test "$GREP" = "NOT FOUND" || \
   test "$AWK" = "NOT FOUND" || \
   test "$SED" = "NOT FOUND" || \
   test "$MD5SUM" = "NOT FOUND" || \
   test "$MPLAYER" = "NOT FOUND" || \
   test "$MENCODER" = "NOT FOUND" || \
   test "$MPLEX" = "NOT FOUND" || \
   test "$MPEG2ENC" = "NOT FOUND" || \
   test "$YUVFPS" = "NOT FOUND" || \
   test "$YUVDENOISE" = "NOT FOUND" || \
   test "$PPMTOY4M" = "NOT FOUND" || \
   test "$MP2ENC" = "NOT FOUND" || \
   test "$FFMPEG" = "NOT FOUND" || \
   test "$SOX" = "NOT FOUND"; then
        AC_MSG_ERROR([

Could not find these REQUIRED dependencies:
 
    grep:               $GREP
    awk:                $AWK
    sed:                $SED
    md5sum:             $MD5SUM
    mplayer:            $MPLAYER
    mencoder:           $MENCODER
    mplex:              $MPLEX
    mpeg2enc:           $MPEG2ENC
    yuvfps:             $YUVFPS
    yuvdenoise:         $YUVDENOISE
    ppmtoy4m:           $PPMTOY4M
    mp2enc:             $MP2ENC
    ffmpeg:             $FFMPEG
    sox:                $SOX
 
 Please install the missing (NOT FOUND) dependencies and ./configure again.
 See www.tovid.org for links.
 
])
fi

# ******************************************************************************
# Optional Dependencies 
# ******************************************************************************

AC_MSG_NOTICE([Checking for optional dependencies...])

# ImageMagick components
AC_MSG_NOTICE([Checking for ImageMagick...])
AC_CHECK_PROG(HAVE_COMPOSITE, [composite], [:], [false])
AC_CHECK_PROG(HAVE_CONVERT, [convert], [:], [false])

if $HAVE_COMPOSITE && $HAVE_CONVERT; then
   HAVE_MAGICK="magick"
   HAVE_COMPOSITE="composite"
   HAVE_CONVERT="convert"
else
   HAVE_MAGICK=""
   if $HAVE_COMPOSITE; then HAVE_COMPOSITE="composite"; else HAVE_COMPOSITE="NOT FOUND"; fi
   if $HAVE_CONVERT; then HAVE_CONVERT="convert"; else HAVE_CONVERT="NOT FOUND"; fi
   AC_MSG_WARN([Cannot find ImageMagick! You cannot use makemenu or mkslides.])
fi

# dvdauthor compononets
# (note: growisofs and mkisofs are NOT distributed with dvdauthor, but for tovid's
# purposes, it fits in the same catagory, as it burns DVDs!)
AC_MSG_NOTICE([Checking for dvd tools...])
AC_CHECK_PROG(HAVE_SPUMUX, [spumux], [:], [false])
AC_CHECK_PROG(HAVE_DVDAUTHOR, [dvdauthor], [:], [false])
AC_CHECK_PROG(HAVE_GROWISOFS, [growisofs], [:], [false])
AC_CHECK_PROG(HAVE_MKISOFS, [mkisofs], [:], [false])

if $HAVE_SPUMUX && $HAVE_DVDAUTHOR && $HAVE_GROWISOFS && $HAVE_MKISOFS; then
   HAVE_DVD="dvd"
   HAVE_SPUMUX="spumux"
   HAVE_DVDAUTHOR="dvdauthor"
   HAVE_GROWISOFS="growisofs"
   HAVE_MKISOFS="mkisofs"
else
   HAVE_DVD=""
   if $HAVE_SPUMUX; then HAVE_SPUMUX="spumux"; else HAVE_SPUMUX="NOT FOUND"; fi
   if $HAVE_DVDAUTHOR; then HAVE_DVDAUTHOR="dvdauthor"; else HAVE_DVDAUTHOR="NOT FOUND"; fi
   if $HAVE_GROWISOFS; then HAVE_GROWISOFS="growisofs"; else HAVE_GROWISOFS="NOT FOUND"; fi
   if $HAVE_MKISOFS; then HAVE_MKISOFS="mkisofs"; else HAVE_MKISOFS="NOT FOUND"; fi
   AC_MSG_WARN([Cannot find dvd authoring tools! You cannot burn DVDs.])
fi

# vcdimager components
# (note: cdrdao is NOT distributed with vcdimager, but for tovid's
# purposes, it fits in the same catagory, as it burns (S)VCDs!)
AC_MSG_NOTICE([Checking for vcd tools...])
AC_CHECK_PROG(HAVE_VCDXBUILD, [vcdxbuild], [:], [false])
AC_CHECK_PROG(HAVE_CDRDAO, [cdrdao], [:], [false])

if $HAVE_VCDXBUILD && $HAVE_CDRDAO; then
   HAVE_VCD="vcd"
   HAVE_VCDXBUILD="vcdxbuild"
   HAVE_CDRDAO="cdrdao"
else
   HAVE_VCD=""
   if $HAVE_VCDXBUILD; then HAVE_VCDXBUILD="vcdxbuild"; else HAVE_VCDXBUILD="NOT FOUND"; fi
   if $HAVE_CDRDAO; then HAVE_CDRDAO="cdrdao"; else HAVE_CDRDAO="NOT FOUND"; fi
   AC_MSG_WARN([Cannot find vcdimager! You cannot burn (S)VCDs.])
fi

# transcode components
AC_MSG_NOTICE([Checking for transcode...])
AC_CHECK_PROG(HAVE_TCPROBE, [tcprobe], [:], [false])
AC_CHECK_PROG(HAVE_TCREQUANT, [tcrequant], [:], [false])

if $HAVE_TCPROBE && $HAVE_TCREQUANT; then
   HAVE_TRANSCODE="transcode"
   HAVE_TCPROBE="tcprobe"
   HAVE_TCREQUANT="tcrequant"
else
   HAVE_TRANSCODE=""
   if $HAVE_TCPROBE; then HAVE_TCPROBE="tcprobe"; else HAVE_TCPROBE="NOT FOUND"; fi
   if $HAVE_TCREQUANT; then HAVE_TCREQUANT="tcrequant"; else HAVE_TCREQUANT="NOT FOUND"; fi
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

Optional dependencies   $OPT_DEPENDENCIES
  
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
    tcrequant           $HAVE_TCREQUANT

 If optional dependencies are missing (NOT FOUND), some features of the 
 tovid suite will be disabled. Please install any missing dependencies 
 and ./configure again. See www.tovid.org for links.
 ])

AC_CONFIG_FILES([Makefile src/Makefile src/tovid-init.sh])
AC_OUTPUT
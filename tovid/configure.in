dnl Process this file with autoconf to produce a configure script.
AC_INIT(tovid)
AM_INIT_AUTOMAKE(tovid, svn)

dnl Checks for programs.
AC_PROG_INSTALL

# check for mandatory programs
AC_CHECK_PROG( MPLAYER,     [mplayer],      "yes" )
AC_CHECK_PROG( MENCODER,    [mencoder],     "yes" )
AC_CHECK_PROG( YUVFPS,      [yuvfps],       "yes" )
AC_CHECK_PROG( MPEG2ENC,    [mpeg2enc],     "yes" )
AC_CHECK_PROG( MP2ENC,      [mp2enc],       "yes" )
AC_CHECK_PROG( MPLEX,       [mplex],        "yes" )
AC_CHECK_PROG( CONVERT,     [convert],      "yes" )
AC_CHECK_PROG( FFMPEG,      [ffmpeg],       "yes" )
AC_CHECK_PROG( DVDAUTHOR,   [dvdauthor],    "yes" )
AC_CHECK_PROG( TRANSCODE,   [transcode],    "yes" )
AC_CHECK_PROG( VCDIMAGER,   [vcdimager],    "yes" )
AC_CHECK_PROG( SOX,         [sox],          "yes" )
AC_CHECK_PROG( MKISOFS,     [mkisofs],      "yes" )
AC_CHECK_PROG( LSDVD,       [lsdvd],        "yes" )

if @<:@ -z "$MPLAYER" @:>@ || \
   @<:@ -z "$MENCODER" @:>@ || \
   @<:@ -z "$YUVFPS" @:>@ || \
   @<:@ -z "$MPEG2ENC" @:>@ || \
   @<:@ -z "$MP2ENC" @:>@ || \
   @<:@ -z "$MPLEX" @:>@ || \
   @<:@ -z "$CONVERT" @:>@ || \
   @<:@ -z "$FFMPEG" @:>@ || \
   @<:@ -z "$DVDAUTHOR" @:>@ || \
   @<:@ -z "$TRANSCODE" @:>@ || \
   @<:@ -z "$VCDIMAGER" @:>@ || \
   @<:@ -z "$SOX" @:>@ || \
   @<:@ -z "$MKISOFS" @:>@ || \
   @<:@ -z "$LSDVD" @:>@; then
    AC_MSG_ERROR([Missing some dependencies. Exiting.])
fi

AC_OUTPUT(Makefile)

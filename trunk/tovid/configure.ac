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
#                    the version number is also substituted into tovid-init.in
AC_INIT([tovid], [svn])
AC_CONFIG_SRCDIR([src/tovid])

# Require minimum versions of the autotools
AC_PREREQ(2.5)
AM_INIT_AUTOMAKE([1.9])




# ******************************************************************************
# ******************************************************************************
#
#
# CHECK FOR DEPENDENCIES 
#
#
# ******************************************************************************
# ******************************************************************************

# The only 'compile time' dependency we have is txt2tags, which is used to
# build the man pages.
AC_CHECK_PROG(TXT2TAGS, [txt2tags], [:], [false])
if ! $TXT2TAGS; then
    AC_MSG_ERROR([

 ERROR:

 txt2tags cannot be found on your system, but tovid needs it to build
 the man pages. Please install txt2tags (http://txt2tags.sf.net) and
 run ./configure again. Thanks! 
 
     -- http://tovid.org
])
fi

# All run-time dependencies are checked in tovid-init now. In addition to being
# the Correct Way to do things, it makes packaging much easier for deb|rpm|???
# maintainers.

# ******************************************************************************
# Python
# ******************************************************************************
# As seen on http://sources.redhat.com/automake/automake.html#Python
# AM_PATH_PYTHON sets many vars, including $(pythondir), which is the directory 
# name for the site-packages subdirectory of the standard Python install tree;
# and $(pyexecdir), which is the directory where Python extension modules 
# (shared libraries) should be installed.

# For example, on friedrij's debian system
# $(pythondir) = ${prefix}/lib/python2.3/site-packages
# $(pyexecdir) = ${exec_prefix}/lib/python2.3/site-packages

# From the autoconf manual, available in anything _but_ html (uf, fsf) from
# http://www.gnu.org/software/autoconf/manual/index.html
# $(prefix) is "The common installation prefix for all files. If $(exec_prefix)
# is defined to a different value, prefix is used only for architecture-
# independent files."
# $(exec_prefix) is "The installation prefix for architecture-dependent files. 
# By default it's the same as $(prefix). You should avoid installing anything
# directly to $(exec_prefix). However, the default value for directories 
# containing architecture-dependent files should be relative to $(exec_prefix)."

# The GNU Coding Standards, available in html (yosh) from
# (http://www.gnu.org/prep/standards/standards.html#Directory-Variables),
# clarifies the difference between $(prefix) and $(exec_prefix): "Generally, 
# $(exec_prefix) is used for directories that contain machine-specific files 
# (such as executables and subroutine libraries), while $(prefix) is used
# directly for other directories."

# So, this dev thinks we need $(pyexecdir) and some 'enlightened' python
# scripts, as pointed out by 
# http://sources.redhat.com/automake/automake.html#Hard_002dCoded-Install-Paths
# If you do [use $(pythondir) or $(pyexecdir)], then:
#    * root users can install your package with the same --prefix as Python (you
#      get the behavior of the previous attempt - eg /usr/lib/python-2.3/...)
#    * non-root users can install your package too, they will have the extension
#      module in a place that is not searched by Python but they can work around
#      this using environment variables (and if you installed scripts that use
#      this shared library, it's easy to tell Python were to look in the
#      beginning of your script, so the script works in both cases). 

# Using pyexecdir_PYTHON for libtovid will install it to 
# ${exec_prefix}/lib/python2.3/site-packages (for example)
# and the pytovid suite (left as bin_SCRIPTS, so that they are installed as
# executables and not byte-compiled like python_PYTHON would do) will need to be
# told how to look for libtovid.

AM_PATH_PYTHON(2.4)

# Attempt to inform user that their pyton installation won't work
#   with the default prefix (/usr/local)
USER_PYTHON_PATH=$(python -c "import sys; print sys.path")
PYTHON_LOCAL=$(echo $USER_PYTHON_PATH | awk -F ',' '{ for (f=1; f<=NF; f++) {print $f}; }' | grep local | tr -d "' ")

if test -z $PYTHON_LOCAL && test x"$prefix" == "xNONE"; then
    AC_MSG_ERROR([

    ERROR: 
    
    It looks like your python installation doesn't look in /usr/local for
    python modules. tovid installs a few modules on your system, and if 
    python can't find them, then tovid won't work!

    Please try:  ./configure --prefix=/usr

    to install tovid in a place where python will look for modules. Thanks!
    
        -- http://tovid.org
    ])
fi


# Check to see if this is a svn checkout and set version to revision number
if test "$PACKAGE_VERSION" = "svn" && test -e bootstrap; then
     VERSION="svn-r$(svn info bootstrap | grep Revision | awk '{print $2}')"
fi

AC_CONFIG_FILES([Makefile src/tovid-init])
AC_OUTPUT


# ******************************************************************************
# ******************************************************************************
#
# PRETTY SUMMARY
#
# ******************************************************************************
# ******************************************************************************

# Works for all distros
INSTALL_COMMAND="su -c \"make install\""

# but *buntu users are used to
if $(cat /proc/version | grep -iq buntu); then
    INSTALL_COMMAND="sudo make install"
fi

AC_MSG_NOTICE([


 You may now type '$INSTALL_COMMAND' to compile and install tovid.

   (or you can try to 'make sense' of it all...)
 ])

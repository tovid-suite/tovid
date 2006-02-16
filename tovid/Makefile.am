# Process this file with automake to produce a Makefile.in

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

# List the source files for each shell script
sh_bin = \
	src/dvrequant \
	src/idvid \
	src/makedvd \
	src/makemenu \
	src/makeslides \
	src/makevcd \
	src/makexml \
	src/postproc \
	src/previd \
	src/tovid \
	src/tovid-batch \
	src/tovid-init \
	src/tovid-interactive \
	src/tovid-test

# List the source files for each python script
py_bin = \
	src/pyidvid \
	src/pytovid \
	src/pymakemenu \
	src/pymakexml \
	src/tovidgui

# Specify the scripts to make and install.
bin_SCRIPTS = \
	$(sh_bin) \
	$(py_bin)

# The manpages
man_MANS = docs/man/*.1

# libtovid
# See lengthy comments in configure.ac
# pkgpyexecdir is a convenience variable that is defined as $(pyexecdir)/$(PACKAGE),
# but libtovid should be installed as $(pyexecdir)/libtovid, not
# $(pyexecdir)/tovid ($(PACKAGE) is 'tovid' from configure.ac's AC_INIT macro.

# WTF: with pkgpyexecdir = $(pyexecdir)/libtovid , automake borks:
# Makefile.am:68: `pkgpyexecdir_PYTHON' is used but `pkgpyexecdirdir' is undefined
# Notice the 'hack' below:
#           vvv
pkgpyexecdirdir = $(pyexecdir)/libtovid
pkgpyexecdir_PYTHON = libtovid/*.py

# And distribute them
EXTRA_DIST = \
	$(bin_SCRIPTS) \
	$(man_MANS) \
	icons/*.png
##	setuplib
##	libtovid/*.py \

# Install libtovid with setuplib
##install-exec-hook: pythonlib

#pythonlib:
##	./setuplib install

# src/tovid-init not needed b/c ./configure derives it from src/tovid-init.in
dist-hook:
	rm -rvf $(top_distdir)/src/tovid-init

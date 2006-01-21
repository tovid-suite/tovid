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

# List the source files for each shell script to be built and 
# installed. Correct names are automatically created for the 
# build process, as well as install directives.
sh_source = \
	dvrequant.sh \
	idvid.sh \
	makedvd.sh \
	makemenu.sh \
	makeslides.sh \
	makevcd.sh \
	makexml.sh \
	postproc.sh \
	previd.sh \
	tovid.sh \
	tovid-batch.sh \
	tovid-init.sh \
	tovid-interactive.sh \
	tovid-test.sh

# List the source files for each python script to be built and 
# installed. Correct names are automatically created for the 
# build process, as well as install directives.
py_source = \
	pytovid.py \
	pymakemenu.py \
	pymakexml.py \
	tovidgui.py

################### LEAVE BELOW ALONE #########################

# No need to modify anything below! The above two lists can 
# handle an arbitrary amount of shell and python scripts.
# Everything is correctly built, installed, and cleaned so long
# as the source files have a .sh suffix for shell scripts and
# a .py suffix for python scripts.

# Strip the source file extentions. A built file will be called
# by the basename of its source.
#   eg: tovid.sh becomes made and installed as tovid
#       tovidgui.py becomes made and installed as tovidgui
sh_bin = $(basename $(sh_source))
py_bin = $(basename $(py_source))

# Specify the scripts to make and install.
bin_SCRIPTS = \
	$(sh_bin) \
	$(py_bin)

# Clean the built scripts only. Leave the source files alone.
CLEANFILES = $(bin_SCRIPTS)

# Distribute the source files so the suite can be built!
EXTRA_DIST = \
	$(sh_source) \
	$(py_source)

# Make all the shell and python scripts 
# These are Static Pattern Rules, found at:
# http://www.gnu.org/software/make/manual/html_mono/make.html#SEC47
$(sh_bin): %: %.sh
	rm -f "$@"
	echo "#! `which env` sh"  > $@
	cat $(srcdir)/$< >> $@
	chmod ugo+x $@

$(py_bin): %: %.py
	rm -f "$@"
	echo "#! `which env` python"  > $@
	cat $(srcdir)/$< >> $@
	chmod ugo+x $@

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
sh_bin = \
	dvrequant \
	idvid \
	makedvd \
	makemenu \
	makeslides \
	makevcd \
	makexml \
	postproc \
	previd \
	tovid \
	tovid-batch \
	tovid-init \
	tovid-interactive \
	tovid-test

# List the source files for each python script to be built and 
# installed. Correct names are automatically created for the 
# build process, as well as install directives.
py_bin = \
	pyidvid \
	pytovid \
	pymakemenu \
	pymakexml \
	tovidgui

# Specify the scripts to make and install.
bin_SCRIPTS = \
	$(sh_bin) \
	$(py_bin)

# And distribute them
EXTRA_DIST = $(bin_SCRIPTS)
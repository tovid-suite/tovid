# Process this file with automake to produce a Makefile.in

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

bin_SCRIPTS = \
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

CLEANFILES = $(bin_SCRIPTS)

EXTRA_DIST = \
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
	tovid-init.sh.in \
	tovid-interactive.sh \
	tovid-test.sh

dvrequant: $(srcdir)/dvrequant.sh
	rm -f "dvrequant"
	echo "#! `which env` sh"  > dvrequant
	cat $(srcdir)/dvrequant.sh >> dvrequant
	chmod ugo+x dvrequant

idvid: $(srcdir)/idvid.sh
	rm -f "idvid"
	echo "#! `which env` sh"  > idvid
	cat $(srcdir)/idvid.sh >> idvid
	chmod ugo+x idvid

makedvd: $(srcdir)/makedvd.sh
	rm -f "makedvd"
	echo "#! `which env` sh"  > makedvd
	cat $(srcdir)/makedvd.sh >> makedvd
	chmod ugo+x makedvd

makemenu: $(srcdir)/makemenu.sh
	rm -f "makemenu"
	echo "#! `which env` sh"  > makemenu
	cat $(srcdir)/makemenu.sh >> makemenu
	chmod ugo+x makemenu

makeslides: $(srcdir)/makeslides.sh
	rm -f "makeslides"
	echo "#! `which env` sh"  > makeslides
	cat $(srcdir)/makeslides.sh >> makeslides
	chmod ugo+x makeslides

makevcd: $(srcdir)/makevcd.sh
	rm -f "makevcd"
	echo "#! `which env` sh"  > makevcd
	cat $(srcdir)/makevcd.sh >> makevcd
	chmod ugo+x makevcd

makexml: $(srcdir)/makexml.sh
	rm -f "makexml"
	echo "#! `which env` sh"  > makexml
	cat $(srcdir)/makexml.sh >> makexml
	chmod ugo+x makexml

postproc: $(srcdir)/postproc.sh
	rm -f "postproc"
	echo "#! `which env` sh"  > postproc
	cat $(srcdir)/postproc.sh >> postproc
	chmod ugo+x postproc

previd: $(srcdir)/previd.sh
	rm -f "previd"
	echo "#! `which env` sh"  > previd
	cat $(srcdir)/previd.sh >> previd
	chmod ugo+x previd

tovid: $(srcdir)/tovid.sh
	rm -f "tovid"
	echo "#! `which env` sh"  > tovid
	cat $(srcdir)/tovid.sh >> tovid
	chmod ugo+x tovid

tovid-batch: $(srcdir)/tovid-batch.sh
	rm -f "tovid-batch"
	echo "#! `which env` sh"  > tovid-batch
	cat $(srcdir)/tovid-batch.sh >> tovid-batch
	chmod ugo+x tovid-batch

tovid-init: $(srcdir)/tovid-init.sh
	rm -f "tovid-init"
	echo "#! `which env` sh"  > tovid-init
	cat $(srcdir)/tovid-init.sh >> tovid-init
	chmod ugo+x tovid-init

tovid-interactive: $(srcdir)/tovid-interactive.sh
	rm -f "tovid-interactive"
	echo "#! `which env` sh"  > tovid-interactive
	cat $(srcdir)/tovid-interactive.sh >> tovid-interactive
	chmod ugo+x tovid-interactive

tovid-test: $(srcdir)/tovid-test.sh
	rm -f "tovid-test"
	echo "#! `which env` sh"  > tovid-test
	cat $(srcdir)/tovid-test.sh >> tovid-test
	chmod ugo+x tovid-test
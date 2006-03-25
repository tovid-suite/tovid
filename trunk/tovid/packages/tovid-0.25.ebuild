# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit eutils
DESCRIPTION="Video converter cripts"
HOMEPAGE="http://tovid.berlios.de/"
SRC_URI="http://prdownload.berlios.de/tovid/${P}.tar.gz"
LICENSE="GPL-2"
SLOT="0"

KEYWORDS="x86"
IUSE="vcd dvd gui"

DEPEND=">=dev-lang/python-2.4
	media-video/mplayer
	media-video/mjpegtools
	media-video/mjpegtools
	media-video/ffmpeg
	media-video/transcode
	media-sound/normalize
	media-sound/sox
	>=media-gfx/imagemagick-6.0

	dvd? ( >=media-video/dvdauthor-0.6.0 )
	vcd? ( media-video/vcdimager )
	vcd? ( virtual/cdrtools )
	gui? ( >=x11-libs/wxGTK-2.6 )
	gui? ( >=dev-python/wxpython-2.6 )"

src_compile() {
	econf || die
	emake
}

src_install() {
	make DESTDIR="${D}" install || die "Install failed"
	dodoc AUTHORS COPYING ChangeLog INSTALL NEWS README
}

Summary: (S)VCD/DVD Authoring Suite 
Name: tovid
Version: 0.23
Release: 1
Vendor: http://tovid.org/
Packager: Matt Hyclak <hyclak@math.ohiou.edu>
Source: http://prdownloads.sourceforge.net/tovid/%{name}-%{version}.tar.gz
Group: Applications/System
Copyright: GPL
BuildRoot: %{_tmppath}/%{name}-root
Requires: mplayer mjpegtools ffmpeg ImageMagick transcode sox mkisofs
Requires: %{_bindir}/mencoder
BuildRequires: dvdauthor vcdimager normalize lsdvd

%description
A suite of shell scripts to make VCD, SVCD and DVD authoring a little easier. 
Converts arbitrary video formats into (S)VCD/DVD-compliant mpeg, and can help 
with menu creation and disc authoring.

%prep
%setup
%configure

%build
make

%install
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}

%changelog
* Sun Aug 28 2005 Matthew Hyclak <hyclak@gmail.com> - 0.21-1
- First build starting with 0.21

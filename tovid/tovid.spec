Summary: (S)VCD/DVD Authoring Suite 
Name: tovid
Version: 0.24
Release: 1
Vendor: http://tovid.org/
Packager: Matt Hyclak <hyclak@math.ohiou.edu>
Source: http://download.berlios.de/tovid/%{name}-%{version}.tar.gz
Group: Applications/System
Copyright: GPL
BuildRoot: %{_tmppath}/%{name}-root
Requires: mplayer mjpegtools ffmpeg sox ImageMagick transcode 
Requires: dvdauthor >= 0.6.0 mkisofs growisofs vcdimager
Requires: %{_bindir}/mencoder
Requires: wxPython >= 2.6
BuildRequires: mplayer mjpegtools ffmpeg sox ImageMagick transcode
BuildRequires: dvdauthor >= 0.6.0 mkisofs dvd+rw-tools vcdimager cdrdao
BuildRequires: %{_bindir}/mencoder
BuildArch: noarch
Obsoletes: tovid-gui

%description
A suite of shell scripts and a wxPython interface to make VCD, SVCD and DVD 
authoring a little easier. Converts arbitrary video formats into 
(S)VCD/DVD-compliant mpeg, and can help with menu creation and disc authoring.

%prep
%setup
%configure

%build
make
python ./setup.py build

%install
%makeinstall
python ./setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-, root, root)
%{_bindir}
%{_mandir}/man1/*.gz

%changelog
* Thu Dec 22 2005 Matthew Hyclak <hyclak@gmail.com> - 0.24
- Updated to 0.24
- Adjusted Requires and BuildRequires
- Adjusted for the included gui

* Mon Sep 19 2005 Matthew Hyclak <hyclak@gmail.com> - 0.22-2
- Remove dependency on normalize

* Mon Sep 19 2005 Matthew Hyclak <hyclak@gmail.com> - 0.22-1
- Update to 0.22

* Sun Aug 28 2005 Matthew Hyclak <hyclak@gmail.com> - 0.21-1
- First build starting with 0.21

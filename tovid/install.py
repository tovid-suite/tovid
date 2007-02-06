#! /usr/bin/env python
# install.py

"""Dependency-checker and installer for tovid.
"""

import os
import sys
import shutil
import compileall
from libtovid import deps
from libtovid.output import red, green, blue

# Executable scripts
exec_dir = 'src'
executables = [
    # Bash scripts
    'idvid',
    'makedvd',
    'makemenu',
    'makeslides',
    'makevcd',
    'makexml',
    'postproc',
    'previd',
    'todisc',
    'todisc-fade-routine',
    'tovid',
    'tovid-batch',
    'tovid-init',
    'tovid-interactive',
    'tovid-test',
    # Python scripts
    'genvid',
    'pyidvid',
    'pytovid',
    'pymakemenu',
    'pymakexml',
    'ripframes',
    'tktodisc',
    'tovidgui',
    'tovid-stats',
    'todraw']

# Manpages
man_dir = 'docs/man'
man_src_dir = 'docs/src/en'
# .t2t/.1 will be added later
manpages = [
    'idvid',
    'makedvd',
    'makemenu',
    'makeslides',
    'makevcd',
    'makexml',
    'postproc',
    'pymakexml',
    'postproc',
    'todisc',
    'tovid',
    'tovid-stats']

# Python modules
modules = [
    # Root libtovid
    'libtovid/__init__.py',
    'libtovid/author.py',
    'libtovid/cli.py',
    'libtovid/deps.py',
    'libtovid/media.py',
    'libtovid/opts.py',
    'libtovid/output.py',
    'libtovid/spumux.py',
    'libtovid/standard.py',
    'libtovid/stats.py',
    'libtovid/utils.py',
    # GUI
    'libtovid/gui/__init__.py',
    'libtovid/gui/configs.py',
    'libtovid/gui/constants.py',
    'libtovid/gui/controls.py',
    'libtovid/gui/dialogs.py',
    'libtovid/gui/frames.py',
    'libtovid/gui/icons.py',
    'libtovid/gui/meta.py',
    'libtovid/gui/options.py',
    'libtovid/gui/panels.py',
    'libtovid/gui/util.py',
    # Render
    'libtovid/render/__init__.py',
    'libtovid/render/animation.py',
    'libtovid/render/drawing.py',
    'libtovid/render/effect.py',
    'libtovid/render/flipbook.py',
    'libtovid/render/layer.py',
    # Template
    'libtovid/template/__init__.py',
    'libtovid/template/textmenu.py',
    'libtovid/template/thumbmenu.py',
    # Transcode
    'libtovid/transcode/__init__.py',
    'libtovid/transcode/encode.py',
    'libtovid/transcode/rip.py']

# Icons
icon_dir = 'icons'
icons = [
    'tovid_icon_128.png',
    'tovid_icon_64.png',
    'tovid_icon_48.png',
    'tovid_icon_32.png',
    'tovid.svg',
    'disc.svg',
    'cd.svg']

shortcuts = [
    'tovidgui.desktop',
    'tktodisc.desktop']

def newer(source, dest):
    """Return True if the source file is more recently modified than the
    destination; False otherwise."""
    source_mod = os.path.getmtime(source)
    if os.path.exists(dest):
        dest_mod = os.path.getmtime(dest)
    else:
        dest_mod = 0
    return source_mod > dest_mod


def install(source, dest):
    """Copy source file to destination file, but only if source is newer.
    """
    if newer(source, dest):
        print "Copying '%s' to '%s'" % (source, dest)
        # shutil.copy(source, dest)
    else:
        print "Skipping: '%s' (no changes)" % source


def install_executables(prefix):
    """Install executable files to the given prefix directory."""
    dest_dir = os.path.join(prefix, 'src')
    print green("Installing executables to %s" % dest_dir)
    for file in executables:
        source = os.path.join(exec_dir, file)
        dest = os.path.join(dest_dir, file)
        install(source, dest)


def build_manpages():
    """Build manual pages from .t2t source files."""
    print green("Building manual pages")
    for manpage in manpages:
        t2tfile = os.path.join(man_src_dir, manpage) + '.t2t'
        manfile = os.path.join(man_dir, manpage) + '.1'
        if newer(t2tfile, manfile):
            print "Building manual page from %s" % t2tfile
            cmd = 'txt2tags -t man -i "%s" -o "%s"' % (t2tfile, manfile)
            os.system(cmd)
        else:
            print "Skipping: %s" % manfile


def install_manpages(prefix):
    """Install manual pages to the given prefix directory."""
    dest_dir = os.path.join(prefix, 'share/man/man1')
    print green("Installing manpages to %s" % dest_dir)
    for manpage in manpages:
        source = os.path.join(man_dir, manpage) + '.1'
        dest = os.path.join(dest_dir, manpage) + '.1'
        install(source, dest)


def install_modules(prefix):
    """Install Python modules to the given prefix directory."""
    dest_dir = os.path.join(prefix, 'lib/python%s.%s/site-packages' %\
                            (sys.version_info[0], sys.version_info[1]))
    print green("Installing Python modules to %s" % dest_dir)
    for module in modules:
        dest = os.path.join(dest_dir, module)
        install(module, dest)
    print green("Byte-compiling Python modules")
    #libtovid_dir = os.path.join(dest_dir, 'libtovid')
    #compileall.compile_dir(libtovid_dir)


def install_icons(prefix):
    """Install icons to the given prefix directory."""
    dest_dir = os.path.join(prefix, 'share/icons/hicolor')
    print green("Installing icons to %s" % dest_dir)
    # Yuck
    for icon in icons:
        if icon.endswith('128.png'):
            subdir = '128x128'
        elif icon.endswith('64.png'):
            subdir = '64x64'
        elif icon.endswith('48.png'):
            subdir = '48x48'
        elif icon.endswith('32.png'):
            subdir = '32x32'
        elif icon.endswith('.svg'):
            subdir = 'scalable'
        source = os.path.join(icon_dir, icon)
        dest = os.path.join(dest_dir, subdir, 'apps', icon)
        install(source, dest)


def install_misc(prefix):
    """Install miscellaneous files to the given prefix directory."""
    desktop_dir = os.path.join(prefix, 'share/applications')
    print green("Installing desktop shortcuts to %s" % desktop_dir)
    for shortcut in shortcuts:
        dest = os.path.join(desktop_dir, shortcut)
        install(shortcut, dest)


if __name__ == '__main__':
    print "tovid installer"
    print "---------------"
    print red("This script is experimental, and only pretends to install.")
    prefix = raw_input("Install to what directory? (default: /usr/local): ")
    if prefix == '':
        prefix = '/usr/local'

    # Build manpages as regular user
    build_manpages()

    if not os.geteuid() == 0:
        print "Please run as root to install files system-wide."
        sys.exit()

    install_executables(prefix)
    install_manpages(prefix)
    install_modules(prefix)
    install_icons(prefix)
    install_misc(prefix)
    
    print blue("Done! Thanks for using the tovid installer.")

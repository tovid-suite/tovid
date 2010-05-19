#! /usr/bin/env python
# setup.py

"""Distutils installation script for tovid.

To install, run:

    sudo ./setup.py install

or:

    su -c './setup.py install'

At this time, there is no 'uninstall' mechanism...
"""

import os

def svn_version():
    """Return the current SVN revision number, as reported by 'svn info',
    as a string like 'svn-r1234'. If svn is not installed, or if something goes
    wrong, return 'svn-unknown'
    """
    rev_line = os.popen('svn info 2>/dev/null | grep ^Revision').read()
    # If rev_line is empty, either svn is missing or the command failed
    if rev_line:
        return 'svn-r' + rev_line.split(':')[1].strip()
    else:
        return 'svn-unknown'

# Current version number of tovid, as a string.
# Examples:
# Current SVN version number
_tovid_version = svn_version()
# Official release number
#_tovid_version = '0.34'


import sys
import shutil
from distutils.core import setup, Command
from distutils.command.install import install
from distutils.command.build import build
from distutils.sysconfig import get_config_var


class InstallCommand (install):
    """Extended install command--automatically records installed files
    to $prefix/lib/tovid/.install.log, so they can be uninstalled later.
    """
    def initialize_options(self):
        install.initialize_options(self)
        # Record installation log to a temporary file
        self.record = 'install.log'

    def run(self):
        """Install tovid, and write a list of installed files to
        $prefix/lib/tovid/.install.log.
        """
        install.run(self)
        # For whatever reason, on Ubuntu, self.prefix only points to /usr/local
        # if setup.py was explicitly called with the --prefix option.
        # self.install_data does correctly point to /usr/local on Ubuntu
        # (both with and without the --prefix option)
        prefix = self.install_data
        print("Installing tovid to %s" % prefix)
        # Move temporary install log to $prefix/lib/tovid
        install_log = os.path.join(prefix, 'lib', 'tovid', '.install.log')
        print("Moving install.log to '%s'" % install_log)
        shutil.move(self.record, install_log)


class UninstallCommand (Command):
    description = "remove everything that was installed by the install command"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_prefix(self):
        """Return the prefix (/usr or /usr/local) where tovid is installed,
        or '' if the prefix could not be determined.
        """
        # Determine which tovid is in the $PATH
        tovid = os.popen('which tovid').read()
        # Get $prefix/bin
        bin_prefix = os.path.dirname(tovid)
        # Get $prefix
        prefix = os.path.dirname(bin_prefix)
        return prefix

    def run(self):
        """Uninstall tovid, removing all files listed in
        $prefix/lib/tovid/.install.log.
        """
        # Determine the installed prefix
        prefix = self.get_prefix()
        if not prefix:
            print("Could not find tovid in your $PATH. "
                  "You may need to uninstall manually")
            return
        print("Uninstalling tovid from %s" % prefix)
        install_log = os.path.join(prefix, 'lib', 'tovid', '.install.log')
        # If install log doesn't exist, there's nothing to do
        if not os.path.exists(install_log):
            print("Missing installation log: '%s'" % install_log)
            print("Either tovid is not installed, or "
                  "something went wrong during installation. "
                  "You may need to uninstall manually.")
            return
        # Remove each file found in install log
        for line in open(install_log, 'r'):
            filename = line.strip(' \n')
            print("Removing '%s'" % filename)
            os.remove(filename)
        # Remove the install log itself
        os.remove(install_log)
        # Remove the $prefix/lib/tovid directory
        os.removedirs(os.path.dirname(install_log))


class BuildDocs (Command):
    description = "build the tovid documentation (currently just the manpage)"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Build the tovid manual page.
        """
        source = 'docs/src/en/tovid.t2t'
        target = 'docs/man/tovid.1'
        # Build only if target does not exist, or if source is newer than target
        mod = os.path.getmtime
        if not os.path.exists(target) or (mod(source) > mod(target)):
            command = 'txt2tags -t man -i "%s" -o "%s"' % (source, target)
            os.system(command)


class BuildTovidInit (Command):
    description = "build tovid-init"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


    def run(self):
        """Build src/tovid-init from tovid-init.in.
        """
        source = 'src/tovid-init.in'
        target = 'src/tovid-init'
        # We basically just need to replace @VERSION@ in tovid-init.in with
        # the current version of tovid.
        lines = [line.replace('@VERSION@', _tovid_version)
                 for line in open(source, 'r')]
        # Write all lines to the target file
        outfile = open(target, 'w')
        outfile.writelines(lines)
        outfile.close()


# The actual setup
setup(
    name = 'tovid',
    version = _tovid_version, # Defined at the top of this file
    url = 'http://tovid.wikia.com/',
    license = 'GPL',
    maintainer = 'Eric Pierce',
    maintainer_email = 'wapcaplet88@gmail.com',

    cmdclass = {
        'install': InstallCommand,
        'uninstall': UninstallCommand,
        'build_docs': BuildDocs,
        'build_tovid_init': BuildTovidInit,
    },

    # Python modules go into /$PREFIX/lib/pythonX.Y/(site|dist)-packages
    packages = [
        'libtovid',
        'libtovid.guis',
        'libtovid.util',
        'libtovid.metagui',
        'libtovid.render',
        'libtovid.backend',
    ],

    # Executable files go into /$PREFIX/bin/
    scripts = [
        # Main executable
        'src/tovid',

    ],

    # Extra files installed relative to /$PREFIX/
    data_files = [
        ('lib/tovid', [
            # Bash scripts
            'src/idvid',
            'src/makedvd',
            'src/makemenu',
            'src/makevcd',
            'src/makexml',
            'src/postproc',
            'src/todisc',
            'src/todisc-fade-routine',
            'src/makempg',
            'src/tovid-batch',
            'src/tovid-init',
            'src/tovid-interactive',
            'src/make_titlesets',

            # Python scripts
            'src/todiscgui',
            'src/tovid-stats',
            'src/titleset-wizard',

            # Icon used by titleset wizard
            'icons/tovid.gif',

            # Config file
            'src/tovid.ini',
        ]),
        # Manual page
        ('share/man/man1',
         ['docs/man/tovid.1']),
        # Desktop shortcut
        ('share/applications',
         ['tovidgui.desktop']),
        # Icons
        ('share/icons/hicolor/scalable/apps',
         ['icons/hicolor/scalable/apps/tovid.svg',
          'icons/hicolor/scalable/apps/tovid_bw.svg',
          'icons/hicolor/scalable/apps/disc.svg',
          'icons/hicolor/scalable/apps/cd.svg',
         ]),
        ('share/icons/hicolor/128x128/apps',
         ['icons/hicolor/128x128/apps/tovid.png']),
        ('share/icons/hicolor/64x64/apps',
         ['icons/hicolor/64x64/apps/tovid.png']),
        ('share/icons/hicolor/48x48/apps',
         ['icons/hicolor/48x48/apps/tovid.png']),
        ('share/icons/hicolor/32x32/apps',
         ['icons/hicolor/32x32/apps/tovid.png']),
    ]
)


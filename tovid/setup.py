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
import sys
import shutil
from distutils.core import setup, Command
from distutils.command.install import install

# Hack to get the 'uninstall' command to work
_tovid_libdir  = os.path.join(sys.prefix, 'lib', 'tovid')
_installed_file_log = os.path.join(_tovid_libdir, '.install.log')


class InstallCommand (install):
    """Overridden install command--automatically records installed files
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
        # Move temporary install log to $prefix/lib/tovid
        print("Moving install.log to '%s'" % _installed_file_log)
        shutil.move('install.log', _installed_file_log)


class UninstallCommand (Command):
    description = "remove everything that was installed by the install command"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Uninstall tovid, removing all files listed in
        $prefix/lib/tovid/.install.log.
        """
        # If install log doesn't exist, there's nothing to do
        if not os.path.exists(_installed_file_log):
            print("Missing installation log: '%s'" % _installed_file_log)
            print("Either tovid is not installed, or "
                  "something went wrong during installation. "
                  "You may need to uninstall manually.")
            return
        # Remove each file found in install log
        for line in open(_installed_file_log, 'r'):
            filename = line.strip(' \n')
            print("Removing '%s'" % filename)
            os.remove(filename)
        # Remove the install log itself
        os.remove(_installed_file_log)
        # Remove the $prefix/lib/tovid directory
        os.removedirs(_tovid_libdir)


# The actual setup
setup(
    name = 'tovid',
    version = 'svn',
    url = 'http://tovid.wikia.com/',
    license = 'GPL',
    cmdclass = {
        'install': InstallCommand,
        'uninstall': UninstallCommand,
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
        ]),
    ]
)


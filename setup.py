#! /usr/bin/env python
# setup.py

"""Distutils installation script for tovid.

To install, run:

    sudo ./setup.py install

or:

    su -c './setup.py install'

At this time, there is no 'uninstall' mechanism...
"""
def git_version():
    """Return the current release number, followed by the current commit sha1,
    as reported by 'git rev-parse HEAD', as a string like 'tovid-0.35.0-f2d20b8'.
    If git is not installed or this is not a git directory, or if something goes
    wrong, return 'tovid-0.35.0+git-unknown'
    """
    import os
    try:
        from commands import getoutput
    except ImportError:
        # python 3
        from subprocess import getoutput
    # if (we are in a git dir and git is installed) #FIXME
    if os.path.isdir('.git') and getoutput('which git'):
        #rev_line = getoutput('git rev-parse --short HEAD 2>/dev/null')
        rev_line = getoutput('git describe --match %s 2>/dev/null' %
                             _last_release).replace('-g', '-')
        _hash = rev_line.split('-')[2]
        # make sure the revision (_hash) is a git hash (hex)
        try:
            int(_hash, 16)
            return  rev_line
        except ValueError:
            return '%s-git-unknown' % _last_release 
    else:
        return '%s-git-unknown' % _last_release 


# Current version number of tovid, as a string.
# Examples:
# Official release number
_last_release = '0.35.0'
_tovid_version = git_version()


import os
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
        self.source = os.path.join('docs', 'src', 'en', 'tovid.t2t')
        self.target = os.path.join('docs', 'man', 'tovid.1')

    def finalize_options(self):
        pass

    def run(self):
        """Build the tovid manual page.
        """
        # Build only if target does not exist, or if source is newer than target
        mod = os.path.getmtime
        if not os.path.exists(self.target) or (mod(self.source) > mod(self.target)):
            # For python 3 txt2tags needs an unofficial script
            import sys
            if (sys.version_info > (3, 0)):
                txt2tags = 'docs/scripts/txt2tags'
                print("using %s " % txt2tags)
            else:
                txt2tags = 'txt2tags'

            print("Rebuilding tovid manual page")
            command = '%s -t man -i "%s" -o "%s"' % (txt2tags, self.source,
                                                               self.target)
            os.system(command)
        else:
            print("Manual page already built, not building again")


class BuildTovidInit (Command):
    description = "build tovid-init"
    user_options = []

    def initialize_options(self):
        self.source = os.path.join('src', 'tovid-init.in')
        self.target = os.path.join('src', 'tovid-init')
        # Touch the source file to ensure that it gets rebuilt
        os.utime(self.source, None)

    def finalize_options(self):
        pass

    def run(self):
        """Build src/tovid-init from tovid-init.in.
        """
        # We basically just need to replace @VERSION@ in tovid-init.in with
        # the current version of tovid.
        lines = [line.replace('@VERSION@', _tovid_version)
                 for line in open(self.source, 'r')]
        # Write all lines to the target file
        outfile = open(self.target, 'w')
        outfile.writelines(lines)
        outfile.close()


# Build tovid-init with regular 'build' command
build.sub_commands.append(('build_tovid_init', None))
build.sub_commands.append(('build_docs', None))

# The actual setup
setup(
    name = 'tovid',
    description = 'A suite of tools for creating video DVDs',
    long_description = 'A suite of tools for creating video DVDs',
    version = _tovid_version, # Defined at the top of this file
    url = 'http://tovid.wikia.com/',
    license = 'GPL',
    maintainer = 'grepper',
    maintainer_email = 'grepper@gmail.com',
    platforms = 'Linux',
    

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
            'src/todisc',
            'src/todisc-fade-routine',
            'src/makempg',
            'src/mpv_identify.sh',
            'src/tovid-init',

            # Python scripts
            'src/todiscgui',
            'src/tovid-stats',
            'src/titleset-wizard',
            'src/set_chapters',

            # Icons used in the GUIs
            'icons/hicolor/128x128/apps/tovid.png',
            'icons/hicolor/128x128/apps/titleset-wizard.png',

            # Config file
            'src/tovid.ini',
        ]),
        # Manual page
        ('share/man/man1',
         ['docs/man/tovid.1']),
        # Desktop shortcut
        ('share/applications',
         ['tovidgui.desktop',
         'titleset-wizard.desktop']),
        # Icons
        ('share/icons/hicolor/scalable/apps',
         [
             'icons/hicolor/scalable/apps/tovid.svg',
             'icons/hicolor/scalable/apps/titleset-wizard.svg',
             'icons/hicolor/scalable/apps/tovid_bw.svg',
             'icons/hicolor/scalable/apps/disc.svg',
             'icons/hicolor/scalable/apps/cd.svg',
         ]),
        ('share/icons/hicolor/128x128/apps',
         [
             'icons/hicolor/128x128/apps/tovid.png',
             'icons/hicolor/128x128/apps/titleset-wizard.png',
         ]),
        ('share/icons/hicolor/64x64/apps',
         [
             'icons/hicolor/64x64/apps/tovid.png',
             'icons/hicolor/64x64/apps/titleset-wizard.png',
         ]),
        ('share/icons/hicolor/48x48/apps',
         [
             'icons/hicolor/48x48/apps/tovid.png',
             'icons/hicolor/48x48/apps/titleset-wizard.png',
         ]),
        ('share/icons/hicolor/32x32/apps',
         [
             'icons/hicolor/32x32/apps/tovid.png',
             'icons/hicolor/32x32/apps/titleset-wizard.png',
         ]),
    ]
)


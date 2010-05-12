#! /usr/bin/env python
# setup.py

"""Distutils installation script for tovid.

To install, run:

    sudo ./setup.py install

or:

    su -c './setup.py install'

At this time, there is no 'uninstall' mechanism...
"""

from distutils.core import setup
setup(
    name = 'tovid',
    version = 'svn',
    url = 'http://tovid.wikia.com/',
    license = 'GPL',

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


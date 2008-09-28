#! /usr/bin/env python
# __init__.py (guis)

"""This module contains metagui-based GUIs for several of the tovid scripts.

Each of these is intended to be imported and run from some command-line
frontend script (such as ``todiscgui``), but the .py files in this directory
are themselves executable.
"""

__all__ = [
    'todisc',
    'tovid',
    'makemenu',
    'makexml',
    'idvid',
    #'wxgtk', # for old tovid GUI, currently in libtovid.gui?
]

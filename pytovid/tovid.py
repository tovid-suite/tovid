#! /usr/bin/env python

# tovid.py
# ==============
# This python module is part of an experimental Python implementation
# of the tovid video authoring suite.
#
# Project homepage: http://tovid.org/
#
# This software is licensed under the GNU General Public License.
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

import sys
from libtovid import tools, Parser

# ===========================================================
# Execution begins here
# ===========================================================

# Test the Parser on an input file containing a tovid disc layout
if len(sys.argv) < 2:
    print "Please provide some command-line options"
else:
    del sys.argv[0]
    # Add a dummy Video element for parsing
    sys.argv.insert(0, 'Video')
    sys.argv.insert(1, 'Untitled')

    p = Parser.Parser()
    elements = p.parse_args(sys.argv)
    elem = elements[0] # Hack

    infile = elem.get('in')
    format = elem.get('format')
    tvsys = elem.get('tvsys')

    mplayer_cmd = tools.get_mplayer_cmd(infile, format, tvsys)
    mpeg2enc_cmd = tools.get_mpeg2enc_cmd(format, tvsys)

    print mplayer_cmd
    print mpeg2enc_cmd


#! /usr/bin/env python

# pytovid
# ==============
# This python module is part of an experimental Python implementation
# of the tovid video authoring suite.
#
# Project homepage: http://tovid.sourceforge.net/
#
# This software is licensed under the GNU General Public License.
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

import sys
from libtovid.Parser import *

# ===========================================================
# Execution begins here
# ===========================================================

# Test the Parser on an input file containing a tovid disc layout
if len( sys.argv ) == 0:
    print "Please provide some command-line options"
else:
    del sys.argv[0]
    # Add a dummy Video element for parsing
    sys.argv.insert( 0, 'Video' )
    sys.argv.insert( 1, 'Untitled' )

    p = Parser()
    elements = p.parse_args( sys.argv )

    for element in elements:
        element.display()

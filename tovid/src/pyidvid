#! /usr/bin/env python

# pyidvid
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

import sys, os
from libtovid.Filetypes import *

# ===========================================================
# Execution begins here
#
# This stuff is just for testing; the true pyidvid script will
# do real argument-parsing and whatnot.
# ===========================================================
if __name__ == '__main__':
    # If no arguments were provided, print usage notes
    if len(sys.argv) == 1:
        print "Usage: %s FILE" % sys.argv[0]
    else:
        print "Creating a MultimediaFile object from file: %s" % sys.argv[1]
        infile = MultimediaFile(sys.argv[1])
        infile.display()
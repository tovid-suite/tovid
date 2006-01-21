#! /usr/bin/env python

# pytovid
# Convert a video into an (S)VCD/DVD-compliant MPEG
# (to replace the 'tovid' shell script)

import sys, libtovid
from libtovid import Video, Parser

if __name__ == '__main__':
    """Create a Video element from the provided command-line options,
    and generate it using the Video module."""
    if len(sys.argv) < 5:
        print "Usage: pytovid [options] -in FILE -out OUTNAME"
        print "See the 'tovid' manual page for more details."
        sys.exit()

    # Create a TDL video element definition using the
    # provided command-line options
    tdl = 'Video "FOO VIDEO" '
    for arg in sys.argv[1:]:
        tdl += '%s ' % arg

    print "TDL string:"
    print tdl

    par = Parser.Parser()
    elems = par.parse_string(tdl)
    print "Parsed Video element:"
    print elems[0].tdl_string()
    print "Generating video..."
    Video.generate(elems[0])


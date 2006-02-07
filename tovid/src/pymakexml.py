# -* python -*

# pymakexml
# Generate vcdimager/dvdauthor XML for an (S)VCD/DVD disc
# (to replace the 'makexml' shell script)

import sys, libtovid
from libtovid import Disc, Parser

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: pymakexml [options] vid1.mpg vid2.mpg ... -out NAME"
        print "See the 'makexml' manual page for more details."
        sys.exit()

    # Create a TDL disc element definition using the
    # provided command-line options

    # Insert a dummy element/name declaration
    sys.argv.insert(0, 'Disc')
    sys.argv.insert(1, '"FOO DISC"')

    par = Parser.Parser()
    elems = par.parse_args(sys.argv)
    print "Parsed Disc element:"
    print elems[0].tdl_string()
    print "Generating disc XML..."
    Disc.generate(elems[0])
    


#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Quick-and-dirty 'make' tool for building tovid documentation."""

import glob
import os
# Get TDL
import Libtovid
from Libtovid import TDL
# Get mypydoc
import mypydoc

# Directory containing .t2t doc sources
source_dir = os.path.realpath( 't2t' )
# Directory to save output in
dest_dir = os.path.realpath( 'html' )

# Subdirectories of source_dir containing translations to build
translation_subdirs = [ 'en', 'es' ]



def generate_html( t2tfile, htmlfile ):
    cmd = 'txt2tags -i %s -o %s' % ( t2tfile, htmlfile )
    cmd += ' -t xhtml --css-sugar --toc --style=tovid_screen.css'
    # Run txt2tags cmd, displaying its normal output
    for output in os.popen( cmd ).readlines():
        print output

    # Run tidy on HTML output
    os.popen( "tidy -utf8 -i -m %s" % htmlfile )


def generate_pydocs():
    print "generate_pydocs()"
    for mod in Libtovid.__all__:
        mod = "Libtovid.%s" % mod
        print "Writing %s/en/%s.html" % (dest_dir, mod)
        htmlfile = open("%s/en/%s.html" % (dest_dir, mod), 'w' )
        gen = mypydoc.HTMLGenerator()
        html = gen.document(mod)
        htmlfile.write( html )
        htmlfile.close()
        # Run tidy on HTML output
        os.popen( "tidy -utf8 -i -m %s" % htmlfile )
    
def generate_tdl_t2t():
    """Generate t2t versions of the TDL documentation defined in TDL.py."""
    # For now, just generate a single file containing TDL usage notes
    t2t_str = "tovid design language\n\n\n" \
    + "==Disc==\n\n" \
    + "```\n" \
    + TDL.usage( 'Disc' ) \
    + "```\n\n" \
    + "==Menu==\n\n" \
    + "```\n" \
    + TDL.usage( 'Menu' ) \
    + "```\n\n" \
    + "==Video==\n\n" \
    + "```\n" \
    + TDL.usage( 'Video' ) \
    + "```\n\n"

    os.popen( "rm -f %s/en/tdl.t2t" % source_dir )
    t2tfile = open('%s/en/tdl.t2t' % source_dir, 'w')
    t2tfile.write( t2t_str )
    t2tfile.close()


if __name__ == '__main__':
    # Generate t2t for TDL
    generate_tdl_t2t()

    # Do all translations
    for trans_dir in translation_subdirs:
        print "Looking for .t2t sources in %s/%s" % ( source_dir, trans_dir )
        for t2tfile in glob.glob( '%s/%s/*.t2t' % ( source_dir, trans_dir ) ):
            # Determine output path/filename
            # (Strip .t2t from basename and put in dest_dir/trans_dir)
            outfile = '%s/%s/%s.html' % \
                    ( dest_dir, trans_dir, os.path.basename( t2tfile )[:-4] )
            
            # Determine last-modified times for the source and target files
            t2t_mod = os.path.getmtime( t2tfile )
            if os.path.exists( outfile ):
                html_mod = os.path.getmtime( outfile )
            else:
                html_mod = 0

            # If the .t2t source is newer than the existing HTML target,
            # recreate the HTML.
            if t2t_mod > html_mod:
                print "Source file: %s is new. Regenerating %s" % \
                    ( t2tfile, outfile )
                generate_html( t2tfile, outfile )
                generate_pydocs()
            else:
                print "Skipping file: %s" % t2tfile



    print "Done!"

#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Quick-and-dirty 'make' tool for building tovid documentation."""

import os, sys, glob
# Get TDL
import libtovid
from libtovid import TDL
# Get mypydoc
import mypydoc

# Directory containing .t2t doc sources
source_dir = os.path.realpath('t2t')
# Directory to save output in
dest_dir = os.path.realpath('html')
man_dir = os.path.realpath('man')
man_pages = ['tovid', 'idvid', 'makemenu', 'makedvd', \
    'makeslides', 'makexml', 'postproc']

# Subdirectories of source_dir containing translations to build
translation_subdirs = [ 'en', 'es' ]

    
def generate_t2t_tarball():
    """Create tar/gzip of all t2t sources in the html/download directory."""
    print "Generating .tar.gz of all .t2t sources..."
    for lang in translation_subdirs:
        cmd = 'tar --exclude .svn -czvvf %s/download/tovid_t2t_%s.tar.gz t2t/%s' % \
                (dest_dir, lang, lang)
        os.system(cmd)
    


def generate_manpage(t2tfile, manfile):
    cmd = 'txt2tags -i %s -o %s' % (t2tfile, manfile)
    cmd += ' -t man'
    os.system(cmd)

def generate_manpages():
    for manpage in man_pages:
        print "Generating manual page for %s..." % manpage
        cmd = 'txt2tags -t man'
        cmd += ' -i %s/en/%s.t2t ' % (source_dir, manpage)
        cmd += ' -o %s/%s.1' % (man_dir, manpage)
        os.system(cmd)


def generate_html(t2tfile, htmlfile):
    cmd = 'txt2tags -i %s -o %s' % (t2tfile, htmlfile)
    cmd += ' --encoding iso-8859-1'
    cmd += ' -t xhtml --css-sugar --toc --style=tovid_screen.css'
    # Run txt2tags cmd, displaying its normal output
    os.system(cmd)

    # Run tidy on HTML output
    #os.popen2("tidy -utf8 -i -m %s" % htmlfile)


def generate_pydocs():
    print "Generating HTML documentation of libtovid Python sources"
    for mod in libtovid.__all__:
        mod = "libtovid.%s" % mod
        print "Writing %s/en/%s.html" % (dest_dir, mod)
        htmlfile = open("%s/en/%s.html" % (dest_dir, mod), 'w')
        gen = mypydoc.HTMLGenerator()
        html = gen.document(mod)
        htmlfile.write(html)
        htmlfile.close()
        # Run tidy on HTML output
        #os.popen2("tidy -utf8 -i -m %s" % htmlfile)

    
def generate_tdl_t2t():
    """Generate t2t versions of the TDL documentation defined in TDL.py."""
    # For now, just generate a single file containing TDL usage notes
    t2t_str = "tovid design language\n\n\n" \
    + "==Disc==\n\n" \
    + "```\n" \
    + TDL.usage('Disc') \
    + "```\n\n" \
    + "==Menu==\n\n" \
    + "```\n" \
    + TDL.usage('Menu') \
    + "```\n\n" \
    + "==Video==\n\n" \
    + "```\n" \
    + TDL.usage('Video') \
    + "```\n\n"

    os.popen("rm -f %s/en/tdl.t2t" % source_dir)
    t2tfile = open('%s/en/tdl.t2t' % source_dir, 'w')
    t2tfile.write(t2t_str)
    t2tfile.close()


if __name__ == '__main__':

    print "tovid documentation maker"

    regen_all = False

    for arg in sys.argv[1:]:
        if arg == 'all':
            regen_all = True

    generate_t2t_tarball()
    generate_manpages()
    #generate_tdl_t2t()
    #generate_pydocs()

    # Convert all language translations (.t2t sources) to HTML
    for trans_dir in translation_subdirs:
        print "Looking for .t2t sources in %s/%s" % (source_dir, trans_dir)
        for t2tfile in glob.glob('%s/%s/*.t2t' % (source_dir, trans_dir)):
            # Determine output path/filename
            # (Strip .t2t from basename and put in dest_dir/trans_dir)
            outfile = '%s/%s/%s.html' % \
                    (dest_dir, trans_dir, os.path.basename(t2tfile)[:-4])
            
            if regen_all:
                generate_html(t2tfile, outfile)
            else:
                # Determine last-modified times for the source and target files
                t2t_mod = os.path.getmtime(t2tfile)
                if os.path.exists(outfile):
                    html_mod = os.path.getmtime(outfile)
                else:
                    html_mod = 0

                # If the .t2t source is newer than the existing HTML target,
                # recreate the HTML.
                if t2t_mod > html_mod:
                    print "Source file: %s is new. Regenerating %s" % \
                        (t2tfile, outfile)
                    generate_html(t2tfile, outfile)
                else:
                    print "Skipping file: %s" % t2tfile


    print "Done!"

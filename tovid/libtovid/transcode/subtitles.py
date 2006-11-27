#! /usr/bin/env python
# subtitles.py

import tempfile
import xml.dom
import os

from libtovid.cli import Command
from libtovid.opts import Option, OptionDict
from libtovid.media import load_media

dom = xml.dom.getDOMImplementation()

def mktempname(*args, **kwargs):
    """Generates a temporary filename. Same args and kwargs
    as mkstemp."""
    fd, fname = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    return fname

def mktempstream(*args, **kwargs):
    """Generates a file object, it's not removed after being closed.
    Same args and kwargs as mkstemp."""
    return open(mktempname(*args, **kwargs), "w")

VALID_TAGS = {
    'filename': None,
    'characterset': 'UTF-8',
    'fontsize': '18.0',
    'font': 'Vera.ttf',
    'horizontal-alignment': 'center',
    'vertical-alignment': 'bottom',
    'left-margin': '60',
    'right-margin': '60',
    'subtitle-fps': '25',
    'movie-fps': None,
    'movie-width': None,
    'movie-height': None,
}

def create_xml(opts):
    """Returns a string with the XML necessary for spumux"""
    doc = dom.createDocument(None, "subpictures", None)
    root = doc.firstChild
    
    stream = doc.createElement("stream")
    root.appendChild(stream)
    
    textsub = doc.createElement("textsub")
    stream.appendChild(textsub)
    
    for key in VALID_TAGS:
        try:
            textsub.setAttribute(key, str(opts[key]))
        except KeyError:
            default = VALID_TAGS[key]
            if default is None:
                raise
            # set the default value
            textsub.setAttribute(key, str(default))
            
    return doc.toprettyxml()

def spumux(movie_filename, xmlopts, stream=0):
    """
    Runs a script from the command line
    """
    sub_filename = xmlopts['filename']
    xmldata = create_xml(xmlopts)
    print "spumux XML file:"
    print xmldata
    xmlfile = mktempstream(suffix=".xml")
    xmlfile.write(xmldata)
    xmlfile.close()
    
    # make sure the temporary mpeg is created on the same directory
    base_dir = os.path.dirname(movie_filename)
    tmp_mpg = mktempname(suffix=".mpg", dir=base_dir)
    
    # spumux -s0 < in > out
    spumux = Command('spumux', '-s%s' % stream, xmlfile.name)
    # TODO: Find a more elegant way to do stream redirection
    stream_in = open(movie_filename)
    stream_out = open(tmp_mpg)
    spumux._run_redir(stream_in, stream_out)
    spumux.wait()
    
    # Remove old file
    os.remove(movie_filename)
    # Rename temporary file to new file
    os.rename(tmp_mpg, movie_filename)
    # Remove the XML file
    os.remove(xmlfile.name)


def add_subs(infile, subs, opts=None):
    """
    Adds subtitles to a certain MPEG.
    infile must be a MediaFile.
    """
    assert isinstance(infile, MediaFile)
    
    xmlopts = {
        'movie-fps': infile.fps,
        'movie-width': infile.width,
        'movie-height': infile.height,
    }
    
    if opts:
        xmlopts.update(opts)
    
    for stream, sub_filename in enumerate(subs):
        xmlopts['filename'] = sub_filename
        spumux(infile.filename, xmlopts, stream)


class Subtitles(object):
    optiondefs = [
        Option("subs", 'STRING [, STRING ...]', [],
        """One file means one language. You'll need to know the order of the
        supplied subtitles when you add support for it on `todisc`."""),
        Option('in', 'STRING', None,
            """Input video file, in any format. This file will be altered
            (inplace)."""),
    ]

    def __init__(self, custom_options=None):
        """Initialize Subtitles with a string or list of options."""
        self.options = OptionDict(self.optiondefs)
        self.options.override(custom_options)
        

    def generate(self):
        """generate the subtitles from the following options"""
        infile = load_media(self.options['in'])
        add_subs(infile, self.options['subs'])

if __name__ == '__main__':
    import sys
    subs = Subtitles(sys.argv[1:])
    subs.generate()

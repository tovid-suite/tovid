#! /usr/bin/env python
# spumux.py

"""This module is for adding subtitles to MPEG video files using spumux.

Defined here are two functions for adding subtitles to an MPEG file:

    add_subpictures:  Add image files (.png)
    add_subtitles:    Add subtitle files (.sub, .srt etc.)

Use these if you just want to add subpictures or subtitles, and don't want
to think much about the XML internals.
"""

__all__ = [\
    'add_subpictures',
    'add_subtitles']

import os
from libtovid import utils
from libtovid import xml
from libtovid import cli
from libtovid.backend import mplayer

# spumux XML elements and valid attributes
"""
subpictures
stream
textsub
    ['filename',
    'characterset',
    'fontsize',
    'font',
    'horizontal-alignment',
    'vertical-alignment',
    'left-margin',
    'right-margin',
    'subtitle-fps',
    'movie-fps',
    'movie-width',
    'movie-height']
button
    ['name',
    'x0', 'y0', # Upper-left corner, inclusively
    'x1', 'y1', # Lower-right corner, exclusively
    'up', 'down', 'left', 'right']
action
    ['name']
spu
    ['start',
    'end',
    'image',
    'highlight',
    'select',
    'transparent',   # color code
    'force',         # 'yes' (force display, required for menus)
    'autooutline',   # 'infer'
    'outlinewidth',
    'autoorder',     # 'rows' or 'columns'
    'xoffset',
    'yoffset']
"""

###
### Internal functions
###

def _get_xml(textsub_or_spu):
    subpictures = xml.Element('subpictures')
    stream = subpictures.add('stream')
    stream.add_child(textsub_or_spu)
    return str(subpictures)


def _get_xmlfile(textsub_or_spu):
    """Write spumux XML file for the given Textsub or Spu element, and
    return the written filename.
    """
    xmldata = _get_xml(textsub_or_spu)
    xmlfile = utils.temp_file(suffix=".xml")
    xmlfile.write(xmldata)
    xmlfile.close()
    return xmlfile.name


def _mux_subs(subtitle, movie_filename, stream_id=0):
    """Run spumux to multiplex the given subtitle with an .mpg file.
    
        subtitle
            Textsub or Spu element
        movie_filename
            Name of an .mpg file to multiplex subtitle into
        stream_id
            Stream ID number to pass to spumux
    """
    # Create XML file for subtitle element
    xmlfile = _get_xmlfile(subtitle)
    # Create a temporary .mpg for the subtitled output
    #base_dir = os.path.dirname(movie_filename)
    subbed_filename = utils.temp_file(suffix=".mpg")
    # spumux xmlfile < movie_filename > subbed_filename
    spumux = cli.Command('spumux',
                     '-s%s' % stream_id,
                     xmlfile.name)
    spumux.run_redir(movie_filename, subbed_filename)
    spumux.wait()

    # Remove old file
    os.remove(movie_filename)
    # Rename temporary file to new file
    os.rename(subbed_filename, movie_filename)
    # Remove the XML file
    os.remove(xmlfile.name)


###
### Exported functions
###

def add_subpictures(movie_filename, select, image=None, highlight=None):
    """Adds PNG image subpictures to an .mpg video file to create a DVD menu.
    
        select
            Image shown as the navigational selector or "cursor"
        image
            Image shown for non-selected regions
        highlight
            Image shown when "enter" is pressed
        
    All images must be indexed, 4-color, transparent, non-antialiased PNG.
    Button regions are auto-inferred.
    """
    spu = xml.Element('spu')
    spu.set(start='0',
            force='yes',
            select=select,
            image=image,
            highlight=highlight)
    # TODO Find a good default outlinewidth
    spu.set(autooutline='infer', outlinewidth='10')
    # TODO: Support explicit button regions
    _mux_subs(spu, movie_filename)


def add_subtitles(movie_filename, sub_filenames):
    """Adds one or more subtitle files to an .mpg video file.
    
        movie_filename
            Name of .mpg file to add subtitles to
        sub_filenames
            Filename or list of filenames of subtitle
            files to include (.sub/.srt etc.)

    """
    infile = mplayer.identify(movie_filename)
    width, height = infile.scale

    # Convert sub_filenames to list if necessary
    if type(sub_filenames) == str:
        sub_filenames = [sub_filenames]
    # spumux each subtitle file with its own stream ID
    for stream_id, sub_filename in enumerate(sub_filenames):
        # <textsub attribute="value" .../>
        textsub = xml.Element('textsub')
        textsub.set(movie_fps=infile.fps,
                    movie_width=width,
                    movie_height=height,
                    filename=sub_filename)
        _mux_subs(textsub, movie_filename, stream_id)


if __name__ == '__main__':
    print "spumux XML examples"

    print "Subpicture example:"
    spu = xml.Element('spu')
    spu.add('button', name='but1', down='but2')
    spu.add('button', name='but2', up='but1')
    print _get_xml(spu)

    print "Text subtitle example:"
    textsub = xml.Element('textsub')
    textsub.set(filename='foo.sub',
                fontsize=14.0,
                font="Luxi Mono")
    print _get_xml(textsub)

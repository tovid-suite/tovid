#! /usr/bin/env python
# spumux.py

"""This module is for adding subtitles to MPEG video files using spumux.
"""
# Incomplete at the moment; run standalone for a brief demo.

__all__ = [\
    'Button',
    'Action',
    'Spu',
    'Textsub',
    'add_subpictures',
    'add_subtitles']

from libtovid.utils import temp_name, temp_file
from libtovid.xml import create_element

# spumux XML elements and valid attributes
Subpictures = create_element('subpictures', [])
Stream = create_element('stream', [])
Textsub = create_element('textsub',
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
    'movie-height'])
Button = create_element('button',
    ['name',
    'x0', 'y0', # Upper-left corner, inclusively
    'x1', 'y1', # Lower-right corner, exclusively
    'up', 'down', 'left', 'right'])
Action = create_element('action',
    ['name'])
Spu = create_element('spu',
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
    'yoffset'])


###
### Internal functions
###

def get_xml(textsub_or_spu):
    subpictures = Subpictures()
    stream = Stream()
    subpictures.add_child(stream)
    stream.add_child(textsub_or_spu)
    return str(subpictures)


def get_xmlfile(textsub_or_spu):
    """Write spumux XML file for the given Textsub or Spu element, and
    return the written filename.
    """
    xmldata = get_xml(textsub_or_spu)
    xmlfile = temp_file(suffix=".xml")
    xmlfile.write(xmldata)
    xmlfile.close()
    return xmlfile.name


def mux_subs(subtitle, movie_filename, stream_id=0):
    """Run spumux to multiplex the given subtitle with an .mpg file.
    
        subtitle:       Textsub or Spu element
        movie_filename: Name of an .mpg file to multiplex subtitle into
        stream_id:      Stream ID number to pass to spumux
    """
    # Create temporary .mpg file in the same directory
    base_dir = os.path.dirname(movie_filename)
    subbed_filename = temp_name(suffix=".mpg", dir=base_dir)
    # spumux xmlfile < movie_filename > subbed_filename
    spumux = Command('spumux',
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

def add_subpictures(movie_filename, select, image=None, highlight=None,
                    buttons=None):
    """Adds PNG image subpictures to an .mpg video file to create a DVD menu.
    
        select:    Image shown as the navigational selector or "cursor"
        image:     Image shown for non-selected regions
        highlight: Image shown when "enter" is pressed
        buttons:   List of Buttons associated with the subpicture, or
                   None to use autodetection (autooutline=infer)
        
    All images must indexed, 4-color, transparent, non-antialiased PNG.
    """
    attributes = {
        'start': 0,
        'force': 'yes',
        'select': select,
        'image': image,
        'highlight': highlight}
    spu = Spu(attributes)
    if buttons == None:
        # TODO Find a good default outlinewidth
        spu.set(autooutline=infer, outlinewidth=10)
    else:
        for button in buttons:
            spu.add_child(button)
    mux_subs(spu, movie_filename)


def add_subtitles(movie_filename, sub_filenames):
    """Adds one or more subtitle files to an .mpg video file.
    
        movie_filename: Name of .mpg file to add subtitles to
        sub_filenames:  Filename or list of filenames of subtitle
                        files to include (.sub/.srt etc.)

    """
    infile = load_media(movie_filename)
    width, height = infile.scale
    # Use attributes from movie file
    attributes = {
        'movie-fps': infile.fps,
        'movie-width': width,
        'movie-height': height}
    # Convert sub_filenames to list if necessary
    if type(sub_filenames) == str:
        sub_filenames = [sub_filenames]
    # spumux each subtitle file with its own stream ID
    for stream_id, sub_filename in enumerate(sub_filenames):
        # <textsub attribute="value" .../>
        textsub = Textsub(attributes, filename=sub_filename)
        mux_subs(textsub, movie_filename, stream_id)


if __name__ == '__main__':
    print "XML demo"
    # Basic spumux XML Elements
    spu = Spu()
    b1 = Button()
    b1.set(name='but1', down='but2')
    b2 = Button()
    b2.set(name='but2', up='but1')
    # Build hierarchy
    spu.add_child(b1)
    spu.add_child(b2)
    # Generate XML
    print "Spu xml:"
    print get_xml(spu)

    textsub = Textsub()
    textsub.set(filename='foo.sub', fontsize=14.0, font="Luxi Mono")
    print "Textsub xml:"
    print get_xml(textsub)

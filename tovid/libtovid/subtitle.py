#! /usr/bin/env python
# subtitle.py

"""This module provides an interface to the subtitling program spumux.

spumux deals with two different kinds of subtitles:

    Image-based, with one or more transparent .png files and button regions
        (used for menu navigational features)
    Text-based, rendering a .sub/.srt/etc. file in a given font and size
        (used for alternate-language dialogue subtitles)

Example usage:

    >>> menu_sub = Subtitle('spu',
            {'highlight': 'highlight.png'})
    >>> spumux(menu_sub, 'menu.mpg')

    >>> ja_sub = Subtitle('textsub',
            {'filename': 'japanese.srt', 'characterset': 'UTF-8'})
    >>> spumux(ja_sub, 'bebop.mpg')
"""

__all__ = [\
    'Button',
    'Subtitle',
    'get_xml',
    'spumux',
    'add_textsubs']

import sys
import os
import tempfile
from xml.dom import getDOMImplementation

from libtovid.cli import Command
from libtovid.opts import Option, OptionDict
from libtovid.media import load_media, MediaFile

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


BUTTON_ATTRS = {
    'name': None,
    'x0': 0,
    'y0': 0,
    'x1': 0,
    'y1': 0,
    'up': None,
    'down': None,
    'left': None,
    'right': None}

class Button:
    def __init__(self, attributes=None):
        """Create a Button with the given attributes.

            attributes: Dictionary of attributes matching those in BUTTON_ATTRS

        """
        self.attributes = {}
        if type(attributes) == dict:
            self.set_attributes(attributes)
                

    def set_attributes(self, attributes=None, **kwargs):
        """Set values for one or more Button attributes.
        
            attributes: Dictionary of attributes matching those in BUTTON_ATTRS
            kwargs:     Set specific attributes by passing keyword arguments
        
        For example:
        
            >>> button.set_attributes({'x0': 10, 'y0': 15})
            >>> button.set_attributes(x0=10, y0=10, x1=210, y1=60)

        """
        # TODO: Generalize/shorten this function so all XML-element classes
        # (like Subtitle below) can use it. (base class?)
        # Use attributes, if present
        if type(attributes) == dict:
            for key, value in attributes.iteritems():
                if key in BUTTON_ATTRS:
                    self.attributes[key] = value
        # Override with provided keyword args
        for key, value in kwargs.iteritems():
            if key in BUTTON_ATTRS:
                self.attributes[key] = value


SUB_ATTRS = {
    'spu': {
        'start': 0,
        'end': 0,
        'image': None,
        'highlight': None,
        'select': None,
        'transparent': None,
        'force': 'yes',
        'autooutline': 'infer',
        'outlinewidth': 0,
        'autoorder': 'rows', # or 'columns'
        'xoffset': 0,
        'yoffset': 0},
    'textsub': {
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
        'movie-height': None}}
    
class Subtitle:
    """A subtitle (textsub or subpicture unit).
    """
    def __init__(self, subtype='spu', attributes=None):
        """Create a subtitle of the given type, with the given attributes.

            subtype:    'spu' or 'textsub'
            attributes: Dictionary of attributes matching those in SUB_ATTRS
                        for the given subtype.

        """
        self.subtype = subtype
        self.attributes = {}
        if type(attributes) == dict:
            self.set_attributes(attributes)
        self.buttons = []

    def add_buttons(self, buttons):
        """Add Button regions to the subtitle. This only works for 'spu' type
        subtitles.
        
            buttons:  A list of Button objects to add

        """
        if self.subtype == 'spu':
            self.buttons.extend(buttons)

    def set_attributes(self, attributes=None, **kwargs):
        """Set values for one or more Subtitle attributes.
        
            attributes: Dictionary of attributes matching those in SUB_ATTRS
            kwargs:     Set specific attributes by passing keyword arguments
        
        Use an underscore in place of hyphens in attribute names.
        """
        # Use attributes, if present
        if type(attributes) == dict:
            for key, value in attributes.iteritems():
                if key in SUB_ATTRS[self.subtype]:
                    self.attributes[key] = value
        # Override with provided keyword args
        for key, value in kwargs.iteritems():
            if key in SUB_ATTRS[self.subtype]:
                self.attributes[key] = value


def get_xml(subtitle):
    """Returns a string containing formatted spumux XML for the given Subtitle.
    
        subtitle:  A Subtitle object to generate XML from

    """
    # subpictures element (top-level XML element for spumux)
    dom = getDOMImplementation()
    doc = dom.createDocument(None, "subpictures", None)
    root = doc.firstChild
    # stream element
    stream = doc.createElement("stream")
    root.appendChild(stream)
    # textsub or spu element
    sub = doc.createElement(subtitle.subtype)
    stream.appendChild(sub)
    # Set attributes for the textsub or spu element
    for key, value in subtitle.attributes.iteritems():
        sub.setAttribute(key, str(value))
    # Add buttons for spu elements
    if subtitle.subtype == 'spu' and subtitle.buttons:
        for button in subtitle.buttons:
            btn = doc.createElement('button')
            for key, value in button.attributes.iteritems():
                btn.setAttribute(key, str(value))
            sub.appendChild(btn)
    # Return formatted XML
    return doc.toprettyxml()


def spumux(subtitle, movie_filename, stream_id=0):
    """Run spumux to multiplex the given subtitle with an .mpg file.
    
        subtitle:       Subtitle object
        movie_filename: Name of an .mpg file to multiplex subtitle into
        stream_id:      Stream ID number to pass to spumux
    """
    # Write the XML to a temporary file
    xmldata = get_xml(subtitle)
    print "spumux XML file:"
    print xmldata
    xmlfile = mktempstream(suffix=".xml")
    xmlfile.write(xmldata)
    xmlfile.close()

    # Create temporary .mpg file in the same directory
    base_dir = os.path.dirname(movie_filename)
    subbed_filename = mktempname(suffix=".mpg", dir=base_dir)
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


def add_textsubs(movie_filename, sub_filenames):
    """Adds text subtitle files to an .mpg video file.
    
        movie_filename:  Name of .mpg to add subtitles to
        sub_filenames:   Name of subtitle files to include (.sub/.srt etc.)

    """
    infile = load_media(movie_filename)
    width, height = infile.scale
    attributes = {
        'movie-fps': infile.fps,
        'movie-width': width,
        'movie-height': height,
    }
    # spumux each subtitle file with its own stream ID
    for stream_id, sub_filename in enumerate(sub_files):
        subtitle = Subtitle('textsub', attributes)
        spumux(subtitle, movie_filename, stream_id)


if __name__ == '__main__':
    pass

#! /usr/bin/env python
# spumux.py

"""This module is for adding subtitles to MPEG video files using spumux.
"""
# Incomplete at the moment; run standalone for a brief demo.

__all__ = [\
    'Element',
    'Button',
    'Action',
    'SPU',
    'Textsub',
    'add_subpictures',
    'add_subtitles']

from libtovid.utils import temp_name, temp_file
from xml.dom import getDOMImplementation


###
### Classes
###


class Element (object):
    """Base class XML element, with name and attributes.
    
    Valid attributes for the element are defined in class variable ATTRIBUTES.
    Attributes may be set in the constructor, or by calling set() with a
    dictionary and/or attribute=value keywords.
    
    Use add_child(element) to create a hierarchy of Elements.
    """
    # List of valid attributes for this element; override in derived classes
    NAME = 'empty'
    ATTRIBUTES = []
    
    def __init__(self, attributes=None, **kwargs):
        """Create a new Element with the given attributes.
        
            attributes: Dictionary of attributes matching those in ATTRIBUTES
            kwargs:     Keyword arguments for setting specific attributes
                        NOTE: Hyphenated attribute names can't be used here
        """
        self.attributes = {}
        self.children = []
        # Set attributes from those provided
        self.set(attributes, **kwargs)
    
    def set(self, attributes=None, **kwargs):
        """Set values for one or more attributes.
        
            attributes: Dictionary of attributes and values
            kwargs:     Keyword arguments for setting specific attributes
                        (Note: Hyphenated attribute names aren't allowed here)
        
        All attributes must match those listed in ATTRIBUTES; a KeyError
        is raised for non-valid attributes.
        """
        # Use attributes, if present (make a copy to avoid changing original)
        if type(attributes) == dict:
            attributes = attributes.copy()
        else:
            attributes = {}
        # Override with any provided keyword arguments
        attributes.update(kwargs)
        # Set all attributes, raising error on invalid attribute names
        for key, value in attributes.iteritems():
            if key in self.ATTRIBUTES:
                self.attributes[key] = value
            else:
                raise KeyError("'%s' element has no attribute '%s'" %
                               (self.NAME, key))

    def add_child(self, element):
        """Add the given Element as a child of this Element."""
        assert isinstance(element, Element)
        self.children.append(element)

    def dom_element(self, document):
        """Add the Element and all its children to the given xml.dom Document.
        Return the xml.dom Element that was added (a different Element class!)
        """
        elem = document.createElement(self.NAME)
        # Set all attributes
        for key, value in self.attributes.iteritems():
            if value != None:
                elem.setAttribute(key, str(value))
        # Append all children
        for child in self.children:
            elem.appendChild(child.dom_element(document))
        return elem

    def __str__(self):
        text = '<%s' % self.NAME
        for attribute, value in self.attributes.items():
            text += ' %s="%s"' % (attribute, value)
        text += '/>'
        return text


def create_element(name, valid_attributes):
    """Create a new XML Element class, having the given name and
    valid attributes.
    """
    return type(name, (Element,),
                {'name': name, 'ATTRIBUTES': valid_attributes})


Textsub = create_element('textsub', [\
    'filename',
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

Button = create_element('button', [\
    'name',
    'x0', 'y0', 'x1', 'y1',
    'up', 'down', 'left', 'right'])

Action = create_element('action', ['name'])

SPU = create_element('spu', [\
    'start',
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
    """Return a string of spumux XML for the given Textsub or SPU element.
    """
    dom = getDOMImplementation()
    # Document root with subpictures element
    doc = dom.createDocument(None, 'subpictures', None)
    root = doc.firstChild
    # Add stream element
    stream = doc.createElement("stream")
    root.appendChild(stream)
    # Add remaining elements (SPU or Textsub)
    stream.appendChild(textsub_or_spu.dom_element(doc))
    # Return formatted XML
    return doc.toprettyxml(indent='    ')


def get_xmlfile(textsub_or_spu):
    """Write spumux XML file for the given Textsub or SPU element, and
    return the written filename.
    """
    xmldata = get_xml(textsub_or_spu)
    xmlfile = temp_file(suffix=".xml")
    xmlfile.write(xmldata)
    xmlfile.close()
    return xmlfile.name


def mux_subs(subtitle, movie_filename, stream_id=0):
    """Run spumux to multiplex the given subtitle with an .mpg file.
    
        subtitle:       Textsub or SPU element
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
    Button regions are auto-inferred from the images; explicit button region
    configuration may be available in the future.
    """
    attributes = {
        'start': 0,
        'force': 'yes',
        'select': select,
        'image': image,
        'highlight': highlight}
    spu = SPU(attributes)
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
    spu = SPU()
    b1 = Button()
    b1.set(name='but1', down='but2')
    b2 = Button()
    b2.set(name='but2', up='but1')
    # Build hierarchy
    spu.add_child(b1)
    spu.add_child(b2)
    # Generate XML
    print "SPU xml:"
    print get_xml(spu)

    textsub = Textsub()
    textsub.set(filename='foo.sub', fontsize=14.0, font="Luxi Mono")
    print "Textsub xml:"
    print get_xml(textsub)


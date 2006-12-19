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
    'add_menusubs',
    'add_textsubs']

from libtovid.utils import temp_name, temp_file
from xml.dom import getDOMImplementation

# TODO: Move some of the xml.dom ugliness into the Element base class, then
# hide it away somewhere...
class Element:
    """Base class XML element, with name and attributes.
    
    Valid attributes for the element are defined in class variable ATTRIBUTES.
    Attributes may be set in the constructor, or by calling set() with a
    dictionary and/or attribute=value keywords.
    
    Use add_child(element) to create a hierarchy of Elements.
    """
    # List of valid attributes for this element; override in derived classes
    ATTRIBUTES = []
    
    def __init__(self, name, attributes=None, **kwargs):
        """Create a new Element with the given name and optional attributes.
        
            name:       Identifying name of the Element
            attributes: Dictionary of attributes matching those in ATTRIBUTES
            kwargs:     Keyword arguments for setting specific attributes
                        NOTE: Hyphenated attribute names can't be used here
        """
        self.name = name
        self.attributes = {}
        self.children = []
        # Set attributes from those provided
        self.set(attributes, **kwargs)
    
    def set(self, attributes=None, **kwargs):
        """Set values for one or more attributes.
        
            attributes: Dictionary of attributes and values
            kwargs:     Keyword arguments for setting specific attributes
                        NOTE: Hyphenated attribute names can't be used here
        
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
                               (self.name, key))

    def add_child(self, element):
        """Add the given Element as a child of this Element."""
        assert isinstance(element, Element)
        self.children.append(element)

    def dom_element(self, document):
        """Add the Element and all its children to the given xml.dom Document.
        Return the xml.dom Element that was added (a different Element class!)
        """
        elem = document.createElement(self.name)
        # Set all attributes
        for key, value in self.attributes.iteritems():
            if value != None:
                elem.setAttribute(key, str(value))
        # Append all children
        for child in self.children:
            elem.appendChild(child.dom_element(document))
        return elem

    def get_xml(self):
        """Return a string containing formatted XML for the current Element.
        """
        # TODO
        pass


class Textsub (Element):
    """Textsub element, for defining text-based subtitle overlays.
    """
    ATTRIBUTES = [
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
        'movie-height']

    def __init__(self, attributes=None, **kwargs):
        Element.__init__(self, 'textsub', attributes, **kwargs)


class Button (Element):
    ATTRIBUTES = [
        'name',
        'x0', 'y0', 'x1', 'y1',
        'up', 'down', 'left', 'right']
    
    def __init__(self, attributes=None, **kwargs):
        Element.__init__(self, 'button', attributes, **kwargs)


class Action (Element):
    ATTRIBUTES = ['name']
    def __init__(self, attributes=None, **kwargs):
        Element.__init__(self, 'action', attributes, **kwargs)


class SPU (Element):
    """SubPicture Unit element, for defining image-based subtitle overlays.
    """
    ATTRIBUTES = [
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
        'yoffset']

    def __init__(self, attributes=None, **kwargs):
        Element.__init__(self, 'spu', attributes, **kwargs)

###
### What a mess!
###

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
    stream.appendChild(element.dom_element(doc))
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
### Main API
###

def add_menusubs(movie_filename, select, image=None, highlight=None):
    """Adds PNG image subtitles to an .mpg video file to create a DVD menu.
    
        select:    Image shown as the navigational selector or "cursor"
        image:     Image shown for non-selected regions
        highlight: Image shown when "enter" is pressed
        
    All images must indexed, 4-color, transparent, non-antialiased PNG.
    Button regions are auto-inferred from the images; explicit button region
    configuration may be available in the future.
    """
    # TODO: Support explicit button regions, actions
    infile = load_media(movie_filename)
    attributes = {
        'start': 0.00,
        'force': 'yes',
        'image': image,
        'select': select,
        'highlight': highlight,
        'autooutline': 'infer',
        'outlinewidth': 10} # TODO Find a good default outlinewidth
    spu = SPU(attributes)
    mux_subs(spu, movie_filename)

def add_textsubs(movie_filename, sub_filenames):
    """Adds text subtitle files to an .mpg video file.
    
        movie_filename:  Name of .mpg to add subtitles to
        sub_filenames:   Name of subtitle files to include (.sub/.srt etc.)

    """
    infile = load_media(movie_filename)
    width, height = infile.scale
    # spumux textsub attributes
    attributes = {
        'movie-fps': infile.fps,
        'movie-width': width,
        'movie-height': height}
    # spumux each subtitle file with its own stream ID
    for stream_id, sub_filename in enumerate(sub_files):
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


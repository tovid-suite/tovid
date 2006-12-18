#! /usr/bin/env python
# spumux.py

from xml.dom import getDOMImplementation

class Element:
    """Base class XML element, with name and attributes.
    """
    # List of valid attributes for this element; override in derived classes
    ATTRIBUTES = []
    
    def __init__(self, name, attributes=None):
        """Create a new Element with the given name and optional attributes.
        
            name:       Identifying name of the Element
            attributes: Dictionary of attributes matching those in ATTRIBUTES
        
        """
        self.name = name
        self.attributes = {}
        self.children = []
        if type(attributes) == dict:
            self.set(attributes)
    
    def set(self, attributes=None, **kwargs):
        """Set values for one or more attributes.
        
            attributes: Dictionary of attributes and values
            kwargs:     Keyword arguments for setting specific attributes
        
        All attributes must match those listed in ATTRIBUTES.    
        """
        # TODO: Cleanup/simplify
        # Use attributes, if present
        if type(attributes) == dict:
            for key, value in attributes.iteritems():
                if key in self.ATTRIBUTES:
                    self.attributes[key] = value
                else:
                    raise KeyError("'%s' element has no attribute '%s'" %
                                   (self.name, key))
        # Override with any provided keyword arguments
        for key, value in kwargs.iteritems():
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
            elem.setAttribute(key, str(value))
        # Append all children
        for child in self.children:
            elem.appendChild(child.dom_element(document))
        return elem


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

    def __init__(self, attributes=None):
        Element.__init__(self, 'textsub', attributes)


class Button (Element):
    ATTRIBUTES = [
        'name',
        'x0', 'y0', 'x1', 'y1',
        'up', 'down', 'left', 'right']
    
    def __init__(self, attributes=None):
        Element.__init__(self, 'button', attributes)


class Action (Element):
    ATTRIBUTES = ['name']
    def __init__(self, attributes=None):
        Element.__init__(self, 'action', attributes)


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
        'force',         # 'yes'
        'autooutline',   # 'infer'
        'outlinewidth',
        'autoorder',     # 'rows' or 'columns'
        'xoffset',
        'yoffset']

    def __init__(self, attributes=None):
        Element.__init__(self, 'spu', attributes)

def get_xml(element):
    """Return XML for a spumux Element hierarchy"""
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

if __name__ == '__main__':
    # Basic spumux XML Elements
    spu = SPU()
    b1 = Button()
    b1.set(name='but1', down='but2')
    b2 = Button()
    b2.set(name='but2', up='but1')
    a1 = Action()
    a2 = Action()
    # Build hierarchy
    spu.add_child(b1)
    spu.add_child(b2)
    spu.add_child(a1)
    spu.add_child(a2)
    # Generate XML
    print "SPU xml:"
    print get_xml(spu)

    textsub = Textsub()
    textsub.set(filename='foo.sub')
    print "Textsub xml:"
    print get_xml(textsub)

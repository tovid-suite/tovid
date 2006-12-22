#! /usr/bin/env python
# xml.py

__all__ = [\
    'Element',
    'create_element']

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
    INDENT = 0
    
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


    def __str__(self):
        text = '<%s' % self.NAME
        for attribute, value in self.attributes.items():
            text += ' %s="%s"' % (attribute, value)
        if self.children:
            text += '>'
            for child in self.children:
                text += '\n%s' % child
            text += '\n</%s>' % self.NAME
        else:
            text += '/>'
        return text


def create_element(name, valid_attributes):
    """Create a new Element subclass, having the given name and
    list of valid attributes.
    """
    return type(name, (Element,),
                {'NAME': name, 'ATTRIBUTES': valid_attributes})


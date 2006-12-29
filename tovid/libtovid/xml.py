#! /usr/bin/env python
# xml.py

"""This module is for defining XML elements and their valid attributes.

To define an element class Video, which may have attributes called 'file'
and 'length', do:

    >>> Video = create_element('video', ['file', 'length'])

Video is now an Element subclass, which can be used to instantiate new video
elements:

    >>> video1 = Video(file='Brian.mpg')
    >>> video2 = Video(file='Judith.mpg')

Attributes may be changed via the set method:

    >>> video1.set(length=10)

To get an XML representation of an Element:

    >>> print video1
    <video file="Brian.mpg" length="10"/>
    >>> print video2
    <video file="Judith.mpg"/>

To create an Element class with no attributes, use the empty list:

    >>> Group = create_element('group', [])
    >>> group = Group()
    >>> print group
    <group/>

Elements can contain other elements, to create a hierarchy:

    >>> group.add_child(video1)
    >>> group.add_child(video2)
    >>> print group
    <group>
      <video file="Brian.mpg" length="10"/>
      <video file="Judith.mpg"/>
    </group>

An Element may also contain plain-text content:

    >>> video1.content = "Always look on the bright side of life"
    >>> print video1
    <video file="Brian.mpg" length="10">Always look on the bright side of life
    </video>

See spumux.py for additional examples.
"""

__all__ = [\
    'Element',
    'format',
    'create_element']

class Element (object):
    """An XML element, with name and attributes.
    
    Valid attributes for the element are defined in class variable ATTRIBUTES.
    Attribute values may be set in the constructor, or by calling set() with a
    dictionary and/or attribute=value keywords.
    
    Use add_child(element) to create a hierarchy of Elements.
    """
    NAME = 'empty'    # Element name (appears in xml tags <name>...</name>)
    ATTRIBUTES = []   # Valid attributes for the element
    
    def __init__(self, parent=None, content='', attributes=None, **kwargs):
        """Create a new Element with the given attributes.
        
            parent:     Parent of this Element
            content:    Text content of the Element
            attributes: Dictionary of attributes matching those in ATTRIBUTES
            kwargs:     Keyword arguments for setting specific attributes
                        (NOTE: Hyphenated attribute names can't be used here)
        """
        if parent:
            parent.add_child(self)
        self.content = content
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
        # Override kwargs with attributes, if provided
        if type(attributes) == dict:
            kwargs.update(attributes)
        # Set all attributes, raising error on invalid attribute names
        for key, value in kwargs.iteritems():
            if key in self.ATTRIBUTES:
                self.attributes[key] = value
            else:
                raise KeyError("'%s' element has no attribute '%s'" %
                               (self.NAME, key))

    def add_child(self, element):
        """Add the given Element as a child of this Element."""
        assert isinstance(element, Element)
        self.children.append(element)

    def xml(self):
        """Return a string containing raw XML for the Element."""
        text = '<%s' % self.NAME
        # Iterate through valid attributes so ordering is preserved
        for key in self.ATTRIBUTES:
            if key in self.attributes:
                text += ' %s="%s"' % (key, self.attributes[key])
        # If children or text content are present, add them with a closing tag
        if self.children or self.content:
            text += '>'
            text += str(self.content)
            for child in self.children:
                text += child.xml()
            text += '</%s>' % self.NAME
        # No children or content; use "empty" element closing tag
        else:
            text += '/>'
        return text

    def __str__(self):
        """Return a string containing formatted XML for the Element."""
        return format(self.xml())


def format(xml_text):
    """Return the given XML text string, formatted with appropriate
    line-breaks and indentation.
    """
    indent = -1
    result = ''
    text = xml_text.replace('<', '\n<').lstrip('\n')
    for line in text.split('\n'):
        if not line.startswith('</'):
            indent += 1
        result += '  ' * indent + line + '\n'
        if line.startswith('</') or line.endswith('/>'):
            indent -= 1
    return result.rstrip('\n')


def create_element(name, valid_attributes):
    """Create a new Element subclass.

        name:              Element name
        valid_attributes:  List of valid attribute names

    Returns a subclass of Element; assign the return value of this function
    to a variable to create your own Element subclass, which may then be used
    to instantiate new Elements.
    """
    return type(name, (Element,),
                {'NAME': name, 'ATTRIBUTES': valid_attributes})


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

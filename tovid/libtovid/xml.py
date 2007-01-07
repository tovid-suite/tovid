#! /usr/bin/env python
# xml.py

"""This module is for defining XML elements and attributes, and for creating
element hierarchies.

To create a new element, use the Element class constructor, providing at least
the element name:

    >>> video = Element('video')

To see an XML representation of the Element:

    >>> print video
    <video/>

Since this is an empty element with no attributes yet, it's pretty boring.
You can add or change attributes using the set method:

    >>> video.set(file="Brian.mpg")
    >>> print video
    <video file="Brian.mpg"/>

To add children to an element, use the add method:

    >>> length = video.add('length', '15')
    >>> print video
    <video file="Brian.mpg">
      <length>15
      </length>
    </video>
    
See spumux.py for additional examples.
"""

__all__ = [\
    'Element',
    'format']

class Element (object):
    """A named XML element having optional content, attributes, and children.
    
    Attribute values may be set in the constructor, or by calling set() with a
    dictionary and/or attribute=value keywords.
    
    Use add() or add_child() to create a hierarchy of Elements.
    """
    
    def __init__(self, name, content='', attributes=None, **kwargs):
        """Create a new Element with the given attributes.
        
            name:       Name of the Element
            content:    Text content of the Element
            attributes: Dictionary of attributes and values
            kwargs:     Keyword arguments for setting specific attributes
        """
        self.name = name
        self.content = content
        self.attributes = {}
        self.children = []
        # Set attributes from those provided
        self.set(attributes, **kwargs)

    def set(self, attributes=None, **kwargs):
        """Set values for one or more attributes.
        
            attributes: Dictionary of attributes and values
            kwargs:     Keyword arguments for setting specific attributes
        
        Underscores in attribute names are converted to hyphens. If you don't
        like this behavior, please implement a workaround :-)
        """
        # Override kwargs with attributes, if provided
        if type(attributes) == dict:
            kwargs.update(attributes)
        # Set attribute values; convert underscores to hyphens
        for key, value in kwargs.iteritems():
            key = key.replace('_', '-')
            self.attributes[key] = value

    def add(self, child_name, content='', **kwargs):
        """Create and add a new child Element by providing its name, content,
        and attributes. Return the newly-added Element.
        
            child_name:  String name of child element
            content:     String content of child element
            kwargs:      Keyword arguments for setting attributes
        
        This is a convenience function for creating and adding children
        on-the-fly.
        """
        child = Element(child_name, content, kwargs)
        self.add_child(child)
        return child

    def add_child(self, element):
        """Add the given Element as a child of this Element."""
        assert isinstance(element, Element)
        self.children.append(element)

    def xml(self):
        """Return a string containing raw (unformatted) XML for the Element."""
        text = '<%s' % self.name
        for key, value in self.attributes.items():
            text += ' %s="%s"' % (key, value)
        # If the element is empty, close the tag
        if self.content == '' and len(self.children) == 0:
            text += '/>'
        # Add content and/or children, followed by a normal closing tag
        else:
            text += '>'
            text += str(self.content)
            for child in self.children:
                text += child.xml()
            text += '</%s>' % self.name
        return text

    def __str__(self):
        """Return a string containing formatted XML for the Element."""
        return format(self.xml())


def format(xml_text, tab_width=2):
    """Return the given XML text string, formatted with appropriate
    line-breaks and indentation.
    """
    indent = -1
    result = ''
    # Add newlines before each tag to facilitate splitting
    text = xml_text.replace('<', '\n<').lstrip('\n')
    for line in text.splitlines():
        if not line.startswith('</'):
            indent += 1
        result += ' ' * tab_width * indent + line + '\n'
        if line.startswith('</') or line.endswith('/>'):
            indent -= 1
    return result.rstrip('\n')


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

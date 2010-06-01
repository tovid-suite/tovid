"""This module is for defining XML elements and attributes, and for creating
element hierarchies.

To create a new element, use the `Element` constructor, providing at
least the element name::

    >>> video = Element('video')

To see an XML representation of the Element::

    >>> print(video)
    <video></video>

Since this is an empty element with no attributes yet, it's pretty boring.
You can add or change attributes using the set method::

    >>> video.set(file="Brian.mpg")
    >>> print(video)
    <video file="Brian.mpg"></video>

To add children to an element, use the add method::

    >>> length = video.add('length', '15')
    >>> print(video)
    <video file="Brian.mpg">
      <length>15</length>
    </video>

See `libtovid.author` and `libtovid.backend.spumux` for additional
examples.
"""

__all__ = ['Element']

class Element (object):
    """A named XML element having optional content, attributes, and children.

    Attribute values may be set in the constructor, or by calling `set` with a
    dictionary and/or attribute=value keywords.

    Use `add` or `add_child` to create a hierarchy of Elements.
    """
    def __init__(self, name, content='', **attributes):
        """Create a new Element with the given attributes.

            name
                Name of the Element
            content
                Text content of the Element
            attributes
                Keyword=value for specific attributes
        """
        self.name = name
        self.content = content
        self.attributes = {}
        self.children = []
        # Set attributes from those provided
        self.set(**attributes)


    def set(self, **attributes):
        """Set values for one or more attributes.

            attributes
                Keyword arguments for setting specific attributes

        Underscores in attribute names are converted to hyphens. If you don't
        like this behavior, please suggest a workaround :-)
        """
        # Set attribute values; convert underscores to hyphens
        for key, value in attributes.iteritems():
            key = key.replace('_', '-')
            self.attributes[key] = value


    def add(self, child_name, content='', **attributes):
        """Create and add a new child Element by providing its name, content,
        and attributes. Return the newly-added Element.

            child
                String name of child element
            content
                String content of child element
            attributes
                Keyword arguments for setting child's attributes

        This is a convenience function for creating and adding children
        on-the-fly.
        """
        child = Element(child_name, content, **attributes)
        self.children.append(child)
        return child


    def add_child(self, element):
        """Add the given Element as a child of this Element.
        """
        assert isinstance(element, Element)
        self.children.append(element)


    def xml(self, indent_level=0):
        """Return formatted XML for this Element and all descendants.
        """
        indent = '  ' * indent_level
        # No children; write a single line
        if len(self.children) == 0:
            text = indent + self._open() + self.content + self._close() + '\n'
        # If children, write an indented block
        else:
            text = indent + self._open() + self.content + '\n'
            for child in self.children:
                text += child.xml(indent_level + 1)
            text += indent + self._close() + '\n'
        return text


    def __str__(self):
        """Return a string containing formatted XML for the Element.
        """
        return self.xml().rstrip('\n')


    def _open(self):
        """Return the XML opening tag for the Element.
        """
        attribs = ''
        for key, value in self.attributes.items():
            attribs += ' %s="%s"' % (key, value)
        return '<' + self.name + attribs + '>'


    def _close(self):
        """Return the XML closing tag for the Element.
        """
        return '</' + self.name + '>'



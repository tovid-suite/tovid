#! /usr/bin/env python
# Element.py


# ===========================================================
class Element:
    """A Disc, Menu, or Video with associated options.

    Create an element by calling Element() with the type of element desired,
    along with an identifying name. For example:

        elem = Element('Menu', "Movie trailers")
    
    The Element is automatically filled with default values for the
    corresponding TDL element ('Menu'); these may then be overridden by
    user-defined values."""

    # TODO: Find a more efficient way to create new Elements filled with default
    # values. (Maybe fill a module-level dictionary once at runtime, then copy it
    # when a new Element is created?)
    
    def __init__(self, tag, name):
        """Create a TDL element of the given type, and with the given (unique)
        name, filled with default values for that element type."""
        self.tag = tag
        self.name = name
        if not element_defs.has_key(tag):
            log.error("TDL.Element(): unknown element '%s'" % tag)

        else:
            # Fill a dictionary of options with their default values
            self.options = {}
            for key, optdef in element_defs[tag].iteritems():
                self.options[key] = copy.copy(optdef.default)

        self.parents = []
        self.children = []


    def set(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        """Set the given option (with/without leading '-') to the given value."""
        # Consider: Treat value=='' as resetting to default value?
        self.options[key.lstrip('-')] = copy.copy(value)
    
    def __getitem__(self, key):
        """Get the value of the given option."""
        if key in self.options:
            return self.options[key]
        else:
            log.error("'%s' is not a valid option for %s elements" % \
                (key, self.tag))
            # TODO: Log level for developer hints? (like the following)
            log.error("Please add an OptionDef to libtovid/%s.py" % self.tag)
            sys.exit()

    def get(self, key):
        return self.__getitem__(key)

    def tdl_string(self):
        """Format element as a TDL-compliant string and return it."""
        tdl = "%s \"%s\"\n" % (self.tag, self.name)
        for key, value in self.options.iteritems():
            # For boolean options, print Trues and omit Falses
            if value.__class__ == bool:
                if value == True:
                    tdl += "    %s\n" % key
                else:
                    pass
            # If value has spaces, quote it
            elif value.__class__ == str and ' ' in value:
                tdl += "    %s \"%s\"\n" % (key, value)
            # Otherwise, don't
            else:
                tdl += "    %s %s\n" % (key, value)
        return tdl


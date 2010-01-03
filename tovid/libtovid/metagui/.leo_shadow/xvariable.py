#@+leo-ver=4-thin
#@+node:eric.20090722212922.2774:@shadow variable.py
"""Contains Tkinter Variable subclasses for List and Dict variables.

This module exists to supplement the built-in Tkinter Variable types,
which do not provide ``list`` and ``dict`` equivalents.
"""

__all__ = [
    'ListVar',
    'DictVar',
    'VAR_TYPES',
]

# Python < 3.x
try:
    import Tkinter as tk
# Python 3.x
except ImportError:
    import tkinter as tk

# Absolute imports
from libtovid.odict import Odict

#@+others
#@+node:eric.20090722212922.2776:class ListVar
class ListVar (tk.Variable):
    """A tk Variable suitable for associating with Listboxes.
    """
    #@    @+others
    #@+node:eric.20090722212922.2777:__init__
    def __init__(self, master=None, items=None):
        """Create a ListVar with a given master and initial list of items.
        """
        tk.Variable.__init__(self, master)
        if items:
            self.set(items)
        self.callbacks = {'insert': [], 'remove': [], 'select': []}


    #@-node:eric.20090722212922.2777:__init__
    #@+node:eric.20090722212922.2778:get
    def get(self):
        """Get the entire list of values.
        """
        return list(tk.Variable.get(self))


    #@-node:eric.20090722212922.2778:get
    #@+node:eric.20090722212922.2779:set
    def set(self, new_list):
        """Set the entire list of values.
        """
        tk.Variable.set(self, tuple(new_list))


    #@-node:eric.20090722212922.2779:set
    #@+node:eric.20090722212922.2780:__getitem__
    def __getitem__(self, index):
        """Get a list value using list-index syntax: ``listvar[index]``.
        """
        return self.get()[index]


    #@-node:eric.20090722212922.2780:__getitem__
    #@+node:eric.20090722212922.2781:__setitem__
    def __setitem__(self, index, value):
        """Set a list value using list-index syntax: ``listvar[index] = value``.
        """
        current = self.get()
        current[index] = value
        self.set(current)


    #@-node:eric.20090722212922.2781:__setitem__
    #@+node:eric.20090722212922.2782:insert
    def insert(self, index, item):
        """Insert an item into the list at the specified index.
        """
        items = self.get()
        items.insert(index, item)
        self.set(items)


    #@-node:eric.20090722212922.2782:insert
    #@+node:eric.20090722212922.2783:remove
    def remove(self, item):
        """Remove the item from the list, if it exists.
        """
        items = self.get()
        items.remove(item)
        self.set(items)


    #@-node:eric.20090722212922.2783:remove
    #@+node:eric.20090722212922.2784:append
    def append(self, item):
        """Append an item to the list.
        """
        self.insert(-1, item)


    #@-node:eric.20090722212922.2784:append
    #@+node:eric.20090722212922.2785:pop
    def pop(self, index=-1):
        """Pop an item off the list and return it.
        """
        items = self.get()
        item = items.pop(index)
        self.set(items)
        return item


    #@-node:eric.20090722212922.2785:pop
    #@+node:eric.20090722212922.2786:index
    def index(self, value):
        """Return the index of the given value.
        """
        items = self.get()
        return items.index(value)


    #@-node:eric.20090722212922.2786:index
    #@+node:eric.20090722212922.2787:count
    def count(self):
        """Return the number of items in the list.
        """
        return len(self.get())


    #@-node:eric.20090722212922.2787:count
    #@-others
#@-node:eric.20090722212922.2776:class ListVar
#@+node:eric.20090722212922.2788:class DictVar
class DictVar (tk.Variable):
    """A tk Variable for storing a dictionary of values.
    """
    #@    @+others
    #@+node:eric.20090722212922.2789:__init__
    def __init__(self, master=None, keys=None, values=None):
        """Create a DictVar with a given master and initial keys/values.
        """
        tk.Variable.__init__(self, master)
        self.set(Odict(keys, values))


    #@-node:eric.20090722212922.2789:__init__
    #@+node:eric.20090722212922.2790:__getitem__
    def __getitem__(self, key):
        """Get a dict value using keyword syntax: ``dictvar[key]``.
        """
        return self.get()[key]


    #@-node:eric.20090722212922.2790:__getitem__
    #@+node:eric.20090722212922.2791:__setitem__
    def __setitem__(self, key, value):
        """Set a dict value using keyword syntax: ``dictvar[key] = value``.
        """
        current = self.get()
        current[key] = value
        self.set(current)


    #@-node:eric.20090722212922.2791:__setitem__
    #@+node:eric.20090722212922.2792:get
    def get(self):
        """Return the entire dictionary of keys/values as an Odict.
        """
        # Convert from tuple
        tup = tk.Variable.get(self)
        if tup:
            keys, values = zip(*tup)
        else:
            keys, values = [], []
        return Odict(keys, values)


    #@-node:eric.20090722212922.2792:get
    #@+node:eric.20090722212922.2793:set
    def set(self, new_dict):
        """Set the entire dictionary of keys/values. If new_dict is empty, or
        is not a ``dict`` or ``Odict``, an empty ``dict`` is used.
        """
        if not isinstance(new_dict, dict) and not isinstance(new_dict, Odict):
            new_dict = {}
        if not new_dict:
            new_dict = {}
        # Convert to a tuple of (key, value) pairs
        tup = tuple([(key, value) for key, value in new_dict.items()])
        tk.Variable.set(self, tup)

    #@-node:eric.20090722212922.2793:set
    #@-others
#@-node:eric.20090722212922.2788:class DictVar
#@-others

# Map python types to Tkinter variable types
VAR_TYPES = {
    str: tk.StringVar,
    bool: tk.BooleanVar,
    int: tk.IntVar,
    float: tk.DoubleVar,
    list: ListVar,
    dict: DictVar,
}
#@-node:eric.20090722212922.2774:@shadow variable.py
#@-leo

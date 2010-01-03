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

class ListVar (tk.Variable):
    """A tk Variable suitable for associating with Listboxes.
    """
    def __init__(self, master=None, items=None):
        """Create a ListVar with a given master and initial list of items.
        """
        tk.Variable.__init__(self, master)
        if items:
            self.set(items)
        self.callbacks = {'insert': [], 'remove': [], 'select': []}


    def get(self):
        """Get the entire list of values.
        """
        return list(tk.Variable.get(self))


    def set(self, new_list):
        """Set the entire list of values.
        """
        tk.Variable.set(self, tuple(new_list))


    def __getitem__(self, index):
        """Get a list value using list-index syntax: ``listvar[index]``.
        """
        return self.get()[index]


    def __setitem__(self, index, value):
        """Set a list value using list-index syntax: ``listvar[index] = value``.
        """
        current = self.get()
        current[index] = value
        self.set(current)


    def insert(self, index, item):
        """Insert an item into the list at the specified index.
        """
        items = self.get()
        items.insert(index, item)
        self.set(items)


    def remove(self, item):
        """Remove the item from the list, if it exists.
        """
        items = self.get()
        items.remove(item)
        self.set(items)


    def append(self, item):
        """Append an item to the list.
        """
        self.insert(-1, item)


    def pop(self, index=-1):
        """Pop an item off the list and return it.
        """
        items = self.get()
        item = items.pop(index)
        self.set(items)
        return item


    def index(self, value):
        """Return the index of the given value.
        """
        items = self.get()
        return items.index(value)


    def count(self):
        """Return the number of items in the list.
        """
        return len(self.get())


class DictVar (tk.Variable):
    """A tk Variable for storing a dictionary of values.
    """
    def __init__(self, master=None, keys=None, values=None):
        """Create a DictVar with a given master and initial keys/values.
        """
        tk.Variable.__init__(self, master)
        self.set(Odict(keys, values))


    def __getitem__(self, key):
        """Get a dict value using keyword syntax: ``dictvar[key]``.
        """
        return self.get()[key]


    def __setitem__(self, key, value):
        """Set a dict value using keyword syntax: ``dictvar[key] = value``.
        """
        current = self.get()
        current[key] = value
        self.set(current)


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


# Map python types to Tkinter variable types
VAR_TYPES = {
    str: tk.StringVar,
    bool: tk.BooleanVar,
    int: tk.IntVar,
    float: tk.DoubleVar,
    list: ListVar,
    dict: DictVar,
}

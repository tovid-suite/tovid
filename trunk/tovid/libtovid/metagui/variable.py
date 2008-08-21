#! /usr/bin/env python
# variable.py

"""Contains Tkinter Variable subclasses for List and Dict variables.
"""

__all__ = [
    'ListVar',
    'DictVar',
]

import Tkinter as tk

### --------------------------------------------------------------------
### Tkinter Variable subclasses
### --------------------------------------------------------------------

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


    def get(self):
        """Get the entire list of values.
        """
        return list(tk.Variable.get(self))


    def set(self, new_list):
        """Set the entire list of values.
        """
        tk.Variable.set(self, tuple(new_list))


    def remove(self, item):
        """Remove the item from the list, if it exists.
        """
        items = self.get()
        index = items.index(item)
        items.remove(item)
        self.set(items)


    def pop(self, index=-1):
        """Pop an item off the list and return it.
        """
        items = self.get()
        item = items.pop(index)
        self.set(items)
        return item


    def append(self, item):
        """Append an item to the list.
        """
        self.insert(-1, item)


    def insert(self, index, item):
        """Insert an item into the list at the specified index.
        """
        items = self.get()
        items.insert(index, item)
        self.set(items)


    def count(self):
        """Return the number of items in the list.
        """
        return len(self.get())


### --------------------------------------------------------------------
from libtovid.odict import Odict

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



#! /usr/bin/env python
# odict.py

"""Ordered dictionary class, from a Python Cookbook recipe:

http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747

"""
__all__ = ['Odict']

from UserDict import UserDict

class Odict (UserDict):
    def __init__(self, keys=None, values=None):
        """Create an Odict from the given keys and values."""
        keys = keys or []
        values = values or []
        if len(keys) != len(values):
            raise ValueError("keys and values are not the same length")
        self._keys = keys
        UserDict.__init__(self, dict(zip(keys, values)))

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)
    
    def __str__(self):
        lines = []
        for key, value in self.items():
            lines.append("%s: %s" % (key, value))
        return '\n'.join(lines)


def convert_list(choices):
    """Convert a list of choices to an Odict (ordered dictionary).
    choices may be in one of several formats:

               string: 'one|two|three'
                 list: ['one', 'two', 'three']
                 dict: {'a': "Choice A", 'b': "Choice B"}
        list-of-lists: [['a', "Choice A"], ['b', "Choice B"], ..]
    
    Note: the dict form does not preserve order. Use list-of-lists
    to maintain the specified order.
    """
    if type(choices) not in [str, list, dict]:
        raise TypeError("choices must be a string, list, or dictionary.")

    if type(choices) == str:
        choices = choices.split('|')
        return Odict(choices, choices)

    if type(choices) == dict:
        return Odict(choices.keys(), choices.values())

    # choices is a list, but what kind?
    first = choices[0]
    # list of strings
    if type(first) == str:
        return Odict(choices, choices)
    # list of 2-element string lists
    elif type(first) == list and len(first) == 2:
        choices, values = zip(*choices)
        return Odict(choices, values)
    else:
        raise TypeError("choices lists must either be"\
            "['a', 'b', 'c'] or [['a', 'A'], ['b', 'B']] style.")

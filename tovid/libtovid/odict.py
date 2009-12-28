# odict.py

"""Ordered dictionary class, from a Python Cookbook recipe:

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747

"""

__all__ = ['Odict']

from UserDict import UserDict

class Odict (UserDict):
    """Ordered dictionary class, compatible with the builtin dict.
    """
    def __init__(self, keys=None, values=None):
        """Create an Odict from the given keys and values.
        """
        keys = list(keys or [])
        values = list(values or [])
        if len(keys) != len(values):
            raise ValueError("keys and values must be the same length")
        self._keys = keys
        UserDict.__init__(self, dict(zip(keys, values)))

    def __delitem__(self, key):
        """Get the value from Odict[key].
        """
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        """Set Odict[key] = item.
        """
        UserDict.__setitem__(self, key, item)
        if key not in self._keys:
            self._keys.append(key)

    def clear(self):
        """Remove all items from the Odict.
        """
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        """Return an exact copy of the Odict.
        """
        dict_copy = UserDict.copy(self)
        dict_copy._keys = self._keys[:]
        return dict_copy

    def items(self):
        """Return a list of (key, value) pairs, in order.
        """
        return zip(self._keys, self.values())

    def keys(self):
        """Return the list of keys, in order.
        """
        return self._keys

    def values(self):
        """Return the list of values, in order.
        """
        return [self.get(key) for key in self._keys]

    def popitem(self):
        """Pop the last (key, value) pair from the Odict, and return it.
        """
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        value = self[key]
        del self[key]

        return (key, value)

    def setdefault(self, key, failobj=None):
        """If Odict[key] doesn't exist, set Odict[key] = failobj,
        and return the resulting value of Odict[key].
        """
        result = UserDict.setdefault(self, key, failobj)
        if key not in self._keys:
            self._keys.append(key)
        return result

    def update(self, other_dict, **kwargs):
        """Update the Odict with values from another dict.
        """
        UserDict.update(self, other_dict, **kwargs)
        for key in other_dict.keys():
            if key not in self._keys:
                self._keys.append(key)

    def __str__(self):
        """Return a string representation of the Odict.
        """
        lines = []
        for key, value in self.items():
            lines.append("%s: %s" % (key, value))
        return '\n'.join(lines)


def convert_list(choices):
    """Convert a list of choices to an Odict (ordered dictionary).
    choices may be in one of several formats:

        string
            'one|two|three'
        list
            ['one', 'two', 'three']
        dict
            {'a': "Choice A", 'b': "Choice B"}
        list-of-lists
            [['a', "Choice A"], ['b', "Choice B"], ..]

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

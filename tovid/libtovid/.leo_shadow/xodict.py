#@+leo-ver=4-thin
#@+node:eric.20090722212922.2447:@shadow odict.py
# odict.py

"""Ordered dictionary class, from a Python Cookbook recipe:

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747

"""

__all__ = ['Odict']

# Python < 3.x
try:
    from UserDict import UserDict
# Python 3.x
except ImportError:
    from collections import UserDict

#@+others
#@+node:eric.20090722212922.2449:class Odict
class Odict (UserDict):
    """Ordered dictionary class, compatible with the builtin dict.
    """
    #@    @+others
    #@+node:eric.20090722212922.2450:__init__
    def __init__(self, keys=None, values=None):
        """Create an Odict from the given keys and values.
        """
        keys = list(keys or [])
        values = list(values or [])
        if len(keys) != len(values):
            raise ValueError("keys and values must be the same length")
        self._keys = keys
        UserDict.__init__(self, dict(zip(keys, values)))

    #@-node:eric.20090722212922.2450:__init__
    #@+node:eric.20090722212922.2451:__delitem__
    def __delitem__(self, key):
        """Get the value from Odict[key].
        """
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    #@-node:eric.20090722212922.2451:__delitem__
    #@+node:eric.20090722212922.2452:__setitem__
    def __setitem__(self, key, item):
        """Set Odict[key] = item.
        """
        UserDict.__setitem__(self, key, item)
        if key not in self._keys:
            self._keys.append(key)

    #@-node:eric.20090722212922.2452:__setitem__
    #@+node:eric.20090722212922.2453:clear
    def clear(self):
        """Remove all items from the Odict.
        """
        UserDict.clear(self)
        self._keys = []

    #@-node:eric.20090722212922.2453:clear
    #@+node:eric.20090722212922.2454:copy
    def copy(self):
        """Return an exact copy of the Odict.
        """
        dict_copy = UserDict.copy(self)
        dict_copy._keys = self._keys[:]
        return dict_copy

    #@-node:eric.20090722212922.2454:copy
    #@+node:eric.20090722212922.2455:items
    def items(self):
        """Return a list of (key, value) pairs, in order.
        """
        return zip(self._keys, self.values())

    #@-node:eric.20090722212922.2455:items
    #@+node:eric.20090722212922.2456:keys
    def keys(self):
        """Return the list of keys, in order.
        """
        return self._keys

    #@-node:eric.20090722212922.2456:keys
    #@+node:eric.20090722212922.2457:values
    def values(self):
        """Return the list of values, in order.
        """
        return [self.get(key) for key in self._keys]

    #@-node:eric.20090722212922.2457:values
    #@+node:eric.20090722212922.2458:popitem
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

    #@-node:eric.20090722212922.2458:popitem
    #@+node:eric.20090722212922.2459:setdefault
    def setdefault(self, key, failobj=None):
        """If Odict[key] doesn't exist, set Odict[key] = failobj,
        and return the resulting value of Odict[key].
        """
        result = UserDict.setdefault(self, key, failobj)
        if key not in self._keys:
            self._keys.append(key)
        return result

    #@-node:eric.20090722212922.2459:setdefault
    #@+node:eric.20090722212922.2460:update
    def update(self, other_dict, **kwargs):
        """Update the Odict with values from another dict.
        """
        UserDict.update(self, other_dict, **kwargs)
        for key in other_dict.keys():
            if key not in self._keys:
                self._keys.append(key)

    #@-node:eric.20090722212922.2460:update
    #@+node:eric.20090722212922.2461:__str__
    def __str__(self):
        """Return a string representation of the Odict.
        """
        lines = []
        for key, value in self.items():
            lines.append("%s: %s" % (key, value))
        return '\n'.join(lines)


    #@-node:eric.20090722212922.2461:__str__
    #@-others
#@-node:eric.20090722212922.2449:class Odict
#@+node:eric.20090722212922.2462:convert_list
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
#@-node:eric.20090722212922.2462:convert_list
#@-others
#@-node:eric.20090722212922.2447:@shadow odict.py
#@-leo

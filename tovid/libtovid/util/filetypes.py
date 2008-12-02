#! /usr/bin/env python
# filetypes.py

"""Defines several commonly-used multimedia and image file types.
"""

__all__ = [
    'match_types',
    'get_extensions',
    'all_files',
    'image_files',
    'video_files',
    'audio_files',
]

import mimetypes

def match_types(containing):
    """Return a list of (type, extensions) tuples for matching mimetypes.
    
        containing
            String or list of strings to match

    For example::

        match_types('image/jpeg')

    Uses a "contains" search, so you can do::

        match_types(['image', 'mpeg'])

    to match any mimetype containing 'image' or 'mpeg'.

    The returned tuples are suitable for use as the 'filetypes' argument of
    Tkinter file dialogs (askopenfilename etc.).
    """
    if type(containing) == str:
        containing = [containing]
    elif type(containing) != list:
        raise TypeError("match_types requires a string or list argument.")

    types = {}
    # Check for matching types and remember their extensions
    for ext, typename in mimetypes.types_map.items():
        for substr in containing:
            if substr in typename:
                # Append or insert extension
                if typename in types:
                    types[typename] += ' *' + ext
                else:
                    types[typename] = '*' + ext

    # Convert to tuple-list form
    return types.items()


def get_extensions(containing):
    """Return a space-separated string of all extensions for matching types.
    Like match_types, but only return the extensions.
    """
    type_dict = dict(match_types(containing))
    ext_list = type_dict.values()
    return ' '.join(ext_list)
    

all_files = ('All files', '*.*')
image_files = ('Image files', get_extensions('image'))
video_files = ('Video files', get_extensions('video'))
audio_files = ('Audio files', get_extensions('audio'))

 

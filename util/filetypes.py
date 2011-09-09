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

import os
import mimetypes


def etc_mimetypes():
    """Get mimetypes from ``/etc/mime.types`` and return a dict of ``{ext: typename}``
    in the same format as returned by `mimetypes.types_map`.
    """
    if not os.path.exists('/etc/mime.types'):
        return {}
    mime_types = {}
    for line in open('/etc/mime.types', 'r'):
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) > 1:
                for ext in parts[1:]:
                    mime_types['.' + ext] = parts[0]
    return mime_types


def match_types(containing):
    """Return a list of ``(type, extensions)`` tuples for matching mimetypes.

        containing
            String or list of strings to match

    For example::

        match_types('image/jpeg')

    Uses a "contains" search, so you can do::

        match_types(['image', 'mpeg'])

    to match any mimetype containing 'image' or 'mpeg'.

    The returned tuples are suitable for use as the 'filetypes' argument of
    Tkinter file dialogs like `askopenfilename`.
    """
    if type(containing) == str:
        containing = [containing]
    elif type(containing) != list:
        raise TypeError("match_types requires a string or list argument.")

    types = {}
    # Check for matching types and remember their extensions
    for ext, typename in sorted(mimetypes.types_map.items()):
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
    Like `match_types`, but only return the extensions.
    """
    type_dict = dict(match_types(containing))
    ext_list = type_dict.values()
    return ' '.join(ext_list)


def new_filetype(name, extensions):
    """Create a filetype tuple from a name and a list of extensions.
    extensions may be a space-separated string, list, tuple, or other iterable.

        >>> new_filetype('My filetype', 'foo bar baz')
        ('My filetype', '*.foo *.FOO *.bar *.BAR *.baz *.BAZ')

    """
    if type(extensions) == str:
        extensions = extensions.split(' ')
    ext_patterns = ('*.%s *.%s' % (ext.lower(), ext.upper()) for ext in extensions)
    return (name, ' '.join(ext_patterns))


all_files = ('All files', '*.*')
image_files = ('Image files', get_extensions('image'))
video_files = ('Video files', get_extensions('video'))
audio_files = ('Audio files', get_extensions('audio'))



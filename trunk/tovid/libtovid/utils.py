#! /usr/bin/env python
# utils.py

# TODO: Categorize/reorganize these (or move some to a class)

__all__ = [\
    'escape',
    'float_to_ratio',
    'get_code_lines',
    'get_file_type',
    'indent_level',
    'pretty_dict',
    'ratio_to_float',
    'safe_filename',
    'tokenize',
    'temp_dir',
    'temp_file',
    'to_unicode',
    'trim',
    'wait'
]

import os
import sys
import shlex
import doctest
import mimetypes
import tempfile

# Special characters that may need escaping
special_chars = '\\ #*:;&?!<>[]()"\''


def safe_filename(filename, work_dir):
    """Ensure the given filename is free of quirky or problematic characters.
    If so, simply return the filename; if not, create a safe symlink in
    work_dir to the original file, and return the symlink name.
    """
    safename = filename
    for char in special_chars:
        safename = safename.replace(char, '_')
    if safename != filename:
        basename = os.path.basename(safename)
        safename = os.path.join(work_dir, basename)
        os.symlink(filename, safename)
    return safename


def escape(text):
    """Return a copy of the given text string with potentially problematic
    "special" characters backslash-escaped.
    """
    result = text
    for char in special_chars:
        result = result.replace(char, '\%s' % char)
    return result


def to_unicode(text):
    """Return the given text string, converted to unicode.
    """
    if not isinstance(text, unicode):
        text = unicode(str(text).decode('latin-1'))
    return text


def indent_level(line):
    """Return the number of leading whitespace characters in the line.
    """
    return len(line) - len(line.lstrip())


def trim(text):
    """Strip leading indentation from a block of text.
    Borrowed from http://www.python.org/peps/pep-0257.html 
    """
    if not text:
        return ''
    # Split text into lines, converting tabs to spaces
    lines = text.expandtabs().splitlines()
    # Determine minimum indentation (except first line)
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special)
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            # Append line, minus indentation
            trimmed.append(line[indent:].rstrip())
    # Strip leading blank lines
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Strip trailing blank lines
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    # Return a string, rejoined with newlines
    return '\n'.join(trimmed)


def ratio_to_float(ratio):
    """Convert a string expressing a numeric ratio, with X and Y parts
    separated by a colon ':', into a decimal number.

    For example:

        >>> ratio_to_float('4:3')
        1.33333

    """
    values = ratio.split(':', 1)
    if len(values) == 2:
        return float(values[0]) / float(values[1])
    elif len(values) == 1:
        return float(values[0])
    else:
        raise Exception("ratio_to_float: too many values in ratio '%s'" % ratio)


def float_to_ratio(number):
    """Convert a decimal number into an integer ratio string 'X:Y'.
    Keeps three digits of precision.
    """
    numerator = float(number) * 1000
    return "%g:1000" % numerator


def tokenize(line, include_chars=''):
    """Separate a text line into tokens, returning them in a list. By default,
    tokens are space-separated, and each token consists of [a-z], [A-Z], [0-9],
    or any of '.:-%()/'. Additional valid token characters may be specified by
    passing them in the include_chars string.
    """
    lexer = shlex.shlex(line, posix = True)
    # Rules for splitting tokens
    lexer.wordchars = lexer.wordchars + '.:-%()/' + include_chars
    lexer.whitespace_split = False
    # Append all tokens to a list
    tokens = []
    while True:
        token = lexer.get_token()
        if not token:
            break
        else:
            tokens.append(token)
    return tokens


def pretty_dict(a_dict):
    """Return a pretty-printed dictionary, with one line for each key.
    Keys are printed in sorted ascending order.
    """
    result = ''
    keys = a_dict.keys()
    keys.sort()
    for key in keys:
        value = a_dict[key]
        # For boolean options, print Trues and omit Falses
        if value.__class__ == bool:
            if value is True:
                result += "    %s\n" % key
            else:
                pass
        # If value has spaces, quote it
        elif value.__class__ == str and ' ' in value:
            result += "    %s \"%s\"\n" % (key, value)
        # Otherwise, don't
        else:
            result += "    %s %s\n" % (key, value)
    return result


def get_code_lines(filename):
    """Return a list of all lines of code in the given file.
    Whitespace and #-style comments are ignored.
    """
    infile = open(filename, 'r')
    codelines = []
    for line in infile.readlines():
        if line.lstrip() and not line.lstrip().startswith('#'):
            codelines.append(line)
    infile.close()
    return codelines


def get_file_type(filename):
    """Return 'image', 'audio', or 'video', if the given filename appears to be
    any of those types; otherwise, return None. Determined by file's mimetype,
    which is based on filename extension, so possibly inaccurate. Returns
    None for any directory or extensionless filename.
    """
    mimetype, encoding = mimetypes.guess_type(filename)
    # Get the base type (the part before '/')
    basetype = None
    if mimetype:
        basetype = mimetype[0:mimetype.find('/')]
    if basetype in ['image', 'audio', 'video']:
        return basetype
    else:
        return None


def temp_dir(prefix=''):
    """Create a unique temporary directory and return its full pathname.
    """
    import libtovid
    work_dir = libtovid.Config().get('DEFAULT', 'work_dir')
    return tempfile.mkdtemp(prefix="%s_" % prefix,
                            dir=work_dir)


def temp_file(prefix='', suffix=''):
    """Create a unique temporary file and return its full pathname.
    """
    import libtovid
    work_dir = libtovid.Config().get('DEFAULT', 'work_dir')
    fd, fname = tempfile.mkstemp(prefix="%s_" % prefix,
                                 suffix=suffix,
                                 dir=work_dir)
    os.close(fd)
    return fname


def wait(seconds):
    """Print a message and pause for the given number of seconds.
    """
    print "Resuming in %s seconds..." % seconds
    os.system('sleep %ss' % seconds)


def imagemagick_version():
    """Return the version of ImageMagick that's currently installed,
    as a list of integers (ex. [6, 3, 5, 10] for version 6.3.5.10).
    """
    command = 'convert -list configure | grep ^LIB_VERSION_NUMBER'
    lines = os.popen(command).readlines()
    version_string = lines[0].split()[1]
    return [int(n) for n in version_string.split(',')]


def imagemagick_fonts():
    """Return a list of fonts available to ImageMagick.
    """
    version = imagemagick_version()

    # ImageMagick 6.4.x prints fonts like this:
    #   Font: Verdana-Italic
    #     family: Verdana
    #     style: Italic
    #     stretch: Normal
    #     weight: 400
    if version >= [6, 4, 0, 0]:
        command = "convert -list font | grep 'Font:' | awk '{print $2}'"

    # ImageMagick 6.3.5.7 and later print fonts like this:
    #   Name             Family       Style  Stretch Weight
    #   ---------------------------------------------------
    #   Verdana-Italic   Verdana      Italic  Normal    400
    elif version >= [6, 3, 5, 7]:
        command = "convert -list font | awk '!/\-\-\-|Path|Name|^$/ {print $1}'"

    # Older versions use 'type' instead of 'font', same formatting as above
    else:
        command = "convert -list type | awk '!/\-\-\-|Path|Name|^$/ {print $1}'"

    # Run the command and return the list of font names
    lines = os.popen(command).readlines()
    return sorted([line.rstrip('\n') for line in lines \
        if not 'undefin' in line.lower()])


if __name__ == '__main__':
    doctest.testmod(verbose=True)

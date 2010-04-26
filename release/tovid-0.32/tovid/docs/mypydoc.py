#! /usr/bin/env python
# -*- coding: Latin-1 -*-


"""Reimplementation of the pydoc HTML generator.

Notes:

__author__
__date__
__version__
__credits__

__class__
__name__
__all__
__path__
__bases__
__module__


======================
try:
    foo = object.__attrib__
except AttributeError:
    foo = None
======================

def describe(thing):
    # Most return thing.__name__
    inspect.ismodule(thing)
    inspect.isbuiltin(thing)
    inspect.isclass(thing)
    inspect.isfunction(thing)
    inspect.ismethod(thing)
    type(thing) is types.InstanceType


# Return a dictionary of member/value pairs
# routines in thing
for key, value in inspect.getmembers(thing, inspect.isroutine)
# classes in thing
for key, value in inspect.getmembers(thing, inspect.isclass)
# etc.

"""

import datetime
import re, sys, inspect, __builtin__
from string import join, split, lower

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
    
class ErrorDuringImport(Exception):
    """Errors that occurred while trying to import something to document it."""
    def __init__(self, filename, (exc, value, tb)):
        self.filename = filename
        self.exc = exc
        self.value = value
        self.tb = tb

    def __str__(self):
        exc = self.exc
        if type(exc) is types.ClassType:
            exc = exc.__name__
        return 'problem in %s - %s: %s' % (self.filename, exc, self.value)

# safeimport, locate and resolve Stolen from pydoc.py
# (Clean up and rewrite later)
def safeimport(path, forceload=0, cache={}):
    """Import a module; handle errors; return None if the module isn't found.

    If the module *is* found but an exception occurs, it's wrapped in an
    ErrorDuringImport exception and reraised.  Unlike __import__, if a
    package path is specified, the module at the end of the path is returned,
    not the package at the beginning.  If the optional 'forceload' argument
    is 1, we reload the module from disk (unless it's a dynamic extension)."""
    if forceload and path in sys.modules:
        # This is the only way to be sure.  Checking the mtime of the file
        # isn't good enough (e.g. what if the module contains a class that
        # inherits from another module that has changed?).
        if path not in sys.builtin_module_names:
            # Python never loads a dynamic extension a second time from the
            # same path, even if the file is changed or missing.  Deleting
            # the entry in sys.modules doesn't help for dynamic extensions,
            # so we're not even going to try to keep them up to date.
            info = inspect.getmoduleinfo(sys.modules[path].__file__)
            if info[3] != imp.C_EXTENSION:
                cache[path] = sys.modules[path] # prevent module from clearing
                del sys.modules[path]
    try:
        print "Trying to import module: %s" % path
        module = __import__(path)
    except:
        # Did the error occur before or after the module was found?
        (exc, value, tb) = info = sys.exc_info()
        if path in sys.modules:
            # An error occured while executing the imported module.
            raise ErrorDuringImport(sys.modules[path].__file__, info)
        elif exc is SyntaxError:
            # A SyntaxError occurred before we could execute the module.
            raise ErrorDuringImport(value.filename, info)
        elif exc is ImportError and \
             split(lower(str(value)))[:2] == ['no', 'module']:
            # The module was not found.
            return None
        else:
            # Some other error occurred during the importing process.
            raise ErrorDuringImport(path, sys.exc_info())
    for part in split(path, '.')[1:]:
        try: module = getattr(module, part)
        except AttributeError: return None
    return module

def locate(path, forceload=0):
    """Locate an object by name or dotted path, importing as necessary."""
    parts = [part for part in split(path, '.') if part]
    module, n = None, 0
    while n < len(parts):
        nextmodule = safeimport(join(parts[:n+1], '.'), forceload)
        if nextmodule: module, n = nextmodule, n + 1
        else: break
    if module:
        object = module
        for part in parts[n:]:
            try: object = getattr(object, part)
            except AttributeError: return None
        return object
    else:
        if hasattr(__builtin__, path):
            return getattr(__builtin__, path)

def resolve(thing, forceload=0):
    """Given an object or a path to an object, get the object and its name."""
    if isinstance(thing, str):
        object = locate(thing, forceload)
        if not object:
            raise ImportError, 'no Python documentation found for %r' % thing
        return object, thing
    else:
        return thing, getattr(thing, '__name__', None)


class HTMLGenerator:

    def __init__(self):
        self.html = ''

    def emit(self, text):
        #if text: print text
        if text: self.html += text

    def emit_pre(self, text, css_class='doc', linenum=False):
        if not text: return
        # Replace '<' with '&lt;'
        text = text.replace('<', '&lt;')
        text = trim(text)
        if linenum:
            lines = text.split('\n')
            self.emit('''<pre class="%s">''' % css_class)
            lineno = 1
            for line in lines:
                strlineno = "%s" % lineno
                self.emit('''%s:   %s\n''' % (strlineno.rjust(4), line))
                lineno += 1
            self.emit('''</pre>''')
        else:
            self.emit('''<pre class="%s">%s</pre>''' % \
                (css_class, text))

    # Generate docs for given name
    def document(self, name):

        # Resolve object name
        self.obj, self.name = resolve(name)

        self.emit("""<!doctype html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
         <html><head>
            <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=ISO-8859-1">
            <title>Python: %s</title>
            <link rel="stylesheet" type="text/css" href="tovid_screen.css">
        </head>
        <body>""" % self.name)

        # Document modules only (for now)
        if inspect.ismodule(self.obj): self.doc_module(self.obj)

        # Write source code as preformatted text
        source = inspect.getsource(self.obj)
        if source:
            self.emit('''<h2>Source code</h2>''')
            self.emit_pre(source, 'source', linenum=True)

        self.emit('''</body></html>''')

        return self.html

    def doc_module(self, mod):
        if not inspect.ismodule(mod): return
        self.emit('''<h1>%s</h1>''' % mod.__name__)
        self.emit('''<p class="date">Generated %s</p>''' % \
            datetime.datetime.now().ctime())
        self.emit_pre(mod.__doc__)

        classes = inspect.getmembers(mod, inspect.isclass)
        if classes:
            self.emit('''<h2>Classes</h2>''')
            self.emit('''<dl class="class">''')
            for name, cls in classes:
                # Only document classes defined in this module
                if inspect.getmodule(cls) == mod:
                    self.doc_class(cls)
            self.emit('''</dl>''')

        funcs = inspect.getmembers(mod, inspect.isfunction)
        if funcs:
            self.emit('''<h2>Functions</h2>''')
            self.emit('''<dl class="function">''')
            for name, func in funcs:
                # Only document functions defined in this module
                if inspect.getmodule(func) == mod:
                    self.doc_function(func)
            self.emit('''</dl>''')

    def doc_class(self, cls):
        if not inspect.isclass(cls): return
        self.emit('''<dt>%s</dt>''' % cls.__name__)
        self.emit('''<dd>''')
        self.emit_pre(cls.__doc__)

        self.emit('''<p>Methods defined in this class:</p>''')
        methods = inspect.getmembers(cls, inspect.ismethod)
        if methods:
            self.emit('''<dl class="method">''')
            for name, method in methods:
                # Only document methods defined in this class's module
                if inspect.getmodule(method) == inspect.getmodule(cls):
                    self.doc_function(method.im_func)
            self.emit('''</dl>''')
        self.emit('''</dd>''')
        
            
    def doc_function(self, func):
        if not inspect.isfunction(func) and not inspect.ismethod(func): return
        args, varargs, varkw, defaults = inspect.getargspec(func)
        signature = inspect.formatargspec(args, varargs, varkw, defaults)
        # Strip parentheses
        signature = signature[1:-1]
        self.emit('''<dt><code class="function">%s(<code class="args">%s</code>)</code></dt>''' % (func.__name__, signature))
        self.emit('''<dd>''')
        self.emit_pre(func.__doc__ or "No documentation")
        self.emit('''</dd>''')

    

if __name__ == '__main__':
    arg = sys.argv[1]
    gen = HTMLGenerator()
    print gen.document(arg)





"""Logging utilities for metagui.
"""

import inspect
import sys
import os
import linecache

def dump_args(func):
    """Decorator for logging calls to the function, along with
    the arguments passed to the function.
    """
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]

    def func_wrapper(*args, **kw):
        all_args = zip(argnames, args) + kw.items()
        arg_string = ', '.join(['%s=%r' % (k, v) for k, v in all_args])
        print("Calling %s(%s)" % (func.__name__, arg_string))
        return func(*args, **kw)

    return func_wrapper


def trace(f):
    """Trace lines in the function.
    From http://wiki.python.org/moin/PythonDecoratorLibrary
    """
    def globaltrace(frame, why, arg):
        if why == "call":
            return localtrace
        return None

    def localtrace(frame, why, arg):
        if why == "line":
            # record the file name and line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            bname = os.path.basename(filename)
            print("%s(%d): %s" % \
                (bname, lineno, linecache.getline(filename, lineno)))
        return localtrace

    def _f(*args, **kwds):
        sys.settrace(globaltrace)
        result = f(*args, **kwds)
        sys.settrace(None)
        return result

    return _f

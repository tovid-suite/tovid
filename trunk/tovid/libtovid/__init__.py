#! /usr/bin/env python
# __init__.py

__doc__ = \
"""This library provides a Python interface to the functionality of tovid.
"""

__version__ = '0.26-dev'

__all__ = [\
    "Globals",
    "Standards",

    "Disc",
    "Menu",
    "MenuPlugins",
    "Video",
    "VideoPlugins",

    "Option",
    "TDL",
    "Project",
    "Streams",
    "Filetypes",
    "gui"]


class Log:
    """Logger for libtovid backend and frontend; can be configured with
    a verbosity level and name. To use, declare:
        
        >>> from libtovid import Log
        >>> log = Log('MyApp')
        >>>

    By default, the log uses Log.INFO verbosity level; messages of INFO
    or less are shown:

        >>> log.info('Hello world')
        Info [MyApp]: Hello world
        >>>

    debug() messages are of higher verbosity level, and won't be shown
    by default:

        >>> log.debug('Extra-verbose stuff for developers')
        >>>

    To set a new level (and show debugging messages, for example), do:

        >>> log.level = Log.DEBUG
        >>> log.debug('No bugs lurking here...')
        Debug [MyApp]: No bugs lurking here...
        >>>
    """

    # Simple integer verbosity level
    DEBUG = 3
    INFO = 2
    ERROR = 1
    NONE = 0

    def __init__(self, name):
        """Create a logger with the given name."""
        self.name = name
        self.level = self.INFO
        
    def debug(self, message):
        if self.level >= self.DEBUG:
            self.console('Debug', message)

    def info(self, message):
        if self.level >= self.INFO:
            self.console('Info', message)

    def error(self, message):
        if self.level >= self.ERROR:
            self.console('*** Error', message)

    def console(self, level, message):
        print "%s [%s]: %s" % (level, self.name, message)

#! /usr/bin/env python
# log.py

from libtovid.globals import Config

# Simple integer verbosity level
DEBUG = 3
INFO = 2
ERROR = 1
NONE = 0

class Log:
    """Logger for libtovid backend and frontend; can be configured with
    a verbosity level and name. To use, declare:
        
        >>> from libtovid.Log import Log
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

    def __init__(self, name, level=DEBUG):
        """Create a logger with the given name and verbosity level."""
        # TODO: Do thread-safe logging to a logfile
        # TODO: Make logfile optional/configurable
        self.name = name
        self.level = level
        try:
            os.remove(Config().logfile)
        except:
            pass
        self.logfile = open(Config().logfile, 'w')
        
    def debug(self, message):
        if self.level >= DEBUG:
            self._log('Debug', message)

    def info(self, message):
        if self.level >= INFO:
            self._log('Info', message)

    def error(self, message):
        if self.level >= ERROR:
            self._log('*** Error', message)

    def _log(self, level, message):
        print message
        self.logfile.write("%s [%s]: %s\n" % (level, self.name, message))


#! /usr/bin/env python2.4
# log.py

# From standard library
import os
# From libtovid
from libtovid.globals import Config


class Log:
    """Logger for libtovid modules, with a name and verbosity level.

    To use, declare:
        
        >>> from libtovid.log import Log
        >>> log = Log('MyApp')
        >>>

    You can also provide a verbosity level:

        >>> log = Log('MyApp', Log.DEBUG)
        >>>

    Send messages to the logger like so:

        >>> log.debug('Ugly verbose debugging message')
        >>> log.info('Normal message to user')
    """

    # Available verbosity levels
    NONE = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

    def __init__(self, name, verbosity=DEBUG):
        """Create a logger with the given name and verbosity level."""
        # TODO: Do thread-safe logging to a logfile
        # TODO: Make logfile optional/configurable
        self.name = name
        self.verbosity = verbosity
        try:
            os.remove(Config().logfile)
        except:
            pass
        self.logfile = open(Config().logfile, 'w')
        
    def debug(self, message):
        if self.verbosity >= Log.DEBUG:
            self._log('Debug', message)

    def info(self, message):
        if self.verbosity >= Log.INFO:
            self._log('Info', message)

    def error(self, message):
        if self.verbosity >= Log.ERROR:
            self._log('*** Error', message)

    def _log(self, header, message):
        # Strip trailing newlines from message
        message = str(message).rstrip('\n\r')
        print "%s [%s]: %s" % (header, self.name, message)
        self.logfile.write("%s [%s]: %s\n" % (header, self.name, message))

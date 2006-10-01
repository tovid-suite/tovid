#! /usr/bin/env python
# log.py

"""This module defines a Log class, providing a wrapper around the standard
Python 'logging' module.

Using this module is similar to using Python's built-in logging module, with
the exception that some of the initial setup procedures are handled
automatically. Simply create a Log instance with a name and logging level:

    >>> log = Log('MyApp', 'info')

The logging level determines output verbosity. Use "info" for normal program
output, "debug" for debugging messages, "error" for important error messages,
and so on:

    >>> log.info("Starting app...")
    Starting app...
    >>> log.debug("Pointer is 0x1582")
    >>> log.error("An error occurred")
    An error occurred

To change the verbosity level, use setLevel:

    >>> log.setLevel('debug')
    >>> log.debug("Pointer is 0x1582")
    Pointer is 0x1582

To disable all output except for "critical" messages:

    >>> log.setLevel('critical')
    >>> log.debug("Pointer is 0x1582")
    >>> log.info("Starting app...")
    >>> log.warning("Deprecation warning")
    >>> log.error("An error occurred")
    >>> log.critical("This is really, really bad!")
    This is really, really bad!

"""

import sys
import logging
import doctest

# Logging levels, in increasing order of severity
levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
    }

class Log:
    """A wrapper class for the Python logging utility."""
    def __init__(self, name, level='info'):
        """Create a log with the given name and verbosity level."""
        assert level
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.setLevel(level)
        # Standard output logger
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        # TODO: Add an interface for file logging

    def setLevel(self, level):
        """Set log verbosity level to one of 'debug', 'info', 'warning',
        'error', or 'critical'."""
        assert level in levels
        self.level = level
        self.logger.setLevel(levels[level])

    def debug(self, message):
        """Log a debugging message (low priority)."""
        self.logger.debug(message)
        
    def info(self, message):
        """Log an informational message (normal priority)."""
        self.logger.info(message)

    def warning(self, message):
        """Log a warning message (medium priority)."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error message (high priority)."""
        self.logger.error(message)

    def critical(self, message):
        """Log a critical message (highest priority)."""
        self.logger.critical(message)

if __name__ == '__main__':
    doctest.testmod(verbose=True)

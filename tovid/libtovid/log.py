#! /usr/bin/env python
# log.py

"""This module defines a Log class, providing a wrapper around the standard
Python 'logging' module.
"""

import sys
import logging

# Logging levels
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

    def setLevel(self, level):
        """Set log verbosity level to one of 'debug', 'info', 'warning',
        'error', or 'critical'."""
        assert level in levels
        self.level = level
        self.logger.setLevel(levels[level])

    def debug(self, message):
        """Log a debugging message."""
        self.logger.debug(message)
        
    def info(self, message):
        """Log an informational message."""
        self.logger.info(message)

    def warn(self, message):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)

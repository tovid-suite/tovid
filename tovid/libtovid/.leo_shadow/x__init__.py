#@+leo-ver=4-thin
#@+node:eric.20090722212922.2395:@shadow __init__.py
"""Provides a Python interface to the functionality of tovid.
"""

__all__ = [
    # Subdirectories
    'backend',
    'gui',
    'guis',
    'metagui',
    'render',
    'template',
    'test',
    'util',
    # .py files
    'author',
    'cli',
    'deps',
    'encode',
    'odict',
    'opts',
    'rip',
    'standard',
    'stats',
    'utils',
    'xml',
]

import os

# Python < 3.x
try:
    from ConfigParser import ConfigParser
# Python 3.x
except ImportError:
    from configparser import ConfigParser

#@+others
#@+node:eric.20090722212922.2397:class Config
# Configuration file reader/writer
class Config (ConfigParser):
    """Interface for reading/writing tovid configuration files. Just a wrapper
    around the standard library ConfigParser. Example usage:

        config = libtovid.Config()
        config.get('DEFAULT', 'work_dir')
        config.set('tovid', 'method', 'ffmpeg')
        config.save()

    See the ConfigParser documentation for details.
    """
    # Dictionary of suite-wide configuration defaults
    DEFAULTS = {
        'work_dir': '/tmp',
        'output_dir': '/tmp'}

    #@    @+others
    #@+node:eric.20090722212922.2398:__init__
    def __init__(self):
        """Load configuration from ~/.tovid/config."""
        ConfigParser.__init__(self, self.DEFAULTS)
        self.filename = os.path.expanduser('~/.tovid/config')
        self.read(self.filename)

    #@-node:eric.20090722212922.2398:__init__
    #@+node:eric.20090722212922.2399:save
    def save(self):
        """Save the configuration to the current filename."""
        outfile = open(self.filename, 'w')
        outfile.write('# tovid configuration file\n\n')
        self.write(outfile)
        outfile.close()


    #@-node:eric.20090722212922.2399:save
    #@-others

#@-node:eric.20090722212922.2397:class Config
#@+node:eric.20090722212922.2400:class Log
# Logging class
class Log:
    """Logging class, with five severity levels.
    """
    # Increasing levels of severity
    _levels = {
        'debug': 1,
        'info': 2,
        'warning': 3,
        'error': 4,
        'critical': 5}

    #@    @+others
    #@+node:eric.20090722212922.2401:__init__
    def __init__(self, level='info'):
        """Create a logger with the given severity level."""
        self.level = level

    #@-node:eric.20090722212922.2401:__init__
    #@+node:eric.20090722212922.2402:message
    def message(self, level, text):
        """Print a message if it's at the current severity level or higher."""
        if Log._levels[level] >= Log._levels[self.level]:
            print(text)

    #@-node:eric.20090722212922.2402:message
    #@+node:eric.20090722212922.2403:debug
    def debug(self, text):
        """Log a debugging message."""
        self.message('debug', text)

    #@-node:eric.20090722212922.2403:debug
    #@+node:eric.20090722212922.2404:info
    def info(self, text):
        """Log an informational message."""
        self.message('info', text)

    #@-node:eric.20090722212922.2404:info
    #@+node:eric.20090722212922.2405:warning
    def warning(self, text):
        """Log a warning message."""
        self.message('warning', "WARNING: " + text)

    #@-node:eric.20090722212922.2405:warning
    #@+node:eric.20090722212922.2406:error
    def error(self, text):
        """Log an error message."""
        self.message('error', "ERROR: " + text)

    #@-node:eric.20090722212922.2406:error
    #@+node:eric.20090722212922.2407:critical
    def critical(self, text):
        """Log a critical error message."""
        self.message('critical', "CRITICAL: " + text)


    #@-node:eric.20090722212922.2407:critical
    #@-others
#@-node:eric.20090722212922.2400:class Log
#@-others

# Global logger
log = Log()
#@-node:eric.20090722212922.2395:@shadow __init__.py
#@-leo

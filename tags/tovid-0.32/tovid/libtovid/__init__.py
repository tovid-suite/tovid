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

    def __init__(self):
        """Load configuration from ~/.tovid/config."""
        ConfigParser.__init__(self, self.DEFAULTS)
        self.filename = os.path.expanduser('~/.tovid/config')
        self.read(self.filename)

    def save(self):
        """Save the configuration to the current filename."""
        outfile = open(self.filename, 'w')
        outfile.write('# tovid configuration file\n\n')
        self.write(outfile)
        outfile.close()



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

    def __init__(self, level='info'):
        """Create a logger with the given severity level."""
        self.level = level

    def message(self, level, text):
        """Print a message if it's at the current severity level or higher."""
        if Log._levels[level] >= Log._levels[self.level]:
            print(text)

    def debug(self, text):
        """Log a debugging message."""
        self.message('debug', text)

    def info(self, text):
        """Log an informational message."""
        self.message('info', text)

    def warning(self, text):
        """Log a warning message."""
        self.message('warning', "WARNING: " + text)

    def error(self, text):
        """Log an error message."""
        self.message('error', "ERROR: " + text)

    def critical(self, text):
        """Log a critical error message."""
        self.message('critical', "CRITICAL: " + text)



# Global logger
log = Log()

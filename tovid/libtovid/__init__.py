#! /usr/bin/env python
# __init__.py

"""Provides a Python interface to the functionality of tovid.
"""

## \mainpage How to use libtovid
# 
# \section intro Introduction
# 
# libtovid is a Python module oriented towards creating video discs. It has
# the following submodules:
#
# - transcode
#   - rip.py
#   - encode.py
#   - subtitles.py
# - layout
# - render
#   - drawing.py
#   - animation.py
#   - layer.py
#   - effect.py
#   - flipbook.py
# - Layers in layer.py, to put something in your canvas
# - Effects in effect.py, for several effects, which you can extend
# - Flipbook for animation
# - Drawing module in drawing.py for drawing primitives
# - Tween and Keyframe in animation.py, for key-framing
#
#
# <i>You'll find this page in %libtovid/__init__.py</i>


__all__ = [\
    # Subdirectories
    'gui',
    'author',
    'render',
    'template',
    'test',
    'transcode',
    # .py files
    'cli',
    'deps',
    'layout'
    'media',
    'opts',
    'output',
    'spumux',
    'standard',
    'stats',
    'utils',
    'xml']

import os
import sys
from ConfigParser import ConfigParser


# Configuration file reader/writer
class Config (ConfigParser):
    """Interface for reading/writing tovid configuration file. Just a wrapper
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
            print text

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


# =========================================================================
# Target interface for version 0.30
# =========================================================================
# Below is a simplistic top-level interface as first described on the tovid
# wiki, at http://tovid.wikia.com/wiki/Development_plans.
#
# This, in effect, gives you exactly the interface described on the
# development plans wiki page; after installing libtovid (via a normal
# tovid installation), you can run Python and type in those commands, and
# you will get roughly the output described there.
#
# Here, I've simply started with printing messages about what the DVD object
# is doing at each stage. Basically, each function says "this is what I'm
# doing", but doesn't actually do it. Call it the "easier said than done"
# philosophy of programming; if we can clearly define what each part is
# supposed to do, then actually implementing it will be just details.
#
# I've started developing down through the layers, just adding new objects
# (like Menu and Video) as they present themselves. Clearly, this will
# branch off and meet up with the existing modules at some middle point.
#
# Without further ado, I give you:

class Disc:
    """A video disc, with functions to manipulate its contents."""
    def __init__(self, title='Untitled disc', format='dvd', tvsys='ntsc'):
        print "Disc: Creating %s entitled: '%s'" % (type.upper(), title)
        self.format = format
        self.tvsys = tvsys
        self.title = title
        self.videos = []
    
    def add_videos(self, directory):
        print "Disc: Adding videos in %s" % directory
        for filename in ["First.mpg", "Second.mpg", "Third.mpg"]:
            title = filename.rstrip('.mpg')
            self.videos.append(Video(filename, title))
            
    def quality(self, level):
        print "Disc: Using %s quality video encoding" % level
        for video in self.videos:
            video.quality = level
        
    def thumb_menu(self, background):
        print "Disc: Using a thumbnail menu with background image %s" % background
        self.menu = Menu(self.format, 'thumbnail')
        self.menu.add_videos(self.videos)
        self.menu.set_background(background)
        
    def transcode(self, author=False):
        print "Disc: Encoding videos..."
        for video in self.videos:
            video.encode('dvd', 'ntsc')
            
        if hasattr(self, 'menu'):
            print "Disc: Generating menus..."
            self.menu.render()
        
        if author:
            self.author()
        print "Disc: Finished transcoding"
    
    def author(self):
        print "Disc: Authoring..."
        
    def preview(self):
        print "Disc: Previewing..."
        
    def burn(self, speed=2, device='/dev/dvdrw'):
        print "Disc: Burning at speed %s on device %s" % (speed, device)

# Three different Disc formats:
class VCD (Disc):
    """A Video CD"""
    def __init__(title='Untitled VCD', tvsys='ntsc'):
        Disc.__init__('vcd', tvsys, title)

class SVCD (Disc):
    """A Super Video CD"""
    def __init__(title='Untitled SVCD', tvsys='ntsc'):
        Disc.__init__('svcd', tvsys, title)

class DVD (Disc):
    """A DVD"""
    def __init__(title='Untitled DVD', tvsys='ntsc'):
        Disc.__init__('dvd', tvsys, title)

class Menu:
    """A video disc menu.
    
        >>> menu = Menu('dvd', 'thumb', videos)
        >>> menu.title("Trailer videos")
        
    Controlling menu style:
    
        >>> menu.font("Georgia Sans")
        >>> menu.font_color("Yellow")
        >>> menu.background("/images/sky.png")
        
    Alternatively:
    
        >>> menu.style(font="Georgia Sans", font_color="Yellow",
                       background="/images/sky.pyg")
        
    """
    def __init__(self, format='dvd', style='text', videos=[]):
        print "Menu: Creating a %s %s menu with %s videos" % \
              (format, style, len(videos))
        self.videos = videos

    def add_videos(self, videos):
        print "Menu: Adding %s Videos" % len(videos)
        self.videos.extend(videos)
        
    def set_background(self, background):
        print "Menu: Adding background image '%s'" % background
        self.background = background
        
    def render(self):
        print "Menu: Rendering..."


class Video:
    """A video for inclusion on a video disc."""
    def __init__(self, filename='', title=''):
        print "Video: Creating a video entitled '%s' from file '%s'" %\
              (title, filename)

    def encode(self, format, tvsys):
        print "Video: Encoding to compliant %s %s format." %\
              (format.upper(), tvsys.upper())

class Group:
    """A group for inclusion on a video disc."""
    def __init__(self, title=''):
        print "Group: Creating a group entitled '%s'" % (title)


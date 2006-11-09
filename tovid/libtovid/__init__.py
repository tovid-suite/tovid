#! /usr/bin/env python
# __init__.py

"""Provides a Python interface to the functionality of tovid.
"""

## \mainpage How to use libtovid
# 
# \section intro Introduction
# 
# The classes needed for a developer to use libtovid are mostly:
# 
#  - Layers in layer.py, to put something in your canvas
#  - Effects in effect.py, for several effects, which you can extend
#  - Flipbook for animation
#  - Drawing module in drawing.py for drawing primitives
#  - Video in video.py, if you want to deal with videos and convert them
#      `-> is that true ?
#  - Tween and Keyframe in animation.py, for key-framing
#
#
# <i>You'll find this page in %libtovid/__init__.py</i>


__all__ = [\
    # Subdirectories
    'gui',
    'encoders',
    'render',
    # .py files
    'animation',
    'cli',
    'disc',
    'effect',
    'flipbook',
    'globals',
    'layer',
    'media',
    'menu',
    'opts',
    'stats',
    'standards',
    'tdl',
    'textmenu',
    'utils',
    'video']

import sys
import logging

# Global logger
log = logging.getLogger('libtovid')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stdout))
# TODO: Support logging to a file with a different severity level



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

class DVD(object):
    """A DVD disc, with functions to manipulate its contents."""
    def __init__(self, title='Untitled disc', tvsys='ntsc'):
        print "DVD: Creating a DVD entitled: '%s'" % title
        self.videos = []
        
    def add_videos(self, directory):
        print "DVD: Adding videos in %s" % directory
        for filename in ["First.mpg", "Second.mpg", "Third.mpg"]:
            title = filename.rstrip('.mpg')
            self.videos.append(Video(filename, title))
            
    def quality(self, level):
        print "DVD: Using %s quality video encoding" % level
        for video in self.videos:
            video.quality = level
        
    def thumb_menu(self, background):
        print "DVD: Using a thumbnail menu with background image %s" % background
        self.menu = Menu('DVD', 'Thumbnails')
        self.menu.add_videos(self.videos)
        self.menu.set_background(background)
        
    def transcode(self, author=False):
        print "DVD: Encoding videos..."
        for video in self.videos:
            video.encode('dvd', 'ntsc')
            
        if hasattr(self, 'menu'):
            print "DVD: Generating menus..."
            self.menu.render()
        
        if author:
            self.author()
        print "DVD: Finished transcoding"
    
    def author(self):
        print "DVD: Authoring..."
        
    def preview(self):
        print "DVD: Previewing..."
        
    def burn(self, speed=2, device='/dev/dvdrw'):
        print "DVD: Burning at speed %s on device %s" % (speed, device)


class Menu(object):
    """A VCD or DVD menu."""
    def __init__(self, format='dvd', style='Text', videos=[]):
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


class Video(object):
    """A video for inclusion on a video disc."""
    def __init__(self, filename='', title=''):
        print "Video: Creating a video entitled '%s' from file '%s'" %\
              (title, filename)

    def encode(self, format, tvsys):
        print "Video: Encoding to compliant %s %s format." %\
              (format.upper(), tvsys.upper())

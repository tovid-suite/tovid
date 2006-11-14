#! /usr/bin/env python
# video.py

__all__ = ['Video']

# From standard library
import sys
# From libtovid
from libtovid.opts import Option, OptionDict
from libtovid.standards import get_resolution
# TODO: Remove explicit dependency on encoder modules; generalize the
# encoder backend so the Video class doesn't have to know about specific
# encoders.
from libtovid.transcode import encode
from libtovid.media import MediaFile
from libtovid import log

class Video:
    """A video title for (optional) inclusion on a video disc."""

    def __init__(self, custom_options=None):
        """Initialize Video with a string, list, or dictionary of options."""
        # TODO: Possibly eliminate code repetition w/ Disc & Menu by adding
        # a base class and inheriting
        self.options = OptionDict(self.optiondefs)
        self.options.override(custom_options)
        self.parent = None
        self.children = []

    def generate(self):
        """Generate a video element by encoding an input file to a target
        standard."""
        encode(self.options['in'], self.options['out'], \
               self.options['format'], self.options['tvsys'], \
               self.options['method'])

if __name__ == '__main__':
    vid = Video(sys.argv[1:])

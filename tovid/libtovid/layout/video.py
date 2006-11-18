#! /usr/bin/env python
# video.py

__all__ = ['Video']

# From standard library
import sys
# From libtovid
from libtovid.opts import Option, OptionDict
from libtovid.standard import resolution
# TODO: Remove explicit dependency on encoder modules; generalize the
# encoder backend so the Video class doesn't have to know about specific
# encoders.
from libtovid.transcode import encode
from libtovid.media import MediaFile
from libtovid import log

class Video:
    """A video title for (optional) inclusion on a video disc."""

    def __init__(self, custom_options=None):
        pass
    
    def generate(self):
        pass

if __name__ == '__main__':
    vid = Video(sys.argv[1:])

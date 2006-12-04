#! /usr/bin/env python
# video.py

__all__ = ['Video']

import doctest
from libtovid.transcode import encode

class Video:
    """A video title for inclusion on a video disc.

    Needed for encoding:
        input filename
        output name
        format/tvsys
    Needed for authoring:
        output filename
        format/tvsys
        widescreen
        length and/or chapter points
    Needed for menu generation:
        title
        output filename (for generating thumbs)
        widescreen
        chapter points
    """

    def __init__(self, infile, title, format, tvsys):
        self.infile = infile
        self.title = title
        self.format = format
        self.tvsys = tvsys

    def generate(self, outfile, method='ffmpeg'):
        """Generate (encode) the video to the given output filename."""
        encode.encode(self.infile, outfile,
                      self.format, self.tvsys, method)


if __name__ == '__main__':
    doctest.testmod(verbose=True)

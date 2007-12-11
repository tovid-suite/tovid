#! /usr/bin/env python
# encode.py

"""This module provides several backend for encoding video and audio.

One high-level function is provided:

    encode(infile, outfile, format, tvsys, method, ...)

where "..." is optional keyword arguments (described below). For example:

    encode('/video/foo.avi', '/video/bar.mpg', 'dvd', 'ntsc', 'mencoder')

This will encode '/video/foo.avi' to NTSC DVD format using mencoder, saving
the result as '/video/bar.mpg'. Keyword arguments may be used to further
refine encoding behavior, for example:

    encode('foo.avi', 'foo.mpg', 'dvd', 'pal', 'ffmpeg',
           quality=7, interlace='bottom', ...)

The supported keywords may vary by backend, but one of our goals should be to
implement a set of commonly-used keywords in all the backends.

Each backend has a top-level function:

    ffmpeg.encode(source, target, ...)
    mplayer.encode(source, target, ...)
    mpeg2enc.encode(source, target, ...)

The source and target are MediaFile objects from libtovid.media, containing
profiles of the input and output videos. Again, the "..." are optional keyword
arguments.
"""

__all__ = [\
    'encode',
    'get_encoder',
    'ffmpeg_encode',
    'encode_audio',
    'mencoder_encode',
    'mpeg2enc_encode']

import os
import math
import copy
import glob
from libtovid.cli import Command, Pipe
from libtovid.utils import float_to_ratio
from libtovid import rip
from libtovid.backend import mplayer
from libtovid.media import *
from libtovid.standard import fps
from libtovid import log


_bitrate_limits = {\
    'vcd': (1150, 1150),
    'kvcd': (400, 4000),
    'dvd-vcd': (400, 4000),
    'svcd': (900, 2400),
    'half-dvd': (600, 6000),
    'dvd': (900, 9000)
    }

# --------------------------------------------------------------------------
#
# Primary interface
#
# --------------------------------------------------------------------------

def encode(infile, outfile, format='dvd', tvsys='ntsc', method='ffmpeg',
           **kw):
    """Encode a multimedia file according to a target profile, saving the
    encoded file to outfile.
    
        infile:  Input filename
        outfile: Desired output filename (.mpg implied)
        format:  One of 'vcd', 'svcd', 'dvd' (case-insensitive)
        tvsys:   One of 'ntsc', 'pal' (case-insensitive)
        method:  Encoding backend: 'ffmpeg', 'mencoder', or 'mpeg2enc'
        **kw:    Additional keyword arguments (name=value)
    
    The supported keyword arguments vary by encoding method. See the encoding
    functions for what is available in each.
    """
    source = mplayer.identify(infile)
    # Add .mpg to outfile if not already present
    if not outfile.endswith('.mpg'):
        outfile += '.mpg'
    # Get an appropriate encoding target
    target = standard_media(format, tvsys)
    target.filename = outfile
    # Set desired aspect ratio, or auto
    if 'aspect' in kw:
        target = correct_aspect(source, target, kw['aspect'])
    else:
        target = correct_aspect(source, target, 'auto')
    
    # Some friendly output
    print "Source media:"
    print source
    print
    print "Target media:"
    print target
    
    # Get the appropriate encoding backend
    encode_method = get_encoder(method)
    # Evaluate high-level keywords
    kw = eval_keywords(**kw)
    # Encode!
    encode_method(source, target, **kw)


# Import available backends
from libtovid.backend import ffmpeg, mplayer, mpeg2enc

def get_encoder(backend):
    """Get an encoding function."""
    if backend == 'ffmpeg':
        return ffmpeg.encode
    elif backend in ['mplayer', 'mencoder']:
        return mplayer.encode
    elif backend == 'mpeg2enc':
        return mpeg2enc.encode


# --------------------------------------------------------------------------
#
# Helper functions
#
# --------------------------------------------------------------------------

def eval_keywords(**kw):
    """Interpret keywords that affect other keywords, and return the result.
    These are keywords that can be shared between multiple encoding backends.

    Supported keywords:
    
        quality:    From 1 (lowest) to 10 (highest) video quality.
                    Overrides 'quant' and 'vbitrate' keywords.
        fit:        Size in MiB to fit output video to (overrides 'quality')
                    Overrides 'quant' and 'vbitrate' keywords.

    """
    # Set quant and vbitrate to match desired quality
    if 'quality' in kw:
        kw['quant'] = 13-kw['quality']
        max_bitrate = _bitrate_limits[target.format][1]
        kw['vbitrate'] = kw['quality'] * max_bitrate / 10
    # Set quant and vbitrate to fit desired size
    if 'fit' in kw:
        kw['quant'], kw['vbitrate'] = _fit(source, target, kw['fit'])
    return kw


def _fit(source, target, fit_size):
    """Return video (quantization, bitrate) to fit a video into a given size.
    
        source:   MediaFile input (the video being encoded)
        target:   MediaFile output (desired target profile)
        fit_size: Desired encoded file size, in MiB

    """
    assert isinstance(source, MediaFile)
    assert isinstance(target, MediaFile)
    fit_size = float(fit_size)
    mpeg_overhead = fit_size / 100
    aud_vid_size = fit_size - mpeg_overhead
    audio_size = float(source.length * target.abitrate) / (8*1024)
    video_size = aud_vid_size - audio_size
    vid_bitrate = int(video_size*8*1024 / source.length)

    print "Length:", source.length, "seconds"
    print "Overhead:", mpeg_overhead, "MiB"
    print "Audio:", audio_size, "MiB"
    print "Video:", video_size, "MiB"
    print "VBitrate:", vid_bitrate, "kbps"

    # Keep bitrates sane for each disc format
    lower, upper = _bitrate_limits[target.format]
    quant = 3
    if vid_bitrate < lower:
        return (quant, lower)
    elif vid_bitrate > upper:
        return (quant, upper)
    else:
        return (quant, vid_bitrate)






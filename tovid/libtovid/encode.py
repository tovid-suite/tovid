#! /usr/bin/env python
# encode.py

"""Encode video to standard formats, using one of several supported backends.

One high-level function is provided::

    encode(infile, outfile, format, tvsys, method, ...)

where "..." is optional keyword arguments (described below). For example::

    encode('/video/foo.avi', '/video/bar.mpg', 'dvd', 'ntsc', 'ffmpeg')

This will encode '/video/foo.avi' to NTSC DVD format using ffmpeg, saving
the result as '/video/bar.mpg'. The ``format``, ``tvsys``, and ``method``
arguments are optional; if you do::

    encode('/video/foo.avi', '/video/bar.mpg')

then encoding will be DVD NTSC, using ffmpeg.

Keyword arguments may be used to further refine encoding behavior, for example::

    encode('foo.avi', 'foo.mpg', 'dvd', 'pal',
           quality=7, interlace='bottom', ...)

The supported keywords may vary by backend, but some keywords are supported
by all backends.
"""

__all__ = [
    'encode',
    'get_encoder',
]

from libtovid.backend import ffmpeg, mplayer, mpeg2enc
from libtovid.media import MediaFile, standard_media, correct_aspect


_bitrate_limits = {
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
           **kwargs):
    """Encode a multimedia file according to a target profile, saving the
    encoded file to outfile.
    
        infile
            Input filename
        outfile
            Desired output filename (.mpg implied)
        format
            One of 'vcd', 'svcd', 'dvd' (case-insensitive)
        tvsys
            One of 'ntsc', 'pal' (case-insensitive)
        method
            Encoding backend: 'ffmpeg', 'mencoder', or 'mpeg2enc'
        kwargs
            Additional keyword arguments (name=value)
    
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
    if 'aspect' in kwargs:
        target = correct_aspect(source, target, kwargs['aspect'])
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
    kwargs = eval_keywords(source, target, **kwargs)
    # Encode!
    encode_method(source, target, **kwargs)


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

def eval_keywords(source, target, **kwargs):
    """Interpret keywords that affect other keywords, and return the result.
    These are keywords that can be shared between multiple encoding backends.

    Supported keywords:
    
        quality
            From 1 (lowest) to 10 (highest) video quality.
            Overrides 'quant' and 'vbitrate' keywords.
        fit
            Size in MiB to fit output video to (overrides 'quality')
            Overrides 'quant' and 'vbitrate' keywords.

    """
    # Set quant and vbitrate to match desired quality
    if 'quality' in kwargs:
        kwargs['quant'] = 13-kwargs['quality']
        max_bitrate = _bitrate_limits[target.format][1]
        kwargs['vbitrate'] = kwargs['quality'] * max_bitrate / 10
    # Set quant and vbitrate to fit desired size
    if 'fit' in kwargs:
        kwargs['quant'], kwargs['vbitrate'] = \
            _fit(source, target, kwargs['fit'])
    return kwargs


def _fit(source, target, fit_size):
    """Return video (quantization, bitrate) to fit a video into a given size.
    
        source
            MediaFile input (the video being encoded)
        target
            MediaFile output (desired target profile)
        fit_size
            Desired encoded file size, in MiB

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






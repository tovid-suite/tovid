#! /usr/bin/env python
# __init__.py

__all__ = [\
    "encoders",
    "subtitles"]

import copy
from libtovid.utils import ratio_to_float
from libtovid.standards import get_target, Target
from libtovid.media import MediaFile
from libtovid.transcode import encoders

def encode(infile, outfile, format='dvd', tvsys='ntsc', method='ffmpeg'):
    """Encode a multimedia file according to a target profile, saving the
    encoded file to outfile.
        infile:  Input filename
        outfile: Desired output filename (.mpg implied)
        format:  One of 'vcd', 'svcd', 'dvd' (case-insensitive)
        tvsys:   One of 'ntsc', 'pal' (case-insensitive)
        method:  Encoding backend: 'ffmpeg', 'mencoder', or 'mpeg2enc'
    """
    media_in = MediaFile(infile)
    media_in.load()
    # Add .mpg to outfile if not already present
    if not outfile.endswith('.mpg'):
        outfile += '.mpg'

    # Get an appropriate encoding target
    target = get_target(format, tvsys)
    target = correct_aspect(media_in, target) # TODO: Allow overriding aspect?
    
    # Get the appropriate encoding backend and encode
    encoder = encoders.get_encoder(method)
    encoder(media_in, outfile, target)


def correct_aspect(infile, target, aspect='auto'):
    """Return a Target with corrected aspect ratio for encoding the given
    MediaFile. Input file aspect ratio may be overridden.

        infile:  Input MediaFile
        target:  Encoding Target
        aspect:  Aspect ratio to assume for input file (e.g., '4:3', '16:9')
                 or 'auto' to use autodetection

    """
    assert isinstance(infile, MediaFile)
    assert isinstance(target, Target)
    # Make a copy of the provided Target
    target = copy.copy(target)
    
    # Convert aspect (ratio) to a floating-point value
    src_aspect = ratio_to_float('4:3')
    if aspect is not 'auto':
        src_aspect = ratio_to_float(aspect)
    elif infile.video:
        src_aspect = ratio_to_float(infile.video.aspect)
    
    # Use anamorphic widescreen for any video 16:9 or wider
    # (Only DVD supports this)
    if src_aspect >= 1.7 and target.format == 'dvd':
        target_aspect = 16.0/9.0
        widescreen = True
    else:
        target_aspect = 4.0/3.0
        widescreen = False

    width, height = target.scale
    # If aspect matches target, no letterboxing is necessary
    # (Match within a tolerance of 0.05)
    if abs(src_aspect - target_aspect) < 0.05:
        scale = (width, height)
        expand = False
    # If aspect is wider than target, letterbox vertically
    elif src_aspect > target_aspect:
        scale = (width, int(height * target_aspect / src_aspect))
        expand = (width, height)
    # Otherwise (rare), letterbox horizontally
    else:
        scale = (int(width * src_aspect / target_aspect), height)
        expand = (width, height)
    # If infile is already the correct size, don't scale
    if infile.video:
        in_res = (infile.video.width,
                  infile.video.height)
        if in_res == scale:
            scale = False
            log.debug('Infile resolution matches target resolution.')
            log.debug('No scaling will be done.')

    # Final scaling/expansion for correct aspect ratio display
    target.scale = scale
    target.expand = expand
    target.widescreen = widescreen
    return target


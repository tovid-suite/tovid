#!/usr/bin/env python
# common.py
##
# Common functions for all encoders backend
##

__all__ = ['encode_audio']

# Imports
from libtovid.cli import Script, Arg
from libtovid.log import Log
import math

log = Log('libtovid.encoders.common')


# Functions

def encode_audio(infile, audiofile, options):
    """Encode the audio stream in infile to the target format.

    infile -- a MediaFile object
    audiofile -- string to filename
    options -- an OptionDict

    If no audio present, encode silence.
    """
    if options['format'] in ['vcd', 'svcd']:
        acodec = 'mp2'
    else:
        acodec = 'ac3'
    cmd = Arg('ffmpeg')
    # If infile was provided, encode it
    if infile.audio:
        cmd.add('-i', infile.filename)
    # Otherwise, generate 4-second silence
    else:
        # Add silence the length of infile.length
        ln = infile.length
        if ln < 4:
            # Minimum 4 secs :)
            ln = 4.0
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '%f' % ln)
    cmd.add_raw('-vn -ac 2 -ab 224')
    cmd.add('-ar', options['samprate'])
    cmd.add('-acodec', acodec)
    cmd.add('-y', audiofile)
    print "CMD: %s" % str(cmd)
    return str(cmd)

#! /usr/bin/env python2.4
# encoder.py

__doc__ = \
"""This module implements several backends for encoding a video file to
a standard MPEG format such as (S)VCD or DVD.
"""

__all__ = ['Encoder']

# TODO: Cleanup/modularize, move stuff to classes, make interface simple

import os
import sys
from subprocess import *

import libtovid
from libtovid.log import Log
from libtovid.utils import verify_app
from libtovid.globals import Config

log = Log('encoder.py')

class Encoder:
    """Base plugin class; all encoders inherit from this."""
    def __init__(self, video):
        log.info('Creating a VideoPlugin')
        self.video = video
        # Base name for output files
        self.basename = os.path.abspath(video['out'])
        self.identify_infile()
        self.preproc()







"""
Notes:

For DVD:
Filtering: -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup
-lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:
mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg


Stuff not yet used in plugins:

# Filters
mplayer:
SUBTITLES
    -noautosub
    -sub FILE
YUV4MPEG_ILACE
    ''
    :interlaced
    :interlaced_bf
VF_PRE
    ''
    -vf-pre il=d:d

VF_POST
    ''
    -vf-pre il=i:i
MPLAYER_OPTS
    (user-defined)

YUVDENOISE
    ''
    yuvdenoise |
ADJUST_FPS
    ''
    yuvfps -s $FORCE_FPSRATIO -r $TGT_FPSRATIO $VERBOSE |
    yuvfps -r $TGT_FPSRATIO $VERBOSE |


mpeg2enc
DISC_SIZE
    ''
    '4500'
    '700'
    (user-defined)

NONVIDEO_BITRATE
MTHREAD

MPEG2_FMT
+   !vcd: -b $VID_BITRATE

MPEG2_QUALITY
    vcd: -4 2 -2 1 -H
    other: -4 2 -2 1 -q $QUANT -H

"""

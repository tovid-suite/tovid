#! /usr/bin/env python

class VideoFilter:
    # Generic, encoder-level filters and customizations
    keywords = [ "ntsc", "dvd" ]
    crop = ( width, height )
    scale = ( width, height )
    expand = ( width, height )
    aspect = ( 16, 9 )
    quant = 4
    bitrate = 6000

class AudioFilter:
    bitrate = 224
    


# -*- coding: utf8 -*-
#@+leo-ver=4-thin
#@+node:eric.20090722212922.3418:@shadow playtime.py
#@@first

# Copyright 2007 Joe Friedrichsen <pengi.films@gmail.com>
# 
# This file is part of tovid.

"""Relate a video's bitrate, size, and play time

A video file (a/v stream) has three related characteristics:

    - Play length
    - Final output size
    - Encoded (average) bitrate

These are related by their units: ``bitrate = size / length``. This module
provides ways to calculate these values. 

You can predict/calculate any one of these characteristics given the
other two. By default, a new AVstream object assumes you want to find
the average bitrate from a known play length and final size::

    >>> avs = playtime.AVstream()
    >>> avs.play_length
    120.0
    >>> avs.final_size
    4400.0
    >>> avs.bitrate.kbps
    5126.3715555555555
    >>> avs.bitrate.MiBpm
    36.666666666666664
    >>> avs.bitrate.GiBph
    2.1484375

Usually when putting video on a disc, the final output size is well
defined and non-changing. By default, AVstream fixes this characteristic so
that you can see how the bitrate changes for different amounts of time on 
that disc::

    >>> avs.set_play_length(180)
    >>> avs.bitrate.kbps
    3417.5810370370368

However, if you know the video is a certain length, you can fix that instead
and find how bitrates change according to different output sizes::

    >>> avs.set_fixed_param('LENGTH')
    >>> avs.set_final_size(2000)
    >>> avs.bitrate.kbps
    1537.9114666666667

Finally, you're not limited to finding bitrates. You can fix the bitrate and
see how output size and play length are related::

    >>> avs.set_bitrate(1152, 'kbps')
    >>> avs.set_fixed_param('RATE')
    >>> avs.set_final_size(700)
    >>> avs.play_length
    84.954074074074072
    >>> avs.set_play_length(120)
    >>> avs.final_size
    988.76953125

"""

#@+others
#@+node:eric.20090722212922.3420:class AVstream
class AVstream:
    """Video file bitrate/size/length calculator object

    An AVstream object lets you calculate a video's bitrate, final size, or
    play length given the other two. Usually, you want to find the bitrate,
    and this is what AVstream does by default.

    Once instantiated, the bitrate can be accessed in three different units:

        - AVstream.bitrate.kbps -- kilobits per second (conventional)
        - AVstream.bitrate.MiBpm -- Mibibytes per minute
        - AVstream.bitrate.GiBph -- Gibibytes per hour

    There are four attributes:
        play_length
            the length of the video in minutes
        final_size
            the size of the video in MiB
        bitrate
            the bitrate of the video
        fixed_param
            the fixed characteristic

    Each of these attributes have a 'set_NAME' method that should be used
    to make changes so that the other attributes are updated automatically.

    """
    #@    @+others
    #@+node:eric.20090722212922.3421:__init__
    def __init__(self, play_length=120.0, final_size=4400.0):
        """Create a new AVstream object

            play_length
                the length in minutes (default = 120.0)
            final_size
                the final size in MiB (default = 4400.0)

        """
        self.play_length = play_length
        self.final_size = final_size
        self.bitrate = Bitrate( (final_size/play_length), 'MiBpm')
        self.fixed_param = "SIZE"

    #@-node:eric.20090722212922.3421:__init__
    #@+node:eric.20090722212922.3422:set_bitrate
    def set_bitrate(self, bitrate, units):
        """Set the bitrate for the stream and recalculate the variables
        according to the fixed parameter.

            bitrate
                number (integer or float ok)
            units
                the units that the bitrate is in. Valid unit arguments are
                'kbps', 'MiBpm', or 'GiBph'

        """
        self.bitrate.set(bitrate, units)
        if self.fixed_param == "RATE":
            pass
        elif self.fixed_param == "LENGTH":
            self._calculate_final_size()
        elif self.fixed_param == "SIZE":
            self._calculate_play_length()

    #@-node:eric.20090722212922.3422:set_bitrate
    #@+node:eric.20090722212922.3423:set_play_length
    def set_play_length(self, play_length):
        """Set the play length in minutes and recalculate variables according
        to the fixed parameter.

            play_length
                how long the video is (minutes)

        """
        self.play_length = play_length
        if self.fixed_param == "RATE":
            self._calculate_final_size()
        elif self.fixed_param == "LENGTH":
            pass
        elif self.fixed_param == "SIZE":
            self._calculate_bitrate()

    #@-node:eric.20090722212922.3423:set_play_length
    #@+node:eric.20090722212922.3424:set_final_size
    def set_final_size(self, final_size):
        """Set the final size in MiB (Mebibytes) and recalculate variables
        according to the fixed parameter.

            final_size
                how large the final size can/should be (MiB)

        """
        self.final_size = final_size
        if self.fixed_param == "RATE":
            self._calculate_play_length()
        elif self.fixed_param == "LENGTH":
            self._calculate_bitrate()
        elif self.fixed_param == "SIZE":
            pass

    #@-node:eric.20090722212922.3424:set_final_size
    #@+node:eric.20090722212922.3425:set_fixed_param
    def set_fixed_param(self, param):
        """Set the fixed parameter of the AVstream object.

            param
                The parameter to fix. Valid arguments are:
                - RATE (the bitrate of the AVstream)
                - LENGTH (the play length of the AVstream)
                - SIZE (the final size of the AVstream)

        """
        valid_params = ["RATE", "SIZE", "LENGTH"]
        if param in valid_params:
            self.fixed_param = param
        else:
            print("%s: bad new fixed_param -- %s" % ('playtime', param))
            print("%s: keeping old fixed_param -- %s" % \
                ('playtime', self.fixed_param))

    #@-node:eric.20090722212922.3425:set_fixed_param
    #@+node:eric.20090722212922.3426:_calculate_bitrate
    def _calculate_bitrate(self):
        """Find the bitrate given the length and size"""
        self.bitrate.set( (self.final_size/self.play_length), 'MiBpm')

    #@-node:eric.20090722212922.3426:_calculate_bitrate
    #@+node:eric.20090722212922.3427:_calculate_final_size
    def _calculate_final_size(self):
        """Find the final size give the bitrate and length"""
        self.final_size = self.bitrate.MiBpm * self.play_length

    #@-node:eric.20090722212922.3427:_calculate_final_size
    #@+node:eric.20090722212922.3428:_calculate_play_length
    def _calculate_play_length(self):
        """Find the length given the bitrate and size"""
        self.play_length =  self.final_size / self.bitrate.MiBpm


    #@-node:eric.20090722212922.3428:_calculate_play_length
    #@-others
#@-node:eric.20090722212922.3420:class AVstream
#@+node:eric.20090722212922.3429:class Bitrate
class Bitrate:
    """Convert between different bitrate units

    A Bitrate object stores a bitrate in three different units:

        kbps
            kilobits per second (the conventional unit)
        MiBpm
            Mibibytes per minute (uses for S/VCD sizes)
        GiBph
            Gibibytes per hour (useful for DVD sizes)

    Access these by name::

        >>> br = playtime.Bitrate(3300)
        >>> br.kbps
        3300
        >>> br.MiBpm
        23.603439331054688
        >>> br.GiBph
        1.3830140233039856

    Once instantiated or set with a given bitrate and unit, the other
    remaining bitrates are automatically calculated and updated::

        >>> br.set(1, 'GiBph')
        >>> br.kbps
        2386.0929422222221

    """
    #@    @+others
    #@+node:eric.20090722212922.3430:__init__
    def __init__(self, bitrate, unit='kbps'):
        """Create a new Bitrate object

            bitrate
                the bitrate (int or float ok)
            units
                'kbps', 'MiBpm', or 'GiBph'
        """
        self.set(bitrate, unit)

    #@-node:eric.20090722212922.3430:__init__
    #@+node:eric.20090722212922.3431:set
    def set(self, bitrate, unit):
        """Set the bitrate in 'unit' units.

            bitrate
                new bitrate (integer or float ok)
            units
                'kbps', 'MiBpm', or 'GiBph'

        Once set with a given bitrate and unit, the other remaining
        bitrates are automatically calculated.

        """
        valid_units = ["kbps", "MiBpm", "GiBph"]
        if unit in valid_units:
            self.unit = unit
            if self.unit == 'kbps':
                self.kbps = bitrate
                self._to_MiBpm()
                self._to_GiBph()
            elif self.unit == 'MiBpm':
                self.MiBpm = bitrate
                self._to_kbps()
                self._to_GiBph()
            elif self.unit == 'GiBph':
                self.GiBph = bitrate
                self._to_kbps()
                self._to_MiBpm()
        else:
            print("%s: bad new units -- %s" % ('playtime', unit))
            print("%s: keeping old units -- %s" % ('playtime', self.unit))
            print("%s: keeping old bitrate -- %s" % \
                ('playtime', getattr(self, self.unit)))

    #@-node:eric.20090722212922.3431:set
    #@+node:eric.20090722212922.3432:_to_kbps
    def _to_kbps(self):
        """Convert the bitrate to kbps"""
        if self.unit == 'kbps':
            bitrate = self.kbps
        elif self.unit == 'MiBpm':
            bitrate = self.MiBpm * (8.0*1024.0*1024.0) / (60.0*1000.0)
        elif self.unit == 'GiBph':
            bitrate = self.GiBph * (8.0*1024.0*1024.0*1024.0) / (60.0*60.0*1000.0)
        self.unit = 'kbps'
        self.kbps = bitrate

    #@-node:eric.20090722212922.3432:_to_kbps
    #@+node:eric.20090722212922.3433:_to_MiBpm
    def _to_MiBpm(self):
        """Convert the bitrate to MiBpm"""
        if self.unit == 'kbps':
            bitrate = self.kbps * (60.0*1000.0) / (8.0*1024.0*1024.0)
        elif self.unit == 'MiBpm':
            bitrate = self.MiBpm
        elif self.unit == 'GiBph':
            bitrate = self.GiBph * 1024.0 / 60.0
        self.unit = 'MiBpm'
        self.MiBpm = bitrate

    #@-node:eric.20090722212922.3433:_to_MiBpm
    #@+node:eric.20090722212922.3434:_to_GiBph
    def _to_GiBph(self):
        """Convert the bitrate to GiBph"""
        if self.unit == 'kbps':
            bitrate = self.kbps * (60.0*60.0*1000.0) / (8.0*1024.0*1024.0*1024.0)
        elif self.unit == 'MiBpm':
            bitrate = self.MiBpm * 60.0 / 1024.0
        elif self.unit == 'GiBph':
            bitrate = self.GiBph
        self.unit = 'GiBph'
        self.GiBph = bitrate

    #@-node:eric.20090722212922.3434:_to_GiBph
    #@-others
#@-node:eric.20090722212922.3429:class Bitrate
#@-others
#@-node:eric.20090722212922.3418:@shadow playtime.py
#@-leo

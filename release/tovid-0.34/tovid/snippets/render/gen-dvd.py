#!/usr/bin/env python
# -=- encoding: utf-8 -=-
#
# GPL - Copyright 2007 - Alexandre Bourget
#
# Program to generate a valid dvdauthor.xml file out of a couple of
# instructions and video files.
#

import os
import sys
import dvdauthor

disc = dvdauthor.Disc('Test Menu jump blah')
# important for many jumps.
disc.set_jumppad(True)

# NOTES:
#
# Enabling jumppad gives better results, otherwise it spits out errors.
#
# Ideally, we tell after each PGC what to do (each Title, Menu..) with set_pre_commands()
# and set_post_commands().
#
# See documentation for more details.
#
# Otherwise, everything seems fine.
#

vmgm = dvdauthor.VMGM()

titleset = dvdauthor.Titleset('The titleset')

title1 = dvdauthor.Title('Video 1')
title1.add_video_file('/path/to/VIDEO.vob')

titleset.add_title(title1)
disc.set_vmgm(vmgm)
disc.add_titleset(titleset)

print disc.xml('dvd')

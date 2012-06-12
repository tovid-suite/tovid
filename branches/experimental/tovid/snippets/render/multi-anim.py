#!/usr/bin/python
# -=- encoding: utf-8 -=-
#
# GPL - Copyright 2007 - Alexandre Bourget
#
# anim.py batch processor.
# Give it a .txt file filled with the command line
# parameters and it will run anim.py sequencially.
#

import os
import sys

if (len(sys.argv) < 2):
    print "Please specify the file to run. In this file, each line will be passed"
    print "directly to ./anim.py. Verify ./anim.py --help for options."
    sys.exit()

f = open(sys.argv[1])
l = f.readlines()
f.close()

for x in l:
    s = x.split()
    os.system("./anim.py %s" % (x.strip()))

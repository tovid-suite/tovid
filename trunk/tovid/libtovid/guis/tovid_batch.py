#! /usr/bin/env python
# tovid_batch.py

from libtovid.metagui import *
from libtovid.guis import tovid

_infiles = List('Input files', '-infiles', '',
    'List of video files to encode',
    Filename())

MAIN = VPanel('Main', _infiles, tovid.BASIC_OPTS)

def run():
    app = Application('tovid-batch',
        MAIN,
        tovid.VIDEO,
        tovid.AUDIO,
        tovid.BEHAVIOR)
    gui = GUI("tovid-batch metagui", 640, 720, app)
    gui.run()

if __name__ == '__main__':
    run()


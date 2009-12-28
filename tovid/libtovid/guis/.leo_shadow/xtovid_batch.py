#@+leo-ver=4-thin
#@+node:eric.20090722212922.3301:@shadow tovid_batch.py
#@+others
#@+node:eric.20090722212922.3302:tovid_batch declarations
# tovid_batch.py

from libtovid.metagui import *
from libtovid.guis import tovid

_infiles = List('Input files', '-infiles', '',
    'List of video files to encode',
    Filename())

MAIN = VPanel('Main', _infiles, tovid.BASIC_OPTS)

#@-node:eric.20090722212922.3302:tovid_batch declarations
#@+node:eric.20090722212922.3303:run
def run():
    app = Application('tovid-batch',
        MAIN,
        tovid.VIDEO,
        tovid.AUDIO,
        tovid.BEHAVIOR)
    gui = GUI("tovid-batch metagui", 640, 720, app)
    gui.run()

#@-node:eric.20090722212922.3303:run
#@-others
if __name__ == '__main__':
    run()

#@-node:eric.20090722212922.3301:@shadow tovid_batch.py
#@-leo

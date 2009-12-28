#@+leo-ver=4-thin
#@+node:eric.20090722212922.3284:@shadow idvid.py
#@+others
#@+node:eric.20090722212922.3285:idvid declarations
# idvid.py

from libtovid.metagui import *

_terse = Flag('Terse', '-terse')
_verbose = Flag('Verbose', '-verbose')
_fast = Flag('Fast', '-fast')
_tabular = Flag('Tabular', '-tabular')
_isformat = Choice('Is format', '-isformat', 'dvd',
    'Check the video for compliance with the given format',
    choices='vcd|svcd|dvd',
    toggles=True)
_istvsys = Choice('Is TV system', '-istvsys', 'ntsc',
    'Check whether the video is compliant with the given TV system',
    choices='ntsc|pal',
    toggles=True)

VIDEO_FILES = List('Video files', '', None,
    'List of multimedia video files to identify',
    Filename())

MAIN = VPanel('Main',
    _terse,
    _verbose,
    _fast,
    _tabular,
    _isformat,
    _istvsys,
    VIDEO_FILES,
)

#@-node:eric.20090722212922.3285:idvid declarations
#@+node:eric.20090722212922.3286:run
def run():
    app = Application('idvid', MAIN)
    gui = GUI('idvid gui', 400, 600, app)
    gui.run()

#@-node:eric.20090722212922.3286:run
#@-others
if __name__ == '__main__':
    run()

#@-node:eric.20090722212922.3284:@shadow idvid.py
#@-leo

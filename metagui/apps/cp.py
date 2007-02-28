#! /usr/bin/env python
# cp.py

from metagui import *

panel = Panel("Main",
    Filename('source', 'Source filename', ''),
    Filename('dest', 'Destination filename', '')
)

app = Application('cp', [panel])
gui = GUI('cp metagui', [app])
gui.run()

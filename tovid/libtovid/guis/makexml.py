#! /usr/bin/env python
# makexml.py

from libtovid.metagui import *

_dvd = Flag("DVD", '-dvd', True)
_vcd = Flag("VCD", '-vcd', False)
_svcd = Flag("SVCD", '-svcd', False)

_overwrite = Flag("Overwrite", '-overwrite', False,
    "Overwrite any existing .xml output file")
_quiet = Flag("Quiet", '-quiet', False,
    "Limit output to essential messages")

# TODO: Figure out how to handle multiple cases
# (video list, -menu <menu> video list, -slides <image list> etc.)
# and how to deal with -group / -endgroup
VIDEOS = List("Video files", '', None,
    "List of .mpg video files to include on the disc",
    Filename())

_menu = Filename("Menu file", '-menu', '',
    "Menu .mpg, linking to one or more videos.")

_slides = List("Slideshow images", '-slides', '',
    "Create a slide-show of still image files.",
    Filename())

_group = ''
_endgroup = ''

_topmenu = Filename("Top menu", '-topmenu', '',
    "Menu .mpg to use for the top (root-level) DVD menu. This menu "
    "should link to each of the other menus.")

_titlesets = Flag("Create titlesets", '-titlesets', False,
    "(DVD only) Forces the creation of a separate titleset per title. "
    "This is useful if the titles of a DVD have different video formats, "
    "e.g. PAL + NTSC or 4:3 + 16:9. If used with menus, there must be a "
    "-topmenu option that specifies a menu file with an entry for each "
    "of the titlesets.")

_chapters = Number("Chapter interval", '-chapters', 5,
    "(DVD only) Creates a chapter every INTERVAL minutes. This option "
    "can be put at any position in a <file list> and is valid for "
    "all subsequent titles until a new -chapters option is encountered. "
    "Using this option may take some time, since the duration of the "
    "video must be calculated.", 1, 60, 'minutes')

_nochapters = Flag("No chapters", '-nochapters', False,
    "Don't add any chapter points to the video.")

OUT_PREFIX = Filename("Output file", '', '',
    "Prefix of .xml file to write as output", 'save',
    "Choose an output prefix")

def run():
    pass

if __name__ == '__main__':
    run()


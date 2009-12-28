#@+leo-ver=4-thin
#@+node:eric.20090722212922.2814:@shadow constants.py
"""Identifiers for something or another.
"""

# Identifier for command-panel timer
ID_CMD_TIMER = 101
# Identifiers for output-format radio buttons
ID_FMT_VCD = 0
ID_FMT_SVCD = 1
ID_FMT_DVD = 2
ID_FMT_HALFDVD = 3
ID_FMT_DVDVCD = 4
# Identifiers for tv systems
ID_TVSYS_NTSC = 0
ID_TVSYS_NTSCFILM = 1
ID_TVSYS_PAL = 2
# Identifiers for aspect ratios
ID_ASPECT_FULL = 0
ID_ASPECT_WIDE = 1
ID_ASPECT_PANA = 2
# Identifiers for alignments
ID_ALIGN_LEFT = 0
ID_ALIGN_CENTER = 1
ID_ALIGN_RIGHT = 2
ID_ALIGN_WEST = 3
ID_ALIGN_MIDDLE = 4
ID_ALIGN_EAST = 5
ID_ALIGN_SOUTHWEST = 6
ID_ALIGN_SOUTH = 7
ID_ALIGN_SOUTHEAST = 8
# Identifiers for test fill types
ID_TEXTFILL_COLOR = 0
ID_TEXTFILL_FRACTAL = 1
ID_TEXTFILL_GRADIENT = 2
ID_TEXTFILL_PATTERN = 3
# Identifiers for notebook tabs
ID_NB_VIDEO = 0
ID_NB_MENU = 1
# Identifiers for disc tree element types
ID_DISC = 0
ID_MENU = 1
ID_VIDEO = 2
ID_SLIDE = 3
ID_GROUP = 4
# Identifiers for menu items
ID_MENU_FILE_PREFS = 101
ID_MENU_FILE_EXIT = 102
ID_MENU_FILE_SAVE = 103
ID_MENU_FILE_OPEN = 104
ID_MENU_FILE_NEW = 105
ID_MENU_VIEW_SHOWGUIDE = 201
ID_MENU_VIEW_SHOWTOOLTIPS = 202
ID_MENU_VIEW_ADVANCED = 203
ID_MENU_HELP_ABOUT = 301
ID_MENU_LANG = 400
ID_MENU_LANG_EN = 401
ID_MENU_LANG_DE = 402
# Identifiers for tasks, for the guide and help system
ID_TASK_GETTING_STARTED = 1001
ID_TASK_MENU_ADDED = 1002
ID_TASK_VIDEO_ADDED = 1003
ID_TASK_DISC_SELECTED= 1004
ID_TASK_VIDEO_SELECTED = 1005
ID_TASK_MENU_SELECTED = 1006
ID_TASK_PREP_ENCODING = 1007
ID_TASK_ENCODING_STARTED = 1008
ID_TASK_BURN_DISC = 1009
ID_TASK_GROUP_ADDED = 1010
ID_TASK_GROUP_SELECTED = 1011
# Identifiers for disc authoring
ID_BURN_VCD_XML = 1
ID_BURN_DVD_XML = 2
ID_BURN_FILE = 3


id_dict = {
    'tvsys': {
        ID_TVSYS_NTSC: "ntsc",
        ID_TVSYS_NTSCFILM: "ntscfilm",
        ID_TVSYS_PAL: "pal"
    },
    'format': {
        ID_FMT_DVD: "dvd",
        ID_FMT_HALFDVD: "half-dvd",
        ID_FMT_DVDVCD: "dvd-vcd",
        ID_FMT_SVCD: "svcd",
        ID_FMT_VCD: "vcd"
    },
    'aspect': {
        ID_ASPECT_FULL: "full",
        ID_ASPECT_WIDE: "wide",
        ID_ASPECT_PANA: "panavision"
    },
    'alignment': {
        ID_ALIGN_LEFT:      "northwest",
        ID_ALIGN_CENTER:    "north",
        ID_ALIGN_RIGHT:     "northeast",
        ID_ALIGN_WEST:      "west",
        ID_ALIGN_MIDDLE:    "middle",
        ID_ALIGN_EAST:      "east",
        ID_ALIGN_SOUTHWEST: "southwest",
        ID_ALIGN_SOUTH:     "south",
        ID_ALIGN_SOUTHEAST: "southeast"
    },
    'fillType': {
        ID_TEXTFILL_COLOR:    "Color",
        ID_TEXTFILL_FRACTAL:  "Fractal",
        ID_TEXTFILL_GRADIENT: "Gradient",
        ID_TEXTFILL_PATTERN:  "Pattern"
    }
}
#@-node:eric.20090722212922.2814:@shadow constants.py
#@-leo

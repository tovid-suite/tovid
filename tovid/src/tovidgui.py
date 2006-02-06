# -* python -*

# tovid GUI
# ===============
# A wxPython frontend for the tovid suite
#
# Project homepage: http://tovid.org/
#
# This software is licensed under the GNU General Public License
# For the full text of the GNU GPL, see:
#
#   http://www.gnu.org/copyleft/gpl.html
#
# No guarantees of any kind are associated with use of this software.

import os
import re
import pickle
import wx
#from wx.Python.help import *
# wx.Editor import
#from wx.Python.lib.editor import wx.Editor
import cStringIO, zlib # Needed for embedded bitmap icons
import threading
import gettext
# Hack until gettext works
def _(str):
    return str


# Import other tovid modules
from libtovid import TDL, Parser, Project

# ###################################################################
# ###################################################################
#
#
#                         GLOBAL CONFIGURATION
#
#
# ###################################################################
# ###################################################################


# Global help provider
#provider = wx.SimpleHelpProvider()
#wx.HelpProvider_Set(provider)

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
# Identifiers for notebook tabs
ID_NB_VIDEO = 0
ID_NB_MENU = 1
# Identifiers for disc tree element types
ID_DISC = 0
ID_MENU = 1
ID_VIDEO = 2
ID_SLIDE = 3
# Identifiers for menu items
ID_MENU_FILE_PREFS = 101
ID_MENU_FILE_EXIT = 102
ID_MENU_FILE_SAVE = 103
ID_MENU_FILE_OPEN = 104
ID_MENU_FILE_NEW = 105
ID_MENU_VIEW_SHOWGUIDE = 201
ID_MENU_VIEW_SHOWTOOLTIPS = 202
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
        ID_ALIGN_LEFT: "left",
        ID_ALIGN_CENTER: "center",
        ID_ALIGN_RIGHT: "right"
    }
}
def ID_to_text(idtype, id):
    """Convert widget ID numbers to string representations.
    """
    return id_dict[ idtype ][ id ]

def text_to_ID(txt):
    """Convert internal text identifiers into widget ID numbers
    """
    for idtype, subdict in id_dict.iteritems():
        for id, value in subdict.iteritems():
            if value == txt:
                return id
    print "text_to_ID: Couldn't match '%s'. Returning 0." % txt
    return 0



# ###################################################################
# ###################################################################
#
#
#                           OPTIONS 
#
#
# ###################################################################
# ###################################################################

# ===================================================================
#
# CLASS DEFINITION
# Disc options that apply to the entire disc
#
# ===================================================================
class DiscOptions:
    # ==========================================================
    # Class data
    # ==========================================================
    type = ID_DISC
    format = 'dvd'
    tvsys = 'ntsc'
    title = "Untitled disc"

    def __init__(self, format = 'dvd', tvsys = 'ntsc'):
        self.format = format
        self.tvsys = tvsys

    def toElement(self):
        """Convert the current disc options into a TDL Element
        and return it.
        """
        element = TDL.Element('Disc', self.title)
        element.set('tvsys', self.tvsys)
        element.set('format', self.format)

        # Find top menu
        for curItem in self.optionList:
            if curItem.type == ID_MENU:
                if curItem.isTopMenu:
                    element.set('topmenu', curItem.title)

        return element

    def fromElement(self, element):
        """Load current disc options from a TDL Element.
        """
        print "Loading Disc element:"
        print element.tdl_string()
        self.type = ID_DISC
        self.title = element.name
        self.format = element.get('format')
        self.tvsys = element.get('tvsys')
        
    # ==========================================================
    # Set disc layout hierarchy, given a list of VideoOptions,
    # MenuOptions, and SlideOptions
    # ==========================================================
    def SetLayout(self, optionList):
        self.optionList = optionList

    # ==========================================================
    # Return the 'makexml' command for generating XML for this disc
    # ==========================================================
    def GetCommand(self):
        # Get global configuration (for output directory)
        curConfig = Config()

        strCommand = "makexml -%s " % self.format
        strCommand += "-overwrite "

        for curItem in self.optionList:
            # Prefix -topmenu or -menu if necessary
            if curItem.type == ID_MENU:
                if curItem.isTopMenu:
                    strCommand += "-topmenu "
                else:
                    strCommand += "-menu "
            # Output path and encoded filename
            strCommand += "\"%s/%s.mpg\" " % \
                (curConfig.strOutputDirectory, curItem.outPrefix)

        # Use output filename based on disc title
        self.outPrefix = self.title.replace(' ', '_')

        # Save output filename in global Config
        curConfig.strOutputXMLFile = "%s/%s" % (curConfig.strOutputDirectory,
            self.outPrefix)
        curConfig.curDiscFormat = self.format

        # Use output directory
        strCommand += "\"%s/%s\"" % (curConfig.strOutputDirectory, self.outPrefix)
        return strCommand
        
# ===================================================================
# End DiscOptions
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Video encoding options. Contains all configuration options
# specific to encoding a video file with tovid.
#
# ===================================================================
class VideoOptions:
    # ==========================================================
    # Class data
    # ==========================================================
    # Type of item being encoded (menu, video or slides)
    type = ID_VIDEO
    # Title of the video itself
    title = "Untitled video"
    # -dvd, -half-dvd, -svcd, -dvd-vcd, -vcd
    format = 'dvd'
    # -ntsc or -pal
    tvsys = 'ntsc'
    # -full, -wide, or -panavision
    aspect = 'full'
    # Additional command-line options
    addoptions = ""
    # Duration is unknown
    #duration = -1 
    inFile = ""
    outPrefix = ""

    # ==========================================================
    # Initialize VideoOptions class
    # ==========================================================
    def __init__(self, format = 'dvd', tvsys = 'ntsc',
        filename = ""):
        self.SetDiscTVSystem(tvsys)
        self.SetDiscFormat(format)
        self.inFile = filename
        self.title = os.path.basename(filename).replace('_', ' ')
        self.outPrefix = "%s.tovid_encoded" % self.title

    def toElement(self):
        """Convert the current video options into a TDL Element
        and return it.
        """
        # Get global configuration (for output directory)
        curConfig = Config()
        # Create TDL Element and set relevant options
        element = TDL.Element('Video', self.title)
        element.set('tvsys', self.tvsys)
        element.set('format', self.format)
        element.set('aspect', self.aspect)
        element.set('in', self.inFile)
        element.set('out', "%s/%s" % (curConfig.strOutputDirectory, self.outPrefix))
        return element

    def fromElement(self, element):
        """Load current video options from a TDL Element.
        """
        print "Loading Video element:"
        print element.tdl_string()
        self.type = ID_VIDEO
        self.tvsys = element.get('tvsys')
        self.format = element.get('format')
        aspect = element.get('aspect')
        if aspect in [ 'full', 'wide', 'panavision' ]:
            self.aspect = aspect
        elif aspect == '4:3':
            self.aspect = 'full'
        elif aspect == '16:9':
            self.aspect = 'wide'
        elif aspect == '235:100':
            self.aspect = 'panavision'
        self.inFile = element.get('in')
        self.outPrefix = element.get('out')


    # ==========================================================
    # Assemble and return the complete command-line command for this object
    # ==========================================================
    def GetCommand(self):
        # Get global configuration (for output directory)
        curConfig = Config()

        # Always overwrite. Use better solution in future?
        strCommand = "tovid -overwrite "
        # Append tvsys, format, and aspect ratio
        strCommand += "-%s -%s -%s " % \
            (self.tvsys, self.format, self.aspect)

        # Append other options
        strCommand += "%s " % self.addoptions

        strCommand += "-in \"%s\" " % self.inFile
        strCommand += "-out \"%s/%s\" " % (curConfig.strOutputDirectory, self.outPrefix)
        return strCommand

    # ==========================================================
    # Make video compliant with given disc format
    # ==========================================================
    def SetDiscFormat(self, format):
        if format == 'vcd':
            self.format = format
        elif format == 'svcd':
            self.format = format
        elif format == 'dvd':
            # Don't change existing format unless it's VCD or SVCD
            if self.format in [ 'vcd', 'svcd' ]:
                self.format = 'dvd'

    # ==========================================================
    # Make menu compliant with given disc TV system
    # ==========================================================
    def SetDiscTVSystem(self, tvsys):
        self.tvsys = tvsys

    # ==========================================================
    # Copy the given VideoOptions' data into this object. Only
    # the encoding settings are copied; title and filename are
    # left alone.
    # ==========================================================
    def CopyFrom(self, opts):
        # If types are different, return
        if self.type != opts.type:
            return
        # Copy opts into self
        self.format = opts.format
        self.tvsys = opts.tvsys
        self.aspect = opts.aspect
        self.addoptions = opts.addoptions
        
# ===================================================================
# End VideoOptions
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Menu generation options. Contains all configuration options
# specific to generating a menu with makemenu
#
# ===================================================================
class MenuOptions:
    # ==========================================================
    # Class data
    # ==========================================================
    # Type of item being encoded (menu, video, or slides)
    type = ID_MENU
    isTopMenu = False
    # Title of the menu itself
    title = _("Untitled menu")
    # -ntsc or -pal
    tvsys = 'ntsc'
    # -dvd, -vcd, or -svcd
    format = 'dvd'
    # -background FILE
    background = ""
    # -audio FILE
    audio = ""
    # -align [left|center|right]
    alignment = 'left'
    # Other settings
    titles = []
    colorText = wx.Colour(255, 255, 255)
    colorHi = wx.Colour(255, 255, 0)
    colorSel = wx.Colour(255, 0, 0)
    outPrefix = ""

    # ==========================================================
    # Initialize MenuOptions class
    # ==========================================================
    def __init__(self, format = 'dvd', tvsys = 'ntsc',
        title = _("Untitled menu"), isTop = False):
        self.SetDiscFormat(format)
        self.SetDiscTVSystem(tvsys)
        self.title = title
        self.outPrefix = title.replace(' ', '_')
        self.isTopMenu = isTop
        # Default font
        self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, False, "Default")

    def toElement(self):
        """Convert the current menu options into a TDL Element
        and return it.
        """
        # Get global configuration (for output directory)
        curConfig = Config()
        # Create TDL Element and set relevant options
        element = TDL.Element('Menu', self.title)
        element.set('tvsys', self.tvsys)
        element.set('format', self.format)
        element.set('alignment', self.alignment)
        # Image and audio backgrounds, if any
        if self.background != "":
            element.set('background', self.background)
        if self.audio != "":
            element.set('audio', self.audio)
        element.set('textcolor', '"#%X%X%X"' % \
            (self.colorText.Red(), self.colorText.Green(), self.colorText.Blue()))
        # For DVD, highlight and select colors
        if self.format == 'dvd':
            element.set('highlightcolor', '"#%X%X%X"' % \
                (self.colorHi.Red(), self.colorHi.Green(), self.colorHi.Blue()))
            element.set('selectcolor', '"#%X%X%X"' % \
                (self.colorSel.Red(), self.colorSel.Green(), self.colorSel.Blue()))
        if self.font.GetFaceName() != "":
            element.set('font', self.font.GetFaceName())
        # Convert self.titles to ordinary strings
        strtitles = []
        for title in self.titles: strtitles.append(str(title))
        element.set('linksto', strtitles)
        return element

    def fromElement(self, element):
        """Load current video options from a TDL Element.
        """
        print "Loading Menu element:"
        print element.tdl_string()
        self.type = ID_MENU
        self.tvsys = element.get('tvsys')
        self.format = element.get('format')
        self.alignment = element.get('alignment')
        self.background = element.get('background')
        self.audio = element.get('audio')
        self.titles = element.get('linksto')
        # TODO: Find a good way to parse/assign colors and font

    # ==========================================================
    # Assemble and return the complete command-line command for this object
    # ==========================================================
    def GetCommand(self):
        # Get global configuration (for output directory)
        curConfig = Config()

        strCommand = "makemenu "
        # Append format and tvsys
        strCommand += "-%s -%s " % (self.tvsys, self.format)
        # Append alignment
        strCommand += "-align %s " % self.alignment

        # Image and audio backgrounds, if any
        if self.background != "":
            strCommand += "-background \"%s\" " % self.background
        if self.audio != "":
            strCommand += "-audio \"%s\" " % self.audio

        # Append text color
        strCommand += "-textcolor \"rgb(%d,%d,%d)\" " % \
            (self.colorText.Red(), self.colorText.Green(), self.colorText.Blue())
        # For DVD, append highlight and select colors
        if self.format == 'dvd':
            strCommand += "-highlightcolor \"rgb(%d,%d,%d)\" " % \
                (self.colorHi.Red(), self.colorHi.Green(), self.colorHi.Blue())
            strCommand += "-selectcolor \"rgb(%d,%d,%d)\" " % \
                (self.colorSel.Red(), self.colorSel.Green(), self.colorSel.Blue())

        # Append font
        if self.font.GetFaceName() != "":
            strCommand += "-font \"%s\" " % self.font.GetFaceName()

        # Append video/still titles
        for title in range(len(self.titles)):
            strCommand += "\"%s\" " % self.titles[ title ]

        strCommand += "-out \"%s/%s\"" % (curConfig.strOutputDirectory, self.outPrefix)

        return strCommand

    # ==========================================================
    # Make menu compliant with given disc format
    # ==========================================================
    def SetDiscFormat(self, format):
        self.format = format 

    # ==========================================================
    # Make menu compliant with given disc TV system
    # ==========================================================
    def SetDiscTVSystem(self, tvsys):
        self.tvsys = tvsys

    # ==========================================================
    # Copy the given MenuOptions' data into this object. Only
    # the encoding settings are copied; title and filename are
    # left alone.
    # ==========================================================
    def CopyFrom(self, opts):
        # Return if types are different
        if self.type != opts.type:
            return
        # Copy opts into self
        self.format = opts.format
        self.tvsys = opts.tvsys
        self.background = opts.background
        self.audio = opts.audio
        self.colorText = opts.colorText
        self.colorHi = opts.colorHi
        self.colorSel = opts.colorSel
        self.font = opts.font
        self.alignment = opts.alignment
        
# ===================================================================
# End MenuOptions
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Slide-generation options. Contains all configuration options
# specific to generating slides using makeslides
#
# ===================================================================
class SlideOptions:
    # ==========================================================
    # Class data
    # ==========================================================
    # Type of item being encoded (menu, video, or slides)
    type = ID_SLIDE
    # Title of the group of slides
    title = _("Untitled slides")
    # List of image files to convert to slides
    files = []
    # -dvd, -vcd, or -svcd
    format = 'dvd' 
    # -ntsc or -pal
    tvsys = 'ntsc'

    # ==========================================================
    # Initialize SlideOptions class
    # ==========================================================
    def __init__(self, format = 'dvd', tvsys = 'ntsc',
        files = []):
        self.tvsys = tvsys
        self.format = format 
        self.files = files

    # ==========================================================
    # Assemble and return the complete command-line command for this object
    # ==========================================================
    def GetCommand(self):
        strCommand = "makeslides -%s -%s " % \
            (self.tvsys, self.format)

    # ==========================================================
    # Make slides compliant with given disc format
    # ==========================================================
    def SetDiscFormat(self, format):
        self.format = format 

    # ==========================================================
    # Make slides compliant with given disc TV system
    # ==========================================================
    def SetDiscTVSystem(self, tvsys):
        self.tvsys = tvsys

    # ==========================================================
    # Copy the given SlideOptions' data into this object. Only
    # the encoding settings are copied; title and filename are
    # left alone.
    # ==========================================================
    def CopyFrom(self, opts):
        # If types are different, return
        if self.type != opts.type:
            return
        # Copy opts into self
        self.format = opts.format
        self.tvsys = opts.tvsys

# ===================================================================
# End SlideOptions
# ===================================================================


def element_to_options(element):
    """Takes a TDL element and returns a DiscOptions, MenuOptions,
    or VideoOptions object filled with appropriate values.
    """
    if element.tag == 'Disc':
        opts = DiscOptions()
    elif element.tag == 'Menu':
        opts = MenuOptions()
    elif element.tag == 'Video':
        opts = VideoOptions()
    else:
        print "element_to_options: unknown element.tag %s" % element.tag

    opts.fromElement(element)
    return opts


# ===================================================================
#
# VERSION WORKAROUNDS
# "Macro" functions to work around wx.Widgets/python
# version incompatibilities
#
# ===================================================================

# wx.TreeCtrl.GetFirstChild
def VER_GetFirstChild(obj, item):
    # For wx.Widgets >=2.5, cookie isn't needed
    if wx.MAJOR_VERSION == 2 and wx.MINOR_VERSION >= 5:
        return obj.GetFirstChild(item)
    # For other versions, use a dummy cookie
    else:
        return obj.GetFirstChild(item, 1)


# ===================================================================
#
# EMBEDDED ICONS
# Functions to return bitmaps for icons converted using img2py
#
# ===================================================================
# Menu icon, for menu elements inserted into disc layout tree
def GetMenuIcon():
    iconMenu = zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4\xe7{\xba8\x86X\xf4\
n\x9d|Z\xb0A\x81\xc7%^\xe6u\xd3\xa4\x15G'm\xd9XQ\xc0f\xec`#\xf1\x80\x89%\xad\
\\^\x9eq\x8a\xc3m\xc6\x90\xff\x99\x1d\x1c\xd1G\xf6\xaa\x19L\xf2_\xff\xabo\
\xef\xcf\x80\x03\x8b\xb6D\xf0=\x8biym\xb3\x8bWsz\x94\xff\xce\x92\xd7L\x19O\
\xc4\xda8\xd7\xac~\xbe\xc7\xac\xb1\xf4\xdf\xa3\xf8\xd9\x0bl\xd9\xa3\xe7\xcfR\
\xf83\xa1\xe5A\xf9>\xc6\xb9\x86\x96\xb2\xf7\xfb\xd6\x18\x03\xadf\xf0t\xf5sY\
\xe7\x94\xd0\x04\x00,qBs")
    stream = cStringIO.StringIO(iconMenu)
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

# Slide icon, for slide elements inserted into disc layout tree
def GetSlideIcon():
    iconSlide = zlib.decompress(
'x\xda\x01\xed\x01\x12\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\
\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\
\x08\x08\x08\x08|\x08d\x88\x00\x00\x01\xa4IDAT8\x8d\x9d\x92\xbbn\x13A\x14\
\x86\xbfsf\xd6\xb0Ndc%\xee\xa0%B\x88\x17\x80w\xa0 \x155B<\x01J^\x01\xa5\xce3\
\xf0\x1aTTH\xd4\x91\x02\x05\x82\x82\x04"\xdb\xf1\xae\xf7>\x14\xb3\x97\tq\x03\
\xa7\xd8\xd5\\\xcew\xfe\xff\xdf\x15\xc0\xf1\x9f\xe5\x9c\xc3\x02\x9c\xbd?C4\
\x1aX\xea\x10[cF\x15f\\`\'\x1b\xa2i\x8a\x9dn0q\x89\xa8c2>\x04\xf0\x00\x9a\
\x8a\x87/\x0f\xfeY\x81\x88t\x80\x12\x80\xc5\xe6\x07#\x1d\x91\x16\x96\xcf\xdf\
\xef\xb0\xca\x0cIa)k\xc5\x85F\x05\xc4\xc1\xabg\x1d\xa0\xce\xbc\'\x0c\xa2J\
\x14\tO\xee\x0b\x17k\xe1j\x03\xe7\xbf\xbd9\t\xfd\xb7o\x0f\xa8\x12\x00\x96\
\xb9\xe5\xdbJ)\x1b\xe5"\x15\xd2JXd\xc2d\x17\xe6c\x88-\x145\xa4\x15\xec\xc7!\
\xa0X\xfa\x851\xdc\x8b\r\x97\x99\xb2F\x99\xef(\x8f\xe6Bl\xfc\xe5\xcaA\xe3\
\xa0j \xd2\x10\x90_\x01\x904\x86\x9f\xb9\xe1\xbaTr\xa3\x9cg\xca\x97\x0c\xee\
\x1a0\nM\x03\xae\xf5/\x12\x02\xb2_\x00|\xcd-y\xa3\x14\xa2d\xaa\xb8\x114@*\
\xf8\x10\x8d\xcf\xc1\x05a\xb4\x80K\xbf\x98\x7f\xc2\x02;\xc0lkl\x12\xc4\'\xb7\
\x01\xd7\xebE{\xec/v\xd3\x04x\xb1\xfb\x9cm\xd5f\xb0\x00`\x95,\x87\xb9\xfd\
\xb0A\xc9\xd1\xc7\xb7\xcc&{\xcc\xa6{\xbcy\xf0z\xf8\x95\xbb\xcf\xb8J\x96=\xb9\
\x13\xef\x82\xa7?\x90\xbeyP\xe0\xea\xde\x02\x08N\x1c\xd2[\x0es\x80\xe3\xc7G}\
s\x0f88\xfdpK\xc1\xe0a\x08\xee\xdd\xd3\x93\x1b\xcd\x00\xe2\xda\x1d\x91\x9b\
\x93\xb6\xd5\xdf\xcd\x00\x7f\x002\xc3\xb1\x14\xa7\xc7#\xa6\x00\x00\x00\x00IE\
ND\xaeB`\x82\n\xfd\xd6$')
    stream = cStringIO.StringIO(iconSlide)
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

# Video icon, for video elements inserted into disc layout tree
def GetVideoIcon():
    iconVideo = zlib.decompress(
'x\xda\x01*\x01\xd5\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x00\xe1IDAT8\x8d\xe5\x93\xc1\x8d\x830\x10E\
\xdf\xb7L\xa4\xe4`\x94\x94\x80\xb4\xb2v\xeb\xa2\x05\x0eP\x00\x07j\xa0\x804\
\xb3- Q\xc9\xe4\x00\xde8$Y\x0e{\\_\xc6\x7f\xfcg\xfe\x9f\x91,\xc0\xea\xba\x06\
`\x1cG\x00\xf6\xf00\x0c\xc4\x18\t!\xe0\xfb\xbe\xa7m[\x00\xaa\xaa\x02\xd8\xc5\
M\xd3\x000\xcf3\x8e?\x1e\xdfu\x1d\xd34=X\xdc\xc3\xde{b\x8c\x94e\x89\xe2\xf5\
\xdb\x0eN\x14\x12\xde\x89\xc2\x89\x83\x96X\xa4\x98\xdf%\xbe\xce\'>/\'>\xce\
\xc7\xfb\x08\xa6%\xcaR\xe2\x17\xdf\x02[\t.\x91e\xa0\r\xe9]q~\\\xae\x9e\x84\
\xdf\x89\'wy\x0f\x97@*R"\xbc\xe8\x92\x84\xf2\'\x97w~\xaa\xd9\x8ea\xd9\x8eV\
\xbe\xb3\x95\xa8G\xde\x92\xd8.T\xd9\xb8\xd2\xdd\x01\xb6pR\xcdS\xb3\x17f0\xfb\
\x19\xf7?\xff\x85\x10\x027\xf2jp2\xad\x82\x02\x0b\x00\x00\x00\x00IEND\xaeB`\
\x82I4{\xad')
    stream = cStringIO.StringIO(iconVideo)
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

# Disc icon, for root element
def GetDiscIcon():
    iconDisc = zlib.decompress(
'x\xda\x01N\x03\xb1\xfc\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x03\x05IDAT8\x8dm\x93Mh\\e\x18\x85\x9f\xef\
\xde\xef\xbbw\xfe2vft&\t\xc6&Qcc\xa9\xa9\x0b\x17"U\x14\xa9\x82\xa2\xd6\x82)F\
\xad.\xa4\xd8\xdcUt\xd14UDP\x11\xc5\x11\x19\\\xb8P4\x15l\xfd[\x14[\x94\x16iI\
R\xb4XB\xabPA\x13kB\xdb$\xd3L23\x99\x9f\x9b{\xef\xe7b\xea\x90\x80\xef\xe6}\
\x17\xe7\x9c\xc59\xef\x11Zk\xcd\x9a\xf9\xee\xdb\xc3\xcc\x17\n\xa4Z\xef$\xdc\
\xd2M\xb1hR\xb88\xc1\xe5\xe93\xf4l\xee\xe2\xd9\x17v\xaf\x85#\xd6\n\x8c\xbe\
\xff.O\xf6?\x8a\xbe>\xc2_\xff\xc4\xb8ZP,.\x99X\xe5?Q\xd5\x19T<\xc5\xe9s\x93\
\xbc:\xf2RS\xc0\xf8\xef8:\xfc\x0eO\xddq7\xa2\xe8B\xa9N\xbc\xc5\xc5\x94\x1a\
\x01\x88\xc0\xc5\xf0*\x98\xd1$\xf7=\xfc4_\xe4\x8e\xac\x17x{\xcf\x107wvS\x9b]\
\xc6\x98-a,\xd5\xb9!\xe1b)\x8dF`\xf8Ud\xb2\x033\x96\xa2\xa3.\xd8\xde\xb7\x8d\
\xcf\xdf\xf8\x14\x00\xf3\xc6L\xfb\xeb\xe9H\x82\xaa\xefS\x0f|\xac\x15\x8f\x88\
\x16\xe8\xa8\xa2\xa4\xc3,.)\xec\xf2\x05\xac\xd6[\xe9 Fb5 \x12x\xdc\xde\xdd\
\xc9\xf7\xe3? \x8f\x9f\x1a\xa7\xf7\x96^ZL\xc5\x9c\x15b\xbe^\xa3{\xca%\x9b\
\xcb\xf2\xd5\xd8O\xb8\xab\x06\x0fl\xbb\x9f\x0fF>!]\xf3\x10\xaa\x82\x9650W)\
\xcd\xce"U<\xce\x82[\xe3\xb2\xae V\x8a\\\'\x15o~y\x8c\xf13\x13\xe4r9\x00\x1c\
\xc7\xa1\xd5\x8e\x91\x1d\xde\x07\xa6\x0b\xd2\x05\xd3c\xcb\xe6\x0c\xb2\xb3\
\xbd\x1di\xcak\x994\xd6\xd9\xdf&\xc9\xe5r\x0c\x0e\x0e6\xcdz\xed\xc00\xd9\xec\
\x8e&\x06\r\x1b{,d2\x1a\xc6\xb6,\xa4a\xa0L\x13[J\xa4\xd9\x0cgM\xe0\x92\x88\
\x7f\x0f\xb8\x01\xda\xf3\x11\x9e\xc6\xac\xd7\x90A\xb5J:\x99 \xa4\x14\x99x\
\x94\x8d\xa9\r<q\xefv\x1c\xc7ir\x1d\xc7a\xefs\x8f\xa3\xe3\x1a<\x1bQ\x0f\xd0^\
\xc0\xf4\xdcEd\xb5\xbc\xc4\xa6\xb6>\xd2\xb1(\xb6\x081\xfdw\x8d\xdd\x0f\r\x92\
_\xf4\xd8\xbfo?\xd2\x14\xf4\xdf5\xc0[/>\x0f\x95\xf3`u@\xb4\rV}&\xa7. \xbe>8\
\xaa\x1f\xe9\xb9\x8d+W\\\xf2W=\x96\x8b>\x85\x82\xcf\x86\xa4I*\xa3\xd8\xd4\
\x1bc\xe6d\x08\xbb\xa5Dfk\x1e+\x11F\xc8\x14Xm\x1c99\x86\xb1s\xe0\x19>:\xf4#s\
\x0b\r\xf2\xf2\xb2O8*\xb0\xc3\x06R5\xdc\xb2b\x9a\xf2\xa5\x18\xa5KQ\x82Z\t\
\xfc<\x87\xbe\xf9\x8c\xc7v\xeeh|\xe2\xd0{#\x8cM\xfeJ\xb9\x1c`J\xb0m\x03e\t\
\xec\x90\x81\x00dH\xe3\xb9\x8a\xcaB\x98\x95\xb9\x08\'NM\xb0k\xcf+\xeb\xbb\
\xf0\xf2\x87C\x9c\xfec\x0c\xeb\x1aY*\x81m\x1b\x8dW\xb64*\x12P\xcd\x879|\xecg\
\x1e\x1c8\xf0\xffm\x04\x18\xfd\xf8 3\xbfO\xd3\xdb\xd5\xc5\xd6\xbe\x9bH\xc6m\
\xce\xff2\xcf\xd9sS\xa4\xb7\xb4\xb2ko\xff\xbat\xff\x05\x8e\xd3%\xe2\x90864\
\x00\x00\x00\x00IEND\xaeB`\x82\xb5\xe0\x8b\x86')
    stream = cStringIO.StringIO(iconDisc)
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

# ===================================================================
# End embedded icons
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# "Borg" monostate class containing global configuration information
# Thanks to Alex Martelli for the design pattern
#
# ===================================================================
class Config:
    __shared_state = {}

    # ==========================================================
    # Class data (will be used as if it is static)
    # ==========================================================
    # Has Config been initialized yet?
    isInitialized = False
    # Will contain fonts available in both WX and IM
    strAvailFonts = []
    # Target output directory for encoded files and finished disc
    strOutputDirectory = "/tmp"
    # XML filename used for makexml output
    strOutputXMLFile = "/tmp/untitled"
    # Is the current project a (S)VCD or DVD?
    # (TEMPORARY: Move this to a "project" class later)
    curDiscFormat = 'dvd' 
    # Reference to the GuidePanel used throughout the GUI
    panGuide = None
    # Reference to the status bar
    statusBar = None

    # ==========================================================
    # Initialize monostate Config class
    # ==========================================================
    def __init__(self):
        self.__dict__ = self.__shared_state

        # Initialize class data if needed
        if self.isInitialized == False:
            self.ConfigInit()

    # ==========================================================
    # The real initialization function, only called once
    # Initializes "static" class data
    # ==========================================================
    def ConfigInit(self):
        self.isInitialized = True
        self.ConfigAvailFonts()
        #self.InitLocales()
    
    # ==========================================================
    # Determine fonts that are available in both wx.Python and ImageMagick
    # ==========================================================
    def ConfigAvailFonts(self):
        # Find out what fonts are available in ImageMagick
        strIMFonts = []
        fIMOutput = os.popen("convert -list type | grep -v \"^$\|^Name\|^Path:\|^--\" | sort", 'r')
        # Read ImageMagick's output and append to strIMFonts
        curLine = fIMOutput.readline().strip('\n ')
        while curLine != "":
            strIMFonts.append(curLine)
            curLine=fIMOutput.readline().strip('\n ')

        fIMOutput.close()
    
        # Get fonts available to wx.Python
        enuWXFonts = wx.FontEnumerator()
        enuWXFonts.EnumerateFacenames()
        strWXFonts = enuWXFonts.GetFacenames()
        strWXFonts.sort()

        # For each font in wx.Python, see if it's also available in
        # ImageMagick. If so, append it to a new list
        for wxfont in range(len(strWXFonts)):
            for im in range(len(strIMFonts)):
                if strIMFonts[im].find(strWXFonts[wxfont]) != -1:
                    self.strAvailFonts.append(strWXFonts[wxfont])
                    break

    def UseLanguage(self, lang):
        self.trans[ lang ].install()

    def InitLocales(self):
        self.trans = {}

        try:
            self.trans['en'] = gettext.translation('tovidgui', '.', ['en'])
            #self.trans['de'] = gettext.translation('tovidgui', '.', ['de'])
        except IOError:
            print "Couldn't initialize translations"


# ===================================================================
# End Config
# ===================================================================


# ###################################################################
# ###################################################################
#
#
#                 MISCELLANEOUS SUPPORTING CLASSES
#
#
# ###################################################################
# ###################################################################


# ===================================================================
#
# CLASS DEFINITION
# Video statistics-seeking thread class. Runs in the
# background determining duration and size of input videos
#
# ===================================================================
class VideoStatSeeker(threading.Thread):

    # ==========================================================
    # Class data (will be used as if it is static)
    # ==========================================================
    # List of VideoOptions objects to gather statistics on
    listVideoOptions = []

    # ==========================================================
    # Initialize VideoStatSeeker and Thread base class
    # ==========================================================
    def __init__(self, vidOptions):
        threading.Thread.__init__(self)

        # Add vidOptions to end of queue; thread will later
        # gather statistics and store them back in vidOptions
        self.listVideoOptions.append(vidOptions)
        self.doneWithStats = False

    # ==========================================================
    # Runs in background to gather and save statistics
    # ==========================================================
    def run(self):
        # For each video in queue, get and save stats
        while len(self.listVideoOptions) > 0:
            curOpts = self.listVideoOptions.pop(0)
            #curStatCmd = os.popen("idvid -terse \"%s\" | grep DURATION | sed -e \"s/DURATION://g\"" % curOpts.inFile, 'r')
            #curOpts.duration = curStatCmd.readline().strip('\n ')
            #curStatCmd.readlines()
            #curStatCmd.close()
            #print "VideoStatSeeker: duration for %s is %s" % (curOpts.inFile, curOpts.duration)

        # Done with current batch of statistics
        self.doneWithStats = True

# ===================================================================
# End VideoStatSeeker
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# A more flexible tree class. Has functions for moving elements
# between branches and copying elements
#
# ===================================================================
class FlexTreeCtrl(wx.TreeCtrl):
    
    def __init__(self, parent, id, pos = wx.DefaultPosition,
        size = wx.DefaultSize, style = wx.TR_HAS_BUTTONS,
        validator = wx.DefaultValidator, name = "FlexTreeCtrl"):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style, validator, name)
        """Initialize FlexTreeCtrl."""
        

    def CopyChildren(self, dest, src, recursively = True):
        """Copy all children of src to dest. Recurse if desired."""
        # Get the first child
        nextChild, cookie = VER_GetFirstChild(self, src)
        # As long as there are more children, append them to dest
        while nextChild.IsOk():
            newChild = self.AppendItem(dest,
                self.GetItemText(nextChild),
                self.GetItemImage(nextChild),
                self.GetItemImage(nextChild, wx.TreeItemIcon_Selected))
            self.SetPyData(newChild, self.GetPyData(nextChild))
            # If the child has children of its own and recursive is
            # True, call CopyChildren on this child
            if recursively and self.ItemHasChildren(nextChild):
                self.CopyChildren(newChild, nextChild, True)
            # Get the next child
            nextChild, cookie = self.GetNextChild(src, cookie)


    def MoveChildren(self, dest, src, recursively = True):
        """Recursively move all children of src to dest."""
        self.CopyChildren(dest, src, recursively)
        self.DeleteChildren(src)


    def AppendItemCopy(self, parent, src, recursively = True):
        """Append a copy of src under parent. Copy all children, and recurse if
        desired.  Returns the wx.TreeItemId of the copy, or an invalid item if
        something went wrong."""
        # Make sure parent and src are valid
        if not parent.IsOk() or not src.IsOk():
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.AppendItem(parent, self.GetItemText(src),
            self.GetItemImage(src), self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem


    def PrependItemCopy(self, parent, src, recursively = True):
        """Prepend a copy of src under parent. Copy all children, and recurse
        if desired.  Returns the wx.TreeItemId of the copy, or an invalid item
        if something went wrong."""
        # Make sure parent and src are valid
        if not parent.IsOk() or not src.IsOk():
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.PrependItem(parent, self.GetItemText(src),
            self.GetItemImage(src),
            self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem


    def InsertItemCopy(self, parent, src, prev, recursively = True):
        """Insert a copy of src under parent, after prev. Copy all children,
        and recurse if desired.  Returns the wx.TreeItemId of the copy, or an
        invalid item if something went wrong."""
        # Make sure parent, src, and prev are valid
        if not parent.IsOk() or not src.IsOk() or not prev.IsOk():
            return wx.TreeItemId()
        # Make sure prev is a child of parent
        if self.GetItemParent(prev) != parent:
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.InsertItem(parent, prev, self.GetItemText(src),
            self.GetItemImage(src),
            self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem


    def AppendItemMove(self, parent, src):
        """Move src, and all its descendants, under parent, at the end of
        parent's children.  If src is an ancestor of parent, do nothing.
        Returns the wx.TreeItemId of the copy, or an invalid item if something
        went wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.AppendItemCopy(parent, src, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem


    def PrependItemMove(self, parent, src):
        """Move src, and all its descendants, under parent, at the beginning of
        parent's children.  If src is an ancestor of parent, do nothing.
        Returns the wx.TreeItemId of the copy, or an invalid item if something
        went wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.PrependItemCopy(parent, src, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem


    def InsertItemMove(self, parent, src, prev):
        """Move src, and all its descendants, under parent, after parent's
        child prev.  If src is an ancestor of parent, do nothing.  Returns the
        wx.TreeItemId of the copy, or an invalid item if something went
        wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.InsertItemCopy(parent, src, prev, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem


    def ItemIsAncestorOf(self, item1, item2):
        """Return True if item1 is an ancestor of item2, False otherwise"""
        curAncestor = self.GetItemParent(item2)
        while curAncestor.IsOk():
            if curAncestor == item1:
                return True
            curAncestor = self.GetItemParent(curAncestor)

        # Root was reached and item1 was not found
        return False

    def MoveItemUp(self):
        """Move the currently-selected item up in the list.  Item stays within
        its group of siblings."""
        curItem = self.GetSelection()
        prevItem = self.GetPrevSibling(curItem)
        parentItem = self.GetItemParent(curItem)
        # If previous sibling is OK, move-insert the previous
        # sibling after the current item
        if prevItem.IsOk():
            newItem = self.InsertItemMove(parentItem, prevItem, curItem)
            if newItem.IsOk():
                self.SelectItem(curItem)

    def MoveItemDown(self):
        """Move the currently-selected item down in the list.  Item stays
        within its group of siblings."""
        curItem = self.GetSelection()

        nextItem = self.GetNextSibling(curItem)
        parentItem = self.GetItemParent(curItem)
        # If next sibling is OK, move-insert current item
        # after next sibling
        if nextItem.IsOk():
            newItem = self.InsertItemMove(parentItem, curItem, nextItem)
            if newItem.IsOk():
                self.SelectItem(newItem)

    def Delete(self, item):
        """Overridden Delete() function. Intelligently selects the previous
        item prior to deletion."""
        lastItem = item
        curParent = self.GetItemParent(item)
        prevSib = self.GetPrevSibling(lastItem)
        wx.TreeCtrl.Delete(self, lastItem)
        # Select the previous sibling, or the parent if
        # there was no previous sibling
        if prevSib.IsOk():
            self.SelectItem(prevSib)
        else:
            self.SelectItem(curParent)

    def GetReferenceList(self, topItem):
        """Returns a list of all data references in the branch descending from
        topItem."""
        # If topItem is not OK, just return
        if not topItem.IsOk():
            return
        refs = []
        # Append topItem's data
        refs.append(self.GetPyData(topItem))
        # Recursively append children
        child, cookie = VER_GetFirstChild(self, topItem)
        while child.IsOk():
            # If item has children, recurse
            if self.ItemHasChildren(child):
                grandchildren = self.GetReferenceList(child)
                refs.extend(grandchildren)
            # Otherwise, just append this item
            else:
                refs.append(self.GetPyData(child))

            # Get the next child
            child, cookie = self.GetNextChild(topItem, cookie)
        # Return the results
        return refs

# ===================================================================
# End FlexTreeCtrl
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# HeadingText, a larger, bold static text control to use for headings
#
# ===================================================================
class HeadingText(wx.StaticText):
    def __init__(self, parent, id, label):
        wx.StaticText.__init__(self, parent, id, label)
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        self.SetFont(font)

# ===================================================================
# End HeadingText
# ===================================================================

# ===================================================================
#
# CLASS DEFINITION
# BoldToggleButton, a normal wx.ToggleButton with bold font
#
# ===================================================================
class BoldToggleButton(wx.ToggleButton):
    def __init__(self, parent, id, label):
        wx.ToggleButton.__init__(self, parent, id, label,
            wx.DefaultPosition, wx.Size(-1, 40))
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        self.SetFont(font)

# ===================================================================
# End BoldToggleButton
# ===================================================================
        
# ===================================================================
#
# CLASS DEFINITION
# Hidable panel. A simple horizontal/vertical panel containing
# show/hide controls and one additional window or sizer, added via
# the Add() method. Caller is responsible for not abusing these
# assumptions.
#
# To use HidablePanel, first declare a HidablePanel object. Then,
# create the wx.Window object that will go into the HidablePanel,
# passing the HidablePanel as its parent. Add the HidablePanel to
# the desired location (inside another sizer). Finally, call SetParent
# with the containing sizer as the argument, to let the HidablePanel
# know what sizer contains it.
#
# ===================================================================
class HidablePanel(wx.Panel):

    # ==========================================================
    # Initialize hidable panel. orientation is wx.VERTICAL or
    # wx.HORIZONTAL. A vertical panel has the hide controls at
    # the top and extends downwards; a horizontal one has
    # controls on the left and extends rightwards.
    # ==========================================================
    def __init__(self, parent, id, orientation = wx.VERTICAL):
        wx.Panel.__init__(self, parent, id)

        # Reference to contained content (window or sizer)
        self.content = None
        self.sizParent = None

        # Show/hide button
        self.btnShowHide = wx.ToggleButton(self, wx.ID_ANY, _("More >>"))
        self.btnShowHide.SetValue(True)
        wx.EVT_TOGGLEBUTTON(self, self.btnShowHide.GetId(), self.ShowHide)

        self.sizMain = wx.BoxSizer(orientation)
        self.sizMain.Add(self.btnShowHide, 0)

        self.SetSizer(self.sizMain)

    # ==========================================================
    # Set the window/sizer that the panel will contain
    # ==========================================================
    def SetContent(self, newContent):
        self.content = newContent
        self.sizMain.Add(self.content, 1, wx.EXPAND)
        self.sizMain.SetItemMinSize(self.content, 200, 200)
        self.sizMain.Layout()
    
    # ==========================================================
    # Set the parent sizer (the sizer that holds the HidablePanel)
    # ==========================================================
    def SetParent(self, parent):
        self.sizParent = parent

    # ==========================================================
    # Show/hide the main part of the sizer based on state of
    # btnShowHide
    # ==========================================================
    def ShowHide(self, evt):
        # If button is down, show content
        if self.btnShowHide.GetValue() == True:
            self.sizMain.Add(self.content)
            self.content.Show()
            self.sizMain.Layout()
        # Otherwise, hide content
        else:
            self.sizMain.Remove(self.content)
            self.content.Hide()
            self.sizMain.Layout()
        # Layout parent, if it has been set
        if self.sizParent != None:
            self.sizParent.Layout()

# ===================================================================
# End HidablePanel
# ===================================================================


# ###################################################################
# ###################################################################
#
#
#                             DIALOGS
#
#
# ###################################################################
# ###################################################################
        

# ===================================================================
#
# CLASS DEFINITION
# Preferences/configuration settings dialog
#
# ===================================================================
class PreferencesDialog(wx.Dialog):
    # ==========================================================
    # Initialize PreferencesDialog
    # ==========================================================
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "tovid GUI Preferences", wx.DefaultPosition,
                (400, 200))

        # Center dialog
        self.Centre()

        # Get global configuration
        self.curConfig = Config()
        
        # Heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "Preferences")

        # OK/Cancel buttons
        self.btnOK = wx.Button(self, wx.ID_OK, "OK")
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.sizButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.sizButtons.Add(self.btnOK, 1, wx.EXPAND | wx.ALL, 16)
        self.sizButtons.Add(self.btnCancel, 1, wx.EXPAND | wx.ALL, 16)
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
        
        # Main sizer to hold all controls
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        # Controls will go here
        self.sizMain.Add(self.sizButtons, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Event handler for OK button
    # Assign configuration to underlying Config
    # ==========================================================
    def OnOK(self, evt):
        # Config assignment goes here
        self.EndModal(wx.ID_OK)
        
# ===================================================================
# End PreferencesDialog
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Simple text editor (for editing configuration files) in a frame
#
# ===================================================================
class MiniEditorFrame(wx.Frame):
    # ==========================================================
    # Initialize MiniEditorFrame
    # Takes same arguments as a frame, in addition to a filename
    # ==========================================================
    def __init__(self, parent, id, filename):
        wx.Frame.__init__(self, parent, id, "%s (MiniEditor)" % filename, wx.DefaultPosition,
            (500, 400), wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Current directory is current dirname
        self.dirname = os.getcwd()

        # Center dialog
        self.Centre()

        # Menu bar
        self.menubar = wx.MenuBar()
        
        # File menu
        self.menuFile = wx.Menu()
        self.menuFile.Append(ID_MENU_FILE_NEW, "&New", "Start a new file")
        self.menuFile.AppendSeparator()
        self.menuFile.Append(ID_MENU_FILE_OPEN, "&Open", "Open a new file")
        self.menuFile.Append(ID_MENU_FILE_SAVE, "&Save", "Save current file")
        self.menuFile.AppendSeparator()
        self.menuFile.Append(ID_MENU_FILE_EXIT, "E&xit", "Exit mini editor")
        
        # Menu events
        wx.EVT_MENU(self, ID_MENU_FILE_NEW, self.OnNew)
        wx.EVT_MENU(self, ID_MENU_FILE_OPEN, self.OnOpen)
        wx.EVT_MENU(self, ID_MENU_FILE_SAVE, self.OnSave)
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.OnExit)

        # Build menubar
        self.menubar.Append(self.menuFile, "&File")
        self.SetMenuBar(self.menubar)

        # Editor window
        self.editWindow = wx.Editor(self, wx.ID_ANY, style = wx.SUNKEN_BORDER)
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.editWindow, 1, wx.EXPAND | wx.ALL, 6)

        # Open the given filename and load its text into the editor window
        self.OpenFile(filename)

        self.SetSizer(self.sizMain)

    # Create a new file
    def OnNew(self, evt):
        # Just empty edit window and set filename to null
        self.editWindow.SetText([""])
        self.currentFilename = ""
        # Set title to indicate that a new file is being edited
        self.SetTitle("Untitled file (MiniEditor)")
        
    def OnOpen(self, evt):
        inFileDialog = wx.FileDialog(self, _("Choose a file to open"), self.dirname, "",
            "*.*", wx.OPEN)
        if inFileDialog.ShowModal() == wx.ID_OK:
            self.dirname = inFileDialog.GetDirectory()
            # Open the file
            self.OpenFile(inFileDialog.GetPath())

        inFileDialog.Destroy()
            
        
    def OnSave(self, evt):
        # Save current file. If currentFilename is set, just overwrite existing
        if self.currentFilename:
            # Save the current filename (prompt for overwrite)
            confirmDialog = wx.MessageDialog(self, _("Overwrite the existing file?"),
                _("Confirm overwrite"), wx.YES_NO)
            # If not overwriting, return now
            if confirmDialog.ShowModal() == wx.ID_NO:
                return

        # currentFilename is empty; prompt for a filename
        else:
            outFileDialog = wx.FileDialog(self, _("Choose a filename to save"), self.dirname,
                "", "*.*", wx.SAVE)
            if outFileDialog.ShowModal() == wx.ID_OK:
                self.dirname = outFileDialog.GetDirectory()
                self.currentFilename = outFileDialog.GetPath()

        outFile = open(self.currentFilename, "w")
        for line in self.editWindow.GetText():
            outFile.write("%s\n" % line)
        outFile.close()

        # Update title bar
        self.SetTitle("%s (MiniEditor)" % self.currentFilename)
        
    def OnExit(self, evt):
        self.Close(True)

    # Open the given filename
    def OpenFile(self, filename):
        # Save the filename locally
        self.currentFilename = filename

        # Create the file input stream
        inFile = open(filename, 'r')
        buffer = inFile.readline()
        strEditText = []
        # Read from the file until EOF
        while buffer:
            buffer = inFile.readline()
            # Append file's text to a string
            strEditText.append(buffer)

        # Fill the editor window with the text buffer
        self.editWindow.SetText(strEditText)
        inFile.close()

        # Update titlebar text
        self.SetTitle("%s (MiniEditor)" % self.currentFilename)
    

# ===================================================================
#
# CLASS DEFINITION
# Simple font chooser dialog
#
# ===================================================================
class FontChooserDialog(wx.Dialog):
    # ==========================================================
    # Initialize FontChooserDialog
    # ==========================================================
    def __init__(self, parent, id, curFacename = "Default"):
        wx.Dialog.__init__(self, parent, id, _("Font chooser"), wx.DefaultPosition,
                (400, 400))

        # Center dialog
        self.Centre()

        # Get global configuration
        self.curConfig = Config()

        # Construct a list of fonts. Always list "Default" first.
        strFontChoices = []
        strFontChoices.extend(self.curConfig.strAvailFonts)
        strFontChoices.insert(0, "Default")

        # List of fonts, label and sample of selected font
        self.listFonts = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                wx.DefaultSize, strFontChoices, wx.LB_SINGLE)
        self.lblFont = wx.StaticText(self, wx.ID_ANY, _("Sample of the selected font:"))
        self.lblFontSample = wx.StaticText(self, wx.ID_ANY, "The quick brown fox\n "
                "jumps over the lazy dog.")
        wx.EVT_LISTBOX(self, self.listFonts.GetId(), self.OnSelectFont)

        # Set listbox selection to given facename
        curFontIdx = self.listFonts.FindString(curFacename)
        self.listFonts.SetSelection(curFontIdx)
        # Remember given facename
        self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, False, "Default")
        # Show sample in current font
        self.lblFontSample.SetFont(self.font)

        # OK/Cancel buttons
        self.btnOK = wx.Button(self, wx.ID_OK, "OK")
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        sizButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizButtons.Add(self.btnOK, 1, wx.EXPAND | wx.ALL, 16)
        sizButtons.Add(self.btnCancel, 1, wx.EXPAND | wx.ALL, 16)
        # Sizer to hold controls
        sizMain = wx.BoxSizer(wx.VERTICAL)
        sizMain.Add(self.listFonts, 1, wx.EXPAND | wx.ALL, 8)
        sizMain.Add(self.lblFont, 0, wx.EXPAND | wx.ALL, 8)
        sizMain.Add(self.lblFontSample, 0, wx.EXPAND | wx.ALL, 16)
        sizMain.Add(sizButtons, 0, wx.EXPAND)
        self.SetSizer(sizMain)
        self.Show()

        # If there are very few (<6) fonts available,
        # show a message telling how to get more
        if len(self.curConfig.strAvailFonts) < 6:
            dlgGetMoreFonts = wx.MessageDialog(self,
                "You have less than six fonts to choose from. See the\n"
                "tovid documentation (http://tovid.org/)\n"
                "for instructions on how to get more.",
                "How to get more fonts", wx.OK | wx.ICON_INFORMATION)
            dlgGetMoreFonts.ShowModal()

    # ==========================================================
    # Change the sample font to reflect the selected font
    # ==========================================================
    def OnSelectFont(self, evt):
        face = self.listFonts.GetStringSelection()
        self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, False, face)
        self.lblFontSample.SetFont(self.font)

    # ==========================================================
    # Get the font that was selected
    # ==========================================================
    def GetSelectedFont(self):
        return self.font

# ===================================================================
# End FontChooserDialog
# ===================================================================


# ###################################################################
# ###################################################################
#
#
#                               PANELS
#
#       
# ###################################################################
# ###################################################################


# ===================================================================
#
# CLASS DEFINITION
# Guide panel. Displays help information relevant to the current
# task in the GUI.
#
# ===================================================================
class GuidePanel(wx.Panel):
    
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize GuidePanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # Heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "What to do next")

        # Guide text box
        self.txtGuide = wx.TextCtrl(self, wx.ID_ANY, "",
            style = wx.TE_MULTILINE | wx.TE_READONLY)

        # Initialize text
        self.InitTaskText()
        self.SetTask(ID_TASK_GETTING_STARTED)

        # Main sizer
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.txtGuide, 1, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Initialize task-based guide text for all tasks
    # ==========================================================
    def InitTaskText(self):
        self.strGettingStarted = _("Welcome to the tovid GUI. This program is " \
            "designed to help you create a video disc (VCD, SVCD, or DVD) " \
            "from videos that you provide. All you need is a CD or DVD " \
            "recorder, and one or more videos in almost any format.\n\n" \
            "If you don't want to see this help window, select the \"View\" " \
            "menu, and then \"Show guide\". Do the same if you want to turn " \
            "this help window back on at any time.\n\n" \
            "First choose the type of disc you want to create. " \
            "VCD and SVCD can be burned to normal CD-R discs with a CD-R(W) drive. " \
            "For DVD, you will need a DVD-recordable drive. VCD is a low-resolution " \
            "format that can hold about 1 hour of video; SVCD is a medium-resolution " \
            "format that also holds about 1 hour of video. DVD is a very versatile " \
            "format that can hold anywhere from 1 to 9 hours of video, depending " \
            "on the resolution and quality you choose.\n\n" \
            "You should also select NTSC or PAL, depending on what kind of TV " \
            "you have. NTSC is most popular in the United States and East Asia, " \
            "while PAL is commonly used in most of Europe, Asia, and Africa. " \
            "(If you aren't sure which one to use, check the manual for your TV " \
            "or DVD player.) For NTSC, you can choose between regular NTSC and " \
            "NTSC film; use NTSC film to encode using a film frame rate (appropriate " \
            "for source videos using a film framerate, or for converting from PAL).\n\n" \
            "You can also select a directory to use for output. Output files will " \
            "go here, as well as any temporary files created during encoding. " \
            "Make sure the directory has plenty of space (2-6 GB).\n\n" \
            "Click \"Add menu\" when you are ready to begin adding content to " \
            "your disc.")
        self.strDiscSelected = _("The disc item in the disc layout tree is " \
            "now selected. You can change the title of the current disc " \
            "by clicking once on the disc title in the tree.\n\n" \
            "When you select the disc item in the tree, a set of disc options " \
            "are displayed. Here, you can choose what kind of disc to create " \
            "(VCD, SVCD, or DVD) and television system to use (NTSC or PAL). " \
            "You can also choose a working directory. This is where " \
            "encoded videos and temporary files created during encoding will be " \
            "stored. Make sure you choose a directory with plenty of space " \
            "(2-6 GB).\n\n")
        self.strMenuAdded = _("A menu has been added to the disc. Menus are " \
            "represented by a menu icon in the disc layout tree. The first menu " \
            "shown in the tree is the first thing you will see when you " \
            "put the disc in your DVD player. A menu may have other menus " \
            "or videos listed below it. You can add videos now by selecting a menu " \
            "and choosing \"Add video(s)\".\n\n")
        self.strMenuSelected = _("A menu is now selected. You can change the " \
            "title of the menu by clicking once on its title in the disc layout " \
            "tree.\n\n" \
            "When you select a menu, a set of options are displayed. You can " \
            "select a background image or audio clip to use for the menu. " \
            "Background images can be in any standard image format such as " \
            "JPEG, PNG, BMP, or GIF, and audio clips can be in any standard " \
            "audio format such as WAV or MP3. It's best to choose a short " \
            "audio clip (30 to 60 seconds in length).\n\n" \
            "Each menu has a list of titles, for each item below the menu in the " \
            "disc layout tree. These titles will be displayed on the finished menu " \
            "in a certain font and color; you can specify what font and color(s) to " \
            "use in the menu options panel.\n\n" \
            "If you want to use the same background, font, and color settings for " \
            "all the menus on your disc, first create all the menus, and configure " \
            "one of them the way you like. Then select \"Use these settings for "\
            "all menus\". The current settings will be applied to all other " \
            "existing menus on the disc.")
        self.strVideoAdded = _("One or more videos have been added to the disc. " \
            "Notice that your videos have been added to the list of titles in " \
            "the currently-selected menu.\n\n" \
            "Videos are represented by a film-strip icon in the disc layout tree. " \
            "Click on a video in the tree to view options for that video.")
        self.strVideoSelected = _("A video is now selected. You can change the " \
            "title of the video by clicking once on its title in the disc layout " \
            "tree.\n\n" \
            "Videos can be in almost any video format, and tovid will convert them " \
            "for you. When you select a video, a set of options are displayed. " \
            "Here, you can choose what resolution and aspect ratio to use for the " \
            "video\n\n" \
            "You can preview the video in GMplayer using the \"Preview video\" " \
            "button. This is useful if you aren't sure what aspect ratio or " \
            "resolution is most appropriate for the video.\n\n" \
            "If you want to use the same resolution, bitrate and other options for all " \
            "the videos on your disc, first add all the videos you want, and " \
            "configure one of them the way you like. Then select \"Use these settings " \
            "for all videos\". The current settings will be applied to all other " \
            "existing videos on the disc.\n\n" \
            "Use the \"Remove\" button to remove a video from the disc. You can " \
            "also use the \"Move up\" and \"Move down\" buttons to rearrange the " \
            "video within the tree.\n\n" \
            "When you are satisfied with the titles, menu options, and video options " \
            "for your disc, select \"2. Encode\" to proceed with encoding " \
            "and authoring your disc.")
        self.strPrepEncoding = _("You are now ready to begin the process of encoding " \
            "all the menus and videos you have selected for your disc.\n\n" \
            "Here, a log window displays a list of all the commands that will be " \
            "executed. Select \"Start encoding\" to begin.\n\n" \
            "If you change your mind and want to go back to the disc layout panel, " \
            "select \"1. Layout\".")
        self.strEncodingStarted = _("The encoding process has begun. Each of the " \
            "necessary commands will be executed sequentially. Output from the " \
            "currently-running command is displayed in the log window, so you " \
            "can monitor its progress. The currently-running command is shown " \
            "above the log window, and the number of commands remaining is shown " \
            "below the log window.\n\n" \
            "Be advised that video encoding can be a very time-consuming process! " \
            "A disc with one hour of video content may take from 1-3 hours to encode, " \
            "depending on your CPU speed. You may need to leave this running for " \
            "several hours in order for your disc to finish authoring.")

    # ==========================================================
    # Show the appropriate guide text for the given task
    # ==========================================================
    def SetTask(self, curTask = ID_TASK_GETTING_STARTED):
        if curTask == ID_TASK_GETTING_STARTED:
            self.txtHeading.SetLabel(_("Getting started"))
            self.txtGuide.SetValue(self.strGettingStarted)
        elif curTask == ID_TASK_MENU_ADDED:
            self.txtHeading.SetLabel(_("Menu added"))
            self.txtGuide.SetValue(self.strMenuAdded)
        elif curTask == ID_TASK_VIDEO_ADDED:
            self.txtHeading.SetLabel(_("Video added"))
            self.txtGuide.SetValue(self.strVideoAdded)
        elif curTask == ID_TASK_DISC_SELECTED:
            self.txtHeading.SetLabel(_("Disc selected"))
            self.txtGuide.SetValue(self.strDiscSelected)
        elif curTask == ID_TASK_MENU_SELECTED:
            self.txtHeading.SetLabel(_("Menu selected"))
            self.txtGuide.SetValue(self.strMenuSelected)
        elif curTask == ID_TASK_VIDEO_SELECTED:
            self.txtHeading.SetLabel(_("Video selected"))
            self.txtGuide.SetValue(self.strVideoSelected)
        elif curTask == ID_TASK_PREP_ENCODING:
            self.txtHeading.SetLabel(_("Encoding preparation"))
            self.txtGuide.SetValue(self.strPrepEncoding)
        elif curTask == ID_TASK_ENCODING_STARTED:
            self.txtHeading.SetLabel(_("Encoding started"))
            self.txtGuide.SetValue(self.strEncodingStarted)

# ===================================================================
# End GuidePanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Command output panel. Specialized panel with a text box
# that captures and prints the output from enqueued command-line
# processes.
#
# To use CommandOutputPanel, the parent should implement a function
# ProcessingDone(bool errStatus), which is called by CommandOutputPanel
# to notify the parent that the panel is done running commands.
# Presumably, the commands that are executing must finish before
# proceeding with another operation, so this function is used to let
# the parent know that the commands are done executing.
# ===================================================================
class CommandOutputPanel(wx.Panel):
    # Current (running) process
    process = None
    # Has an error occurred in any of the commands?
    errorOccurred = False
    # Command queue (starts out empty)
    strCmdQueue = []
    strCurCmd = ""
      
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize CommandOutputPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # Process list and labels
        self.lblCurCmd = wx.StaticText(self, wx.ID_ANY, _("Running command:"))
        self.txtCurCmd = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txtCurCmd.Enable(False)
        self.lblQueue = wx.StaticText(self, wx.ID_ANY, _("Commands left to run:") + '0')

        # Output window (fixed-width font)
        self.txtOut = wx.TextCtrl(self, wx.ID_ANY,
            style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.txtOut.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.txtOut.AppendText(_("The following commands will be run:") + \
            "\n=========================================\n")

        # Log window font size widget
        self.lblFontSize = wx.StaticText(self, wx.ID_ANY, _("Log window font size:"))
        strFontSizes = ["8", "10", "12", "14"]
        self.cboFontSize = wx.ComboBox(self, wx.ID_ANY, "10", choices = strFontSizes,
            style = wx.CB_READONLY)
        wx.EVT_TEXT(self, self.cboFontSize.GetId(), self.OnFontSize)

        # Save log button
        self.btnSaveLog = wx.Button(self, wx.ID_ANY, _("Save log"))
        self.btnSaveLog.SetToolTipString(_("Save the output log to a file"))
        wx.EVT_BUTTON(self, self.btnSaveLog.GetId(), self.OnSaveLog)

        # Keep track of who parent is
        self.parent = parent

        # Timer to produce continuous output and keep
        # running the next command
        self.idleTimer = wx.Timer(self, ID_CMD_TIMER)
        
        # Event handlers
        #wx.EVT_IDLE(self, self.OnIdle)
        wx.EVT_TIMER(self, ID_CMD_TIMER, self.OnIdleTime)
        wx.EVT_END_PROCESS(self, wx.ID_ANY, self.OnProcessEnded)

        # Current command sizer
        self.sizCurCmd = wx.BoxSizer(wx.HORIZONTAL)
        self.sizCurCmd.Add(self.lblCurCmd, 0, wx.EXPAND | wx.RIGHT, 6)
        self.sizCurCmd.Add(self.txtCurCmd, 1, wx.EXPAND)
        # Control sizer (may have more controls later)
        self.sizControl = wx.BoxSizer(wx.HORIZONTAL)
        self.sizControl.Add(self.lblQueue, 1, wx.EXPAND | wx.ALIGN_LEFT)
        self.sizControl.Add(self.lblFontSize, 0, wx.EXPAND | wx.ALIGN_RIGHT)
        self.sizControl.Add(self.cboFontSize, 0, wx.EXPAND | wx.ALIGN_RIGHT)
        self.sizControl.Add(self.btnSaveLog, 0, wx.EXPAND)
        # Main sizer
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.sizCurCmd, 0, wx.EXPAND | wx.BOTTOM, 6)
        self.sizMain.Add(self.txtOut, 3, wx.EXPAND | wx.BOTTOM, 6)
        self.sizMain.Add(self.sizControl, 0, wx.EXPAND | wx.BOTTOM, 6)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Destructor. Detach any running process
    # ==========================================================
    def __del__(self):
        # Detach any running process
        self.process.Detach()

    # ==========================================================
    # Change log window font size
    # ==========================================================
    def OnFontSize(self, evt):
        newFontSize = int(self.cboFontSize.GetValue())
        self.txtOut.SetFont(wx.Font(newFontSize, wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        #self.txtOut.Refresh()

    # ==========================================================
    # Save output log
    # ==========================================================
    def OnSaveLog(self, evt):
        # Prompt for a filename
        outFileDlg = wx.FileDialog(self, _("Choose a filename to save to"),
            "", "", "*.*", wx.SAVE | wx.OVERWRITE_PROMPT)
        if outFileDlg.ShowModal() == wx.ID_OK:
            outFile = outFileDlg.GetPath()
            success = self.txtOut.SaveFile(outFile)
            if success:
                dlgAck = wx.MessageDialog(self,
                    _("The log was successfully saved to ") + outFile,
                    _("Log saved"), wx.OK | wx.ICON_INFORMATION)
            else:
                dlgAck = wx.MessageDialog(self,
                    _("The log could not be saved to ") + outFile + \
                    _("Maybe you don't have write permission to the given file?"),
                    _("Log not saved"), wx.OK | wx.ICON_INFORMATION)

            dlgAck.ShowModal()
            outFileDlg.Destroy()

    # ==========================================================
    # OnIdleTime event. When idle, execute commands in queue and
    # print output to the command window
    # ==========================================================
    def OnIdleTime(self, evt):
        # If processing hasn't been started/enabled, do nothing
        if not self.idleTimer.IsRunning():
            return

        # If no process is currently executing, start the next
        # one in the queue.
        if self.process is None:
            self.StartNextProcess()

        # If a process is currently running, get its output and
        # print it to the command window
        if self.process is not None and self.pid != 0:
            stream = self.process.GetInputStream()
            if stream.CanRead():
                self.txtOut.AppendText(stream.read())
            
    # ==========================================================
    # Start the next process in the queue
    # ==========================================================
    def StartNextProcess(self):
        # If there is a command in the queue
        if len(self.strCmdQueue) > 0:
            self.strCurCmd = self.strCmdQueue.pop(0)
            # Show the command that is being executed,
            # and the number remaining in queue
            self.txtCurCmd.SetValue(self.strCurCmd)
            self.txtOut.AppendText("Running command: %s\n" % self.strCurCmd)
            # Start the process running
            self.process = wx.Process(self)
            self.process.Redirect()
            self.pid = wx.Execute(self.strCurCmd, wx.EXEC_ASYNC, self.process)
            self.lblQueue.SetLabel("Commands left to run: %d" % len(self.strCmdQueue))

    # ==========================================================
    # Process-end event. Print any remaining output, and destroy
    # the process
    # ==========================================================
    def OnProcessEnded(self, evt):
        # Get process exit status
        curExitStatus = evt.GetExitCode()
        # Print message to console if there was an error
        if curExitStatus != 0:
            print "ERROR:"
            print "The following command returned an exit status of %d:" % curExitStatus
            print self.strCurCmd
            print "Please report this bug on the tovid forum or IRC channel:"
            print "    Forum: http://www.createphpbb.com/phpbb/tovid.html"
            print "    IRC:   irc://irc.freenode.net/tovid"
            print "Include all the output shown above, as well as any output"
            print "shown in the log window of the tovid GUI."
            self.errorOccurred = True
        # Print any remaining output
        stream = self.process.GetInputStream()
        if stream.CanRead():
            self.txtOut.AppendText(stream.read())
        self.process.Destroy()
        self.process = None

        # If there are more commands in the queue, start the next one
        if len(self.strCmdQueue) > 0:
            self.StartNextProcess()
        # Otherwise, stop running and update status messages
        else:
            self.idleTimer.Stop()
            self.txtCurCmd.SetValue("")
            self.lblQueue.SetLabel("Commands left to run: 0")
            # Let parent know that processing is done
            self.parent.ProcessingDone(self.errorOccurred)


    # ==========================================================
    #
    # Public utility functions
    #
    # ==========================================================

    # ==========================================================
    # Clear out the command queue
    # ==========================================================
    def Clear(self):
        self.strCmdQueue = []
        self.txtCurCmd.SetValue("")
        self.txtOut.Clear()
        self.txtOut.AppendText("The following commands will be run:\n"
            "=========================================\n")
        self.lblQueue.SetLabel("Commands left to run: 0")
        self.process = None

    # ==========================================================
    # Put the given command-line string into the queue for
    # execution.
    # ==========================================================
    def Execute(self, command):
        self.strCmdQueue.append(command)
        self.txtOut.AppendText("%s\n------------------------\n" % command)
        # Update the queue size indicator
        self.lblQueue.SetLabel("Commands left to run: %d" % len(self.strCmdQueue))
        self.sizCurCmd.Layout()

    # ==========================================================
    # Start processing all commands in queue
    # ==========================================================
    def Start(self):
        # NOTE FOR FUTURE VERSION: Include capability to resume
        # a cancelled queue, or start over from the beginning
        # (requires keeping a copy of the original queue)
        
        # If already running, do nothing
        if self.idleTimer.IsRunning():
            return

        # Start running commands, if any remain to be executed
        if len(self.strCmdQueue) > 0:
            # Start the idle timer (1s interval)
            self.idleTimer.Start(1000)
        else:
            self.parent.ProcessingDone()


    # ==========================================================
    # Stop processing (and return current process to queue)
    # ==========================================================
    def Stop(self):
        # Stop the idle timer and kill current process
        self.idleTimer.Stop()
        if self.process is not None:
            #wx.Kill(self.pid)
            self.process.Destroy()
            self.process = None
            # Return current command to queue
            self.strCmdQueue.insert(0, self.strCurCmd)

        # Reset indicators
        self.txtCurCmd.SetValue("")
        self.lblQueue.SetLabel("Commands left to run: %d" % len(self.strCmdQueue))

# ===================================================================
# End CommandOutputPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Panel for choosing disc format (DVD/VCD/SVCD, PAL/NTSC)
#
# ===================================================================
class DiscPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize DiscPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # Global configuration
        self.curConfig = Config()

        # Disc options associated with this panel
        self.curOptions = DiscOptions()
        self.parent = parent

        # Disc format selector
        self.lblDiscFormat = wx.StaticText(self, wx.ID_ANY, "Choose what kind of video disc"
            " you want to make:")
        strFormats = ["VCD: Low-quality, up to about one hour of video",
            "SVCD: Medium quality, 30 to 70 minutes of video",
            "DVD: Range of quality, from 1 to 8 hours of video"]

        
        self.rbFormat = wx.RadioBox(self, wx.ID_ANY, "Disc format", wx.DefaultPosition,
            wx.DefaultSize, strFormats, 1, wx.RA_SPECIFY_COLS)
        self.rbFormat.SetToolTipString("Select what disc format you want to use."
            " For VCD and SVCD, you can use a normal CD-recordable drive. For"
            " DVD, you need a DVD-recordable drive.")
        self.rbFormat.SetSelection(ID_FMT_DVD)
        wx.EVT_RADIOBOX(self, self.rbFormat.GetId(), self.OnFormat)
        
        # Disc TV system selector
        strTVSystems = ["NTSC: Used in the Americas and East Asia",
                        "NTSC Film: Same as NTSC, with a film frame rate",
                        "PAL: Used in most of Europe, Asia, and Africa"]
        self.rbTVSystem = wx.RadioBox(self, wx.ID_ANY, "TV format", wx.DefaultPosition,
                wx.DefaultSize, strTVSystems, 1, wx.RA_SPECIFY_COLS)
        self.rbTVSystem.SetToolTipString("Select NTSC or PAL, depending on what kind"
            " of TV you want to play the disc on.")
        self.rbTVSystem.SetSelection(ID_TVSYS_NTSC)
        wx.EVT_RADIOBOX(self, self.rbTVSystem.GetId(), self.OnTVSystem)

        # Disc options heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "Disc")

        # Output directory
        self.lblOutputDirectory = wx.StaticText(self, wx.ID_ANY, "Output directory:")
        self.txtOutputDirectory = wx.TextCtrl(self, wx.ID_ANY,
            self.curConfig.strOutputDirectory)
        self.txtOutputDirectory.SetToolTipString("Type the full path of a "
            "directory where you want to save finished videos and disc images, "
            "or use the browse button. Should have 2-6GB of free space.")
        self.btnBrowseOutputDirectory = wx.Button(self, wx.ID_ANY, "Browse")
        wx.EVT_BUTTON(self, self.btnBrowseOutputDirectory.GetId(),
            self.OnBrowseOutputDirectory)
        wx.EVT_TEXT(self, self.txtOutputDirectory.GetId(),
            self.OnEditOutputDirectory)

        # Sizer to hold working directory controls
        self.sizDirs = wx.BoxSizer(wx.HORIZONTAL)
        self.sizDirs.AddMany([ (self.lblOutputDirectory, 0, wx.ALIGN_RIGHT | wx.ALL, 8),
                                (self.txtOutputDirectory, 1, wx.EXPAND | wx.ALL, 8),
                                (self.btnBrowseOutputDirectory, 0, wx.ALL, 8) ])

        # Sizer to hold controls
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.lblDiscFormat, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.rbFormat, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.rbTVSystem, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizDirs, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Set disc format according to radiobox
    # ==========================================================
    def OnFormat(self, evt):
        self.curOptions.format = ID_to_text('format', evt.GetInt())
        # Tell parent to adjust disc format
        self.parent.SetDiscFormat(self.curOptions.format)

    # ==========================================================
    # Set disc TV system according to radiobox
    # ==========================================================
    def OnTVSystem(self, evt):
        self.curOptions.tvsys = ID_to_text('tvsys', evt.GetInt())
        # Tell parent to adjust disc TVSystem
        self.parent.SetDiscTVSystem(self.curOptions.tvsys)

    # ==========================================================
    # Browse for output directory
    # ==========================================================
    def OnBrowseOutputDirectory(self, evt):
        workDirDlg = wx.DirDialog(self, "Select a directory for output",
            style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        workDirDlg.SetPath(self.txtOutputDirectory.GetValue())
        # Show the dialog
        if workDirDlg.ShowModal() == wx.ID_OK:
            self.curConfig.strOutputDirectory = workDirDlg.GetPath()
            self.txtOutputDirectory.SetValue(self.curConfig.strOutputDirectory)
            workDirDlg.Destroy()

    # ==========================================================
    # Update Config with newly-entered output directory
    # ==========================================================
    def OnEditOutputDirectory(self, evt):
        self.curConfig.strOutputDirectory = self.txtOutputDirectory.GetValue()


    # ==========================================================
    #
    # Public utility functions
    #
    # ==========================================================

    # ==========================================================
    # Set control values based on the provided MenuOptions
    # ==========================================================
    def SetOptions(self, discOpts):
        self.curOptions = discOpts

        self.rbFormat.SetSelection(text_to_ID(self.curOptions.format))
        self.rbTVSystem.SetSelection(text_to_ID(self.curOptions.tvsys))
        self.txtHeading.SetLabel("Disc options: %s" % self.curOptions.title)

# ===================================================================
# End DiscPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Panel for makemenu options
#
# ===================================================================
class MenuPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize MenuPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # ================================
        # Class data
        # ================================
        self.curOptions = MenuOptions()
        self.curColorData = wx.ColourData()
        self.parent = parent

        self.sboxBG = wx.StaticBox(self, wx.ID_ANY, "Menu background options")
        self.sizBG = wx.StaticBoxSizer(self.sboxBG, wx.VERTICAL)

        # ================================
        # Background image/audio selection controls
        # ================================
        # Image
        self.lblBGImage = wx.StaticText(self, wx.ID_ANY, "Image:")
        self.txtBGImage = wx.TextCtrl(self, wx.ID_ANY)
        self.txtBGImage.SetToolTipString("Type the full name of the image file "
            "you want to use in the background of the menu, or use the browse button.")
        self.btnBrowseBGImage = wx.Button(self, wx.ID_ANY, "Browse")
        self.btnBrowseBGImage.SetToolTipString("Browse for an image file to "
            "use for the background of the menu")
        wx.EVT_TEXT(self, self.txtBGImage.GetId(), self.OnBGImage)
        wx.EVT_BUTTON(self, self.btnBrowseBGImage.GetId(), self.OnBrowseBGImage)
        # Audio
        self.lblBGAudio = wx.StaticText(self, wx.ID_ANY, "Audio:")
        self.txtBGAudio = wx.TextCtrl(self, wx.ID_ANY)
        self.txtBGAudio.SetToolTipString("Type the full name of the audio file "
            "you want to play while the menu is shown, or use the browse button.")
        self.btnBrowseBGAudio = wx.Button(self, wx.ID_ANY, "Browse")
        self.btnBrowseBGAudio.SetToolTipString("Browse for an audio file to "
            "play while the menu is shown")
        wx.EVT_TEXT(self, self.txtBGAudio.GetId(), self.OnBGAudio)
        wx.EVT_BUTTON(self, self.btnBrowseBGAudio.GetId(), self.OnBrowseBGAudio)

        # Inner sizer for background controls
        self.sizBGInner = wx.FlexGridSizer(2, 3, 2, 8)
        self.sizBGInner.AddMany([ (self.lblBGImage, 0, wx.ALIGN_RIGHT),
                                   (self.txtBGImage, 0, wx.EXPAND),
                                   (self.btnBrowseBGImage, 0, wx.EXPAND),
                                   (self.lblBGAudio, 0, wx.ALIGN_RIGHT),
                                   (self.txtBGAudio, 0, wx.EXPAND),
                                   (self.btnBrowseBGAudio, 0, wx.EXPAND) ])
        self.sizBGInner.AddGrowableCol(1)
        # Add inner sizer to outer staticbox sizer
        self.sizBG.Add(self.sizBGInner, 0, wx.EXPAND | wx.ALL, 8)

        # ================================
        # Menu font and alignment controls
        # ================================
        self.lblFontFace = wx.StaticText(self, wx.ID_ANY, "Font:")
        self.btnFontChooserDialog = wx.Button(self, wx.ID_ANY, "Default")
        self.btnFontChooserDialog.SetToolTipString("Select a font to use for the "
                "menu text")
        wx.EVT_BUTTON(self, self.btnFontChooserDialog.GetId(), self.OnFontSelection)
        strAlignments = ['Left', 'Center', 'Right']
        self.rbAlignment = wx.RadioBox(self, wx.ID_ANY, "Alignment",
                wx.DefaultPosition, wx.DefaultSize, strAlignments, 1, wx.RA_SPECIFY_ROWS)
        self.rbAlignment.SetToolTipString("Select how the menu text should be aligned")
        wx.EVT_RADIOBOX(self, self.rbAlignment.GetId(), self.OnAlignment)
        self.sizFontFace = wx.BoxSizer(wx.HORIZONTAL)
        self.sizFontFace.AddMany([ (self.lblFontFace, 0, wx.ALL, 4),
                                    (self.btnFontChooserDialog, 1, wx.EXPAND | wx.ALL, 4) ])

        # ================================
        # Menu text color controls
        # ================================
        self.lblTextColor = wx.StaticText(self, wx.ID_ANY, _("Text color:"))
        self.lblHiColor = wx.StaticText(self, wx.ID_ANY, _("Highlight color:"))
        self.lblSelColor = wx.StaticText(self, wx.ID_ANY, _("Selection color:"))
        self.btnTextColor = wx.Button(self, wx.ID_ANY, _("Choose..."))
        self.btnHiColor = wx.Button(self, wx.ID_ANY, _("Choose..."))
        self.btnSelColor = wx.Button(self, wx.ID_ANY, _("Choose..."))
        # Tooltips
        self.btnTextColor.SetToolTipString(_("Choose the color used "
            "for the menu text"))
        self.btnHiColor.SetToolTipString(_("Choose the color used "
            "to highlight menu items as they are navigated"))
        self.btnSelColor.SetToolTipString(_("Choose the color used "
            "when a menu item is chosen or activated for playback"))
        self.btnTextColor.SetBackgroundColour(self.curOptions.colorText)
        self.btnHiColor.SetBackgroundColour(self.curOptions.colorHi)
        self.btnSelColor.SetBackgroundColour(self.curOptions.colorSel)
        # Events
        wx.EVT_BUTTON(self, self.btnTextColor.GetId(), self.OnTextColor)
        wx.EVT_BUTTON(self, self.btnHiColor.GetId(), self.OnHiColor)
        wx.EVT_BUTTON(self, self.btnSelColor.GetId(), self.OnSelColor)

        # Sizer to hold color buttons
        self.sizFontColor = wx.FlexGridSizer(3, 2, 2, 8)
        self.sizFontColor.AddMany([ (self.lblTextColor, 0, wx.ALIGN_RIGHT),
                                     (self.btnTextColor, 0, wx.EXPAND),
                                     (self.lblHiColor, 0, wx.ALIGN_RIGHT),
                                     (self.btnHiColor, 0, wx.EXPAND),
                                     (self.lblSelColor, 0, wx.ALIGN_RIGHT),
                                     (self.btnSelColor, 0, wx.EXPAND) ])

        # ================================
        # List of titles in this menu
        # ================================
        self.lblTitleList = wx.StaticText(self, wx.ID_ANY, 
            _("Titles shown in this menu"))
        self.lbTitles = wx.ListBox(self, wx.ID_ANY)
        self.lbTitles.SetToolTipString(_("This lists all the sub-menus "
            "and videos that are under this menu. To change the text that "
            "appears here, edit the titles in the disc layout tree."))
        self.lbTitles.Enable(False)
        # Sizer to hold title list
        self.sizTitles = wx.BoxSizer(wx.VERTICAL)
        self.sizTitles.AddMany([ (self.lblTitleList, 0),
                                  (self.lbTitles, 1, wx.EXPAND) ])
    
        # ================================
        # Put menu font/color controls in a static box
        # ================================
        self.sboxTextFormat = wx.StaticBox(self, wx.ID_ANY, "Menu text format")
        self.sizTextFormat = wx.StaticBoxSizer(self.sboxTextFormat, wx.VERTICAL)
        self.sizTextFormat.AddMany([ (self.sizFontFace, 0, wx.EXPAND | wx.ALL, 8),
                                      (self.rbAlignment, 0, wx.EXPAND | wx.ALL, 8),
                                      (self.sizFontColor, 0, wx.EXPAND | wx.ALL, 8) ])
        
        # Horizontal sizer holding sizTextFormat and sizTitles
        self.sizTextTitles = wx.BoxSizer(wx.HORIZONTAL)
        self.sizTextTitles.Add(self.sizTextFormat, 1, wx.EXPAND, 0)
        self.sizTextTitles.Add(self.sizTitles, 1, wx.EXPAND | wx.LEFT, 10)

        # Menu options heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "Menu options")

        # Button to copy menu options to all menus on disc
        self.btnUseForAll = wx.Button(self, wx.ID_ANY,
            "Use these settings for all menus")
        self.btnUseForAll.SetToolTipString("Apply the current menu settings,"
            " including background image, audio, text alignment, text color and font,"
            " to all menus on the disc.")
        wx.EVT_BUTTON(self, self.btnUseForAll.GetId(), self.OnUseForAll)

        # ================================
        # Main sizer to hold all controls
        # ================================
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizBG, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizTextTitles, 1, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnUseForAll, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)


    def OnBGImage(self, evt):
        """Set the background image in curOptions whenever text is altered."""
        self.curOptions.background = self.txtBGImage.GetValue()


    def OnBGAudio(self, evt):
        """Set the background audio in curOptions whenever text is altered."""
        self.curOptions.audio = self.txtBGAudio.GetValue()


    def OnBrowseBGImage(self, evt):
        """Show a file dialog and set the background image."""
        inFileDlg = wx.FileDialog(self, "Select an image file", "", "", "*.*", wx.OPEN)
        if inFileDlg.ShowModal() == wx.ID_OK:
            self.txtBGImage.SetValue(inFileDlg.GetPath())
            inFileDlg.Destroy()


    def OnBrowseBGAudio(self, evt):
        """Show a file dialog and set the background audio."""
        inFileDlg = wx.FileDialog(self, "Select an audio file", "", "", "*.*", wx.OPEN)
        if inFileDlg.ShowModal() == wx.ID_OK:
            self.txtBGAudio.SetValue(inFileDlg.GetPath())
            inFileDlg.Destroy()


    def OnAlignment(self, evt):
        """Set the text alignment according to the radiobox setting."""
        self.curOptions.alignment = ID_to_text('alignment', evt.GetInt())


    def OnFontSelection(self, evt):
        """Show a font selection dialog and set the font."""
        dlgFontChooserDialog = FontChooserDialog(self, wx.ID_ANY,
            self.curOptions.font.GetFaceName())
        if dlgFontChooserDialog.ShowModal() == wx.ID_OK:
            strFontName = dlgFontChooserDialog.GetSelectedFont().GetFaceName()
            self.curOptions.font = wx.Font(10, wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, strFontName)
            
            # Button shows selected font name in selected font
            self.btnFontChooserDialog.SetFont(self.curOptions.font)
            self.btnFontChooserDialog.SetLabel(strFontName)


    def OnTextColor(self, evt):
        """Display a color dialog to select the text color."""
        self.curColorData.SetColour(self.curOptions.colorText)
        dlgColor = wx.ColourDialog(self, self.curColorData)
        if dlgColor.ShowModal() == wx.ID_OK:
            self.curColorData = dlgColor.GetColourData()
            self.curOptions.colorText = self.curColorData.GetColour()
            self.btnTextColor.SetBackgroundColour(self.curOptions.colorText)


    def OnHiColor(self, evt):
        """Display a color dialog to select the text highlight color."""
        self.curColorData.SetColour(self.curOptions.colorHi)
        dlgColor = wx.ColourDialog(self, self.curColorData)
        if dlgColor.ShowModal() == wx.ID_OK:
            self.curColorData = dlgColor.GetColourData()
            self.curOptions.colorHi = self.curColorData.GetColour()
            self.btnHiColor.SetBackgroundColour(self.curOptions.colorHi)


    def OnSelColor(self, evt):
        """Display a color dialog to select the text selection color."""
        self.curColorData.SetColour(self.curOptions.colorSel)
        dlgColor = wx.ColourDialog(self, self.curColorData)
        if dlgColor.ShowModal() == wx.ID_OK:
            self.curColorData = dlgColor.GetColourData()
            self.curOptions.colorSel = self.curColorData.GetColour()
            self.btnSelColor.SetBackgroundColour(self.curOptions.colorSel)


    def OnUseForAll(self, evt):
        """Use the current menu settings for all menus on disc."""
        countItems = self.parent.UseForAllItems(self.curOptions)
        # Display acknowledgement
        dlgAck = wx.MessageDialog(self,
            "The current menu settings were copied to\n"
            "%d other menus on the disc." % countItems,
            "Settings copied", wx.OK | wx.ICON_INFORMATION)
        dlgAck.ShowModal()
      

    # ==========================================================
    #
    # Public utility functions
    #
    # ==========================================================

    def SetOptions(self, menuOpts):
        """Set control values based on the provided MenuOptions."""
        self.curOptions = menuOpts

        self.txtHeading.SetLabel("Menu options: %s" % self.curOptions.title)
        self.txtBGImage.SetValue(self.curOptions.background)
        self.txtBGAudio.SetValue(self.curOptions.audio or '')
        self.rbAlignment.SetSelection(text_to_ID(self.curOptions.alignment))
        self.btnTextColor.SetBackgroundColour(self.curOptions.colorText)
        self.btnHiColor.SetBackgroundColour(self.curOptions.colorHi)
        self.btnSelColor.SetBackgroundColour(self.curOptions.colorSel)
        self.btnFontChooserDialog.SetFont(self.curOptions.font)
        if self.curOptions.font.GetFaceName() == "":
            self.btnFontChooserDialog.SetLabel("Default")
        else:
            self.btnFontChooserDialog.SetLabel(self.curOptions.font.GetFaceName())
        self.lbTitles.Set(self.curOptions.titles)


    def GetOptions(self):
        """Get currently-set encoding options."""
        return self.curOptions


    def SetDiscFormat(self, format):
        """Enable/disable controls appropriate to the given disc format."""
        if format == 'dvd':
            self.btnHiColor.Enable(True)
            self.btnSelColor.Enable(True)
            self.lblHiColor.Enable(True)
            self.lblSelColor.Enable(True)
        elif format in [ 'vcd', 'svcd' ]:
            self.btnHiColor.Enable(False)
            self.btnSelColor.Enable(False)
            self.lblHiColor.Enable(False)
            self.lblSelColor.Enable(False)

# ===================================================================
# End MenuPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Panel for video conversion options
#
# ===================================================================
class VideoPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize VideoPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # ================================
        # Class data
        # ================================
        self.curOptions = VideoOptions()
        self.parent = parent

        # ================================
        # File information display
        # ================================
        self.lblInFile = wx.StaticText(self, wx.ID_ANY, "Filename:")
        self.txtInFile = wx.StaticText(self, wx.ID_ANY, "None")

        # Statix box and sizer to hold file info
        self.sboxFileInfo = wx.StaticBox(self, wx.ID_ANY, "Video information")
        self.sizFileInfo = wx.StaticBoxSizer(self.sboxFileInfo, wx.HORIZONTAL)
        self.sizFileInfo.Add(self.lblInFile, 0, wx.EXPAND | wx.ALL, 6)
        self.sizFileInfo.Add(self.txtInFile, 1, wx.EXPAND | wx.ALL, 6)
        
        # ================================
        # Radio buttons
        # ================================
        # Format-selection radio buttons
        outFormatList = ['352x240 VCD',
                         '480x480 SVCD',
                         '720x480 DVD',
                         '352x480 Half-DVD',
                         '352x240 VCD on DVD' ]

        # Aspect ratio radio buttons
        aspectList = ['4:3 Fullscreen TV',
                      '16:9 Widescreen TV',
                      '2.35:1 Theatrical widescreen']

        # Radio boxes and tooltips
        self.rbResolution = wx.RadioBox(self, wx.ID_ANY, "Output resolution",
            wx.DefaultPosition, wx.DefaultSize,
            outFormatList, 1, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, self.rbResolution.GetId(), self.OnFormat)
        self.rbResolution.SetToolTipString("Select which resolution you want to "
            "encode your video in. The available resolutions are shown depending on "
            "whether you are making a VCD, SVCD, or DVD disc.")
        self.rbAspect = wx.RadioBox(self, wx.ID_ANY, "Aspect ratio of input",
            wx.DefaultPosition, wx.DefaultSize,
            aspectList, 1, wx.RA_SPECIFY_COLS)
        wx.EVT_RADIOBOX(self, self.rbAspect.GetId(), self.OnAspect)
        self.rbAspect.SetToolTipString("Select which aspect ratio the original video "
            "is in. If it is roughly TV-shaped, use '4:3'. If it is more than "
            "twice as wide as it is tall, use '2.35:1'. If it's somewhere in "
            "between, use '16:9'.")

        # Sizer for radioboxes
        self.sizResAspect = wx.BoxSizer(wx.HORIZONTAL)
        self.sizResAspect.Add(self.rbResolution, 1, wx.EXPAND | wx.ALL)
        self.sizResAspect.Add(self.rbAspect, 1, wx.EXPAND | wx.ALL)
                
        # ================================
        # Direct-entry CLI option box
        # ================================
        self.lblCLIOptions = wx.StaticText(self, wx.ID_ANY, "Custom options:")
        self.txtCLIOptions = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txtCLIOptions.SetToolTipString("Type custom tovid command-line "
            "options that you'd like to use, separated by spaces. Warning:"
            "Please make sure you know what you are doing!")
        wx.EVT_TEXT(self, self.txtCLIOptions.GetId(), self.OnCLIOptions)
        self.sizCLIOptions = wx.BoxSizer(wx.HORIZONTAL)
        self.sizCLIOptions.Add(self.lblCLIOptions, 0, wx.EXPAND | wx.ALL, 8)
        self.sizCLIOptions.Add(self.txtCLIOptions, 1, wx.EXPAND | wx.ALL, 8)

        # Sizer to hold all encoding options
        self.sizEncOpts = wx.BoxSizer(wx.VERTICAL)
        self.sizEncOpts.Add(self.sizResAspect, 1, wx.EXPAND | wx.ALL)
        self.sizEncOpts.Add(self.sizCLIOptions, 0, wx.EXPAND | wx.ALL)

        # Button to preview the video
        self.btnPreview = wx.Button(self, wx.ID_ANY, "Preview video")
        self.btnPreview.SetToolTipString("Play the video using mplayer")
        wx.EVT_BUTTON(self, self.btnPreview.GetId(), self.OnPreview)

        # Button to copy video options to all videos on disc
        self.btnUseForAll = wx.Button(self, wx.ID_ANY,
            "Use these settings for all videos")
        self.btnUseForAll.SetToolTipString("Apply the current video"
            " settings, including resolution, aspect ratio, and"
            " custom command-line options, to all videos on the disc.")
        wx.EVT_BUTTON(self, self.btnUseForAll.GetId(), self.OnUseForAll)

        # Video options heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "Video options")

        # ================================
        # Add controls to main vertical sizer
        # ================================
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizFileInfo, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizEncOpts, 1, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnPreview, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnUseForAll, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Set appropriate format based on radio button selection
    # ==========================================================
    def OnFormat(self, evt):
        # Convert integer value to text representation
        # (e.g., ID_FMT_DVD to 'dvd')
        self.curOptions.format = ID_to_text('format', evt.GetInt())

    # ==========================================================
    # Set aspect ratio based on radio button selection
    # ==========================================================
    def OnAspect(self, evt):
        self.curOptions.aspect = ID_to_text('aspect', evt.GetInt())

    # ==========================================================
    # Update CLI options
    # ==========================================================
    def OnCLIOptions(self, evt):
        self.curOptions.addoptions = self.txtCLIOptions.GetValue()

    # ==========================================================
    # Use the current video settings for all videos on disc
    # ==========================================================
    def OnUseForAll(self, evt):
        countItems = self.parent.UseForAllItems(self.curOptions)
        # Display acknowledgement
        dlgAck = wx.MessageDialog(self,
            "The current video settings were copied to\n"
            "%d other videos on the disc." % countItems,
            "Settings copied", wx.OK | wx.ICON_INFORMATION)
        dlgAck.ShowModal()

    # ==========================================================
    # Preview the video in mplayer
    # ==========================================================
    def OnPreview(self, evt):
        strCommand = "gmplayer \"%s\"" % self.curOptions.inFile
        wx.Execute(strCommand, wx.EXEC_SYNC)
    

    # ==========================================================
    #
    # Public utility functions
    #
    # ==========================================================

    # ==========================================================
    # Set control values based on the provided VideoOptions
    # ==========================================================
    def SetOptions(self, videoOpts):
        self.curOptions = videoOpts

        self.txtHeading.SetLabel("Video options: %s" % self.curOptions.title)
        self.txtInFile.SetLabel(self.curOptions.inFile)
        self.rbResolution.SetSelection(text_to_ID(self.curOptions.format))
        self.rbAspect.SetSelection(text_to_ID(self.curOptions.aspect))
        self.txtCLIOptions.SetValue(self.curOptions.addoptions)

    # ==========================================================
    # Get currently-set encoding options
    # ==========================================================
    def GetOptions(self):
        return self.curOptions

    # ==========================================================
    # Enable/disable controls to suit DVD, VCD, or SVCD-compliance
    # ==========================================================
    def SetDiscFormat(self, format):
        # For DVD, disable non-DVD output formats
        if format == 'dvd':
            for rbItem in [ID_FMT_DVD, ID_FMT_HALFDVD, ID_FMT_DVDVCD]:
                self.rbResolution.EnableItem(rbItem, True)
            for rbItem in [ID_FMT_SVCD, ID_FMT_VCD]:
                self.rbResolution.EnableItem(rbItem, False)
        # For VCD, enable only VCD output and disable bitrate controls
        elif format == 'vcd':
            for rbItem in range(0, 5):
                self.rbResolution.EnableItem(rbItem, False)
            self.rbResolution.EnableItem(ID_FMT_VCD, True)
        # For SVCD, enable only SVCD output
        elif format == 'svcd':
            for rbItem in range(0, 5):
                self.rbResolution.EnableItem(rbItem, False)
            self.rbResolution.EnableItem(ID_FMT_SVCD, True)
        # Unknown format?
        else:
            print "VideoPanel.SetDiscFormat: Unknown format %s" % format 
    
    # ==========================================================
    # Set the disc TV system to NTSC or PAL
    # Enable/disable controls accordingly
    # ==========================================================
    def SetDiscTVSystem(self, format):
        # Display NTSC resolutions in format radiobox
        if format in [ 'ntsc', 'ntscfilm' ]:
            self.rbResolution.SetItemLabel(ID_FMT_VCD, '352x240 VCD')
            self.rbResolution.SetItemLabel(ID_FMT_SVCD, '480x480 SVCD')
            self.rbResolution.SetItemLabel(ID_FMT_DVD, '720x480 DVD')
            self.rbResolution.SetItemLabel(ID_FMT_HALFDVD, '352x480 Half-DVD')
            self.rbResolution.SetItemLabel(ID_FMT_DVDVCD, '352x240 VCD on DVD')
        # Display PAL resolutions in format radiobox
        elif format == 'pal':
            self.rbResolution.SetItemLabel(ID_FMT_VCD, '352x288 VCD')
            self.rbResolution.SetItemLabel(ID_FMT_SVCD, '480x576 SVCD')
            self.rbResolution.SetItemLabel(ID_FMT_DVD, '720x576 DVD')
            self.rbResolution.SetItemLabel(ID_FMT_HALFDVD, '352x576 Half-DVD')
            self.rbResolution.SetItemLabel(ID_FMT_DVDVCD, '352x288 VCD on DVD')
        # Unknown format?
        else:
            print "VideoPanel.SetDiscTVSystem: Unknown format %s" % format

# ===================================================================
# End VideoPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Disc structure control. Contains a wx.TreeListCtrl showing the disc
# structure, and buttons for manipulating the tree
#
# ===================================================================
class DiscLayoutPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize DiscLayoutPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # ================================
        # Class data
        # ================================
        self.numMenus = 0   # Layout begins with no menus
        self.discFormat = 'dvd'
        self.discTVSystem = 'ntsc'
        self.parent = parent
        self.curConfig = Config()
        self.lastUsedPath = ""

        # ================================
        # Set up controls and sizers
        # ================================

        # Buttons and their tooltips
        self.btnAddVideos = wx.Button(self, wx.ID_ANY, "Add video(s)")
        self.btnAddSlides = wx.Button(self, wx.ID_ANY, "Add slide(s)")
        self.btnAddMenu = wx.Button(self, wx.ID_ANY, "Add menu")
        self.btnMoveUp = wx.Button(self, wx.ID_ANY, "Move up")
        self.btnMoveDown = wx.Button(self, wx.ID_ANY, "Move down")
        self.btnRemove = wx.Button(self, wx.ID_ANY, "Remove")
        self.btnAddVideos.SetToolTipString("Add video files under this menu")
        self.btnAddSlides.SetToolTipString("Add still-image files under this menu")
        self.btnAddMenu.SetToolTipString("Add a navigation menu to the disc; "
            "you must add at least one navigation menu before adding any videos.")
        self.btnMoveUp.SetToolTipString("Move the current item up")
        self.btnMoveDown.SetToolTipString("Move the current item down")
        self.btnRemove.SetToolTipString("Remove the current item from the disc")
        wx.EVT_BUTTON(self, self.btnAddVideos.GetId(), self.OnAddVideos)
        wx.EVT_BUTTON(self, self.btnAddSlides.GetId(), self.OnAddSlides)
        wx.EVT_BUTTON(self, self.btnAddMenu.GetId(), self.OnAddMenu)
        wx.EVT_BUTTON(self, self.btnMoveUp.GetId(), self.OnCuritemUp)
        wx.EVT_BUTTON(self, self.btnMoveDown.GetId(), self.OnCuritemDown)
        wx.EVT_BUTTON(self, self.btnRemove.GetId(), self.OnRemoveCuritem)
        # All buttons except AddMenu disabled to start with
        self.btnAddVideos.Enable(False)
        self.btnAddSlides.Enable(False)
        self.btnMoveUp.Enable(False)
        self.btnMoveDown.Enable(False)
        self.btnRemove.Enable(False)

        # The disc layout tree
        self.discTree = FlexTreeCtrl(self, wx.ID_ANY,
            style = wx.TR_SINGLE | wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | wx.SUNKEN_BORDER)
        # The disc layout tree
        # Icons to use in the tree
        iconSize = (16, 16)
        self.listIcons = wx.ImageList(iconSize[0], iconSize[1])
        self.idxIconMenu = self.listIcons.Add(GetMenuIcon())
        self.idxIconSlide = self.listIcons.Add(GetSlideIcon())
        self.idxIconVideo = self.listIcons.Add(GetVideoIcon())
        self.idxIconDisc = self.listIcons.Add(GetDiscIcon())

        self.discTree.SetImageList(self.listIcons)

        # Root of disc. Non-deletable.
        self.rootItem = self.discTree.AddRoot("Untitled disc", self.idxIconDisc)
        self.discTree.SetPyData(self.rootItem, DiscOptions())
        self.discTree.SetToolTipString("Navigation layout of the disc. "
            "Use the buttons below to add elements. Click on the title of "
            "an element to edit it.")
        wx.EVT_TREE_SEL_CHANGED(self.discTree, self.discTree.GetId(), self.OnTreeSelChanged)
        wx.EVT_TREE_END_LABEL_EDIT(self.discTree, self.discTree.GetId(), self.OnTreeItemEdit)
        self.discTree.Expand(self.rootItem)
        # topItem starts out being root
        self.topItem = self.rootItem
        
        # Horizontal box sizer to hold tree manipulation buttons
        self.sizBtn = wx.GridSizer(2, 3, 0, 0)
        self.sizBtn.AddMany([ (self.btnAddMenu, 1, wx.EXPAND),
                               (self.btnRemove, 1, wx.EXPAND),
                               (self.btnMoveUp, 1, wx.EXPAND),
                               (self.btnAddVideos, 1, wx.EXPAND),
                               (self.btnAddSlides, 1, wx.EXPAND),
                               (self.btnMoveDown, 1, wx.EXPAND) ])

        # Outer vertical box sizer to hold tree and button-box
        self.sizTree = wx.BoxSizer(wx.VERTICAL)
        self.sizTree.Add(self.discTree, 1, wx.EXPAND | wx.ALL, 0)
        self.sizTree.Add(self.sizBtn, 0, wx.EXPAND)

        # Panel to contain disc options (format, tvsys, etc.)
        self.panDisc = DiscPanel(self, wx.ID_ANY)
        self.panDisc.SetOptions(self.discTree.GetPyData(self.rootItem))
        # Panels to contain video/menu encoding options
        self.panVideoOptions = VideoPanel(self, wx.ID_ANY)
        self.panMenuOptions = MenuPanel(self, wx.ID_ANY)
        # Hide currently-unused options panels
        self.panVideoOptions.Hide()
        self.panMenuOptions.Hide()
        # Sizers to hold options panel (and more later?)
        self.sizOptions = wx.BoxSizer(wx.VERTICAL)
        self.sizOptions.Add(self.panDisc, 1, wx.EXPAND | wx.ALL, 8)

        # Horizontal splitter to hold tree and options panel
        self.sizTreeOpts = wx.BoxSizer(wx.HORIZONTAL)
        self.sizTreeOpts.Add(self.sizTree, 2, wx.EXPAND | wx.ALL, 8)
        self.sizTreeOpts.Add(self.sizOptions, 3, wx.EXPAND | wx.ALL, 0)

        # Main splitter to hold panels
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.sizTreeOpts, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self.sizMain)

        # Select DVD/NTSC by default
        self.SetDiscFormat('dvd')
        self.SetDiscTVSystem('ntsc')

    # ==========================================================
    # When a tree selection changes
    # ==========================================================
    def OnTreeSelChanged(self, evt):
        curItem = self.discTree.GetSelection()
        curOpts = self.discTree.GetPyData(curItem)
        curType = curOpts.type
        curParent = self.discTree.GetItemParent(curItem)

        # If root is selected, disable unusable buttons
        if curItem == self.rootItem:
            self.btnMoveUp.Enable(False)
            self.btnMoveDown.Enable(False)
            self.btnRemove.Enable(False)
            self.btnAddVideos.Enable(False)
            self.btnAddSlides.Enable(False)
        # Otherwise, enable usable buttons
        else:
            # Can always remove non-root items
            self.btnRemove.Enable(True)
            # Can only move up/down for items with siblings
            if self.discTree.GetChildrenCount(curParent, False) > 1:
                self.btnMoveUp.Enable(True)
                self.btnMoveDown.Enable(True)
            else:
                self.btnMoveUp.Enable(False)
                self.btnMoveDown.Enable(False)
            # If a non top-level menu is selected, enable the
            # AddVideos/AddSlides buttons
            if curType == ID_MENU and curItem != self.topItem:
                self.btnAddVideos.Enable(True)
                #self.btnAddSlides.Enable(True)
            # Otherwise, disable them
            else:
                self.btnAddVideos.Enable(False)
                #self.btnAddSlides.Enable(False)

        # If disc was selected, show disc options
        if curType == ID_DISC:
            self.sizOptions.Remove(0)
            self.sizOptions.Add(self.panDisc, 1, wx.EXPAND | wx.ALL, 8)
            self.panMenuOptions.Hide()
            self.panVideoOptions.Hide()
            self.panDisc.Show()
            self.sizOptions.Layout()

            # Set appropriate guide text
            self.curConfig.panGuide.SetTask(ID_TASK_DISC_SELECTED)

        # For a video, show video encoding options
        elif curType == ID_VIDEO:
            # Remove existing panel and show panVideoOptions
            self.sizOptions.Remove(0)
            self.panVideoOptions.SetOptions(curOpts)
            self.sizOptions.Add(self.panVideoOptions, 1, wx.EXPAND | wx.ALL, 8)
            self.panDisc.Hide()
            self.panMenuOptions.Hide()
            self.panVideoOptions.Show()
            self.sizOptions.Layout()

            # Set appropriate guide text
            self.curConfig.panGuide.SetTask(ID_TASK_VIDEO_SELECTED)

        # For a menu, show menu encoding options
        elif curType == ID_MENU:
            # Do I need to do this?
            self.RefreshItem(curItem)

            # Remove existing panel and show panMenuOptions
            self.sizOptions.Remove(0)
            self.panMenuOptions.SetOptions(curOpts)
            self.sizOptions.Add(self.panMenuOptions, 1, wx.EXPAND | wx.ALL, 8)
            self.panDisc.Hide()
            self.panVideoOptions.Hide()
            self.panMenuOptions.Show()
            self.sizOptions.Layout()
        
            # Set appropriate guide text
            self.curConfig.panGuide.SetTask(ID_TASK_MENU_SELECTED)

    # ==========================================================
    # When a tree item's title is edited
    # ==========================================================
    def OnTreeItemEdit(self, evt):
        if not evt.IsEditCancelled():
            curItem = evt.GetItem()
            curOpts = self.discTree.GetPyData(curItem)
            curOpts.title = evt.GetLabel()
            # Assign outPrefix based on title
            curOpts.outPrefix = curOpts.title.replace(' ', '_')

            # Update the appropriate panel
            if curOpts.type == ID_DISC:
                self.panDisc.SetOptions(curOpts)
            elif curOpts.type == ID_MENU:
                self.panMenuOptions.SetOptions(curOpts)
            elif curOpts.type == ID_VIDEO:
                self.panVideoOptions.SetOptions(curOpts)
                
                # Update the titles shown list in the menu panel
                
                # Get the parent menu
                curParent = self.discTree.GetItemParent(curItem)
                # and the options for the parent menu
                parentOpts = self.discTree.GetPyData(curParent)
                # Get the text of the item as it was before it the change
                curText = self.discTree.GetItemText(curItem)
                # find the title to change
                for title in parentOpts.titles:
                    # compare title with old text
                    if title == curText:
                        # item found, change it
                        title = evt.GetLabel()
                        # get out of the loop
                        break

    # ==========================================================
    # Append a menu
    # ==========================================================
    def OnAddMenu(self, evt):
        self.numMenus += 1
        # If this is the second menu on the disc, and a top menu does
        # not already exist, create a top menu and insert the current
        # menu after it
        if self.numMenus == 2 and self.topItem == self.rootItem:
            oldMenu, cookie = VER_GetFirstChild(self.discTree, self.topItem)
            self.topItem = self.discTree.AppendItem(self.rootItem,
                "Main menu", self.idxIconMenu)
            # Create a new top menu at the root of the tree
            self.discTree.SetPyData(self.topItem,
                MenuOptions(self.discFormat, self.discTVSystem, "Main menu", True))

            copiedMenu = self.discTree.AppendItemMove(self.topItem, oldMenu)
            # Refresh the copied menu
            self.RefreshItem(copiedMenu)
            self.discTree.Expand(copiedMenu)
            # One more menu (top menu)
            self.numMenus += 1

        # New menu is appended under topItem
        curItem = self.discTree.AppendItem(self.topItem,
            "Untitled menu %d" % self.numMenus, self.idxIconMenu)
        self.discTree.SetPyData(curItem, MenuOptions(self.discFormat,
            self.discTVSystem, "Untitled menu %d" % self.numMenus))
        # Refresh the current item (for empty menus, just adds the "Back" button)
        self.RefreshItem(curItem)
        # Expand, show, and select the new menu
        self.discTree.EnsureVisible(curItem)
        self.discTree.Expand(curItem)
        self.discTree.SelectItem(curItem)

        # If tree has more than one item, enable encoding button
        if self.discTree.GetCount() > 1:
            self.parent.EncodeOK(True)

        # Refresh the top item to include any added menus
        self.RefreshItem(self.topItem)

        # Set appropriate guide text
        self.curConfig.panGuide.SetTask(ID_TASK_MENU_ADDED)

    # ==========================================================
    # Add video files to the disc structure
    # One or more videos are inserted after the current item
    # ==========================================================
    def OnAddVideos(self, evt):
        curParent = self.discTree.GetSelection()

        # If there are no menus yet, create one before adding
        # the videos under it
        if self.numMenus < 1:
            self.OnAddMenu(wx.CommandEvent())

        # If there are menus, but none is selected, ask user to
        # select a menu before adding videos
        elif self.numMenus > 0 and \
             self.discTree.GetPyData(curParent).type != ID_MENU:
            # Show a message dialog
            msgDlg = wx.MessageDialog(self, "Please select a menu before adding videos",
                "No menu selected",
                wx.OK | wx.ICON_EXCLAMATION)
            msgDlg.ShowModal()
            msgDlg.Destroy()
            return
            
        # Open a file dialog for user to choose videos to add
        addFileDlg= wx.FileDialog(self, "Select video files", self.lastUsedPath,
            "", "*.*", wx.OPEN | wx.MULTIPLE)
        if addFileDlg.ShowModal() == wx.ID_OK:
            # Get all the filenames that were selected
            strPathnames = addFileDlg.GetPaths()
            # Remember the last used directory
            self.lastUsedPath = os.path.dirname(strPathnames[0])
            # Store the directory name for later use
            addFileDlg.Destroy()
        else:
            return

        # Append items as children of the current selection
        for curFile in range(len(strPathnames)):
            # Make sure path exists
            if not os.path.exists(strPathnames[ curFile ]):
                return

            # Use file basename, underscores replaced with spaces,
            # for the default title
            curTitle = os.path.basename(strPathnames[ curFile ]).replace('_', ' ')
            curItem = self.discTree.AppendItem(curParent, curTitle, self.idxIconVideo)
            curOpts = VideoOptions(self.discFormat, self.discTVSystem,
                strPathnames[ curFile ])
            self.discTree.SetPyData(curItem, curOpts)
            curStats = VideoStatSeeker(curOpts)
            curStats.start()

        # If tree has more than one item, enable encoding button
        if self.discTree.GetCount() > 1:
            self.parent.EncodeOK(True)

        self.discTree.EnsureVisible(curItem)

        # Refresh the parent to include all added videos
        self.RefreshItem(curParent)
        # Refresh the panel view of the parent menu
        self.discTree.SelectItem(curParent)
        curOpts = self.discTree.GetPyData(curParent)
        self.panMenuOptions.SetOptions(curOpts)
    
        # Set appropriate guide text
        self.curConfig.panGuide.SetTask(ID_TASK_VIDEO_ADDED)

    # ==========================================================
    # Add slides to the disc structure
    # A group of slides is added under the current menu
    # ==========================================================
    def OnAddSlides(self, evt):
        # ***********************************
        # SLIDES ARE DISABLED IN THIS RELEASE
        # ***********************************
        # Display a message and return
        msgDlg = wx.MessageDialog(self, "Slideshows are not supported "
            "in this version. Sorry!", "Slides not functional yet",
            wx.OK | wx.ICON_EXCLAMATION)
        msgDlg.ShowModal()
        msgDlg.Destroy()
        return

        # The real functionality, for when slides are supported

        curParent = self.discTree.GetSelection()
        # If a menu is not selected, print an error and return
        if self.discTree.GetPyData(curParent).type != ID_MENU:
            msgDlg = wx.MessageDialog(self, "Please select a menu before "
               "adding slides.",
               "No menu selected",
               wx.OK | wx.ICON_EXCLAMATION)
            msgDlg.ShowModal()
            msgDlg.Destroy()
            return

        # Open a file dialog for user to choose slides to add
        addFileDlg= wx.FileDialog(self, "Select image files", "", "", "*.*",
            wx.OPEN | wx.MULTIPLE)
        if addFileDlg.ShowModal() == wx.ID_OK:
            # Get all the filenames that were selected
            strPathnames = addFileDlg.GetPaths()
            # Store the directory name for later use
            addFileDlg.Destroy()
        else:
            return

        # Append a new slide element containing the given list of files
        curItem = self.discTree.AppendItem(curParent, "Untitled slides",
            self.idxIconSlide)
        curOpts = SlideOptions(self.discFormat, self.discTVSystem, strPathnames)
        self.discTree.SetPyData(curItem, curOpts)

        self.discTree.EnsureVisible(curItem)

        # Refresh the parent to include all added videos
        self.RefreshItem(curParent)

        # If tree has more than one item, enable encoding button
        if self.discTree.GetCount() > 1:
            self.parent.EncodeOK(True)

    # ==========================================================
    # Move the currently-selected item up in the list
    # Item stays within its group of siblings
    # ==========================================================
    def OnCuritemUp(self, evt):
        self.discTree.MoveItemUp()
        # Refresh the parent
        curParent = self.discTree.GetItemParent(self.discTree.GetSelection())
        self.RefreshItem(curParent)

    # ==========================================================
    # Move the currently-selected item down in the list
    # Item stays within its group of siblings
    # ==========================================================
    def OnCuritemDown(self, evt):
        self.discTree.MoveItemDown()
        # Refresh the parent
        curParent = self.discTree.GetItemParent(self.discTree.GetSelection())
        self.RefreshItem(curParent)

    # ==========================================================
    # Remove the currently-selected item and its descendants
    # ==========================================================
    def OnRemoveCuritem(self, evt):
        curItem = self.discTree.GetSelection()
        curParent = self.discTree.GetItemParent(curItem)

        # If root is selected, do nothing
        if curItem == self.rootItem:
            return

        # If the top item is selected, verify before deletion
        elif curItem.IsOk() and curItem == self.topItem:
            dlgConfirm = wx.MessageDialog(self,
                "This will remove all menus and videos\n"
                "from the disc layout. Proceed?",
                "Confirm removal", wx.YES_NO | wx.ICON_QUESTION)
            if dlgConfirm.ShowModal() == wx.ID_YES:
                self.discTree.Delete(curItem)
                # Top item goes back to being root
                self.topItem = self.rootItem
            dlgConfirm.Destroy()
            # Back to having 0 menus
            self.numMenus = 0

        # Make sure the item isn't root or topItem before being deleted
        elif curItem.IsOk():
            # If deleting a menu, confirm deletion and
            # decrement the menu counter
            if self.discTree.GetPyData(curItem).type == ID_MENU:
                dlgConfirm = wx.MessageDialog(self,
                    "This will remove the currently selected\n"
                    "menu, along with all videos and stills\n"
                    "under it. Proceed?",
                    "Confirm removal", wx.YES_NO | wx.ICON_QUESTION)
                if dlgConfirm.ShowModal() == wx.ID_NO:
                    return
                self.numMenus -= 1

            # Delete the current item
            self.discTree.Delete(curItem)

        # Refresh the parent
        self.RefreshItem(curParent)

        # If only one item remains, disable encode button
        if self.discTree.GetCount() < 2:
            self.parent.EncodeOK(False)


    # ==========================================================
    #
    # Public utility functions
    #
    # ==========================================================

    # ==========================================================
    # Set the encoding options associated with the current item
    # ==========================================================
    def SetOptions(self, options):
        self.discTree.SetPyData(self.discTree.GetSelection(), options)

    # ==========================================================
    # Get the encoding options associated with the current item
    # ==========================================================
    def GetOptions(self):
        return self.discTree.GetPyData(self.discTree.GetSelection())

    # ==========================================================
    # Set the disc format (DVD, VCD, SVCD)
    # ==========================================================
    def SetDiscFormat(self, format):
        self.discFormat = format 
        # Make video panel controls appropriate for this disc format
        self.panVideoOptions.SetDiscFormat(format)
        # Make menu panel controls appropriate for this disc format
        self.panMenuOptions.SetDiscFormat(format)
        # Make all encoding options in the disc compliant
        format = self.discTree.GetPyData(self.rootItem).format
        refs = self.discTree.GetReferenceList(self.rootItem)
        for curItem in refs:
            if curItem.type != ID_DISC:
                curItem.SetDiscFormat(format)

    # ==========================================================
    # Set the disc TV system (NTSC, PAL)
    # ==========================================================
    def SetDiscTVSystem(self, tvsys):
        self.discTVSystem = tvsys
        # Make video panel controls appropriate for this disc TVsystem
        self.panVideoOptions.SetDiscTVSystem(tvsys)
        # Make all encoding options in the disc compliant
        tvsys = self.discTree.GetPyData(self.rootItem).tvsys
        refs = self.discTree.GetReferenceList(self.rootItem)
        for curItem in refs:
            # Menus and slides need to know TV system
            if curItem.type != ID_DISC:
                curItem.SetDiscTVSystem(tvsys)

    # ==========================================================
    # Refresh the given tree item and make sure it is up-to-date
    # Should be called for an item after its children have changed
    # ==========================================================
    def RefreshItem(self, curItem):

        curOpts = self.discTree.GetPyData(curItem)

        # If it's a menu, fill it with the titles listed below it
        if curOpts.type == ID_MENU:
            curOpts.titles = []
            curChild, cookie = VER_GetFirstChild(self.discTree, curItem)
            while curChild.IsOk():
                curOpts.titles.append(self.discTree.GetItemText(curChild))
                curChild, cookie = self.discTree.GetNextChild(curItem, cookie)
            # If this is not a top menu, add a "Back" title (link)
            if not curOpts.isTopMenu and self.numMenus > 1:
                curOpts.titles.append("Back")
        # Nothing to do for other items (yet?)
        
    # ==========================================================
    # Use the given options for all videos/menus/slides
    # ==========================================================
    def UseForAllItems(self, opts):
        # Get references for all items
        refs = self.discTree.GetReferenceList(self.rootItem)
        # Count how many items are changed
        countItems = 0
        # Apply options to all items in the tree of the same type
        # Don't copy to self
        for curItem in refs:
            if curItem != opts:
                if curItem.type == opts.type:
                    curItem.CopyFrom(opts)
                    countItems += 1

        return countItems


    def GetAllCommands(self):
        """Return an array of strings containing all encoding commands to be
        executed."""
        # Get references for all items
        refs = self.discTree.GetReferenceList(self.rootItem)
        # Send the reference list to the root DiscOptions item
        # (so it can generate the authoring command)
        discOpts = self.discTree.GetPyData(self.rootItem)
        discOpts.SetLayout(refs)

        # Pop root command off, since it needs to be
        # put at the end of the command list
        strDiscCmd = refs.pop(0).GetCommand()

        # Append command associated with each item
        commands = []
        for curItem in refs:
            commands.append(curItem.GetCommand())

        # Append root command
        commands.append(strDiscCmd)

        return commands


    def GetElements(self):
        refs = self.discTree.GetReferenceList(self.rootItem)
        for item in refs:
            print item.title

        # Set discOpts, so topmenu will be included
        discOpts = self.discTree.GetPyData(self.rootItem)
        discOpts.SetLayout(refs)
        # Append each element in disc
        elements = []
        for curitem in refs:
            elements.append(curitem.toElement())
        print "DiscLayoutPanel.GetElements(): elements:"
        for elem in elements:
            print elem.tdl_string()
        return elements


    def SetElements(self, topitems):
        # Empty existing tree
        self.discTree.DeleteAllItems()
        
        # Append root-level elements
        for parent in topitems:
            self.rootItem = self.discTree.AddRoot(parent.name, self.idxIconDisc)
            opts = element_to_options(parent)
            self.discTree.SetPyData(self.rootItem, opts)
            # Append second-level elements (top-level menus)
            for child in parent.children:
                childitem = self.AddElement(child, self.rootItem)
                # Append third-level elements (videos)
                for grandchild in child.children:
                    grandchilditem = self.AddElement(grandchild, childitem)
                    # This is getting redundant...
                    # TODO: Better algorithm (possibly recursive)
                    for greatgrandchild in grandchild.children:
                        self.AddElement(greatgrandchild, grandchilditem)
            # HACK: Stop after the first top item (Disc element)
            break
                    

    def AddElement(self, element, parent):
        """Add a TDL element to the tree, under the given parent item,
        and return the new item ID."""
        item = self.discTree.AppendItem(parent,
                element.name, self.GetIcon(element))
        # Convert element into [Disc|Menu|Video]Options
        opts = element_to_options(element)
        # Store Options in the tree
        self.discTree.SetPyData(item, opts)
        # Ensure visibility
        self.discTree.EnsureVisible(item)
        return item


    def GetIcon(self, element):
        if element.tag == 'Disc':
            return self.idxIconDisc
        elif element.tag == 'Menu':
            return self.idxIconMenu
        else:
            return self.idxIconVideo

# ===================================================================
# End DiscLayoutPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Encoding setup panel. Allow selection of output directory,
# display estimated encoding and final size requirements, controls
# and log window for running all encoding commands.
#
# ===================================================================
class EncodingPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize EncodingPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Class variables
        self.parent = parent

        # Get a Config instance
        self.curConfig = Config()

        # Estimated final size
        #self.lblFinalSize = wx.StaticText(self, wx.ID_ANY, "Estimated final size:")
        #self.txtFinalSize = wx.StaticText(self, wx.ID_ANY, "Unknown")
        # Estimated encoding space needed
        #self.lblEncodingSize = wx.StaticText(self, wx.ID_ANY, "Estimated space needed:")
        #self.txtEncodingSize = wx.StaticText(self, wx.ID_ANY, "Unknown")

        # Sizer to hold size estimates
        #self.sizEstimates = wx.FlexGridSizer(2, 2, 8, 8)
        #self.sizEstimates.AddMany([ (self.lblFinalSize, 0, wx.RIGHT),
        #                             (self.txtFinalSize, 1, wx.EXPAND),
        #                             (self.lblEncodingSize, 0, wx.RIGHT),
        #                             (self.txtEncodingSize, 1, wx.EXPAND) ])
        
        # Command window
        self.panCmdList = CommandOutputPanel(self, wx.ID_ANY)

        # Start/interrupt button
        self.btnStartStop = wx.Button(self, wx.ID_ANY, "Start encoding")
        self.btnStartStop.SetToolTipString("Begin encoding and preparing " \
            "all videos and menus on the disc")
        # Button events
        wx.EVT_BUTTON(self, self.btnStartStop.GetId(), self.OnStartStop)

        # Sizer to hold controls
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        #self.sizMain.Add(self.sizEstimates, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.panCmdList, 1, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnStartStop, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    # ==========================================================
    # Browse for output directory
    # ==========================================================
    def OnBrowseOutDir(self, evt):
        outDirDlg = wx.DirDialog(self, "Select a directory for output",
            style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if outDirDlg.ShowModal() == wx.ID_OK:
            self.curConfig.strOutputDirectory = outDirDlg.GetPath()
            self.txtOutDir.SetValue(self.curConfig.strOutputDirectory)
            outDirDlg.Destroy()

    # ==========================================================
    # Start/suspend/resume encoding
    # ==========================================================
    def OnStartStop(self, evt):
        # If currently running, stop/suspend processing
        if self.panCmdList.idleTimer.IsRunning():
            # Disable button temporarily, to allow processes to die
            self.btnStartStop.Enable(False)
            self.panCmdList.Stop()
            self.btnStartStop.SetLabel("Resume encoding")
            self.btnStartStop.SetToolTipString("Resume the encoding process " \
                "where it left off")
            # Show message that processing stopped
            msgStopped = wx.MessageDialog(self,
                "Encoding is now suspended. You can continue\n" \
                "by selecting \"Resume encoding\".",
                "Encoding suspended", wx.OK | wx.ICON_INFORMATION)
            msgStopped.ShowModal()
            # Give processes time to die before re-enabling button
            os.system("sleep 2s")
            self.btnStartStop.Enable(True)

        # Not running; start/resume processing
        else:
            self.curConfig.panGuide.SetTask(ID_TASK_ENCODING_STARTED)
            self.panCmdList.Start()
            self.btnStartStop.SetLabel("Suspend encoding")
            self.btnStartStop.SetToolTipString("Interrupt the current " \
                "encoding process and return the current command to the queue")

    # ==========================================================
    # Set command-list to be executed from DiscLayoutPanel
    # ==========================================================
    def SetCommands(self, commands):
        for cmd in commands:
            self.panCmdList.Execute(cmd)

    # ==========================================================
    # Set the output directory to use
    # ==========================================================
    def SetOutputDirectory(self, outDir):
        self.txtOutDir.SetValue(outDir)
          
    # ==========================================================
    # Signify that processing (video encoding) is done
    # ==========================================================
    def ProcessingDone(self, errorOccurred):
        self.parent.btnBurn.Enable(False)
        # Let user know if error(s) occurred
        if errorOccurred:
            msgError = wx.MessageDialog(self,
                "Error(s) occurred during encoding. If you want to\n" \
                "help improve this software, please file a bug report\n" \
                "containing a copy of the output log. Unfortunately,\n" \
                "this also means you won't be able to continue with\n" \
                "creating your disc. Sorry for the inconvenience!",
                "Error occurred during encoding", wx.ICON_ERROR | wx.OK)
            msgError.ShowModal()
        # Show success message and enable burning
        else:
            strSuccess = "Done encoding. You may now proceed " \
                "with burning the disc."
            msgSuccess = wx.MessageDialog(self, strSuccess, "Success!",
                wx.ICON_INFORMATION | wx.OK)
            msgSuccess.ShowModal()

            # Burning is OK now
            self.parent.BurnOK(True)

        # Re-enable buttons
        self.btnStartStop.SetLabel("Start encoding")
        self.btnStartStop.Enable(False)


# ===================================================================
# End EncodingPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# Disc-burning panel. Show controls for authoring and burning the
# disc.
#
# ===================================================================
class BurnDiscPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize BurnDiscPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Keep track of parent
        self.parent = parent
        self.device = "/dev/dvdrw"
        self.doAuthor = True
        self.doImage = True
        self.doBurn = False

        self.txtHeading = HeadingText(self, wx.ID_ANY, "Author and burn")

        self.chkDoAuthor = wx.CheckBox(self, wx.ID_ANY, "Author disc structure")
        self.chkDoImage = wx.CheckBox(self, wx.ID_ANY, "Create disc image (.iso)")
        self.chkDoBurn = wx.CheckBox(self, wx.ID_ANY, "Burn disc")
        self.chkDoAuthor.SetToolTipString("Create the disc filesystem hierarchy " \
            "using dvdauthor")
        self.chkDoImage.SetToolTipString("Create an .iso image of the disc before" \
            "burning")
        self.chkDoBurn.SetToolTipString("Burn the image to the selected " \
            "device")
        self.chkDoAuthor.SetValue(self.doAuthor)
        self.chkDoImage.SetValue(self.doImage)
        self.chkDoBurn.SetValue(self.doBurn)
        wx.EVT_CHECKBOX(self, self.chkDoAuthor.GetId(), self.OnDoAuthor)
        wx.EVT_CHECKBOX(self, self.chkDoImage.GetId(), self.OnDoImage)
        wx.EVT_CHECKBOX(self, self.chkDoBurn.GetId(), self.OnDoBurn)

        self.lblDiscDevice = wx.StaticText(self, wx.ID_ANY, "Burn to device:")
        self.txtDiscDevice = wx.TextCtrl(self, wx.ID_ANY, self.device)
        wx.EVT_TEXT(self, self.txtDiscDevice.GetId(), self.OnSetDevice)

        # Sizer to hold burning controls
        self.sizBurn = wx.FlexGridSizer(4, 2, 8, 8)
        self.sizBurn.Add((2, 2))
        self.sizBurn.Add(self.chkDoAuthor, 0, wx.EXPAND)
        self.sizBurn.Add((2, 2))
        self.sizBurn.Add(self.chkDoImage, 0, wx.EXPAND)
        self.sizBurn.Add((2, 2))
        self.sizBurn.Add(self.chkDoBurn, 0, wx.EXPAND)
        self.sizBurn.Add(self.lblDiscDevice, 0, wx.EXPAND)
        self.sizBurn.Add(self.txtDiscDevice, 1, wx.EXPAND)

        # Command window
        self.panCmdList = CommandOutputPanel(self, wx.ID_ANY)
        self.panCmdList.Enable(False)

        # Start button
        self.btnStart = wx.Button(self, wx.ID_ANY, "Start")
        wx.EVT_BUTTON(self, self.btnStart.GetId(), self.OnStart)

        # Sizer to hold controls
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizBurn, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.panCmdList, 1, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnStart, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)
    
    # ==========================================================
    # Turn on/off authoring, imaging, or burning
    # ==========================================================
    def OnDoAuthor(self, evt):
        self.doAuthor = evt.Checked()
    def OnDoImage(self, evt):
        self.doImage = evt.Checked()
    def OnDoBurn(self, evt):
        self.doBurn = evt.Checked()

    # ==========================================================
    # Use selected device
    # ==========================================================
    def OnSetDevice(self, evt):
        self.device = self.txtDiscDevice.GetValue()

    # ==========================================================
    # Author (and burn) the disc
    # ==========================================================
    def OnStart(self, evt):
        # Get global config (for XML filename and format)
        curConfig = Config()

        msgWarning = wx.MessageDialog(self,
            "Disc burning is still experimental in this release,\n" \
            "and might not work. Please report any bugs you encounter!",
            "Experimental feature", wx.ICON_INFORMATION | wx.OK)
        msgWarning.ShowModal()

        makedvdOptions = ""

        # Construct authoring/imaging/burning options
        if self.doAuthor:
            makedvdOptions += "-author "
        if self.doImage:
            makedvdOptions += "-image "
        if self.doBurn:
            makedvdOptions += "-burn "

        if curConfig.curDiscFormat == 'vcd' or \
           curConfig.curDiscFormat == 'svcd':
            strAuthorCmd = "makevcd -device %s %s %s.xml" % \
                (self.device, makedvdOptions, curConfig.strOutputXMLFile)
        else:
            strAuthorCmd = "makedvd -device %s %s %s.xml" % \
                (self.device, makedvdOptions, curConfig.strOutputXMLFile)

        #self.btnStart.Enable(False)
        self.panCmdList.Enable(True)
        self.panCmdList.Execute(strAuthorCmd)
        self.panCmdList.Start()

    # ==========================================================
    # Signify that disc burning is done
    # ==========================================================
    def ProcessingDone(self, errorOccurred):
        # Let user know if error(s) occurred
        if errorOccurred:
            msgError = wx.MessageDialog(self,
                "Error(s) occurred during burning. If you want to\n" \
                "help improve this software, please file a bug report\n" \
                "containing a copy of the output log. Unfortunately,\n" \
                "this also means you won't be able to continue with\n" \
                "creating your disc. Sorry for the inconvenience!",
                "Error occurred during encoding", wx.ICON_ERROR | wx.OK)
            msgError.ShowModal()
        # Show success message and enable burning
        else:
            strSuccess = "Done burning the disc."
            msgSuccess = wx.MessageDialog(self, strSuccess, "Success!",
                wx.ICON_INFORMATION | wx.OK)
            msgSuccess.ShowModal()


# ===================================================================
# End BurnDiscPanel
# ===================================================================

# ===================================================================
#
# CLASS DEFINITION
# AuthorFilesTaskPanel. Handles 3-step authoring from video files,
# using DiscLayoutPanel, EncodingPanel, and BurnDiscPanel.
#
# ===================================================================
class AuthorFilesTaskPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize AuthorFilesTaskPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Global configuration
        self.curConfig = Config()

        # Task panels
        self.panDiscLayout = DiscLayoutPanel(self, wx.ID_ANY)
        self.panEncoding = EncodingPanel(self, wx.ID_ANY)
        self.panBurnDisc = BurnDiscPanel(self, wx.ID_ANY)
        self.panEncoding.Hide()
        self.panBurnDisc.Hide()
        # Keep an eye on the current panel
        self.curPanel = self.panDiscLayout

        # 3-step buttons (toggle buttons)
        # Layout / Encode / Burn

        # ======================
        # gettext test
        self.btnLayout = BoldToggleButton(self, wx.ID_ANY, _("1. Layout"))
        self.btnEncode = BoldToggleButton(self, wx.ID_ANY, _("2. Encode"))
        self.btnBurn = BoldToggleButton(self, wx.ID_ANY, _("3. Burn"))
        # ======================

        self.btnLayout.SetToolTipString("Modify the arrangement of videos "
            "and menus on the disc")
        self.btnEncode.SetToolTipString("Set up and encode the videos "
            "and menus in the current disc layout")
        self.btnBurn.SetToolTipString("Burn the completed disc")

        # Toggle button events
        wx.EVT_TOGGLEBUTTON(self, self.btnLayout.GetId(), self.OnLayout)
        wx.EVT_TOGGLEBUTTON(self, self.btnEncode.GetId(), self.OnEncode)
        wx.EVT_TOGGLEBUTTON(self, self.btnBurn.GetId(), self.OnBurn)
        self.btnLayout.SetValue(True)
        self.btnEncode.Enable(False)
        self.btnBurn.Enable(False)

        # 3-step sizer
        self.sizSteps = wx.BoxSizer(wx.HORIZONTAL)
        self.sizSteps.Add(self.btnLayout, 1, wx.EXPAND | wx.ALL, 2)
        self.sizSteps.Add(self.btnEncode, 1, wx.EXPAND | wx.ALL, 2)
        self.sizSteps.Add(self.btnBurn, 1, wx.EXPAND | wx.ALL, 2)

        # Task sizer. Holds panel(s) related to current task
        # (layout, encoding, burning). Shows only one panel
        # at a time.
        self.sizTask = wx.BoxSizer(wx.VERTICAL)
        self.sizTask.Add(self.panDiscLayout, 1, wx.EXPAND)

        # Main sizer. Holds task (layout, encoding) panel and 3-step buttons
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.sizSteps, 0, wx.EXPAND | wx.ALL, 6)
        self.sizMain.Add(wx.StaticLine(self, wx.ID_ANY, style = wx.LI_HORIZONTAL),
            0, wx.EXPAND)
        self.sizMain.Add(self.sizTask, 1, wx.EXPAND)

        self.SetSizer(self.sizMain)


    def SetElements(self, topitems):
        """Load the given list of TDL Elements into the GUI,
        replacing the current project."""
        self.panDiscLayout.SetElements(topitems)


    def GetElements(self):
        """Return a list of TDL elements representing the current project."""
        # Hackery: Call GetAllCommands so the disc item will
        # be updated (and thus, topmenu can be saved correctly)
        self.panDiscLayout.GetAllCommands()
        return self.panDiscLayout.GetElements()


    # Set encoding to OK/not OK (True/False)
    def EncodeOK(self, ok):
        if ok == True:
            self.btnEncode.Enable(True)
        else:
            self.btnEncode.Enable(False)

    # Set burning to OK/not OK (True/False)
    def BurnOK(self, ok):
        if ok:
            self.btnBurn.Enable(True)
        else:
            self.btnBurn.Enable(False)

    # Layout button
    def OnLayout(self, evt):
        # Set buttons
        self.btnLayout.SetValue(True)
        self.btnEncode.SetValue(False)
        self.btnBurn.SetValue(False)

        # If Layout is showing, do nothing else
        if self.curPanel == self.panDiscLayout:
            return

        # Clear Encoding panel command list
        self.panEncoding.panCmdList.Clear()

        # Show Layout panel
        self.curPanel = self.panDiscLayout
        self.sizTask.Remove(0)
        self.panEncoding.Hide()
        self.panBurnDisc.Hide()
        self.sizTask.Add(self.panDiscLayout, 1, wx.EXPAND)
        self.panDiscLayout.Show()
        self.sizTask.Layout()
        self.curPanel = self.panDiscLayout
        # Set buttons
        self.btnLayout.SetValue(True)
        self.btnEncode.SetValue(False)
        self.btnBurn.SetValue(False)

        # Set appropriate guide text
        self.curConfig.panGuide.SetTask(ID_TASK_GETTING_STARTED)

    # Encode button
    def OnEncode(self, evt):
        # Set buttons
        self.btnLayout.SetValue(False)
        self.btnEncode.SetValue(True)
        self.btnBurn.SetValue(False)

        # If Encode is showing, do nothing else
        if self.curPanel == self.panEncoding:
            return
        
        # Show Encode panel
        self.curPanel = self.panEncoding
        self.sizTask.Remove(0)
        self.panDiscLayout.Hide()
        self.panBurnDisc.Hide()
        self.sizTask.Add(self.panEncoding, 1, wx.EXPAND)
        self.panEncoding.Show()
        self.sizTask.Layout()
        self.curPanel = self.panEncoding

        # Give command list to encoding panel
        cmdList = self.panDiscLayout.GetAllCommands()
        self.panEncoding.SetCommands(cmdList)
        # Set appropriate guide text
        self.curConfig.panGuide.SetTask(ID_TASK_PREP_ENCODING)

    # Burn button
    def OnBurn(self, evt):
        # Set buttons
        self.btnLayout.SetValue(False)
        self.btnEncode.SetValue(False)
        self.btnBurn.SetValue(True)

        # If Burn is showing, do nothing
        if self.curPanel == self.panBurnDisc:
            return

        # Show Burn panel
        self.curPanel = self.panBurnDisc
        self.sizTask.Remove(0)
        self.panDiscLayout.Hide()
        self.panEncoding.Hide()
        self.sizTask.Add(self.panBurnDisc, 1, wx.EXPAND)
        self.panBurnDisc.Show()
        self.sizTask.Layout()
        self.curPanel = self.panBurnDisc
        # Set appropriate guide text
        self.curConfig.panGuide.SetTask(ID_TASK_BURN_DISC)

# ===================================================================
# End AuthorFilesTaskPanel
# ===================================================================


# ===================================================================
#
# CLASS DEFINITION
# DVRequant panel. Allows configuration and execution of the dvrequant
# script.
#
# ===================================================================
class DVRequantPanel(wx.Panel):
    # ==========================================================
    #
    # Internal functions and event handlers
    #
    # ==========================================================

    # ==========================================================
    # Initialize DVRequantPanel
    # ==========================================================
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.txtHeading = HeadingText(self, wx.ID_ANY, "Disc requantization")

        self.strPossDevices = []
        self.strPossDevices.append("/dev/dvd")
        self.strPossDevices.append("/dev/dvdrw")
        # DVD Device combo box
        self.lblDVDDevice = wx.StaticText(self, wx.ID_ANY, "DVD Device:")
        self.cboDVDDevice = wx.ComboBox(self, wx.ID_ANY, "/dev/dvd", wx.DefaultPosition,
            wx.DefaultSize, self.strPossDevices)
        self.strPossLanguages = []
        self.strPossLanguages.append("en")
        self.strPossLanguages.append("es")
        # Language selector combo box
        self.lblLanguage = wx.StaticText(self, wx.ID_ANY, "Language audio to use:")
        self.cboLanguage = wx.ComboBox(self, wx.ID_ANY, "en", wx.DefaultPosition,
            wx.DefaultSize, self.strPossLanguages)

        # Sizer to hold device and language combo boxes
        self.sizChoices = wx.FlexGridSizer(2, 2, 0, 0)
        self.sizChoices.AddMany([ (self.lblDVDDevice, 0, wx.EXPAND | wx.ALL, 8),
                                   (self.cboDVDDevice, 0, wx.EXPAND | wx.ALL, 8),
                                   (self.lblLanguage, 0, wx.EXPAND | wx.ALL, 8),
                                   (self.cboLanguage, 0, wx.EXPAND | wx.ALL, 8) ])

        # Storage location text box
        self.txtStorage = wx.TextCtrl(self, wx.ID_ANY, "/tmp")

        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizChoices, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.txtStorage, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

# ===================================================================
# End DVRequantPanel
# ===================================================================


# ###################################################################
# ###################################################################
#
#
#                             FRAMES
#
#
# ###################################################################
# ###################################################################


# ===================================================================
#
# CLASS DEFINITION
# Main tovid GUI frame. Contains and manages all sub-panels.
#
# ===================================================================
class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id , title, wx.DefaultPosition,
            (800, 600), wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Global configuration
        self.curConfig = Config()

        self.dirname = os.getcwd()

        # Menu bar
        self.menubar = wx.MenuBar()
        
        # File menu
        self.menuFile = wx.Menu()
        #self.menuFile.Append(ID_MENU_FILE_PREFS, "&Preferences",
        #    "Configuration settings for tovid GUI")
        #self.menuFile.AppendSeparator()
        self.menuFile.Append(ID_MENU_FILE_OPEN, "&Open project",
                "Open an existing TDL text file (EXPERIMENTAL)")
        self.menuFile.Append(ID_MENU_FILE_SAVE, "&Save project",
                "Save this project as a TDL text file (EXPERIMENTAL)")
        self.menuFile.AppendSeparator()
        self.menuFile.Append(ID_MENU_FILE_EXIT, "E&xit",
                "Exit tovid GUI")
        
        # Help menu
        self.menuHelp = wx.Menu()
        self.menuHelp.Append(ID_MENU_HELP_ABOUT, "&About",
            "Information about this program")

        # View menu
        self.menuView = wx.Menu()
        # Toggle options
        self.menuViewShowGuide = wx.MenuItem(self.menuView, ID_MENU_VIEW_SHOWGUIDE,
            "Show &guide", "Show/hide the tovid guide panel", wx.ITEM_CHECK)
        self.menuViewShowTooltips = wx.MenuItem(self.menuView,
            ID_MENU_VIEW_SHOWTOOLTIPS,
            "Show &tooltips", "Show/hide tooltips in the GUI", wx.ITEM_CHECK)
        # Add items to View menu
        self.menuView.AppendItem(self.menuViewShowGuide)
        self.menuView.AppendItem(self.menuViewShowTooltips)
        self.menuViewShowGuide.Check(False)
        self.menuViewShowTooltips.Check(True)

        #self.menuLang = wx.Menu()
        #self.menuLang.Append(ID_MENU_LANG_EN, "&English")
        #self.menuLang.Append(ID_MENU_LANG_DE, "&Deutsch")
        # Append language menu as a submenu of View
        #self.menuView.AppendMenu(ID_MENU_LANG, "Language", self.menuLang)

        
        # Menu events
        #wx.EVT_MENU(self, ID_MENU_FILE_PREFS, self.OnFilePrefs)
        wx.EVT_MENU(self, ID_MENU_FILE_SAVE, self.OnFileSave)
        wx.EVT_MENU(self, ID_MENU_FILE_OPEN, self.OnFileOpen)
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_MENU_VIEW_SHOWGUIDE, self.OnShowGuide)
        wx.EVT_MENU(self, ID_MENU_VIEW_SHOWTOOLTIPS, self.OnShowTooltips)
        wx.EVT_MENU(self, ID_MENU_HELP_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_MENU_LANG_EN, self.OnLang)
        wx.EVT_MENU(self, ID_MENU_LANG_DE, self.OnLang)

        # Build menubar
        self.menubar.Append(self.menuFile, "&File")
        self.menubar.Append(self.menuView, "&View")
        self.menubar.Append(self.menuHelp, "&Help")
        self.SetMenuBar(self.menubar)

        # Toolbar
        #self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL)
        #self.toolbar.AddControl(wx.ContextHelpButton(self.toolbar))
        #self.toolbar.Realize()

        # Statusbar
        self.curConfig.statusBar = self.CreateStatusBar();
        self.Show(True)

        # Guide panel
        self.panGuide = GuidePanel(self, wx.ID_ANY)
        self.panGuide.Hide()
        # Store guide panel reference in global config
        self.curConfig.panGuide = self.panGuide
        
        # Task panels. AuthorFiles is currently the only working task.
        self.panAuthorFiles = AuthorFilesTaskPanel(self, wx.ID_ANY)

        # Task sizer. Holds current 3-step task
        self.sizTask = wx.BoxSizer(wx.VERTICAL)
        self.sizTask.Add(self.panAuthorFiles, 1, wx.EXPAND)

        # Main sizer. Holds task (layout, encoding) panel and Guide panel
        self.sizMain = wx.BoxSizer(wx.HORIZONTAL)
        #self.sizMain.Add(self.panGuide, 2, wx.EXPAND | wx.ALL, 8)
        #self.sizMain.Add(wx.StaticLine(self, wx.ID_ANY, style = wx.LI_VERTICAL),
        #    0, wx.EXPAND)
        self.sizMain.Add(self.sizTask, 5, wx.EXPAND)
        self.SetSizer(self.sizMain)


    def OnFileSave(self, evt):
        """Save the current project to a TDL file."""
        outFileDialog = wx.FileDialog(self, _("Select a save location"),
            self.dirname, "", "*.tdl", wx.SAVE)
        if outFileDialog.ShowModal() == wx.ID_OK:
            # Remember current directory
            self.dirname = outFileDialog.GetDirectory()
            # Open a file for writing
            outFile = open(outFileDialog.GetPath(), 'w')
            
            elements = self.panAuthorFiles.GetElements()
            for element in elements:
                outFile.write(element.tdl_string())

            outFile.close()
    

    def OnFileOpen(self, evt):
        inFileDialog = wx.FileDialog(self, _("Choose a TDL file to open"),
            self.dirname, "", "*.tdl", wx.OPEN)
        if inFileDialog.ShowModal() == wx.ID_OK:
            self.dirname = inFileDialog.GetDirectory()
            proj = Project.Project()
            proj.load_file(inFileDialog.GetPath())
            self.panAuthorFiles.SetElements(proj.topitems)

        inFileDialog.Destroy()

        
    def OnExit(self, evt):
        """Exit the GUI and close all windows."""
        self.Close(True)


    def OnShowGuide(self, evt):
        """Show or hide the guide panel."""
        if evt.IsChecked():
            self.sizMain.Prepend(self.panGuide, 2, wx.EXPAND | wx.ALL, 8)
            self.panGuide.Show()
            self.sizMain.Layout()
        else:
            self.sizMain.Remove(0)
            self.panGuide.Hide()
            self.sizMain.Layout()

    def OnShowTooltips(self, evt):
        """Show or hide GUI tooltips."""
        if evt.IsChecked():
            # Enable tooltips globally
            wx.ToolTip_Enable(True)
        else:
            # Disable tooltips globally
            wx.ToolTip_Enable(False)
        
    def OnAbout(self, evt):
        """Display a dialog showing information about tovidgui."""
        strAbout = "You are using the tovid GUI, version 0.24,\n" \
          "part of the tovid video disc authoring suite.\n\n" \
          "For more information and documentation, please\n" \
          "visit the tovid web site:\n\n" \
          "http://tovid.org/"
        dlgAbout = wx.MessageDialog(self, strAbout, "About tovid GUI", wx.OK)
        dlgAbout.ShowModal()


    def OnLang(self, evt):
        """Change GUI to selected language."""
        if evt.GetId() == ID_MENU_LANG_EN:
            self.curConfig.UseLanguage('en')
            
        elif evt.GetId() == ID_MENU_LANG_DE:
            self.curConfig.UseLanguage('de')
        

    # ==========================================================
    # Open preferences window and set configuration
    # ==========================================================
    #def OnFilePrefs(self, evt):
    #    dlgPrefs = PreferencesDialog(self, wx.ID_ANY)
    #    dlgPrefs.ShowModal()
    #    # Set the output directory in the PreEncoding panel
    #    self.panEncoding.SetOutputDirectory(self.curConfig.strOutputDirectory)
          
# ===================================================================
# End MainFrame
# ===================================================================


TovidGUI = wx.PySimpleApp()
#frame = TovidFrame(None, wx.ID_ANY, "tovid GUI")
#frame = MiniEditorFrame(None, wx.ID_ANY, "tovid GUI")
frame = MainFrame(None, wx.ID_ANY, "tovid GUI")
frame.Show(True)
TovidGUI.MainLoop()

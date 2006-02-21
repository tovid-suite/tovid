# ###################################################################
# ###################################################################
#
#
#                           OPTIONS 
#
#
# ###################################################################
# ###################################################################
import os, wx
from libtovid import TDL
from libtovid.gui.constants import *
from libtovid.gui.configs import TovidConfig
from libtovid.gui.util import _

__all__ = ["DiscOptions", "MenuOptions", "SlideOptions", "VideoOptions"]
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
        curConfig = TovidConfig()

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
        curConfig = TovidConfig()
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
        curConfig = TovidConfig()

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
        curConfig = TovidConfig()
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
        curConfig = TovidConfig()

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
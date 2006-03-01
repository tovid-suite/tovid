#! /usr/bin/env python
# options.py

import os
import wx

import libtovid
from libtovid.disc import Disc
from libtovid.menu import Menu
from libtovid.video import Video
from libtovid.gui.constants import *
from libtovid.gui.configs import TovidConfig
from libtovid.gui.util import _

__all__ = ["DiscOptions", "MenuOptions", "SlideOptions", "VideoOptions"]

class DiscOptions:
    """Options that apply to an entire disc"""
    type = ID_DISC
    format = 'dvd'
    tvsys = 'ntsc'
    title = "Untitled disc"

    def __init__(self, format = 'dvd', tvsys = 'ntsc'):
        self.format = format
        self.tvsys = tvsys

    def toElement(self):
        """Convert the current options into a Disc Element and return it."""
        element = Disc(self.title)
        element['tvsys'] = self.tvsys
        element['format'] = self.format

        # Find top menu
        for curItem in self.optionList:
            if curItem.type == ID_MENU:
                if curItem.isTopMenu:
                    element['topmenu'] = curItem.title

        return element

    def fromElement(self, element):
        """Load current options from a Disc Element."""
        print "Loading Disc element:"
        print element.tdl_string()
        self.type = ID_DISC
        self.title = element.name
        self.format = element['format']
        self.tvsys = element['tvsys']
        
    def SetLayout(self, optionList):
        """Set disc layout hierarchy, given a list of VideoOptions,
        MenuOptions, and SlideOptions."""
        self.optionList = optionList

    def GetCommand(self):
        """Return the 'makexml' command for generating XML for this disc."""
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


class MenuOptions:
    """Options related to generating a menu"""
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
    # -align [northwest|north|northeast]
    alignment = 'northwest'
    # Other settings
    titles = []
    colorText = wx.Colour(255, 255, 255)
    colorHi = wx.Colour(255, 255, 0)
    colorSel = wx.Colour(255, 0, 0)
    outPrefix = ""

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
        """Convert the current options into a Menu Element and return it."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Create Menu Element and set relevant options
        element = Menu(self.title)
        element['tvsys'] = self.tvsys
        element['format'] = self.format
        element['align'] = self.alignment
        # Image and audio backgrounds, if any
        if self.background != "":
            element['background'] = self.background
        if self.audio != "":
            element['audio'] = self.audio
        element['textcolor'] = '"#%X%X%X"' % \
            (self.colorText.Red(), self.colorText.Green(), self.colorText.Blue())
        # For DVD, highlight and select colors
        if self.format == 'dvd':
            element['highlightcolor'] = '"#%X%X%X"' % \
                (self.colorHi.Red(), self.colorHi.Green(), self.colorHi.Blue())
            element['selectcolor'] = '"#%X%X%X"' % \
                (self.colorSel.Red(), self.colorSel.Green(), self.colorSel.Blue())
        if self.font.GetFaceName() != "":
            element['font'] = self.font.GetFaceName()
        # Convert self.titles to ordinary strings
        strtitles = []
        for title in self.titles: strtitles.append(str(title))
        element['titles'] = strtitles
        return element

    def fromElement(self, element):
        """Load options from a Video Element."""
        print "Loading Menu element:"
        print element.tdl_string()
        self.type = ID_MENU
        self.tvsys = element['tvsys']
        self.format = element['format']
        self.alignment = element['align']
        self.background = element['background']
        self.audio = element['audio']
        self.titles = element['titles']
        # TODO: Find a good way to parse/assign colors and font

    def GetCommand(self):
        """Return the complete makemenu command to generate this menu."""
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

        strCommand += "-out \"%s/%s\"" % \
                (curConfig.strOutputDirectory, self.outPrefix)
        return strCommand

    def SetDiscFormat(self, format):
        """Make menu compliant with given disc format."""
        self.format = format 

    def SetDiscTVSystem(self, tvsys):
        """Make menu compliant with given disc TV system."""
        self.tvsys = tvsys

    def CopyFrom(self, opts):
        """Copy the given MenuOptions' data into this menu."""
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


class SlideOptions:
    """Options related to generating a slideshow"""
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

    def __init__(self, format = 'dvd', tvsys = 'ntsc',
        files = []):
        self.tvsys = tvsys
        self.format = format 
        self.files = files

    def GetCommand(self):
        """Return the makeslides command to generate this slideshow."""
        strCommand = "makeslides -%s -%s " % \
            (self.tvsys, self.format)

    def SetDiscFormat(self, format):
        """Make slides compliant with given disc format."""
        self.format = format 

    def SetDiscTVSystem(self, tvsys):
        """Make slides compliant with given disc TV system."""
        self.tvsys = tvsys

    def CopyFrom(self, opts):
        """Copy the given options into this object."""
        # If types are different, return
        if self.type != opts.type:
            return
        # Copy opts into self
        self.format = opts.format
        self.tvsys = opts.tvsys

class VideoOptions:
    """Options related to encoding a video"""
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

    def __init__(self, format = 'dvd', tvsys = 'ntsc',
        filename = ""):
        self.SetDiscTVSystem(tvsys)
        self.SetDiscFormat(format)
        self.inFile = filename
        self.title = os.path.basename(filename).replace('_', ' ')
        self.outPrefix = "%s.tovid_encoded" % self.title

    def toElement(self):
        """Convert the current options into a Video Element and return it."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Create Video Element and set relevant options
        element = Video(self.title)
        element['tvsys'] = self.tvsys
        element['format'] = self.format
        element['aspect'] = self.aspect
        element['in'] = self.inFile
        element['out'] = "%s/%s" % (curConfig.strOutputDirectory, self.outPrefix)
        return element

    def fromElement(self, element):
        """Load options from a Video Element."""
        print "Loading Video element:"
        print element.tdl_string()
        self.type = ID_VIDEO
        self.tvsys = element['tvsys']
        self.format = element['format']
        aspect = element['aspect']
        if aspect in [ 'full', 'wide', 'panavision' ]:
            self.aspect = aspect
        elif aspect == '4:3':
            self.aspect = 'full'
        elif aspect == '16:9':
            self.aspect = 'wide'
        elif aspect == '235:100':
            self.aspect = 'panavision'
        self.inFile = element['in']
        self.outPrefix = element['out']


    def GetCommand(self):
        """Return the complete tovid command for converting this video."""
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

    def SetDiscFormat(self, format):
        """Make video compliant with given disc format."""
        if format == 'vcd':
            self.format = format
        elif format == 'svcd':
            self.format = format
        elif format == 'dvd':
            # Don't change existing format unless it's VCD or SVCD
            if self.format in [ 'vcd', 'svcd' ]:
                self.format = 'dvd'

    def SetDiscTVSystem(self, tvsys):
        """Make menu compliant with given disc TV system."""
        self.tvsys = tvsys

    def CopyFrom(self, opts):
        """Copy the given options into this object."""
        # If types are different, return
        if self.type != opts.type:
            return
        # Copy opts into self
        self.format = opts.format
        self.tvsys = opts.tvsys
        self.aspect = opts.aspect
        self.addoptions = opts.addoptions


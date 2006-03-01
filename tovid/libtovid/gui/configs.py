#! /usr/bin/env python
# configs.py

import os
import gettext
import wx

__all__ = ["TovidConfig"]
class TovidConfig:
    """Borg monostate class containing global configuration information"""
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

    def __init__(self):
        self.__dict__ = self.__shared_state
    
        # Initialize class data if needed
        if self.isInitialized == False:
            self.ConfigInit()
    
    def ConfigInit(self):
        """Initialize "static" class data.
        The real initialization function, only called once."""
        self.isInitialized = True
        self.ConfigAvailFonts()
        #self.InitLocales()
    
    def ConfigAvailFonts(self):
        """Determine fonts that are available in both wx.Python and
        ImageMagick."""
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


#! /usr/bin/env python
# options.py

__all__ = ["DiscOptions", "MenuOptions", "SlideOptions", "VideoOptions"]

import os
import wx

import libtovid
from libtovid import Disc
from libtovid import Menu
from libtovid import Video
from libtovid.gui.constants import *
from libtovid.gui.configs import TovidConfig
from libtovid.gui.util import _

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
        """Convert the current options into a Disc and return it."""
        disc = Disc(self.title)
        disc['tvsys'] = self.tvsys
        disc['format'] = self.format

        # Find top menu
        for curItem in self.optionList:
            if curItem.type == ID_MENU:
                if curItem.isTopMenu:
                    disc['topmenu'] = curItem.title

        return disc

    def fromElement(self, disc):
        """Load current options from a Disc."""
        print "Loading Disc:"
        print disc.to_string()
        self.type = ID_DISC
        self.title = disc.name
        self.format = disc['format']
        self.tvsys = disc['tvsys']
        
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
        strCommand += "-out \"%s/%s\"" % \
                   (curConfig.strOutputDirectory, self.outPrefix)
        return strCommand

    def DiscNameOK(self, panel):
        """"Ensure there are no problems with the disc name"""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Use output filename based on disc title
        self.outPrefix = self.title.replace(' ', '_')

        # Save output filename in global Config
        discName = "%s/%s.xml" % (curConfig.strOutputDirectory, self.outPrefix) 
        
	#If specified, check whether it exists
	if os.path.exists(discName) == True:
            #If exists, check whether it is a file or directory
	    if os.path.isfile(discName) == True:
                msgDiscFileExistsDlg = wx.MessageDialog(panel, \
	            "A file needs to be created based on the disc name.\n" \
	            "But, this file (based on the disc name) already exists.\n"\
	            "The file is: %s\n\n" \
                    "Do you want to continue?\n"
	            "This will overwrite this existing file." % (discName),
                    "Existing Disc Name File",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
                response = msgDiscFileExistsDlg.ShowModal()
                msgDiscFileExistsDlg.Destroy()
                if response != wx.ID_YES:
                    return False
            else:   
                msgDiscFolderExistsDlg = wx.MessageDialog(panel, \
	            "A file needs to be created based on the disc name.\n" \
	            "But, a directory with the same name already exists.\n" \
	            "This directory is: %s\n\n" \
	            "Please either rename/remove the directory or " \
                    "change the disc name!" % (discName),
                    "Existing Directory",
                    wx.OK | wx.ICON_ERROR)
                msgDiscFolderExistsDlg.ShowModal()
                msgDiscFolderExistsDlg.Destroy()
                return False   

        #ICheck whether contains problematic characters
        if discName.find("'") > -1 or discName.find("\"") > -1 or discName.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout makemenu do aswell.
            msgDiscNameErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n"\
                "and $ signs may cause problems when in the disc name.\n" \
                "The disc name is: %s\n\n" \
                "Do you want to return to rename the disc?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (self.title),
                "Problematic character in Disc Name",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgDiscNameErrorDlg.ShowModal()
            msgDiscNameErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        #If get this far, file is OK
        return True

    def RelevantFilesAreOK(self, panel):
        """Check the disc options for errors detectable before encoding"""
	if self.DiscNameOK(panel) == False:
            return False
        return True


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
        """Convert the current options into a Menu and return it."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Create Menu Element and set relevant options
        menu = Menu(self.title)
        menu['tvsys'] = self.tvsys
        menu['format'] = self.format
        menu['align'] = self.alignment
        # Image and audio backgrounds, if any
        if self.background != "":
            menu['background'] = self.background
        if self.audio != "":
            menu['audio'] = self.audio
        menu['textcolor'] = '"#%X%X%X"' % \
            (self.colorText.Red(), self.colorText.Green(), self.colorText.Blue())
        # For DVD, highlight and select colors
        if self.format == 'dvd':
            menu['highlightcolor'] = '"#%X%X%X"' % \
                (self.colorHi.Red(), self.colorHi.Green(), self.colorHi.Blue())
            menu['selectcolor'] = '"#%X%X%X"' % \
                (self.colorSel.Red(), self.colorSel.Green(), self.colorSel.Blue())
        if self.font.GetFaceName() != "":
            menu['font'] = self.font.GetFaceName()
        # Convert self.titles to ordinary strings
        strtitles = []
        for title in self.titles: strtitles.append(str(title))
        menu['titles'] = strtitles
        return menu

    def fromElement(self, menu):
        """Load options from a Menu."""
        print "Loading Menu:"
        print element.to_string()
        self.type = ID_MENU
        self.tvsys = menu['tvsys']
        self.format = menu['format']
        self.alignment = menu['align']
        self.background = menu['background']
        self.audio = menu['audio']
        self.titles = menu['titles']
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
            wx_FontName = self.font.GetFaceName()
            IM_FontName = curConfig.wx_IM_FontMap[wx_FontName] 
            strCommand += "-font \"%s\" " % IM_FontName

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

    def AudioFileOK(self, panel):
        """Check for any errors associated with the audio file"""
        #First check if Audio File is specified
        audioFile = self.audio
        if audioFile == "":
            return True
        
        #If specified, check whether it exists
        if os.path.isfile(audioFile) == False:
            msgAudioFileMissingDlg = wx.MessageDialog(panel, \
                    "A menu has an audio file that does not appear to exist.\n" \
                    "The file is: %s\n\n" \
                    "Please choose another audio file." % (audioFile),
                    "Missing Audio File",
                    wx.OK | wx.ICON_ERROR)
            msgAudioFileMissingDlg.ShowModal()
            msgAudioFileMissingDlg.Destroy()
            return False

        #If exists, check whether contains problematic characters
        if audioFile.find("'") > -1 or audioFile.find("\"") > -1 or audioFile.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgAudioErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems in files associated with menus.\n" \
                "One audio file contains at least one of these characters.\n"
                "This audio file is: %s\n\n" \
                "Do you want to return to rename / choose another audio file?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (audioFile),
                "Problematic character in Audio File",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgAudioErrorDlg.ShowModal()
            msgAudioErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        #If get this far, file is OK
        return True

    def ImageFileOK(self, panel):
        """Check for any errors associated with the image file"""
        #First check if Image File is specified
        imageFile = self.background
        if imageFile == "":
            return True
        
        #If specified, check whether it exists
        if os.path.isfile(imageFile) == False:
            msgImageFileMissingDlg = wx.MessageDialog(panel, \
                    "A menu has an image file that does not appear to exist.\n" \
                    "The file is: %s\n\n" \
                    "Please choose another image file." % (imageFile),
                    "Missing Image File",
                    wx.OK | wx.ICON_ERROR)
            msgImageFileMissingDlg.ShowModal()
            msgImageFileMissingDlg.Destroy()
            return False

        #If exists, check whether contains problematic characters
        if imageFile.find("'") > -1 or imageFile.find("\"") > -1 or imageFile.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgImageErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems in files associated with menus.\n" \
                "One image file contains at least one of these characters.\n"
                "This image file is: %s\n\n" \
                "Do you want to return to rename / choose another image file?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (imageFile),
                "Problematic character in Image File",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgImageErrorDlg.ShowModal()
            msgImageErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        #If get this far, file is OK
        return True

    def OutputFileOK(self, panel):
        """Check for any errors associated with the output file"""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        #First check if Image File is specified
        outputFile = "%s/%s.mpg" % (curConfig.strOutputDirectory, self.outPrefix)
        
	#If specified, check whether it exists
        if os.path.exists(outputFile) == True:
            #If exists, check whether it is a file or directory
            if os.path.isfile(outputFile) == True:
                msgOutputFileMissingDlg = wx.MessageDialog(panel, \
                    "A file with the same name as a menu output file already exists.\n" \
                    "This file is: %s\n\n" \
                    "Do you want to continue?\n"
                    "This will overwrite this existing file." % (outputFile),
                    "Existing Menu Output File",
                    wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
                response = msgOutputFileMissingDlg.ShowModal()
                msgOutputFileMissingDlg.Destroy()
                if response != wx.ID_YES:
                    return False   
            else:   
                msgOutputFolderExistsDlg = wx.MessageDialog(panel, \
                    "A file needs to be created based on a menu name.\n" \
                    "But, a directory with the same name already exists.\n" \
                    "This directory is: %s\n\n" \
                    "Please either rename/remove the directory or " \
                    "change the menu name!" % (outputFile),
                    "Existing Directory",
                    wx.OK | wx.ICON_ERROR)
                msgOutputFolderExistsDlg.ShowModal()
                msgOutputFolderExistsDlg.Destroy()
                return False   


        #Check whether output file contains problematic characters
        if outputFile.find("'") > -1 or outputFile.find("\"") > -1 or outputFile.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgMenuNameErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems in the name of menus.\n" \
                "One menu name contains at least one of these characters.\n"
                "This menu name is: %s\n\n" \
                "Do you want to return to rename this menu?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (outputFile),
                "Problematic character in Menu Name",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgMenuNameErrorDlg.ShowModal()
            msgMenuNameErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        #If get this far, file is OK
        return True

    def RelevantFilesAreOK(self, panel):
        """Check the menu options for any errors detectable before encoding"""
        if self.AudioFileOK(panel) == False:
            return False
        if self.ImageFileOK(panel) == False:
            return False
        if self.OutputFileOK(panel) == False:
            return False
        return True


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

    def RelevantFilesAreOK(self, panel):
        """Check the slide options for any errors detectable before encoding"""
        return True

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
        """Convert the current options into a Video and return it."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Create Video and set relevant options
        video = Video(self.title)
        video['tvsys'] = self.tvsys
        video['format'] = self.format
        video['aspect'] = self.aspect
        video['in'] = self.inFile
        video['out'] = "%s/%s" % (curConfig.strOutputDirectory, self.outPrefix)
        return video

    def fromElement(self, video):
        """Load options from a Video."""
        print "Loading Video:"
        print video.to_string()
        self.type = ID_VIDEO
        self.tvsys = video['tvsys']
        self.format = video['format']
        aspect = video['aspect']
        if aspect in [ 'full', 'wide', 'panavision' ]:
            self.aspect = aspect
        elif aspect == '4:3':
            self.aspect = 'full'
        elif aspect == '16:9':
            self.aspect = 'wide'
        elif aspect == '235:100':
            self.aspect = 'panavision'
        self.inFile = video['in']
        self.outPrefix = video['out']


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
        if self.addoptions:
            strCommand += "%s " % self.addoptions

        strCommand += "-in \"%s\" " % self.inFile
        strCommand += "-out \"%s/%s\" " % (curConfig.strOutputDirectory, self.outPrefix)
        strCommand += "-from-gui"
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


    def VideoFileOK(self, panel):
        """Check the video options for any errors detectable before encoding"""
        #First check if Video File is specified
        videoFile = self.inFile
        
        #Check whether it exists
        if os.path.isfile(videoFile) == False:
            msgVideoFileMissingDlg = wx.MessageDialog(panel, \
                    "A Video does not appear to exist.\n" \
                    "The file is: %s\n\n" \
                    "Please choose another video file." % (videoFile),
                    "Missing Video File",
                    wx.OK | wx.ICON_ERROR)
            msgVideoFileMissingDlg.ShowModal()
            msgVideoFileMissingDlg.Destroy()
            return False

        #If exists, check whether contains problematic characters
        if videoFile.find("'") > -1 or \
           videoFile.find("\"") > -1 or \
           videoFile.find("$") > -1 :

            #If so, give option of going back or trying anyway
            msgVideoErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems in the file name of videos.\n" \
                "One video file contains at least one of these characters.\n"
                "This video file is: %s\n\n" \
                "Do you want to return and rename / choose another video file?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (videoFile),
                "Problematic character in Video File",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgVideoErrorDlg.ShowModal()
            msgVideoErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        return True

    def VideoOutputOK(self, panel):
        """Check the video output for any errors detectable before encoding"""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        videoOutput = "%s/%s.mpg" % (curConfig.strOutputDirectory, self.outPrefix)

        #Check whether it is none null (as this gives an error)
        if self.outPrefix == "":
            msgDiscFileExistsDlg = wx.MessageDialog(panel, \
                    "Please enter a valid name (i.e. not empty) for each Video.", 
                    "Missing Video Name",
                    wx.OK | wx.ICON_ERROR)
            msgDiscFileExistsDlg.ShowModal()
            msgDiscFileExistsDlg.Destroy()
            return False

        #Check whether output already exists
        #If specified, check whether it exists
        if os.path.exists(videoOutput) == True:
            #If exists, check whether it is a file or directory
            if os.path.isfile(videoOutput) == True:
                msgVideoOutputExistsErrorDlg = wx.MessageDialog(panel, \
                    "This program converts the video files into the correct format,\n" \
                    "and saves these resultant files with names based on the entered values.\n\n" \
                    "One of these output files already exists.\n" \
                    "This output file is: %s\n\n" \
                    "Do you want to overwrite this file?" % (videoOutput),
                    "Problematic character in Video Output Filename",
                    wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
                response = msgVideoOutputExistsErrorDlg.ShowModal()
                msgVideoOutputExistsErrorDlg.Destroy()
       
                if response != wx.ID_YES:
                    return False   
            else:   
                msgVideoOutputFolderExistsDlg = wx.MessageDialog(panel, \
                    "A file needs to be created based on the video name.\n" \
                    "But, a directory with the same name already exists.\n" \
                    "This directory is: %s\n\n" \
                    "Please either rename/remove the directory or " \
                    "change the menu name!" % (videoOutput),
                    "Existing Directory",
                    wx.OK | wx.ICON_ERROR)
                msgVideoOutputFolderExistsDlg.ShowModal()
                msgVideoOutputFolderExistsDlg.Destroy()
                return False   

        #Check whether the output file contains problematic characters
        if videoOutput.find("'") > -1 or videoOutput.find("\"") > -1 or videoOutput.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgVideoOutputErrorDlg = wx.MessageDialog(panel, \
                "This program converts the video files into the correct format,\n" \
                "and saves these resultant files with names based on the entered values.\n\n" \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems when in these filenames.\n" \
                "One output file contains at least one of these characters.\n"
                "This output video file is: %s\n\n" \
                "Do you want to return to modify these values?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (videoOutput),
                "Problematic character in Video Output Filename",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgVideoOutputErrorDlg.ShowModal()
            msgVideoOutputErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        return True

    def RelevantFilesAreOK(self, panel):
        """Check the video options for any errors detectable before encoding"""
        if self.VideoFileOK(panel) == False:
            return False
        if self.VideoOutputOK(panel) == False:
            return False
        return True

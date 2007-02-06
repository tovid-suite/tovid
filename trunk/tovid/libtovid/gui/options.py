#! /usr/bin/env python
# options.py

__all__ = [\
    "DiscOptions",
    "MenuOptions",
    "SlideOptions",
    "VideoOptions",
    "GroupOptions"]

import os
import wx

import libtovid
from libtovid import Group
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

    def SetLayout(self, optionList):
        """Set disc layout hierarchy, given a list of VideoOptions,
        MenuOptions, and SlideOptions."""
        self.optionList = optionList

    def GetCommand(self):
        """Return the 'makexml' command for generating XML for this disc."""
        # Tricky part of this is know when to add -endgroup!
        amInAGroup = False
        videosInGroup = 0

        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        strCommand = "makexml -quiet -overwrite -%s " % self.format

        for curItem in self.optionList:
            # Prefix -topmenu or -menu if necessary
            if curItem.type == ID_MENU:
                if curItem.isTopMenu:
                    strCommand += "-topmenu "
                else:
                    strCommand += "-menu "
            elif curItem.type == ID_GROUP:
                strCommand += "-group "
                amInAGroup = True
                videosInGroup = curItem.groupMemberCount

            if curItem.type != ID_GROUP:
                # Output path and encoded filename for all but groups
                strCommand += "\"%s/%s.mpg\" " % \
                    (curConfig.strOutputDirectory, curItem.outPrefix)
            if amInAGroup == True:
                #Need to work out whether need to endgroup
                if videosInGroup == 0:
                    # Cannot be in a group anymore
                    strCommand += "-endgroup "
                    amInAGroup = False
                else:
                    videosInGroup = videosInGroup - 1
                
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
        if discName.find("'") > -1 or discName.find("\"") > -1 \
           or discName.find("$") > -1 or discName.find("&") > -1:

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout makemenu do aswell.
            msgDiscNameErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n"\
                "$ signs and & signs may cause problems when in the disc name.\n" \
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

    def OutputDirectoryExists(self, panel):
        """"Ensure there are no problems with the output directory name"""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        outputDirectory = "%s" % (curConfig.strOutputDirectory)
 
        #If specified, check whether it exists
        if os.path.exists(outputDirectory) == True:
            #If exists, check whether it is a file or directory
            if os.path.isfile(outputDirectory) == True:
                msgOutputDirectoryIsAFileDlg = wx.MessageDialog(panel, \
                    "The output directory cannot be created as a file\n" \
                    "already exists in that location.\n"\
                    "The file is: %s\n\n" \
                    "Please change the output directory." % (outputDirectory),
                    "Output Directory Error",
                    wx.OK | wx.ICON_ERROR)
                msgOutputDirectoryIsAFileDlg.ShowModal()
                msgOutputDirectoryIsAFileDlg.Destroy()
                return False
        else:   
            msgOutputDirectoryDoesNotExistDlg = wx.MessageDialog(panel, \
                "The specified output directory does not exist.\n" \
                "The specified output directory is: %s\n\n" \
                "Please either create the directory or change the name." \
                % (outputDirectory),
                "Output Directory Does Not Exist",
                    wx.OK | wx.ICON_ERROR)
            msgOutputDirectoryDoesNotExistDlg.ShowModal()
            msgOutputDirectoryDoesNotExistDlg.Destroy()
            return False   

        #Check whether contains problematic characters
        if outputDirectory.find("'") > -1 or outputDirectory.find("\"") > -1 or outputDirectory.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout makemenu do aswell.
            msgOutputDirectoryErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n"\
                "and $ signs may cause problems when in the output directory name.\n" \
                "The output directory name is: %s\n\n" \
                "Do you want to return to rename the output directory?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (outputDirectory),
                "Problematic Character in Output Directory",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgOutputDirectoryErrorDlg.ShowModal()
            msgOutputDirectoryErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        #If get this far, file is OK
        return True

    def RelevantFilesAreOK(self, panel):
        """Check the disc options for errors detectable before encoding"""
        if self.OutputDirectoryExists(panel) == False:
            return False
        if self.DiscNameOK(panel) == False:
            return False
        return True

class GroupOptions:
    """Options related to encoding a group"""
    # Type of item being encoded (menu, video, group or slides)
    type = ID_GROUP
    # Title of the group itself
    title = "Untitled group"
    # Additional command-line options
#    addoptions = ""
    # Duration is unknown
    #duration = -1 
    inFile = ""
    outPrefix = ""
    groupMemberCount = 0

    def __init__(self, filename = ""):
        self.inFile = filename
        self.title = os.path.basename(filename).replace('_', ' ')
        self.outPrefix = "%s.tovid_encoded" % self.title

    def toElement(self):
        """Convert the current options into a Group and return it."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()
        # Create Group and set relevant options
        group = Group(self.title)
        group['tvsys'] = self.tvsys
        group['format'] = self.format
        group['aspect'] = self.aspect
        group['in'] = self.inFile
        group['group'] = "%s/%s" % (curConfig.strOutputDirectory, self.outPrefix)
        return group

    def fromElement(self, group):
        """Load options from a Group."""
        print "Loading Group:"
        print group.to_string()
        self.type = ID_GROUP
        self.inFile = group['in']
        self.outPrefix = group['out']


    def GetCommand(self):
        """Return the complete tovid command for converting this group."""
        #No command is required for groups
        return ""

    def SetDiscFormat(self, format):
        """Make group compliant with given disc format."""
        #Placeholder        

    def SetDiscTVSystem(self, tvsys):
        """Make group compliant with given disc TV system."""
        #Placeholder

    def CopyFrom(self, opts):
        """Copy the given options into this object."""
        # If types are different, return
        if self.type != opts.type:
            return

    def GroupOutputOK(self, panel):
        """Check the group output for any errors detectable before encoding"""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        groupOutput = "%s" % (self.outPrefix)

        #Check whether it is none null (as this gives an error)
        if self.outPrefix == "":
            msgDiscFileExistsDlg = wx.MessageDialog(panel, \
                    "Please enter a valid name (i.e. not empty) for each Group.", 
                    "Missing Group Name",
                    wx.OK | wx.ICON_ERROR)
            msgDiscFileExistsDlg.ShowModal()
            msgDiscFileExistsDlg.Destroy()
            return False

        #Check whether the output file contains problematic characters
        if groupOutput.find("'") > -1 or groupOutput.find("\"") > -1 or groupOutput.find("$") > -1 :

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgGroupOutputErrorDlg = wx.MessageDialog(panel, \
                "This program converts the group files into the correct format,\n" \
                "and saves these resultant files with names based on the entered values.\n\n" \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems when in these filenames.\n" \
                "One output file contains at least one of these characters.\n"
                "This output group file is: %s\n\n" \
                "Do you want to return to modify these values?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (groupOutput),
                "Problematic character in Group Output Filename",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgGroupOutputErrorDlg.ShowModal()
            msgGroupOutputErrorDlg.Destroy()
       
            if response != wx.ID_NO:
                return False   
        return True

    def RelevantFilesAreOK(self, panel):
        """Check the group options for any errors detectable before encoding"""
        if self.GroupOutputOK(panel) == False:
            return False
        if self.groupMemberCount == 0:
            msgEmptyGroupDlg = wx.MessageDialog(panel, \
                    "Each Group must have at least one video.", 
                    "Empty Group",
                    wx.OK | wx.ICON_ERROR)
            msgEmptyGroupDlg.ShowModal()
            msgEmptyGroupDlg.Destroy()
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
    # -menu-title
    menutitle = ""
    titlefontsize = "32"
    # -background FILE
    background = ""
    # -audio FILE
    audio = ""
    # -length NUM
    menulength = ""
    # -align [northwest|north|northeast]
    alignment = 'northwest'
    # Menu text settings
    fontsize = "24"
    fillType = "Color"
    fillColor1 = "rgb(255,255,255)"      # For fill, gradient, fractals
    fillColor2 = "rgb(255,255,255)"      # For gradient and fractals
    color1 = wx.Colour(255, 255, 255)    # Stores dialog box color
    color2 = wx.Colour(255, 255, 255)    # Stores dialog box color
    textStrokeColor = "rgb(0,0,0)"       # For text outline
    colorStroke = wx.Colour(0, 0, 0)     # Stores dialog box color
    textStrokeWidth = "1"
    pattern = "bricks"
    # DVD button settings
    button = ">"
    highlightColor = "rgb(255,255,0)"              # For highlight color
    selectColor = "rgb(255,0,0)"                   # for selection color
    colorHi = wx.Colour(255, 255, 0)               # Stores dialog box color
    colorSel = wx.Colour(255, 0, 0)                # Stores dialog box color
    buttonOutlineColor = "rgb(140,140,140)"        # For button outline
    colorButtonOutline = wx.Colour(140, 140, 140)  # Stores dialog box color
    # Other settings
    titles = []
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
        self.buttonFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, 
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Default")

    def GetCommand(self):
        """Return the complete makemenu command to generate this menu."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        strCommand = "makemenu -noask -quiet -overwrite "
        # Append format and tvsys
        strCommand += "-%s -%s " % (self.tvsys, self.format)
        # Append alignment
        strCommand += "-align %s " % self.alignment

        # Image and audio backgrounds, if any
        if self.menutitle != "":
            strCommand += "-menu-title \"%s\" " % self.menutitle
            strCommand += "-menu-title-fontsize %s " % self.titlefontsize
        if self.background != "":
            strCommand += "-background \"%s\" " % self.background
        if self.audio != "":
            strCommand += "-audio \"%s\" " % self.audio
        if self.menulength != "":
            strCommand += "-length %s " % self.menulength

        # Append font and size
        if self.font.GetFaceName() != "":
            wx_FontName = self.font.GetFaceName()
            IM_FontName = curConfig.wx_IM_FontMap[wx_FontName] 
            strCommand += "-font \"%s\" " % IM_FontName
        strCommand += "-fontsize %s " % self.fontsize

        # Express text fill and outline in ways makemenu will understand
        # Text outline:
        fontDecoration = "-stroke %s" % (self.textStrokeColor)
        fontDecoration += " -strokewidth %s" % (self.textStrokeWidth)
        # Text fill:
        # solid is simple:
        if self.fillType == "Color":
            strCommand += "-textcolor \"%s\" " % self.fillColor1
        # fractals, gradients, and patterns get put in -fontdeco
        elif self.fillType == "Fractal":
            fontDecoration += " -tile fractal:%s-%s" % \
                (self.fillColor1, self.fillColor2)
        elif self.fillType == "Gradient":
            fontDecoration += " -tile gradient:%s-%s" % \
                (self.fillColor1, self.fillColor2)
        elif self.fillType == "Pattern":
            fontDecoration += " -tile pattern:%s" % (self.pattern)
        else:
            pass
        
        strCommand += "-fontdeco '%s' " % fontDecoration

        # For DVD, add button options
        if self.format == 'dvd':
            # Font
            if self.buttonFont.GetFaceName() != "":
                wx_FontName = self.buttonFont.GetFaceName()
                IM_FontName = curConfig.wx_IM_FontMap[wx_FontName] 
                # Don't need button font for 'play' or 'movie', take the rest
                if self.button != "play" and self.button != "movie":
                    strCommand += "-button-font \"%s\" " % IM_FontName
            # Shape
            strCommand += "-button \"%s\" " % self.button
            # colors
            strCommand += "-highlightcolor \"%s\" " % self.highlightColor
            strCommand += "-selectcolor \"%s\" " % self.selectColor
            strCommand += "-button-outline \"%s\" " % self.buttonOutlineColor

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
        self.font = opts.font
        self.alignment = opts.alignment
        self.menutitle = opts.menutitle
        self.titlefontsize = opts.titlefontsize
        self.menulength = opts.menulength
        self.fontsize = opts.fontsize
        self.fillType = opts.fillType
        self.fillColor1 = opts.fillColor1
        self.color1 = opts.color1
        self.fillColor2 = opts.fillColor2
        self.color2 = opts.color2
        self.textStrokeColor = opts.textStrokeColor
        self.colorStroke = opts.colorStroke
        self.textStrokeWidth = opts.textStrokeWidth
        self.buttonFont = opts.buttonFont
        self.highlightColor = opts.highlightColor
        self.colorHi = opts.colorHi
        self.selectColor = opts.selectColor
        self.colorSel = opts.colorSel
        self.button = opts.button
        self.buttonOutlineColor = opts.buttonOutlineColor
        self.colorButtonOutline = opts.colorButtonOutline

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

    def HeaderOK(self, panel):
        """Check for any errors associated with the menu header"""
        menuTitle = "%s" % (self.menutitle)

        #Check whether menu title contains problematic characters
        if menuTitle.find("'") > -1 or menuTitle.find("\"") > -1 \
           or menuTitle.find("$") > -1:

            #If so, give option of going back or trying anyway
            msgMenuTitleErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "and $ signs may cause problems in the menu headers.\n" \
                "One menu header contains at least one of these characters.\n"
                "This menu header is: %s\n\n" \
                "Do you want to return to rename this menu header?\n" \
                "NB, continuing (i.e. No) is very unlikely to work!" % (menuTitle),
                "Problematic character in Menu Title",
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR)
            response = msgMenuTitleErrorDlg.ShowModal()
            msgMenuTitleErrorDlg.Destroy()
       
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
        if outputFile.find("'") > -1 or outputFile.find("\"") > -1 \
           or outputFile.find("$") > -1 or outputFile.find("&") > -1:

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgMenuNameErrorDlg = wx.MessageDialog(panel, \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "& signs and $ signs may cause problems in the name of menus.\n" \
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
        if self.HeaderOK(panel) == False:
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
    # string 1 to 10
    quality = "8"
    # mpeg2enc or ffmpeg
    encodingMethod = "mpeg2enc"
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

    def GetCommand(self):
        """Return the complete tovid command for converting this video."""
        # Get global configuration (for output directory)
        curConfig = TovidConfig()

        # Always overwrite. Use better solution in future?
        strCommand = "tovid -quiet -overwrite "
        # Append tvsys, format, and aspect ratio
        strCommand += "-%s -%s -%s " % \
            (self.tvsys, self.format, self.aspect)

        # Append quality
        strCommand += "-quality %s " % self.quality

        # Append encoding method if not default
        if self.encodingMethod == "ffmpeg":
            strCommand += "-ffmpeg "
 
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
        self.quality = opts.quality
        self.encodingMethod = opts.encodingMethod
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
        if videoOutput.find("'") > -1 or videoOutput.find("\"") > -1 \
           or videoOutput.find("$") > -1 or videoOutput.find("&") > -1:

            #If so, give option of going back or trying anyway
            #NB, it is not just Python files that need fixing. 
            #Many lines throughout e.g. makemenu do aswell.
            msgVideoOutputErrorDlg = wx.MessageDialog(panel, \
                "This program converts the video files into the correct format,\n" \
                "and saves these resultant files with names based on the entered values.\n\n" \
                "For technical reasons, currently apostrophes, double quotes\n" \
                "& and $ signs may cause problems when in these filenames.\n" \
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

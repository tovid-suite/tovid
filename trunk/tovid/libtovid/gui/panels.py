#! /usr/bin/env python
# panels.py

import os
import wx

import libtovid
from libtovid.gui.configs import TovidConfig
from libtovid.gui.constants import *
from libtovid.gui.controls import BoldToggleButton, FlexTreeCtrl, HeadingText
from libtovid.gui.dialogs import FontChooserDialog
from libtovid.gui.icons import MenuIcon, SlideIcon, VideoIcon, DiscIcon
from libtovid.gui.options import DiscOptions, MenuOptions, VideoOptions
from libtovid.gui import util
from libtovid.gui.util import _, VER_GetFirstChild, VideoStatSeeker, element_to_options
from libtovid.disc import Disc
from libtovid.menu import Menu
from libtovid.video import Video

__all__ = ["AuthorFilesTaskPanel", "DiscLayoutPanel", "EncodingPanel", "BurnDiscPanel",\
           "CommandOutputPanel", "DiscPanel", "GuidePanel", "HidablePanel", "MenuPanel",\
           "VideoPanel", "PlaylistTabPanel", "MenuTabPanel", "ThumbnailTabPanel", "DebugTabPanel"]

class AuthorFilesTaskPanel(wx.Panel):
    """A three-step interface for authoring video files to disc.
    Uses DiscLayoutPanel, EncodingPanel, and BurnDiscPanel."""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Global configuration
        self.curConfig = TovidConfig()

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


    def EncodeOK(self, ok):
        """Indicate whether it's okay to begin encoding."""
        if ok == True:
            self.btnEncode.Enable(True)
        else:
            self.btnEncode.Enable(False)

    def BurnOK(self, ok):
        """Indicate whether it's okay to begin burning."""
        if ok:
            self.btnBurn.Enable(True)
        else:
            self.btnBurn.Enable(False)

    def OnLayout(self, evt):
        """Display controls for doing disc layout."""
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

    def OnEncode(self, evt):
        """Display controls for encoding."""
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

    def OnBurn(self, evt):
        """Display controls for burning the disc."""
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


class BurnDiscPanel(wx.Panel):
    """A panel of controls for burning a disc"""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Keep track of parent
        self.parent = parent
        self.device = "/dev/dvdrw"
        self.doAuthor = True
        self.doBurn = False

        self.txtHeading = HeadingText(self, wx.ID_ANY, "Author and burn")

        self.chkDoAuthor = wx.CheckBox(self, wx.ID_ANY, "Author disc structure")
        self.chkDoBurn = wx.CheckBox(self, wx.ID_ANY, "Burn disc")
        self.chkDoAuthor.SetToolTipString("Create the disc filesystem " \
                "hierarchy using dvdauthor")
        self.chkDoBurn.SetToolTipString("Burn a disc in the selected " \
                "device")
        self.chkDoAuthor.SetValue(self.doAuthor)
        self.chkDoBurn.SetValue(self.doBurn)
        wx.EVT_CHECKBOX(self, self.chkDoAuthor.GetId(), self.OnDoAuthor)
        wx.EVT_CHECKBOX(self, self.chkDoBurn.GetId(), self.OnDoBurn)

        self.lblDiscDevice = wx.StaticText(self, wx.ID_ANY, "Burn to device:")
        self.txtDiscDevice = wx.TextCtrl(self, wx.ID_ANY, self.device)
        wx.EVT_TEXT(self, self.txtDiscDevice.GetId(), self.OnSetDevice)

        # Sizer to hold burning controls
        self.sizBurn = wx.FlexGridSizer(4, 2, 8, 8)
        self.sizBurn.Add((2, 2))
        self.sizBurn.Add(self.chkDoAuthor, 0, wx.EXPAND)
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
    
    def OnDoAuthor(self, evt):
        self.doAuthor = evt.Checked()
        
    def OnDoBurn(self, evt):
        self.doBurn = evt.Checked()

    def OnSetDevice(self, evt):
        """Use the selected device."""
        self.device = self.txtDiscDevice.GetValue()

    def OnStart(self, evt):
        """Begin authoring and burning the disc."""
        # Get global config (for XML filename and format)
        curConfig = TovidConfig()

        msgWarning = wx.MessageDialog(self,
            "Disc burning is still experimental in this release,\n" \
            "and might not work. Please report any bugs you encounter!",
            "Experimental feature", wx.ICON_INFORMATION | wx.OK)
        msgWarning.ShowModal()

        makedvdOptions = ""

        # Construct authoring/imaging/burning options
        if self.doAuthor:
            makedvdOptions += "-author "
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

    def ProcessingDone(self, errorOccurred):
        """Signify that disc burning is done."""
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
            if self.doBurn:
                strSuccess = "Done burning the disc."
            else:
                strSuccess = "Done authoring the disc."
            msgSuccess = wx.MessageDialog(self, strSuccess, "Success!",
                wx.ICON_INFORMATION | wx.OK)
            msgSuccess.ShowModal()



# ===================================================================
class CommandOutputPanel(wx.Panel):
    """A panel for executing and logging command-lines.

    To use CommandOutputPanel, the parent should implement a function
    ProcessingDone(bool errStatus), which is called by CommandOutputPanel to
    notify the parent that the panel is done running commands.  Presumably, the
    commands that are executing must finish before proceeding with another
    operation, so this function is used to let the parent know that the commands
    are done executing."""
    # Current (running) process
    process = None
    # Has an error occurred in any of the commands?
    errorOccurred = False
    # Command queue (starts out empty)
    strCmdQueue = []
    strCurCmd = ""
      
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

    def __del__(self):
        """Detach any running process."""
        # Detach any running process
        if self.process:
            self.process.Detach()

    def OnFontSize(self, evt):
        """Change log window font size."""
        newFontSize = int(self.cboFontSize.GetValue())
        self.txtOut.SetFont(wx.Font(newFontSize, wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        #self.txtOut.Refresh()

    def OnSaveLog(self, evt):
        """Save output log to a file."""
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

    def OnIdleTime(self, evt):
        """Execute commands in the queue and print output to the log."""
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
            
    def StartNextProcess(self):
        """Start the next process in the queue."""
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
            self.lblQueue.SetLabel("Commands left to run: %d" % \
                    len(self.strCmdQueue))

    def OnProcessEnded(self, evt):
        """Print any remaining output, and destroy the process."""
        # Get process exit status
        curExitStatus = evt.GetExitCode()
        # Print message to console if there was an error
        if curExitStatus != 0:
            print "ERROR:"
            print "The following command returned an exit status of %d:" % \
                    curExitStatus
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
            try:
                self.txtOut.AppendText(unicode(stream.read())
            except UnicodeDecodeError:
                pass
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

    def Clear(self):
        """Clear out the command queue."""
        self.strCmdQueue = []
        self.txtCurCmd.SetValue("")
        self.txtOut.Clear()
        self.txtOut.AppendText("The following commands will be run:\n"
            "=========================================\n")
        self.lblQueue.SetLabel("Commands left to run: 0")
        self.process = None

    def Execute(self, command):
        """Put the given command-line string into the queue for execution."""
        self.strCmdQueue.append(command)
        self.txtOut.AppendText("%s\n------------------------\n" % command)
        # Update the queue size indicator
        self.lblQueue.SetLabel("Commands left to run: %d" % len(self.strCmdQueue))
        self.sizCurCmd.Layout()

    def Start(self):
        """Start processing all commands in queue."""
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

    def Stop(self):
        """Stop processing and return current process to queue."""
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


class DiscLayoutPanel(wx.Panel):
    """Panel for adding menus and videos to a disc, with configurations"""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.numMenus = 0   # Layout begins with no menus
        self.discFormat = 'dvd'
        self.discTVSystem = 'ntsc'
        self.parent = parent
        self.curConfig = TovidConfig()
        self.lastUsedPath = ""

        # Set up controls and sizers
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
        self.discTree = FlexTreeCtrl(self, wx.ID_ANY, style = wx.TR_SINGLE \
                | wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | wx.SUNKEN_BORDER)
        # Icons to use in the tree
        iconSize = (16, 16)
        self.listIcons = wx.ImageList(iconSize[0], iconSize[1])
        self.idxIconMenu = self.listIcons.Add(MenuIcon())
        self.idxIconSlide = self.listIcons.Add(SlideIcon())
        self.idxIconVideo = self.listIcons.Add(VideoIcon())
        self.idxIconDisc = self.listIcons.Add(DiscIcon())
        self.discTree.SetImageList(self.listIcons)

        # Root of disc. Non-deletable.
        self.rootItem = self.discTree.AddRoot("Untitled disc", self.idxIconDisc)
        self.discTree.SetPyData(self.rootItem, DiscOptions())
        self.discTree.SetToolTipString("Navigation layout of the disc. "
            "Use the buttons below to add elements. Click on the title of "
            "an element to edit it.")
        wx.EVT_TREE_SEL_CHANGED(self.discTree, self.discTree.GetId(), \
                self.OnTreeSelChanged)
        wx.EVT_TREE_END_LABEL_EDIT(self.discTree, self.discTree.GetId(), \
                self.OnTreeItemEdit)
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

    def OnTreeSelChanged(self, evt):
        """Update controls when a tree selection changes."""
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

    def OnTreeItemEdit(self, evt):
        """Update controls when a tree item's title is edited."""
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

    def OnAddMenu(self, evt):
        """Append a menu to the disc."""
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
                MenuOptions(self.discFormat, self.discTVSystem, \
                        "Main menu", True))
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

    def OnAddVideos(self, evt):
        """Add videos to the disc, under the currently-selected menu."""
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

    def OnAddSlides(self, evt):
        """Add slides to the disc structure. Not enabled yet."""
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

    def OnCuritemUp(self, evt):
        """Move the currently-selected item up in the tree."""
        self.discTree.MoveItemUp()
        # Refresh the parent
        curParent = self.discTree.GetItemParent(self.discTree.GetSelection())
        self.RefreshItem(curParent)

    def OnCuritemDown(self, evt):
        """Move the currently-selected item down in the tree."""
        self.discTree.MoveItemDown()
        # Refresh the parent
        curParent = self.discTree.GetItemParent(self.discTree.GetSelection())
        self.RefreshItem(curParent)

    def OnRemoveCuritem(self, evt):
        """Remove the currently-selected item and its descendants from the
        tree."""
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


    def SetOptions(self, options):
        """Set the encoding options associated with the current item."""
        self.discTree.SetPyData(self.discTree.GetSelection(), options)

    def GetOptions(self):
        """Get the encoding options associated with the current item."""
        return self.discTree.GetPyData(self.discTree.GetSelection())

    def SetDiscFormat(self, format):
        """Set the disc format (DVD, VCD, SVCD)."""
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

    def SetDiscTVSystem(self, tvsys):
        """Set the disc TV system (NTSC, PAL)."""
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

    def RefreshItem(self, curItem):
        """Refresh the given tree item and make sure it is up-to-date.
        Should be called for an item after its children have changed."""
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
        
    def UseForAllItems(self, opts):
        """Use the given options for all videos/menus/slides."""
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
            print elem.to_string()
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
        if isinstance(element, Disc):
            return self.idxIconDisc
        elif isinstance(element, Menu):
            return self.idxIconMenu
        else:
            return self.idxIconVideo


class DiscPanel(wx.Panel):
    """Panel for choosing disc format (DVD/VCD/SVCD, PAL/NTSC)"""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        
        # Global configuration
        self.curConfig = TovidConfig()

        # Disc options associated with this panel
        self.curOptions = DiscOptions()
        self.parent = parent

        # Disc format selector
        self.lblDiscFormat = wx.StaticText(self, wx.ID_ANY, \
                "Choose what kind of video disc you want to make:")
        strFormats = ["VCD: Low-quality, up to about one hour of video",
            "SVCD: Medium quality, 30 to 70 minutes of video",
            "DVD: Range of quality, from 1 to 8 hours of video"]

        
        self.rbFormat = wx.RadioBox(self, wx.ID_ANY, "Disc format", \
                wx.DefaultPosition, wx.DefaultSize, strFormats, 1, \
                wx.RA_SPECIFY_COLS)
        self.rbFormat.SetToolTipString("Select what disc format you want to use."
            " For VCD and SVCD, you can use a normal CD-recordable drive. For"
            " DVD, you need a DVD-recordable drive.")
        self.rbFormat.SetSelection(ID_FMT_DVD)
        wx.EVT_RADIOBOX(self, self.rbFormat.GetId(), self.OnFormat)
        
        # Disc TV system selector
        strTVSystems = ["NTSC: Used in the Americas and East Asia",
                        "NTSC Film: Same as NTSC, with a film frame rate",
                        "PAL: Used in most of Europe, Asia, and Africa"]
        self.rbTVSystem = wx.RadioBox(self, wx.ID_ANY, "TV format", \
                wx.DefaultPosition, wx.DefaultSize, strTVSystems, 1, \
                wx.RA_SPECIFY_COLS)
        self.rbTVSystem.SetToolTipString("Select NTSC or PAL, depending " \
                "on what kind of TV you want to play the disc on.")
        self.rbTVSystem.SetSelection(ID_TVSYS_NTSC)
        wx.EVT_RADIOBOX(self, self.rbTVSystem.GetId(), self.OnTVSystem)

        # Disc options heading
        self.txtHeading = HeadingText(self, wx.ID_ANY, "Disc")

        # Output directory
        self.lblOutputDirectory = wx.StaticText(self, wx.ID_ANY, \
                "Output directory:")
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
        self.sizDirs.AddMany([\
            (self.lblOutputDirectory, 0, wx.ALIGN_RIGHT | wx.ALL, 8),
            (self.txtOutputDirectory, 1, wx.EXPAND | wx.ALL, 8),
            (self.btnBrowseOutputDirectory, 0, wx.ALL, 8)
            ])

        # Sizer to hold controls
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.lblDiscFormat, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.rbFormat, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.rbTVSystem, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizDirs, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    def OnFormat(self, evt):
        """Set disc format according to radiobox."""
        self.curOptions.format = util.ID_to_text('format', evt.GetInt())
        # Tell parent to adjust disc format
        self.parent.SetDiscFormat(self.curOptions.format)

    def OnTVSystem(self, evt):
        """Set disc TV system according to radiobox."""
        self.curOptions.tvsys = util.ID_to_text('tvsys', evt.GetInt())
        # Tell parent to adjust disc TVSystem
        self.parent.SetDiscTVSystem(self.curOptions.tvsys)

    def OnBrowseOutputDirectory(self, evt):
        """Browse for output directory."""
        workDirDlg = wx.DirDialog(self, "Select a directory for output",
            style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        workDirDlg.SetPath(self.txtOutputDirectory.GetValue())
        # Show the dialog
        if workDirDlg.ShowModal() == wx.ID_OK:
            self.curConfig.strOutputDirectory = workDirDlg.GetPath()
            self.txtOutputDirectory.SetValue(self.curConfig.strOutputDirectory)
            workDirDlg.Destroy()

    def OnEditOutputDirectory(self, evt):
        """Update Config with newly-entered output directory."""
        self.curConfig.strOutputDirectory = self.txtOutputDirectory.GetValue()

    def SetOptions(self, discOpts):
        """Set control values based on the provided DiscOptions"""
        self.curOptions = discOpts
        self.rbFormat.SetSelection(util.text_to_ID(self.curOptions.format))
        self.rbTVSystem.SetSelection(util.text_to_ID(self.curOptions.tvsys))
        self.txtHeading.SetLabel("Disc options: %s" % self.curOptions.title)


class EncodingPanel(wx.Panel):
    """Encoding setup panel. Allow selection of output directory, display
    estimated encoding and final size requirements, controls and log window for
    running all encoding commands.
    """
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.parent = parent
        self.curConfig = TovidConfig()
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

    def OnBrowseOutDir(self, evt):
        """Browse for output directory."""
        outDirDlg = wx.DirDialog(self, "Select a directory for output",
            style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if outDirDlg.ShowModal() == wx.ID_OK:
            self.curConfig.strOutputDirectory = outDirDlg.GetPath()
            self.txtOutDir.SetValue(self.curConfig.strOutputDirectory)
            outDirDlg.Destroy()

    def OnStartStop(self, evt):
        """Start/suspend/resume encoding."""
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

    def SetCommands(self, commands):
        """Set command-list to be executed from DiscLayoutPanel."""
        for cmd in commands:
            self.panCmdList.Execute(cmd)

    def SetOutputDirectory(self, outDir):
        """Set the output directory to use."""
        self.txtOutDir.SetValue(outDir)
          
    def ProcessingDone(self, errorOccurred):
        """Signify that processing (video encoding) is done."""
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


class GuidePanel(wx.Panel):
    """A panel showing live context-sensitive help."""

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

    def InitTaskText(self):
        """Initialize task-based guide text for all tasks."""
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

    def SetTask(self, curTask = ID_TASK_GETTING_STARTED):
        """Show the appropriate guide text for the given task."""
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


class HidablePanel(wx.Panel):
    """A panel that can be hidden from view.

    The panel may be horizontal or vertical, and contains show/hide controls
    along with one additional window or sizer, added via the Add() method.

    To use HidablePanel, first declare a HidablePanel object. Then, create the
    wx.Window object that will go into the HidablePanel, passing the
    HidablePanel as its parent. Add the HidablePanel to the desired location
    (inside another sizer). Finally, call SetParent with the containing sizer as
    the argument, to let the HidablePanel know what sizer contains it.
    """

    def __init__(self, parent, id, orientation = wx.VERTICAL):
        """Initialize hidable panel. orientation is wx.VERTICAL or
        wx.HORIZONTAL. A vertical panel has the hide controls at the top and
        extends downwards; a horizontal one has controls on the left and extends
        rightwards.
        """
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

    def SetContent(self, newContent):
        """Set the window/sizer that the panel will contain."""
        self.content = newContent
        self.sizMain.Add(self.content, 1, wx.EXPAND)
        self.sizMain.SetItemMinSize(self.content, 200, 200)
        self.sizMain.Layout()
    
    def SetParent(self, parent):
        """Set the parent sizer (the sizer that holds the HidablePanel)."""
        self.sizParent = parent

    def ShowHide(self, evt):
        """Show/hide the main part of the sizer based on state of
        btnShowHide."""
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


class MenuPanel(wx.Panel):
    """A panel showing controls appropriate to generating a menu"""
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.curOptions = MenuOptions()
        self.curColorData = wx.ColourData()
        self.parent = parent
        self.sboxBG = wx.StaticBox(self, wx.ID_ANY, "Menu background options")
        self.sizBG = wx.StaticBoxSizer(self.sboxBG, wx.VERTICAL)

        # Background image/audio selection controls
        # Image
        self.lblBGImage = wx.StaticText(self, wx.ID_ANY, "Image:")
        self.txtBGImage = wx.TextCtrl(self, wx.ID_ANY)
        self.txtBGImage.SetToolTipString(\
            "Type the full name of the image file you want to use in the" \
            " background of the menu, or use the browse button.")
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

        # Menu font and alignment controls
        self.lblFontFace = wx.StaticText(self, wx.ID_ANY, "Font:")
        self.btnFontChooserDialog = wx.Button(self, wx.ID_ANY, "Default")
        self.btnFontChooserDialog.SetToolTipString(\
                "Select a font to use for the menu text")
        wx.EVT_BUTTON(self, self.btnFontChooserDialog.GetId(), \
                self.OnFontSelection)
        strAlignments = ['Left', 'Center', 'Right']
        self.rbAlignment = wx.RadioBox(self, wx.ID_ANY, "Alignment", \
                wx.DefaultPosition, wx.DefaultSize, strAlignments, 1, \
                wx.RA_SPECIFY_ROWS)
        self.rbAlignment.SetToolTipString(\
                "Select how the menu text should be aligned")
        wx.EVT_RADIOBOX(self, self.rbAlignment.GetId(), self.OnAlignment)
        self.sizFontFace = wx.BoxSizer(wx.HORIZONTAL)
        self.sizFontFace.AddMany([\
                (self.lblFontFace, 0, wx.ALL, 4),
                (self.btnFontChooserDialog, 1, wx.EXPAND | wx.ALL, 4) ])

        # Menu text color controls
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

        # List of titles in this menu
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
    
        # Put menu font/color controls in a static box
        self.sboxTextFormat = wx.StaticBox(self, wx.ID_ANY, "Menu text format")
        self.sizTextFormat = wx.StaticBoxSizer(self.sboxTextFormat, wx.VERTICAL)
        self.sizTextFormat.AddMany([\
                (self.sizFontFace, 0, wx.EXPAND | wx.ALL, 8),
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
            " including background image, audio, text alignment, text color" \
            " and font, to all menus on the disc.")
        wx.EVT_BUTTON(self, self.btnUseForAll.GetId(), self.OnUseForAll)

        # Main sizer to hold all controls
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
        inFileDlg = wx.FileDialog(self, "Select an image file", "", "", \
                "*.*", wx.OPEN)
        if inFileDlg.ShowModal() == wx.ID_OK:
            self.txtBGImage.SetValue(inFileDlg.GetPath())
            inFileDlg.Destroy()

    def OnBrowseBGAudio(self, evt):
        """Show a file dialog and set the background audio."""
        inFileDlg = wx.FileDialog(self, "Select an audio file", "", "", \
                "*.*", wx.OPEN)
        if inFileDlg.ShowModal() == wx.ID_OK:
            self.txtBGAudio.SetValue(inFileDlg.GetPath())
            inFileDlg.Destroy()

    def OnAlignment(self, evt):
        """Set the text alignment according to the radiobox setting."""
        self.curOptions.alignment = util.ID_to_text('alignment', evt.GetInt())

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
      
    def SetOptions(self, menuOpts):
        """Set control values based on the provided MenuOptions."""
        self.curOptions = menuOpts

        self.txtHeading.SetLabel("Menu options: %s" % self.curOptions.title)
        self.txtBGImage.SetValue(self.curOptions.background)
        self.txtBGAudio.SetValue(self.curOptions.audio or '')
        self.rbAlignment.SetSelection(util.text_to_ID(self.curOptions.alignment))
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


class VideoPanel(wx.Panel):
    """A panel showing controls appropriate to encoding a video."""
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Class data
        self.curOptions = VideoOptions()
        self.parent = parent

        # File information display
        self.lblInFile = wx.StaticText(self, wx.ID_ANY, "Filename:")
        self.txtInFile = wx.StaticText(self, wx.ID_ANY, "None")

        # Statix box and sizer to hold file info
        self.sboxFileInfo = wx.StaticBox(self, wx.ID_ANY, "Video information")
        self.sizFileInfo = wx.StaticBoxSizer(self.sboxFileInfo, wx.HORIZONTAL)
        self.sizFileInfo.Add(self.lblInFile, 0, wx.EXPAND | wx.ALL, 6)
        self.sizFileInfo.Add(self.txtInFile, 1, wx.EXPAND | wx.ALL, 6)
        
        # Radio buttons
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
                
        # Direct-entry CLI option box
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

        # Add controls to main vertical sizer
        self.sizMain = wx.BoxSizer(wx.VERTICAL)
        self.sizMain.Add(self.txtHeading, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizFileInfo, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.sizEncOpts, 1, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnPreview, 0, wx.EXPAND | wx.ALL, 8)
        self.sizMain.Add(self.btnUseForAll, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(self.sizMain)

    def OnFormat(self, evt):
        """Set appropriate format based on radio button selection."""
        # Convert integer value to text representation
        # (e.g., ID_FMT_DVD to 'dvd')
        self.curOptions.format = util.ID_to_text('format', evt.GetInt())

    def OnAspect(self, evt):
        """Set aspect ratio based on radio button selection."""
        self.curOptions.aspect = util.ID_to_text('aspect', evt.GetInt())

    def OnCLIOptions(self, evt):
        """Update custom CLI options when the user edits the textbox."""
        self.curOptions.addoptions = self.txtCLIOptions.GetValue()

    def OnUseForAll(self, evt):
        """Use the current video settings for all videos on disc."""
        countItems = self.parent.UseForAllItems(self.curOptions)
        # Display acknowledgement
        dlgAck = wx.MessageDialog(self,
            "The current video settings were copied to\n"
            "%d other videos on the disc." % countItems,
            "Settings copied", wx.OK | wx.ICON_INFORMATION)
        dlgAck.ShowModal()

    def OnPreview(self, evt):
        """Preview the video in mplayer."""
        strCommand = "gmplayer \"%s\"" % self.curOptions.inFile
        wx.Execute(strCommand, wx.EXEC_SYNC)


    def SetOptions(self, videoOpts):
        """Set control values based on the provided VideoOptions."""
        self.curOptions = videoOpts

        self.txtHeading.SetLabel("Video options: %s" % self.curOptions.title)
        self.txtInFile.SetLabel(self.curOptions.inFile)
        self.rbResolution.SetSelection(util.text_to_ID(self.curOptions.format))
        self.rbAspect.SetSelection(util.text_to_ID(self.curOptions.aspect))
        self.txtCLIOptions.SetValue(self.curOptions.addoptions)

    def GetOptions(self):
        """Return the currently-set encoding options."""
        return self.curOptions

    def SetDiscFormat(self, format):
        """Enable/disable controls to suit DVD, VCD, or SVCD-compliance."""
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
    
    def SetDiscTVSystem(self, format):
        """Set NTSC or PAL, and show appropriate controls."""
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

# ************************************************************************
#
# todiscgui panels
#
# Note: Each panel stores a subset of todisc command-line options in a
# todisc_opts dictionary; GUI events should set dictionary items appropriately.
#
# todisc options that do not have GUI controls yet:
#
#    -debug
#    -keepfiles
#    -submenu-length
#    -loop
#    -menu-fontsize
#    -tovidopts
#    -thumb-fontsize
#
# ************************************************************************

class PlaylistTabPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        # todisc options controlled by this panel, and default values
        # (as a dictionary of option/value pairs)
        self.todisc_opts = {\
            'dvd': True,
            'svcd': False,
            'ntsc': True,
            'pal': False,
            'submenus': False,
            'chapters': 6,
            'files': [],
            'titles': [],
            'submenu-titles': [],
            'submenu-audio': None,
            'out': ''
            }
        self.szVideoInfoBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Video Information"))
        self.szTitleInfoBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Title"))
        self.szAudioInfoBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Audio"))
        self.discFormat = \
            wx.RadioBox(self, wx.ID_ANY, _("Disc Format"),
                        choices=[_("DVD"), _("SVCD")],
                        majorDimension=1,
                        style=wx.RA_SPECIFY_ROWS)
        self.videoFormat = \
            wx.RadioBox(self, wx.ID_ANY, _("Video Format"),
                        choices=[_("NTSC"), _("PAL")],
                        majorDimension=1,
                        style=wx.RA_SPECIFY_ROWS)

        # Submenus checkbox
        self.submenus = wx.CheckBox(self, wx.ID_ANY, _("Create submenus?"))
        wx.EVT_CHECKBOX(self, self.submenus.GetId(), self.submenus_OnClick)

        self.lblChapters = \
            wx.StaticText(self, wx.ID_ANY, _("Chapters per video:"))
        self.chapters = \
            wx.SpinCtrl(self, wx.ID_ANY, "6", min=0, max=100,
                        style=wx.TE_RIGHT)
        self.files = wx.ListBox(self, wx.ID_ANY, choices=[])

        # Thumb title
        self.lblTitle = \
            wx.StaticText(self, wx.ID_ANY, _("Video Thumb Title:"))
        self.title = wx.TextCtrl(self, wx.ID_ANY, "")
        #wx.EVT_TEXT(self, self.title.GetId(), self.title_OnEdit)

        # Submenu title
        self.lblSubmenuTitle = \
            wx.StaticText(self, wx.ID_ANY, _("Video Submenu Title:"))
        self.submenu_title = wx.TextCtrl(self, wx.ID_ANY, "")
        #wx.EVT_TEXT(self, self.submenu_title.GetId(), self.submenu_title_OnEdit)

        # Submenu audio
        self.lblSubmenuAudio = \
            wx.StaticText(self, wx.ID_ANY, _("Audio for Submenu:"))
        self.submenu_audio = wx.TextCtrl(self, wx.ID_ANY, "")
        #wx.EVT_TEXT(self, self.submenu_audio.GetId(), self.submenu_audio_OnEdit)
        self.subaudio_all = \
            wx.CheckBox(self, wx.ID_ANY, _("Use for all submenu audio?"))
        #wx.EVT_BUTTON(self, self.subaudio_all.GetId(), self.subaudio_all_OnClick)
        self.btnAudio = wx.Button(self, wx.ID_ANY, _("Browse"))
        wx.EVT_BUTTON(self, self.btnAudio.GetId(), self.btnAudio_OnClick)

        # "Add Video" button
        self.btnAddVideo = wx.Button(self, wx.ID_ANY, _("Add Video"))
        wx.EVT_BUTTON(self, self.btnAddVideo.GetId(), self.btnAddVideo_OnClick)
        # "Remove Video" button
        self.btnRemoveVideo = wx.Button(self, wx.ID_ANY, _("Remove Video"))
        wx.EVT_BUTTON(self, self.btnRemoveVideo.GetId(), \
                      self.btnRemoveVideo_OnClick)

        self.static_line_4 = wx.StaticLine(self, wx.ID_ANY)
        self.lblOut = wx.StaticText(self, wx.ID_ANY, _("Output"))

        # Output file textbox and browse button
        self.out = wx.TextCtrl(self, wx.ID_ANY, "")
        self.btnOut = wx.Button(self, wx.ID_ANY, _("Browse"))
        wx.EVT_BUTTON(self, self.btnOut.GetId(), self.btnOut_OnClick)
        
        self.discFormat.SetSelection(0)
        self.videoFormat.SetSelection(0)
        self.files.SetMinSize((414, 225))
        self.btnAddVideo.SetDefault()
        self.btnRemoveVideo.Disable()
        self.DisableSubmenus()
        
        szFormats = wx.FlexGridSizer(1, 2, 0, 5)
        szFormats.Add(self.discFormat, 0,
                      wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szFormats.Add(self.videoFormat, 0,
                      wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szFormats.AddGrowableCol(0)
        szFormats.AddGrowableCol(1)
        
        szChapters = wx.GridSizer(1, 2, 0, 0)
        szChapters.Add(self.lblChapters, 0,
                       wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szChapters.Add(self.chapters, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        
        szTitleInfo = wx.FlexGridSizer(2, 2, 5, 5)
        szTitleInfo.Add(self.lblTitle, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTitleInfo.Add(self.title, 0, wx.EXPAND, 0)
        szTitleInfo.Add(self.lblSubmenuTitle, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTitleInfo.Add(self.submenu_title, 0, wx.EXPAND, 0)
        szTitleInfo.AddGrowableCol(1)
        
        szTitleInfoBox = \
            wx.StaticBoxSizer(self.szTitleInfoBox_staticbox, wx.VERTICAL)
        szTitleInfoBox.Add(szTitleInfo, 1, wx.EXPAND, 0)
        
        szAudioInfo = wx.FlexGridSizer(1, 2, 5, 5)
        szAudioInfo.Add(self.lblSubmenuAudio, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioInfo.Add(self.submenu_audio, 0, wx.EXPAND, 0)
        szAudioInfo.AddGrowableCol(1)
        
        szAudioOptions = wx.GridSizer(1, 2, 0, 5)
        szAudioOptions.Add(self.subaudio_all, 0,
                           wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioOptions.Add(self.btnAudio, 0,
                           wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szAudioInfoBox = \
            wx.StaticBoxSizer(self.szAudioInfoBox_staticbox, wx.VERTICAL)
        szAudioInfoBox.Add(szAudioInfo, 1, wx.EXPAND, 0)
        szAudioInfoBox.Add(szAudioOptions, 1, wx.EXPAND, 0)
        
        szVideoInfo = wx.FlexGridSizer(3, 1, 5, 5)
        szVideoInfo.Add(self.files, 0, wx.EXPAND, 0)
        szVideoInfo.Add(szTitleInfoBox, 1, wx.EXPAND, 0)
        szVideoInfo.Add(szAudioInfoBox, 1, wx.EXPAND, 0)
        szVideoInfo.AddGrowableRow(0)
        szVideoInfo.AddGrowableCol(0)
        
        szVideoInfoBox = \
            wx.StaticBoxSizer(self.szVideoInfoBox_staticbox, wx.VERTICAL)
        szVideoInfoBox.Add(szVideoInfo, 0, wx.EXPAND, 0)
        
        szVidButtons = wx.BoxSizer(wx.HORIZONTAL)
        szVidButtons.Add(self.btnAddVideo, 1, wx.ADJUST_MINSIZE, 0)
        szVidButtons.Add(self.btnRemoveVideo, 1, wx.ADJUST_MINSIZE, 0)
        
        szOutput = wx.FlexGridSizer(1, 3, 0, 7)
        szOutput.Add(self.lblOut, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szOutput.Add(self.out, 0, wx.EXPAND, 0)
        szOutput.Add(self.btnOut, 0, wx.ADJUST_MINSIZE, 0)
        szOutput.AddGrowableCol(1)
        
        szPlaylist = wx.FlexGridSizer(7, 1, 7, 0)
        szPlaylist.Add(szFormats, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szPlaylist.Add(self.submenus, 0,
                       wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szPlaylist.Add(szChapters, 1, wx.EXPAND, 0)
        szPlaylist.Add(szVideoInfoBox, 1, wx.EXPAND, 0)
        szPlaylist.Add(szVidButtons, 1, wx.EXPAND, 0)
        szPlaylist.Add(self.static_line_4, 0, wx.EXPAND, 0)
        szPlaylist.Add(szOutput, 1, wx.EXPAND, 0)
        szPlaylist.Fit(self)
        szPlaylist.SetSizeHints(self)
        szPlaylist.AddGrowableRow(3)
        szPlaylist.AddGrowableCol(0)
        
        self.SetAutoLayout(True)
        self.SetSizer(szPlaylist)
        

    def EnableSubmenus(self):
        self.submenu_title.Enable()
        self.submenu_audio.Enable()
        self.subaudio_all.Enable()
        self.btnAudio.Enable()

    def DisableSubmenus(self):
        self.submenu_title.Disable()
        self.submenu_audio.Disable()
        self.subaudio_all.Disable()
        self.btnAudio.Disable()

    def submenus_OnClick(self, evt):
        if (evt.IsChecked()):
            self.EnableSubmenus()
            self.GetParent().GetParent().nbMenus.EnableSubmenus()
            self.todisc_opts['submenus'] = True
        else:
            self.DisableSubmenus()
            self.GetParent().GetParent().nbMenus.DisableSubmenus()
            self.todisc_opts['submenus'] = False

    def btnAddVideo_OnClick(self, evt):
        dlgFile = wx.FileDialog(None)
        if (dlgFile.ShowModal() == wx.ID_OK):
            self.files.Append(dlgFile.GetPath())
            if (not self.btnRemoveVideo.IsEnabled()):
                self.btnRemoveVideo.Enable()

    def btnRemoveVideo_OnClick(self, evt):
        self.files.Delete(self.files.GetSelection())
        if (self.files.GetCount() == 0):
            self.btnRemoveVideo.Disable()

    def btnAudio_OnClick(self, evt):
        dlgFile = wx.FileDialog(None)
        if (dlgFile.ShowModal() == wx.ID_OK):
            self.submenu_audio.SetValue(dlgFile.GetPath())

    def btnOut_OnClick(self, evt):
        dlgFile = wx.DirDialog(None)
        if (dlgFile.ShowModal() == wx.ID_OK):
            self.out.SetValue(dlgFile.GetPath())
            self.tovid_opts['out'] = dlgFile.GetPath()

class MenuTabPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        # todisc options controlled by this panel, and default values
        # (as a dictionary of option/value pairs)
        self.todisc_opts = {\
            'menu-title': "My Video Collection",
            'menu-font': wx.FontData(),
            'title-colour': None,
            'stroke-color': None,
            'menu-fade': None,
            'text-mist': None,
            'text-mist-color': None,
            'text-mist-opacity': None,
            'bgaudio': None,
            'bgimage': None,
            'bgvideo': None,
            'menu-audio-fade': None,
            'submenu-audio-fade': None,
            'static': None,
            'menu-length': None,
            'ani-submenus': None,
            'submenu-title-color': None,
            'submenu-stroke-color': None
            }

        self.szMistOpacity_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Text Mist Opacity"))
        self.szMainMenuBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Main Menu"))
        self.szBackgroundBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Background"))
        self.szAudioFadeBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Audio Fade"))
        self.szMenuAnim_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Menu Animations"))
        self.szSubmenuBox_staticbox = \
            wx.StaticBox(self, wx.ID_ANY, _("Submenus"))
        
        # Main menu title
        self.lblMenuTitle = wx.StaticText(self, wx.ID_ANY, _("Title:"))
        self.menu_title = wx.TextCtrl(self, wx.ID_ANY, "")
        #wx.EVT_TEXT(self, self.menu_title.GetId(), self.menu_title_OnEdit)
        
        self.lblMenuFont = wx.StaticText(self, wx.ID_ANY, _("Title Font:"))
        self.btnMenuFont = wx.Button(self, wx.ID_ANY, _("Default"))
        self.lblTitleColor = wx.StaticText(self, wx.ID_ANY, _("Title Color:"))
        self.btnTitleColor = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.lblStrokeColor = wx.StaticText(self, wx.ID_ANY, _("Stroke Color:"))
        self.btnStrokeColor = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.static_line_3 = wx.StaticLine(self, wx.ID_ANY)
        self.menu_fade = wx.CheckBox(self, wx.ID_ANY, _("Use menu fade?"))
        self.static_line_2 = wx.StaticLine(self, wx.ID_ANY)
        self.text_mist = wx.CheckBox(self, wx.ID_ANY, _("Use text mist?"))
        self.lblTextMistColor = \
            wx.StaticText(self, wx.ID_ANY, _("Text Mist Color:"))
        self.btnTextMistColor = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.opacity = \
            wx.Slider(self, wx.ID_ANY, 100, 0, 100,
                      style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)

        # Background audio
        self.lblBgAudio = wx.StaticText(self, wx.ID_ANY, _("Background Audio"))
        self.bgaudio = wx.TextCtrl(self, wx.ID_ANY, "")
        wx.EVT_TEXT(self, self.bgaudio.GetId(), self.bgaudio_OnEdit)
        self.btnBgAudio = wx.Button(self, wx.ID_ANY, _("Browse"))

        # Background image
        self.lblBgImage = wx.StaticText(self, wx.ID_ANY, _("Background Image"))
        self.bgimage = wx.TextCtrl(self, wx.ID_ANY, "")
        wx.EVT_TEXT(self, self.bgimage.GetId(), self.bgimage_OnEdit)
        self.btnBgImage = wx.Button(self, wx.ID_ANY, _("Browse"))

        # Background video
        self.lblBgVideo = wx.StaticText(self, wx.ID_ANY, _("Background Video"))
        self.bgvideo = wx.TextCtrl(self, wx.ID_ANY, "")
        wx.EVT_TEXT(self, self.bgvideo.GetId(), self.bgvideo_OnEdit)
        self.btnBgVideo = wx.Button(self, wx.ID_ANY, _("Browse"))

        self.lblMenuAudioFade = wx.StaticText(self, wx.ID_ANY, _("Menu:"))
        self.menu_audio_fade = wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100)
        self.lblSubmenuAudioFade = \
            wx.StaticText(self, wx.ID_ANY, _("Submenu:"))
        self.submenu_audio_fade = \
            wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100)
        self.static = wx.CheckBox(self, wx.ID_ANY, _("Animate menus?"))
        self.lblMenuLength = \
            wx.StaticText(self, wx.ID_ANY, _("Menu animation length:"))
        self.menu_length = wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100)
        self.lblLoop = wx.StaticText(self, wx.ID_ANY, _("Menu pause length:"))
        self.loop = wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100)
        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.ani_submenus = wx.CheckBox(self, wx.ID_ANY, _("Animate submenus?"))
        self.lblSubmenuTitleColor = \
            wx.StaticText(self, wx.ID_ANY, _("Title Color:"))
        self.btnSubmenuTitleColor = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.lblSubmenuStrokeColor = \
            wx.StaticText(self, wx.ID_ANY, _("Stroke Color:"))
        self.btnSubmenuStrokeColor = wx.Button(self, wx.ID_ANY, _("Choose"))
        
        self.lblMenuTitle.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblMenuFont.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblTitleColor.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblStrokeColor.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblBgAudio.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblBgImage.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.static.SetValue(1)
        self.lblSubmenuTitleColor.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblSubmenuStrokeColor.SetFont(\
            wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.btnTextMistColor.Disable()
        self.DisableSubmenus()
        
        szMenuTitle = wx.FlexGridSizer(1, 2, 0, 5)
        szMenuTitle.Add(self.lblMenuTitle, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMenuTitle.Add(self.menu_title, 0, wx.EXPAND, 0)
        szMenuTitle.AddGrowableCol(1)
        
        szTitleFont = wx.FlexGridSizer(2, 4, 0, 5)
        szTitleFont.Add(self.lblMenuFont, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnMenuFont, 0, wx.ADJUST_MINSIZE, 0)
#        szTitleFont.Add(self.lblMenuFontSize, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
#        szTitleFont.Add(self.menu_fontsize, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szTitleFont.Add(self.lblTitleColor, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnTitleColor, 0, wx.ADJUST_MINSIZE, 0)
        szTitleFont.Add(self.lblStrokeColor, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnStrokeColor, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTitleFont.AddGrowableCol(1)
        
        szTextMist = wx.FlexGridSizer(1, 3, 0, 5)
        szTextMist.Add(self.text_mist, 0,
                       wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTextMist.Add(self.lblTextMistColor, 0,
                       wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        szTextMist.Add(self.btnTextMistColor, 0, wx.ADJUST_MINSIZE, 0)
        szTextMist.AddGrowableCol(1)
        
        szMistOpacity = \
            wx.StaticBoxSizer(self.szMistOpacity_staticbox, wx.VERTICAL)
        szMistOpacity.Add(self.opacity, 0, wx.EXPAND, 0)
        
        szMainMenuBox = \
            wx.StaticBoxSizer(self.szMainMenuBox_staticbox, wx.VERTICAL)
        szMainMenuBox.Add(szMenuTitle, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(szTitleFont, 1,
                          wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szMainMenuBox.Add(self.static_line_3, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(self.menu_fade, 0,
                          wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMainMenuBox.Add(self.static_line_2, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(szTextMist, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(szMistOpacity, 0, wx.EXPAND, 0)
        
        szBackground = wx.FlexGridSizer(3, 3, 5, 5)
        szBackground.Add(self.lblBgAudio, 0,
                         wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgaudio, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgAudio, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.lblBgImage, 0,
                         wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgimage, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgImage, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.lblBgVideo, 0,
                         wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgvideo, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgVideo, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.AddGrowableCol(1)
        
        szBackgroundBox = \
            wx.StaticBoxSizer(self.szBackgroundBox_staticbox, wx.VERTICAL)
        szBackgroundBox.Add(szBackground, 1, wx.EXPAND, 0)
        
        szAudioFade = wx.FlexGridSizer(1, 4, 0, 5)
        szAudioFade.Add(self.lblMenuAudioFade, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.menu_audio_fade, 0, wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.lblSubmenuAudioFade, 0,
                        wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.submenu_audio_fade, 0, wx.ADJUST_MINSIZE, 0)
        szAudioFade.AddGrowableCol(1)
        
        szAudioFadeBox = \
            wx.StaticBoxSizer(self.szAudioFadeBox_staticbox, wx.HORIZONTAL)
        szAudioFadeBox.Add(szAudioFade, 1, wx.EXPAND, 0)
        
        szMenuLength = wx.FlexGridSizer(1, 2, 0, 0)
        szMenuLength.Add(self.lblMenuLength, 0,
                         wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMenuLength.Add(self.menu_length, 0,
                         wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szMenuLength.AddGrowableCol(0)
        szMenuLength.AddGrowableCol(1)
        
        szLoop = wx.GridSizer(1, 2, 0, 0)
        szLoop.Add(self.lblLoop, 0,
                   wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szLoop.Add(self.loop, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        
        szSubmenus = wx.FlexGridSizer(10, 1, 5, 0)
        szSubmenus.Add(self.static, 0, wx.ADJUST_MINSIZE, 0)
        szSubmenus.Add(szMenuLength, 1, wx.EXPAND, 0)
        szSubmenus.Add(szLoop, 1, wx.EXPAND, 0)
        szSubmenus.Add(self.static_line_1, 0, wx.EXPAND, 0)
        szSubmenus.Add(self.ani_submenus, 0,
                       wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szSubmenus.AddGrowableCol(0)
        
        szMenuAnim = wx.StaticBoxSizer(self.szMenuAnim_staticbox, wx.VERTICAL)
        szMenuAnim.Add(szSubmenus, 1, wx.EXPAND, 0)
        
        szSubmenuColor = wx.FlexGridSizer(1, 4, 0, 7)
        szSubmenuColor.Add(self.lblSubmenuTitleColor, 0,
                           wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szSubmenuColor.Add(self.btnSubmenuTitleColor, 0, wx.ADJUST_MINSIZE, 0)
        szSubmenuColor.Add(self.lblSubmenuStrokeColor, 0,
                           wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szSubmenuColor.Add(self.btnSubmenuStrokeColor, 0, wx.ADJUST_MINSIZE, 0)
        szSubmenuColor.AddGrowableCol(1)
        
        szSubmenuBox = \
            wx.StaticBoxSizer(self.szSubmenuBox_staticbox, wx.HORIZONTAL)
        szSubmenuBox.Add(szSubmenuColor, 1, wx.EXPAND, 0)
        
        szMenus = wx.FlexGridSizer(5, 1, 7, 0)
        szMenus.Add(szMainMenuBox, 1, wx.EXPAND, 0)
        szMenus.Add(szBackgroundBox, 1, wx.EXPAND, 0)
        szMenus.Add(szAudioFadeBox, 1, wx.EXPAND, 0)
        szMenus.Add(szMenuAnim, 1, wx.EXPAND, 0)
        szMenus.Add(szSubmenuBox, 1, wx.EXPAND, 0)
        szMenus.Fit(self)
        szMenus.SetSizeHints(self)
        szMenus.AddGrowableCol(0)
        
        self.SetAutoLayout(True)
        self.SetSizer(szMenus)
        
        wx.EVT_BUTTON(self, self.btnMenuFont.GetId(), self.btnMenuFont_OnClick)
        wx.EVT_BUTTON(self, self.btnTitleColor.GetId(),
                      self.btnTitleColor_OnClick)
        wx.EVT_BUTTON(self, self.btnStrokeColor.GetId(),
                      self.btnStrokeColor_OnClick)
        wx.EVT_CHECKBOX(self, self.text_mist.GetId(), self.text_mist_OnClick)
        wx.EVT_CHECKBOX(self, self.static.GetId(), self.static_OnClick)

    def EnableSubmenus(self):
        self.submenu_audio_fade.Enable()
        self.ani_submenus.Enable()
        self.btnSubmenuTitleColor.Enable()
        self.btnSubmenuStrokeColor.Enable()

    def DisableSubmenus(self):
        self.submenu_audio_fade.Disable()
        self.ani_submenus.Disable()
        self.btnSubmenuTitleColor.Disable()
        self.btnSubmenuStrokeColor.Disable()

    def btnMenuFont_OnClick(self, evt):
        dlgFont = wx.FontDialog(None, wx.FontData())
        if (dlgFont.ShowModal() == wx.ID_OK):
            font = dlgFont.GetFontData().GetChosenFont()
            self.todisc_opts['menu-font'] = font.GetFaceName()
            self.todisc_opts['menu-fontsize'] = font.GetPointSize()
            self.btnMenuFont.SetLabel(font.GetFaceName())

    def btnTitleColor_OnClick(self, evt):
        dlgColour = wx.ColourDialog(None, self.todisc_opts['title-colour'])
        if (dlgColour.ShowModal() == wx.ID_OK):
            self.todisc_opts['title-colour'] = dlgColour.GetColourData()

    def btnStrokeColor_OnClick(self, evt):
        dlgColour = wx.ColourDialog(None)
        if (dlgColour.ShowModal() == wx.ID_OK):
            colour = dlgColour.GetColourData().GetColour()
            self.todisc_opts['stroke-colour'] = colour

    def text_mist_OnClick(self, evt):
        if (evt.IsChecked()):
            self.btnTextMistColor.Enable()
        else:
            self.btnTextMistColor.Disable()

    def static_OnClick(self, evt):
        if (evt.IsChecked()):
            self.menu_length.Enable()
            self.loop.Enable()
        else:
            self.menu_length.Disable()
            self.loop.Disable()
    def bgaudio_OnEdit(self, evt):
        self.todisc_opts['bgaudio'] = self.bgaudio.GetValue()

    def bgimage_OnEdit(self, evt):
        self.todisc_opts['bgimage'] = self.bgimage.GetValue()

    def bgvideo_OnEdit(self, evt):
        self.todisc_opts['bgvideo'] = self.bgvideo.GetValue()
    
class ThumbnailTabPanel(wx.Panel):
    def __init__(self, parent, id):
        self.todisc_opts = {\
            'thumb-shape': None,
            'thumb-font': None,
            'thumb-text-color': None, 
            'thumb-mist-color': None, 
            'blur': None, 
            'opacity': None, 
            'seek': None
            }

        wx.Panel.__init__(self, parent, id)
        self.feather_thumbs = wx.CheckBox(self, wx.ID_ANY, _("Feather thumbnails?"))
        self.szBlur_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Blur"))
        self.szOpacity_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Opacity"))
        self.thumb_shape = wx.RadioBox(self, wx.ID_ANY, _("Feather Shape"), choices=[_("Normal"), _("Oval"), _("Cloud"), _("Egg")], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.lblThumbTitleFont = wx.StaticText(self, wx.ID_ANY, _("Thumb Font:"))
        self.thumb_font = wx.Button(self, wx.ID_ANY, _("Default"))
        self.lblThumbTitleColor = wx.StaticText(self, wx.ID_ANY, _("Thumb Font Color:"))
        self.thumb_text_color = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.lblThumbTitleMistColor = wx.StaticText(self, wx.ID_ANY, _("Thumb Mist Color:"))
        self.thumb_mist_color = wx.Button(self, wx.ID_ANY, _("Choose"))
        self.blur = wx.Slider(self, wx.ID_ANY, 5, 0, 10, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.opacity = wx.Slider(self, wx.ID_ANY, 100, 0, 100, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.lblSeek = wx.StaticText(self, wx.ID_ANY, _("Seconds to seek before generating thumbs:"))
        self.seek = wx.SpinCtrl(self, wx.ID_ANY, "", min=0, max=100, style=wx.TE_RIGHT)
        
        self.thumb_shape.SetSelection(0)
        self.thumb_shape.Disable()
        
        szThumbFont = wx.FlexGridSizer(2, 4, 5, 5)
        szThumbFont.Add(self.lblThumbTitleFont, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_font, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.Add(self.lblThumbTitleColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_text_color, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.Add(self.lblThumbTitleMistColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_mist_color, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.AddGrowableCol(1)
        
        szThumbShape = wx.FlexGridSizer(2, 1, 5, 0)
        szThumbShape.Add(self.thumb_shape, 0, wx.EXPAND, 0)
        szThumbShape.Add(szThumbFont, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szThumbShape.AddGrowableCol(0)
        
        szBlur = wx.StaticBoxSizer(self.szBlur_staticbox, wx.VERTICAL)
        szBlur.Add(self.blur, 0, wx.EXPAND, 0)
        
        szOpacity = wx.StaticBoxSizer(self.szOpacity_staticbox, wx.VERTICAL)
        szOpacity.Add(self.opacity, 0, wx.EXPAND, 0)
        
        szSeek = wx.FlexGridSizer(1, 2, 0, 5)
        szSeek.Add(self.lblSeek, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szSeek.Add(self.seek, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szSeek.AddGrowableCol(0)
        
        szThumbnails = wx.FlexGridSizer(5, 1, 7, 0)
        szThumbnails.Add(self.feather_thumbs, 0, wx.ADJUST_MINSIZE, 0)
        szThumbnails.Add(szThumbShape, 1, wx.EXPAND, 0)
        szThumbnails.Add(szBlur, 0, wx.EXPAND, 0)
        szThumbnails.Add(szOpacity, 0, wx.EXPAND, 0)
        szThumbnails.Add(szSeek, 1, wx.EXPAND, 0)
        szThumbnails.Fit(self)
        szThumbnails.SetSizeHints(self)
        szThumbnails.AddGrowableCol(0)
        
        self.SetAutoLayout(True)
        self.SetSizer(szThumbnails)
        
        wx.EVT_CHECKBOX(self, self.feather_thumbs.GetId(), self.feather_thumbs_OnClick)

    def feather_thumbs_OnClick(self, evt):
        if (evt.IsChecked()):
            self.thumb_shape.Enable()
        else:
            self.thumb_shape.Disable()

class DebugTabPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.szDebugBox_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Debug Flags"))
        self.debug = wx.CheckBox(self, wx.ID_ANY, _("Turn on debug logging?"))
        self.keepfiles = wx.CheckBox(self, wx.ID_ANY, _("Keep files when finished?"))
        
        szDebugBox = wx.StaticBoxSizer(self.szDebugBox_staticbox, wx.VERTICAL)
        szDebugBox.Add(self.debug, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szDebugBox.Add(self.keepfiles, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        
        szDebug = wx.FlexGridSizer(1, 1, 7, 0)
        szDebug.Add(szDebugBox, 0, wx.EXPAND, 0)
        szDebug.Fit(self)
        szDebug.SetSizeHints(self)
        szDebug.AddGrowableRow(1)
        szDebug.AddGrowableCol(0)
        
        self.SetAutoLayout(True)
        self.SetSizer(szDebug)

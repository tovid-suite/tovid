#@+leo-ver=4-thin
#@+node:eric.20090722212922.2847:@shadow frames.py
# frames.py

import os
import wx

import libtovid
from libtovid.gui.configs import TovidConfig
from libtovid.gui.constants import *
from libtovid.gui.icons import AppIcon
from libtovid.gui.panels import *
from libtovid.gui.util import _

__all__ = [\
    "TovidFrame",
    "MiniEditorFrame",
    "TodiscFrame"]

#@+others
#@+node:eric.20090722212922.2849:class TovidFrame
class TovidFrame(wx.Frame):
    """Main tovid GUI frame. Contains and manages all sub-panels.
    """
    #@    @+others
    #@+node:eric.20090722212922.2850:__init__

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id , title, wx.DefaultPosition,
            (800, 820), wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(AppIcon())
        self.SetIcon(icon)

        # Global configuration
        self.curConfig = TovidConfig()

        self.dirname = os.getcwd()

        # Menu bar
        self.menubar = wx.MenuBar()

        # File menu
        self.menuFile = wx.Menu()
        #self.menuFile.Append(ID_MENU_FILE_PREFS, "&Preferences",
        #    "Configuration settings for tovid GUI")
        #self.menuFile.AppendSeparator()
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
        self.menuViewShowTooltips = wx.MenuItem(self.menuView, ID_MENU_VIEW_SHOWTOOLTIPS,
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
        # TODO: Re-enable save/open
        #wx.EVT_MENU(self, ID_MENU_FILE_PREFS, self.OnFilePrefs)
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_MENU_VIEW_SHOWGUIDE, self.OnShowGuide)
        wx.EVT_MENU(self, ID_MENU_VIEW_SHOWTOOLTIPS, self.OnShowTooltips)
        wx.EVT_MENU(self, ID_MENU_HELP_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_MENU_LANG_EN, self.OnLang)
        wx.EVT_MENU(self, ID_MENU_LANG_DE, self.OnLang)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

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

    #@-node:eric.20090722212922.2850:__init__
    #@+node:eric.20090722212922.2851:OnExit
    def OnExit(self, evt):
        """Exit the GUI and close all windows."""
        self.Close(True)

    #@-node:eric.20090722212922.2851:OnExit
    #@+node:eric.20090722212922.2852:OnShowGuide
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

    #@-node:eric.20090722212922.2852:OnShowGuide
    #@+node:eric.20090722212922.2853:OnShowTooltips
    def OnShowTooltips(self, evt):
        """Show or hide GUI tooltips."""
        if evt.IsChecked():
            # Enable tooltips globally
            wx.ToolTip_Enable(True)
        else:
            # Disable tooltips globally
            wx.ToolTip_Enable(False)

    #@-node:eric.20090722212922.2853:OnShowTooltips
    #@+node:eric.20090722212922.2854:OnAbout
    def OnAbout(self, evt):
        """Display a dialog showing information about tovidgui."""
        strAbout = "You are using the tovid GUI, version 0.31,\n" \
          "part of the tovid video disc authoring suite.\n\n" \
          "For more information and documentation, please\n" \
          "visit the tovid web site:\n\n" \
          "http://tovid.org/"
        dlgAbout = wx.MessageDialog(self, strAbout, "About tovid GUI", wx.OK)
        dlgAbout.ShowModal()

    #@-node:eric.20090722212922.2854:OnAbout
    #@+node:eric.20090722212922.2855:OnLang
    def OnLang(self, evt):
        """Change GUI to selected language."""
        if evt.GetId() == ID_MENU_LANG_EN:
            self.curConfig.UseLanguage('en')

        elif evt.GetId() == ID_MENU_LANG_DE:
            self.curConfig.UseLanguage('de')

    #@-node:eric.20090722212922.2855:OnLang
    #@+node:eric.20090722212922.2856:OnKeyUp
    def OnKeyUp(self, evt):
        """Key up event handler.  Primarily used to close the app if certain keys are pressed.
        """
        key = evt.KeyCode()
        if (key >= 0 and key < 256):
            controlDown = evt.ControlDown()
            if controlDown and "Q" == chr(key):
                self.Close()

    #@-node:eric.20090722212922.2856:OnKeyUp
    #@-others
    #def OnFilePrefs(self, evt):
    #    """Open preferences window and set configuration"""
    #    dlgPrefs = PreferencesDialog(self, wx.ID_ANY)
    #    dlgPrefs.ShowModal()
    #    # Set the output directory in the PreEncoding panel
    #    self.panEncoding.SetOutputDirectory(self.curConfig.strOutputDirectory)
#@-node:eric.20090722212922.2849:class TovidFrame
#@+node:eric.20090722212922.2857:class MiniEditorFrame
# end of class TovidFrame          

class MiniEditorFrame(wx.Frame):
    """Simple text editor (for editing configuration files) in a frame"""
    #@    @+others
    #@+node:eric.20090722212922.2858:__init__
    def __init__(self, parent, id, filename):
        wx.Frame.__init__(self, parent, id, "%s (MiniEditor)" % filename, \
            wx.DefaultPosition, (500, 400), \
            wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

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

    #@-node:eric.20090722212922.2858:__init__
    #@+node:eric.20090722212922.2859:OnNew
    def OnNew(self, evt):
        """Edit a new file"""
        # Just empty edit window and set filename to null
        self.editWindow.SetText([""])
        self.currentFilename = ""
        # Set title to indicate that a new file is being edited
        self.SetTitle("Untitled file (MiniEditor)")

    #@-node:eric.20090722212922.2859:OnNew
    #@+node:eric.20090722212922.2860:OnOpen
    def OnOpen(self, evt):
        inFileDialog = wx.FileDialog(self, _("Choose a file to open"), self.dirname, "",
            "*.*", wx.OPEN)
        if inFileDialog.ShowModal() == wx.ID_OK:
            self.dirname = inFileDialog.GetDirectory()
            # Open the file
            self.OpenFile(inFileDialog.GetPath())

        inFileDialog.Destroy()

    #@-node:eric.20090722212922.2860:OnOpen
    #@+node:eric.20090722212922.2861:OnSave
    def OnSave(self, evt):
        """Save the current file."""
        if self.currentFilename:
            # Save the current filename (prompt for overwrite)
            confirmDialog = wx.MessageDialog(self, \
                    _("Overwrite the existing file?"), \
                    _("Confirm overwrite"), wx.YES_NO)
            # If not overwriting, return now
            if confirmDialog.ShowModal() == wx.ID_NO:
                return

        # currentFilename is empty; prompt for a filename
        else:
            outFileDialog = wx.FileDialog(self, \
                    _("Choose a filename to save"), \
                    self.dirname, "", "*.*", wx.SAVE)
            if outFileDialog.ShowModal() == wx.ID_OK:
                self.dirname = outFileDialog.GetDirectory()
                self.currentFilename = outFileDialog.GetPath()

        outFile = open(self.currentFilename, "w")
        for line in self.editWindow.GetText():
            outFile.write("%s\n" % line)
        outFile.close()
        # Update title bar
        self.SetTitle("%s (MiniEditor)" % self.currentFilename)

    #@-node:eric.20090722212922.2861:OnSave
    #@+node:eric.20090722212922.2862:OnExit
    def OnExit(self, evt):
        self.Close(True)

    #@-node:eric.20090722212922.2862:OnExit
    #@+node:eric.20090722212922.2863:OpenFile
    def OpenFile(self, filename):
        """Open the given filename in the editor."""
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
    #@-node:eric.20090722212922.2863:OpenFile
    #@-others
#@-node:eric.20090722212922.2857:class MiniEditorFrame
#@+node:eric.20090722212922.2864:class TodiscFrame
# end of class MiniEditorFrame

class TodiscFrame(wx.Frame):
    """Main todisc GUI frame. Contains and manages all sub-panels.
    """
    #@    @+others
    #@+node:eric.20090722212922.2865:__init__
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle(_("todisc GUI"))

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(AppIcon())
        self.SetIcon(_icon)
        self.SetFocus()
        #
        # Create the menu bar
        #
        self.mbMain = wx.MenuBar()
        self.SetMenuBar(self.mbMain)
        mnFile = wx.Menu()
        mnFile.Append(ID_MENU_FILE_EXIT, _("E&xit"), "mnExit", wx.ITEM_NORMAL)
        self.mbMain.Append(mnFile, _("&File"))
        mnView = wx.Menu()
        mnView.Append(ID_MENU_VIEW_ADVANCED, _("&Advanced"), "mnAdvanced", wx.ITEM_CHECK)
        self.mbMain.Append(mnView, _("&View"))
        mnHelp = wx.Menu()
        mnHelp.Append(ID_MENU_HELP_ABOUT, _("&About"), "mnAbout", wx.ITEM_NORMAL)
        self.mbMain.Append(mnHelp, _("&Help"))
        #
        # Create the notebook for tabs
        #
        self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=0)
        self.nbPlaylist = PlaylistTabPanel(self.notebook_1, wx.ID_ANY)
        self.nbMenus = MenuTabPanel(self.notebook_1, wx.ID_ANY)
        self.nbThumbnails = ThumbnailTabPanel(self.notebook_1, wx.ID_ANY)
        self.nbDebug = DebugTabPanel(self.notebook_1, wx.ID_ANY)
        self.nbDebug.Hide()
        #
        # Add pages to notebook
        #
        self.notebook_1.AddPage(self.nbPlaylist, _("Playlist"))
        self.notebook_1.AddPage(self.nbMenus, _("Menus"))
        self.notebook_1.AddPage(self.nbThumbnails, _("Thumbnails"))
        self.notebook_1.AddPage(self.nbDebug, _("Debug"))
        #
        # Create navigation buttons
        #
        self.btnPrevious = wx.Button(self, wx.ID_ANY, _("< Previous"))
        self.btnPrevious.Disable()
        self.btnNext = wx.Button(self, wx.ID_ANY, _("Next >"))
        self.btnFinish = wx.Button(self, wx.ID_ANY, _("Finish"))
        #
        # Add the navigation buttons
        #
        szNav = wx.BoxSizer(wx.HORIZONTAL)
        szNav.Add(self.btnPrevious, 0, wx.ADJUST_MINSIZE, 0)
        szNav.Add(self.btnNext, 0, wx.ADJUST_MINSIZE, 0)
        szNav.Add(self.btnFinish, 0, wx.ADJUST_MINSIZE, 0)
        #
        # Add elements to the screen
        #
        szFrame = wx.FlexGridSizer(2, 1, 5, 0)
        szFrame.Add(self.notebook_1, 1, wx.EXPAND, 0)
        szFrame.Add(szNav, 1, wx.ALIGN_RIGHT, 0)

        szFrame.Fit(self)
        szFrame.SetSizeHints(self)
        szFrame.AddGrowableRow(0)
        szFrame.AddGrowableCol(0)

        self.SetAutoLayout(True)
        self.SetSizer(szFrame)
        self.Layout()
        self.Centre()

        # global events
        self.Bind(wx.EVT_KEY_UP, self.app_OnKeyUp)
        # menu events
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.Close)
        wx.EVT_MENU(self, ID_MENU_VIEW_ADVANCED, self.menu_SetAdvancedView)
        wx.EVT_MENU(self, ID_MENU_HELP_ABOUT, self.menu_OnAbout)
        # button events
        wx.EVT_BUTTON(self, self.btnPrevious.GetId(), self.btnPrevious_OnClick)
        wx.EVT_BUTTON(self, self.btnNext.GetId(), self.btnNext_OnClick)
        wx.EVT_BUTTON(self, self.btnFinish.GetId(), self.btnFinish_OnClick)

    #@-node:eric.20090722212922.2865:__init__
    #@+node:eric.20090722212922.2866:btnPrevious_OnClick
    def btnPrevious_OnClick(self, evt):
        """ Event handler for clicking of '< Previous' button
        """
        currPage = self.notebook_1.GetSelection()
        if (currPage > 0):
            self.notebook_1.SetSelection(currPage - 1)
            if (not self.btnNext.IsEnabled()):
                self.btnNext.Enable()
            if (currPage - 1 == 0):
                self.btnPrevious.Disable()
        elif (self.btnPrevious.IsEnabled()):
            self.btnPrevious.Disable()

    #@-node:eric.20090722212922.2866:btnPrevious_OnClick
    #@+node:eric.20090722212922.2867:btnNext_OnClick
    def btnNext_OnClick(self, evt):
        """ Event handler for clicking on the 'Next >' button
        """
        currPage = self.notebook_1.GetSelection() + 1
        if (currPage < self.notebook_1.GetPageCount()):
            if (self.notebook_1.GetPage(currPage).IsEnabled()):
                self.notebook_1.SetSelection(currPage)
                if (not self.btnPrevious.IsEnabled()):
                    self.btnPrevious.Enable()
                if (currPage + 1 == self.notebook_1.GetPageCount()):
                    self.btnNext.Disable()
        elif (self.btnNext.IsEnabled()):
            self.btnNext.Disable()

    #@-node:eric.20090722212922.2867:btnNext_OnClick
    #@+node:eric.20090722212922.2868:btnFinish_OnClick
    def btnFinish_OnClick(self, evt):
        """ Event handler for clicking on the 'Finish' button
        """
        # Collect todisc options from all three panels
        todisc_opts = {}
        todisc_opts.update(self.nbPlaylist.todisc_opts)
        todisc_opts.update(self.nbMenus.todisc_opts)
        todisc_opts.update(self.nbThumbnails.todisc_opts)
        # TODO: Verify required options (-files, -titles, -out)
        # Build a todisc command-line
        cmd = 'todisc '
        for opt, arg in todisc_opts.iteritems():
            # For booleans, use '-opt' (if True)
            if arg in [True, False]:
                if arg:
                    cmd += '-%s ' % opt
            # For lists, use '-opt "first" "second" ...'
            elif isinstance(arg, list):
                if len(arg) > 0:
                    cmd += '-%s ' % opt
                    for item in arg:
                        cmd += '"%s" ' % item
            # For all others, '-opt arg'
            elif arg is not None:
                cmd += '-%s %s ' % (opt, arg)
        print("Would run the following todisc command:")
        print(cmd)
        return

    #@-node:eric.20090722212922.2868:btnFinish_OnClick
    #@+node:eric.20090722212922.2869:menu_OnAbout
    def menu_OnAbout(self, evt):
        """Display a dialog showing information about todiscgui.
        """
        strAbout = "You are using the todisc GUI, version 0.28,\n" \
          "part of the tovid video disc authoring suite.\n\n" \
          "For more information and documentation, please\n" \
          "visit the tovid web site:\n\n" \
          "http://tovid.org/"
        dlgAbout = wx.MessageDialog(self, strAbout, "About todisc GUI", wx.OK)
        dlgAbout.ShowModal()

    #@-node:eric.20090722212922.2869:menu_OnAbout
    #@+node:eric.20090722212922.2870:menu_SetAdvancedView
    def menu_SetAdvancedView(self, evt):
        if (evt.IsChecked()):
            self.notebook_1.GetPage(self.notebook_1.GetPageCount() - 1).Show()
        else:
            self.notebook_1.GetPage(self.notebook_1.GetPageCount() - 1).Hide()

    #@-node:eric.20090722212922.2870:menu_SetAdvancedView
    #@+node:eric.20090722212922.2871:app_OnKeyUp
    def app_OnKeyUp(self, evt):
        """Key down event handler.  Primarily used to close the app if certain keys are pressed.
        """
        key = evt.KeyCode()
        if (key >= 0 and key < 256):
            controlDown = evt.ControlDown()
            if ((controlDown) and ("Q" == chr(key))):
                self.Close()
    #@-node:eric.20090722212922.2871:app_OnKeyUp
    #@-others
#@-node:eric.20090722212922.2864:class TodiscFrame
#@-others
#@-node:eric.20090722212922.2847:@shadow frames.py
#@-leo

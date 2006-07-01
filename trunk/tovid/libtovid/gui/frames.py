#! /usr/bin/env python
# frames.py

import os
import wx

import libtovid
from libtovid.tdl import Project
from libtovid.gui.configs import TovidConfig
from libtovid.gui.constants import *
from libtovid.gui.icons import AppIcon
from libtovid.gui.panels import AuthorFilesTaskPanel, GuidePanel
from libtovid.gui.util import _

__all__ = ["TovidFrame", "MiniEditorFrame", "TodiscFrame"]

class TovidFrame(wx.Frame):
    """Main tovid GUI frame. Contains and manages all sub-panels."""

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id , title, wx.DefaultPosition,
            (800, 600), wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

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
        # TODO: Re-enable save/open
        # Commented out for the 0.26 release; not working
        #self.menuFile.Append(ID_MENU_FILE_OPEN, "&Open project",
        #        "Open an existing TDL text file (EXPERIMENTAL)")
        #self.menuFile.Append(ID_MENU_FILE_SAVE, "&Save project",
        #        "Save this project as a TDL text file (EXPERIMENTAL)")
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
        # Commented out for the 0.26 release; not working
        #wx.EVT_MENU(self, ID_MENU_FILE_SAVE, self.OnFileSave)
        #wx.EVT_MENU(self, ID_MENU_FILE_OPEN, self.OnFileOpen)
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
                outFile.write(element.to_string())

            outFile.close()
    
    def OnFileOpen(self, evt):
        inFileDialog = wx.FileDialog(self, _("Choose a TDL file to open"),
            self.dirname, "", "*.tdl", wx.OPEN)
        if inFileDialog.ShowModal() == wx.ID_OK:
            self.dirname = inFileDialog.GetDirectory()
            proj = Project()
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
        strAbout = "You are using the tovid GUI, version 0.27,\n" \
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

    def OnKeyUp(self, evt):
        """Key up event handler.  Primarily used to close the app if certain keys are pressed.
        """
        key = evt.KeyCode()
        if (key >= 0 and key < 256):
            controlDown = evt.ControlDown()
            if controlDown and "Q" == chr(key):
                self.Close()

    #def OnFilePrefs(self, evt):
    #    """Open preferences window and set configuration"""
    #    dlgPrefs = PreferencesDialog(self, wx.ID_ANY)
    #    dlgPrefs.ShowModal()
    #    # Set the output directory in the PreEncoding panel
    #    self.panEncoding.SetOutputDirectory(self.curConfig.strOutputDirectory)
# end of class TovidFrame          

class MiniEditorFrame(wx.Frame):
    """Simple text editor (for editing configuration files) in a frame"""
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

    def OnNew(self, evt):
        """Edit a new file"""
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

    def OnExit(self, evt):
        self.Close(True)

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
# end of class MiniEditorFrame

class TodiscFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # Menu Bar
        self.mbMain = wx.MenuBar()
        self.SetMenuBar(self.mbMain)
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(ID_MENU_FILE_EXIT, _("E&xit"), "mnExit", wx.ITEM_NORMAL)
        self.mbMain.Append(wxglade_tmp_menu, _("&File"))
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(ID_MENU_VIEW_ADVANCED, _("&Advanced"), "mnAdvanced", wx.ITEM_CHECK)
        self.mbMain.Append(wxglade_tmp_menu, _("&View"))
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(ID_MENU_HELP_ABOUT, _("&About"), "mnAbout", wx.ITEM_NORMAL)
        self.mbMain.Append(wxglade_tmp_menu, _("&Help"))
        # Menu Bar end
        
        self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=0)
        #
        # Playlist tab
        #
        self.nbPlaylist = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.szVideoInfoBox_staticbox = wx.StaticBox(self.nbPlaylist, wx.ID_ANY, _("Video Information"))
        self.szTitleInfoBox_staticbox = wx.StaticBox(self.nbPlaylist, wx.ID_ANY, _("Title"))
        self.szAudioInfoBox_staticbox = wx.StaticBox(self.nbPlaylist, wx.ID_ANY, _("Audio"))
        self.discFormat = wx.RadioBox(self.nbPlaylist, wx.ID_ANY, _("Disc Format"), choices=[_("DVD"), _("SVCD")], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.videoFormat = wx.RadioBox(self.nbPlaylist, wx.ID_ANY, _("Video Format"), choices=[_("NTSC"), _("PAL")], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.submenus = wx.CheckBox(self.nbPlaylist, wx.ID_ANY, _("Create submenus?"))
        self.lblChapters = wx.StaticText(self.nbPlaylist, wx.ID_ANY, _("Chapters per video:"))
        self.chapters = wx.SpinCtrl(self.nbPlaylist, wx.ID_ANY, "6", min=0, max=100, style=wx.TE_RIGHT)
        self.files = wx.ListBox(self.nbPlaylist, wx.ID_ANY, choices=[])
        self.lblTitle = wx.StaticText(self.nbPlaylist, wx.ID_ANY, _("Main Title:"))
        self.title = wx.TextCtrl(self.nbPlaylist, wx.ID_ANY, "")
        self.lblSubmenuTitle = wx.StaticText(self.nbPlaylist, wx.ID_ANY, _("Submenu Title:"))
        self.submenu_title = wx.TextCtrl(self.nbPlaylist, wx.ID_ANY, "")
        self.lblSubmenuAudio = wx.StaticText(self.nbPlaylist, wx.ID_ANY, _("Audio for Submenu"))
        self.submenu_audio = wx.TextCtrl(self.nbPlaylist, wx.ID_ANY, "")
        self.subaudio_all = wx.CheckBox(self.nbPlaylist, wx.ID_ANY, _("Use for all submenu audio?"))
        self.btnAudio = wx.Button(self.nbPlaylist, wx.ID_ANY, _("Choose"))
        self.btnAddVideo = wx.Button(self.nbPlaylist, wx.ID_ANY, _("Add Video"))
        self.btnRemoveVideo = wx.Button(self.nbPlaylist, wx.ID_ANY, _("Remove Video"))
        self.static_line_4 = wx.StaticLine(self.nbPlaylist, wx.ID_ANY)
        self.lblOut = wx.StaticText(self.nbPlaylist, wx.ID_ANY, _("Output"))
        self.out = wx.TextCtrl(self.nbPlaylist, wx.ID_ANY, "")
        self.btnOut = wx.Button(self.nbPlaylist, wx.ID_ANY, _("Choose"))
        #
        # Menus tab
        #
        self.nbMenus = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.szMistOpacity_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Text Mist Opacity"))
        self.szMainMenuBox_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Main Menu"))
        self.szBackgroundBox_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Background"))
        self.szAudioFadeBox_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Audio Fade"))
        self.szMenuAnim_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Menu Animations"))
        self.szSubmenuBox_staticbox = wx.StaticBox(self.nbMenus, wx.ID_ANY, _("Submenus"))
        self.lblMenuTitle = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Title:"))
        self.menu_title = wx.TextCtrl(self.nbMenus, wx.ID_ANY, "")
        self.lblMenuFont = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Title Font:"))
        self.btnMenuFont = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        self.lblMenuFontSize = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Font Size:"))
        self.menu_fontsize = wx.SpinCtrl(self.nbMenus, wx.ID_ANY, "", min=0, max=100)
        self.lblTitleColor = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Title Color:"))
        self.btnTitleColor = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        self.lblStrokeColor = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Stroke Color:"))
        self.btnStrokeColor = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        self.static_line_3 = wx.StaticLine(self.nbMenus, wx.ID_ANY)
        self.menu_fade = wx.CheckBox(self.nbMenus, wx.ID_ANY, _("Use menu fade?"))
        self.static_line_2 = wx.StaticLine(self.nbMenus, wx.ID_ANY)
        self.text_mist = wx.CheckBox(self.nbMenus, wx.ID_ANY, _("Use text mist?"))
        self.lblTextMistColor = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Text Mist Color:"))
        self.btnTextMistColor = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        self.opacity_copy = wx.Slider(self.nbMenus, wx.ID_ANY, 100, 0, 100, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.lblBgAudio = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Background Audio"))
        self.bgaudio = wx.TextCtrl(self.nbMenus, wx.ID_ANY, "")
        self.btnBgAudio = wx.Button(self.nbMenus, wx.ID_ANY, _("Choose"))
        self.lblBgImage = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Background Image"))
        self.bgimage = wx.TextCtrl(self.nbMenus, wx.ID_ANY, "")
        self.btnBgImage = wx.Button(self.nbMenus, wx.ID_ANY, _("Choose"))
        self.lblBgVideo = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Background Video"))
        self.bgvideo = wx.TextCtrl(self.nbMenus, wx.ID_ANY, "")
        self.btnBgVideo = wx.Button(self.nbMenus, wx.ID_ANY, _("Choose"))
        self.lblMenuAudioFade = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Menu:"))
        self.menu_audio_fade = wx.SpinCtrl(self.nbMenus, wx.ID_ANY, "", min=0, max=100)
        self.lblSubmenuAudioFade = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Submenu:"))
        self.submenu_audio_fade = wx.SpinCtrl(self.nbMenus, wx.ID_ANY, "", min=0, max=100)
        self.static = wx.CheckBox(self.nbMenus, wx.ID_ANY, _("Animate menus?"))
        self.lblMenuLength_copy = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Menu animation length:"))
        self.menu_length_copy = wx.SpinCtrl(self.nbMenus, wx.ID_ANY, "", min=0, max=100)
        self.lblLoop = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Menu pause length:"))
        self.loop = wx.SpinCtrl(self.nbMenus, wx.ID_ANY, "", min=0, max=100)
        self.static_line_1 = wx.StaticLine(self.nbMenus, wx.ID_ANY)
        self.ani_submenus = wx.CheckBox(self.nbMenus, wx.ID_ANY, _("Animate submenus?"))
        self.lblSubmenuTitleColor = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Title Color:"))
        self.btnSubmenuTitleColor = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        self.lblSubmenuStrokeColor = wx.StaticText(self.nbMenus, wx.ID_ANY, _("Stroke Color:"))
        self.btnSubmenuStrokeColor = wx.Button(self.nbMenus, wx.ID_ANY, _("Default"))
        #
        # Thumbnails tab
        #
        self.nbThumbnails = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.szBlur_staticbox = wx.StaticBox(self.nbThumbnails, wx.ID_ANY, _("Blur"))
        self.szOpacity_staticbox = wx.StaticBox(self.nbThumbnails, wx.ID_ANY, _("Opacity"))
        self.thumb_shape = wx.RadioBox(self.nbThumbnails, wx.ID_ANY, _("Feather Shape"), choices=[_("None"), _("Normal"), _("Oval"), _("Cloud"), _("Egg")], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.lblThumbTitleFont = wx.StaticText(self.nbThumbnails, wx.ID_ANY, _("Thumb Font:"))
        self.thumb_font = wx.Button(self.nbThumbnails, wx.ID_ANY, _("Default"))
        self.lblThumbTitleSize = wx.StaticText(self.nbThumbnails, wx.ID_ANY, _("Thumb Font Size:"))
        self.thumb_font_size = wx.SpinCtrl(self.nbThumbnails, wx.ID_ANY, "", min=0, max=100)
        self.lblThumbTitleColor = wx.StaticText(self.nbThumbnails, wx.ID_ANY, _("Thumb Font Color:"))
        self.thumb_text_color = wx.Button(self.nbThumbnails, wx.ID_ANY, _("Default"))
        self.lblThumbTitleMistColor = wx.StaticText(self.nbThumbnails, wx.ID_ANY, _("Thumb Mist Color:"))
        self.thumb_mist_color = wx.Button(self.nbThumbnails, wx.ID_ANY, _("Default"))
        self.blur = wx.Slider(self.nbThumbnails, wx.ID_ANY, 5, 0, 10, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.opacity = wx.Slider(self.nbThumbnails, wx.ID_ANY, 100, 0, 100, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.lblSeek = wx.StaticText(self.nbThumbnails, wx.ID_ANY, _("Seconds to seek before generating thumbs:"))
        self.seek = wx.SpinCtrl(self.nbThumbnails, wx.ID_ANY, "", min=0, max=100, style=wx.TE_RIGHT)
        #
        # Debug tab
        #
        self.nbDebug = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.szDebugBox_staticbox = wx.StaticBox(self.nbDebug, wx.ID_ANY, _("Debug Flags"))
        self.debug = wx.CheckBox(self.nbDebug, wx.ID_ANY, _("Turn on debug logging?"))
        self.keepfiles = wx.CheckBox(self.nbDebug, wx.ID_ANY, _("Keep files when finished?"))
        
        self.__set_properties()
        self.__do_layout()
        self.__do_events()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(_("todisc GUI"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(AppIcon())
        self.SetIcon(_icon)
        self.SetFocus()
        self.discFormat.SetSelection(0)
        self.videoFormat.SetSelection(0)
        self.files.SetMinSize((414, 225))
        self.btnAddVideo.SetDefault()
        self.lblMenuTitle.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblMenuFont.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblMenuFontSize.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblTitleColor.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblStrokeColor.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblBgAudio.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblBgImage.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.static.SetValue(1)
        self.lblSubmenuTitleColor.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.lblSubmenuStrokeColor.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "DejaVu Sans"))
        self.thumb_shape.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        szFrame = wx.FlexGridSizer(2, 1, 5, 0)
        szNav = wx.BoxSizer(wx.HORIZONTAL)
        szDebug = wx.FlexGridSizer(1, 1, 7, 0)
        szDebugBox = wx.StaticBoxSizer(self.szDebugBox_staticbox, wx.VERTICAL)
        szThumbnails = wx.FlexGridSizer(5, 1, 7, 0)
        szSeek = wx.FlexGridSizer(1, 2, 0, 5)
        szOpacity = wx.StaticBoxSizer(self.szOpacity_staticbox, wx.VERTICAL)
        szBlur = wx.StaticBoxSizer(self.szBlur_staticbox, wx.VERTICAL)
        szThumbShape = wx.FlexGridSizer(2, 1, 5, 0)
        szThumbFont = wx.FlexGridSizer(2, 4, 5, 5)
        szMenus = wx.FlexGridSizer(5, 1, 7, 0)
        szSubmenuBox = wx.StaticBoxSizer(self.szSubmenuBox_staticbox, wx.HORIZONTAL)
        szSubmenuColor = wx.FlexGridSizer(1, 4, 0, 7)
        szMenuAnim = wx.StaticBoxSizer(self.szMenuAnim_staticbox, wx.VERTICAL)
        szSubmenus = wx.FlexGridSizer(10, 1, 5, 0)
        szLoop = wx.GridSizer(1, 2, 0, 0)
        szMenuLength_copy = wx.FlexGridSizer(1, 2, 0, 0)
        szAudioFadeBox = wx.StaticBoxSizer(self.szAudioFadeBox_staticbox, wx.HORIZONTAL)
        szAudioFade = wx.FlexGridSizer(1, 4, 0, 5)
        szBackgroundBox = wx.StaticBoxSizer(self.szBackgroundBox_staticbox, wx.VERTICAL)
        szBackground = wx.FlexGridSizer(3, 3, 5, 5)
        szMainMenuBox = wx.StaticBoxSizer(self.szMainMenuBox_staticbox, wx.VERTICAL)
        szMistOpacity = wx.StaticBoxSizer(self.szMistOpacity_staticbox, wx.VERTICAL)
        szTextMist = wx.FlexGridSizer(1, 3, 0, 5)
        szTitleFont = wx.FlexGridSizer(2, 4, 0, 5)
        szMenuTitle = wx.FlexGridSizer(1, 2, 0, 5)
        szPlaylist = wx.FlexGridSizer(7, 1, 7, 0)
        szOutput = wx.FlexGridSizer(1, 3, 0, 7)
        szVidButtons = wx.BoxSizer(wx.HORIZONTAL)
        szVideoInfoBox = wx.StaticBoxSizer(self.szVideoInfoBox_staticbox, wx.VERTICAL)
        szVideoInfo = wx.FlexGridSizer(3, 1, 5, 5)
        szAudioInfoBox = wx.StaticBoxSizer(self.szAudioInfoBox_staticbox, wx.VERTICAL)
        szAudioOptions = wx.GridSizer(1, 2, 0, 5)
        szAudioInfo = wx.FlexGridSizer(1, 2, 5, 5)
        szTitleInfoBox = wx.StaticBoxSizer(self.szTitleInfoBox_staticbox, wx.VERTICAL)
        szTitleInfo = wx.FlexGridSizer(4, 2, 5, 5)
        szChapters = wx.GridSizer(1, 2, 0, 0)
        szFormats = wx.FlexGridSizer(1, 2, 0, 5)
        szFormats.Add(self.discFormat, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szFormats.Add(self.videoFormat, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szFormats.AddGrowableCol(0)
        szFormats.AddGrowableCol(1)
        szPlaylist.Add(szFormats, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szPlaylist.Add(self.submenus, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szChapters.Add(self.lblChapters, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szChapters.Add(self.chapters, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szPlaylist.Add(szChapters, 1, wx.EXPAND, 0)
        szVideoInfo.Add(self.files, 0, wx.EXPAND, 0)
        szTitleInfo.Add(self.lblTitle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTitleInfo.Add(self.title, 0, wx.EXPAND, 0)
        szTitleInfo.Add(self.lblSubmenuTitle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTitleInfo.Add(self.submenu_title, 0, wx.EXPAND, 0)
        szTitleInfo.AddGrowableCol(1)
        szTitleInfoBox.Add(szTitleInfo, 1, wx.EXPAND, 0)
        szVideoInfo.Add(szTitleInfoBox, 1, wx.EXPAND, 0)
        szAudioInfo.Add(self.lblSubmenuAudio, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioInfo.Add(self.submenu_audio, 0, wx.EXPAND, 0)
        szAudioInfo.AddGrowableCol(1)
        szAudioInfoBox.Add(szAudioInfo, 1, wx.EXPAND, 0)
        szAudioOptions.Add(self.subaudio_all, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioOptions.Add(self.btnAudio, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szAudioInfoBox.Add(szAudioOptions, 1, wx.EXPAND, 0)
        szVideoInfo.Add(szAudioInfoBox, 1, wx.EXPAND, 0)
        szVideoInfo.AddGrowableRow(0)
        szVideoInfo.AddGrowableCol(0)
        szVideoInfoBox.Add(szVideoInfo, 0, wx.EXPAND, 0)
        szPlaylist.Add(szVideoInfoBox, 1, wx.EXPAND, 0)
        szVidButtons.Add(self.btnAddVideo, 1, wx.ADJUST_MINSIZE, 0)
        szVidButtons.Add(self.btnRemoveVideo, 1, wx.ADJUST_MINSIZE, 0)
        szPlaylist.Add(szVidButtons, 1, wx.EXPAND, 0)
        szPlaylist.Add(self.static_line_4, 0, wx.EXPAND, 0)
        szOutput.Add(self.lblOut, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szOutput.Add(self.out, 0, wx.EXPAND, 0)
        szOutput.Add(self.btnOut, 0, wx.ADJUST_MINSIZE, 0)
        szOutput.AddGrowableCol(1)
        szPlaylist.Add(szOutput, 1, wx.EXPAND, 0)
        self.nbPlaylist.SetAutoLayout(True)
        self.nbPlaylist.SetSizer(szPlaylist)
        szPlaylist.Fit(self.nbPlaylist)
        szPlaylist.SetSizeHints(self.nbPlaylist)
        szPlaylist.AddGrowableRow(3)
        szPlaylist.AddGrowableCol(0)
        szMenuTitle.Add(self.lblMenuTitle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMenuTitle.Add(self.menu_title, 0, wx.EXPAND, 0)
        szMenuTitle.AddGrowableCol(1)
        szMainMenuBox.Add(szMenuTitle, 0, wx.EXPAND, 0)
        szTitleFont.Add(self.lblMenuFont, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnMenuFont, 0, wx.ADJUST_MINSIZE, 0)
        szTitleFont.Add(self.lblMenuFontSize, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.menu_fontsize, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szTitleFont.Add(self.lblTitleColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnTitleColor, 0, wx.ADJUST_MINSIZE, 0)
        szTitleFont.Add(self.lblStrokeColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szTitleFont.Add(self.btnStrokeColor, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szTitleFont.AddGrowableCol(1)
        szMainMenuBox.Add(szTitleFont, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szMainMenuBox.Add(self.static_line_3, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(self.menu_fade, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMainMenuBox.Add(self.static_line_2, 0, wx.EXPAND, 0)
        szTextMist.Add(self.text_mist, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szTextMist.Add(self.lblTextMistColor, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        szTextMist.Add(self.btnTextMistColor, 0, wx.ADJUST_MINSIZE, 0)
        szTextMist.AddGrowableCol(1)
        szMainMenuBox.Add(szTextMist, 0, wx.EXPAND, 0)
        szMistOpacity.Add(self.opacity_copy, 0, wx.EXPAND, 0)
        szMainMenuBox.Add(szMistOpacity, 0, wx.EXPAND, 0)
        szMenus.Add(szMainMenuBox, 1, wx.EXPAND, 0)
        szBackground.Add(self.lblBgAudio, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgaudio, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgAudio, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.lblBgImage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgimage, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgImage, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.lblBgVideo, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szBackground.Add(self.bgvideo, 0, wx.EXPAND, 0)
        szBackground.Add(self.btnBgVideo, 0, wx.ADJUST_MINSIZE, 0)
        szBackground.AddGrowableCol(1)
        szBackgroundBox.Add(szBackground, 1, wx.EXPAND, 0)
        szMenus.Add(szBackgroundBox, 1, wx.EXPAND, 0)
        szAudioFade.Add(self.lblMenuAudioFade, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.menu_audio_fade, 0, wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.lblSubmenuAudioFade, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szAudioFade.Add(self.submenu_audio_fade, 0, wx.ADJUST_MINSIZE, 0)
        szAudioFade.AddGrowableCol(1)
        szAudioFadeBox.Add(szAudioFade, 1, wx.EXPAND, 0)
        szMenus.Add(szAudioFadeBox, 1, wx.EXPAND, 0)
        szSubmenus.Add(self.static, 0, wx.ADJUST_MINSIZE, 0)
        szMenuLength_copy.Add(self.lblMenuLength_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szMenuLength_copy.Add(self.menu_length_copy, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szMenuLength_copy.AddGrowableCol(0)
        szMenuLength_copy.AddGrowableCol(1)
        szSubmenus.Add(szMenuLength_copy, 1, wx.EXPAND, 0)
        szLoop.Add(self.lblLoop, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szLoop.Add(self.loop, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szSubmenus.Add(szLoop, 1, wx.EXPAND, 0)
        szSubmenus.Add(self.static_line_1, 0, wx.EXPAND, 0)
        szSubmenus.Add(self.ani_submenus, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szSubmenus.AddGrowableCol(0)
        szMenuAnim.Add(szSubmenus, 1, wx.EXPAND, 0)
        szMenus.Add(szMenuAnim, 1, wx.EXPAND, 0)
        szSubmenuColor.Add(self.lblSubmenuTitleColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szSubmenuColor.Add(self.btnSubmenuTitleColor, 0, wx.ADJUST_MINSIZE, 0)
        szSubmenuColor.Add(self.lblSubmenuStrokeColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szSubmenuColor.Add(self.btnSubmenuStrokeColor, 0, wx.ADJUST_MINSIZE, 0)
        szSubmenuColor.AddGrowableCol(1)
        szSubmenuBox.Add(szSubmenuColor, 1, wx.EXPAND, 0)
        szMenus.Add(szSubmenuBox, 1, wx.EXPAND, 0)
        self.nbMenus.SetAutoLayout(True)
        self.nbMenus.SetSizer(szMenus)
        szMenus.Fit(self.nbMenus)
        szMenus.SetSizeHints(self.nbMenus)
        szMenus.AddGrowableCol(0)
        szThumbShape.Add(self.thumb_shape, 0, wx.EXPAND, 0)
        szThumbFont.Add(self.lblThumbTitleFont, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_font, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.Add(self.lblThumbTitleSize, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_font_size, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szThumbFont.Add(self.lblThumbTitleColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_text_color, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.Add(self.lblThumbTitleMistColor, 0, wx.ALIGN_CENTER_VERTICAL|wx.SHAPED, 0)
        szThumbFont.Add(self.thumb_mist_color, 0, wx.ADJUST_MINSIZE, 0)
        szThumbFont.AddGrowableCol(1)
        szThumbShape.Add(szThumbFont, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        szThumbShape.AddGrowableCol(0)
        szThumbnails.Add(szThumbShape, 1, wx.EXPAND, 0)
        szBlur.Add(self.blur, 0, wx.EXPAND, 0)
        szThumbnails.Add(szBlur, 0, wx.EXPAND, 0)
        szOpacity.Add(self.opacity, 0, wx.EXPAND, 0)
        szThumbnails.Add(szOpacity, 0, wx.EXPAND, 0)
        szSeek.Add(self.lblSeek, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szSeek.Add(self.seek, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        szSeek.AddGrowableCol(0)
        szThumbnails.Add(szSeek, 1, wx.EXPAND, 0)
        self.nbThumbnails.SetAutoLayout(True)
        self.nbThumbnails.SetSizer(szThumbnails)
        szThumbnails.Fit(self.nbThumbnails)
        szThumbnails.SetSizeHints(self.nbThumbnails)
        szThumbnails.AddGrowableCol(0)
        szDebugBox.Add(self.debug, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szDebugBox.Add(self.keepfiles, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        szDebug.Add(szDebugBox, 0, wx.EXPAND, 0)
        self.nbDebug.SetAutoLayout(True)
        self.nbDebug.SetSizer(szDebug)
        self.nbDebug.Hide()
        szDebug.Fit(self.nbDebug)
        szDebug.SetSizeHints(self.nbDebug)
        szDebug.AddGrowableRow(1)
        szDebug.AddGrowableCol(0)
        self.notebook_1.AddPage(self.nbPlaylist, _("Playlist"))
        self.notebook_1.AddPage(self.nbMenus, _("Menus"))
        self.notebook_1.AddPage(self.nbThumbnails, _("Thumbnails"))
        self.notebook_1.AddPage(self.nbDebug, _("Debug"))
        szFrame.Add(self.notebook_1, 1, wx.EXPAND, 0)
        self.btnPrevious = wx.Button(self, wx.ID_ANY, _("< Previous"))
        self.btnNext = wx.Button(self, wx.ID_ANY, _("Next >"))
        self.btnFinish = wx.Button(self, wx.ID_ANY, _("Finish"))
        szNav.Add(self.btnPrevious, 0, wx.ADJUST_MINSIZE, 0)
        szNav.Add(self.btnNext, 0, wx.ADJUST_MINSIZE, 0)
        szNav.Add(self.btnFinish, 0, wx.ADJUST_MINSIZE, 0)
        szFrame.Add(szNav, 1, wx.ALIGN_RIGHT, 0)
        self.SetAutoLayout(True)
        self.SetSizer(szFrame)
        szFrame.Fit(self)
        szFrame.SetSizeHints(self)
        szFrame.AddGrowableRow(0)
        szFrame.AddGrowableCol(0)
        self.Layout()
        self.Centre()
        # end wxGlade

    def __do_events(self):
        """ Setup event handling for widgets
        """
        # global events
        self.Bind(wx.EVT_KEY_UP, self.app_OnKeyUp)
        # menu events
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.Close)
        wx.EVT_MENU(self, ID_MENU_VIEW_ADVANCED, self.menu_SetAdvancedView)
        # button events
        wx.EVT_BUTTON(self, self.btnPrevious.GetId(), self.btnPrevious_OnClick)
        wx.EVT_BUTTON(self, self.btnNext.GetId(), self.btnNext_OnClick)
        wx.EVT_BUTTON(self, self.btnFinish.GetId(), self.btnFinish_OnClick)

    def btnPrevious_OnClick(self, evt):
        """ Event handler for clicking of '< Previous' button
        """
        currPage = self.notebook_1.GetSelection()
        if (currPage > 0):
            self.notebook_1.SetSelection(currPage - 1)

    def btnNext_OnClick(self, evt):
        """ Event handler for clicking on the 'Next >' button
        """
        currPage = self.notebook_1.GetSelection()
        if (currPage < self.notebook_1.GetPageCount()):
            self.notebook_1.SetSelection(currPage + 1)

    def btnFinish_OnClick(self, evt):
        """ Event handler for clicking on the 'Finish' button
        """
        return

    def menu_OnAbout(self, evt):
        """Display a dialog showing information about todiscgui.
        """
        strAbout = "You are using the todisc GUI, version 0.27,\n" \
          "part of the tovid video disc authoring suite.\n\n" \
          "For more information and documentation, please\n" \
          "visit the tovid web site:\n\n" \
          "http://tovid.org/"
        dlgAbout = wx.MessageDialog(self, strAbout, "About todisc GUI", wx.OK)
        dlgAbout.ShowModal()

    def menu_SetAdvancedView(self, evt):
        if (evt.IsChecked()):
            self.notebook_1.GetPage(self.notebook_1.GetPageCount() - 1).Show()
        else:
            self.notebook_1.GetPage(self.notebook_1.GetPageCount() - 1).Hide()

    def app_OnKeyUp(self, evt):
        """Key down event handler.  Primarily used to close the app if certain keys are pressed.
        """
        key = evt.KeyCode()
        if (key >= 0 and key < 256):
            controlDown = evt.ControlDown()
            if ((controlDown) and ("Q" == chr(key))):
                self.Close()
# end of class TodiscFrame
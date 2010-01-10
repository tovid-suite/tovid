# dialogs.py

import wx

import libtovid
from libtovid.gui.configs import TovidConfig
from libtovid.gui.constants import *
from libtovid.gui.util import _

__all__ = [\
    "FontChooserDialog",
    "PreferencesDialog"]

class FontChooserDialog(wx.Dialog):
    """A simple font chooser"""

    def __init__(self, parent, id, curFacename = "Default"):
        wx.Dialog.__init__(self, parent, id, _("Font chooser"), wx.DefaultPosition,
                (400, 400))

        # Center dialog
        self.Centre()

        # Get global configuration
        self.curConfig = TovidConfig()

        # Construct a list of fonts. Always list "Default" first.
        strFontChoices = []
        strFontChoices.extend(self.curConfig.wx_IM_FontMap.keys())
        strFontChoices.sort()
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
        if len(self.curConfig.wx_IM_FontMap.keys()) < 6:
            dlgGetMoreFonts = wx.MessageDialog(self,
                "You have less than six fonts to choose from. See the\n"
                "tovid documentation (http://tovid.wikia.com/)\n"
                "for instructions on how to get more.",
                "How to get more fonts", wx.OK | wx.ICON_INFORMATION)
            dlgGetMoreFonts.ShowModal()

    def OnSelectFont(self, evt):
        """Change the sample font to reflect the selected font"""
        face = self.listFonts.GetStringSelection()
        self.font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL, False, face)
        self.lblFontSample.SetFont(self.font)

    def GetSelectedFont(self):
        """Return the font that was selected"""
        return self.font

class PreferencesDialog(wx.Dialog):
    """Preferences/configuration settings dialog. Not yet used."""

    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "tovid GUI Preferences", \
                wx.DefaultPosition, (400, 200))
        # Center dialog
        self.Centre()
        # Get global configuration
        self.curConfig = TovidConfig()
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

    def OnOK(self, evt):
        """Assign configuration to underlying Config class"""
        # Config assignment goes here
        self.EndModal(wx.ID_OK)


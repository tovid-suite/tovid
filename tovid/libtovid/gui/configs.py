#! /usr/bin/env python
# configs.py

import os
import sys
import re
import gettext
import wx
import locale
from libtovid.utils import get_listtype

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
    wx_IM_FontMap = {}
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
    # The user's locale/system encoding information
    cur_lang_code, cur_encoding = locale.getdefaultlocale()
    # Hack: Error out on undefined locale
    if cur_encoding is None:
        print "Error: Could not get default locale."
        print "You should be able to fix this by setting LANG or LC_ALL:"
        print "   LANG=en_US.utf8 tovidgui, or"
        print "   LC_ALL=en_US.utf8 tovidgui"
        print "Set LANG or LC_ALL in your ~/.profile to avoid this error."
        sys.exit(1)

    def __init__(self):
        """Initialize "static" class data.
        The real initialization function, only called once."""
        self.__dict__ = self.__shared_state
        self.isInitialized = True
        self.ConfigAvailFonts()
        #self.InitLocales()
    

    def ConfigAvailFonts(self):
        """Determine fonts that are available in both wx.Python and
        ImageMagick."""
        # Find the shared fonts between ImageMagick and wx.Python
        ###########################################################
        # IM and wx store their available fonts differently, so we need a 
        # dictionary that maps the wx name for a font to its IM name. For 
        # example: "Bitstream Vera Sans Mono" in wx maps to 
        # "Bitstream-Vera-Sans-Mono" in IM. Fortunately, the difference 
        # between font names are only non-word characters. So by abbreviating
        # the names of each font, common fonts can be found in the
        # intersection of the two sets of abbreviated names. If the
        # abbreviated names are keys in a dictionary that map the abbreviated
        # name to the original name, then the shared keys between the IM and 
        # wx dictionaries can be used to build the final wx <--> IM dictionary.
        # phew!

        # Process outline:
        # 1. Find the fonts of IM and wx
        # 2. Abbreviate the names by removing spaces, underscores, and dashes
        # 3. Use dicts to map the abbreviated name (key) to the original name 
        #    (value)
        # 4. Find the common keys between both dicts (and thus the common 
        #    fonts)
        # 5. Build the wx <--> dict using the common keys

        # 1a. Find IM's fonts. IM's output is a mixture of font names and 
        #     paths. We only want the names of fonts, not the 'pretty' print 
        #     given by IM. However, since we're looking for _shared_ font 
        #     names, the 'bad' lines from IM can be left alone (as they will 
        #     be taken out later when looking for matching font names from 
        #     wx). wx is acting as our regex in a way ;) Each line that 
        #     describes a font also includes the foundry and other information
        #     we don't want. We only want the font_name, which is the 
        #     first word on each line.
        im_cmd = "convert -list " + get_listtype()
        IM_lines = os.popen(im_cmd).readlines()
        IM_lines = [unicode(line, self.cur_encoding) for line in IM_lines]
        font_name_re = re.compile("^[\w-]+")   # match [a-zA-Z_-] at least once
        IM_fonts = [font_name_re.search(line).group() 
            for line in IM_lines if hasattr(font_name_re.search(line), 'group')]

        # 1b. Find wx's fonts. wx returns a list of font names as unicode 
        #     strings. This can create problems for folks with exotic fonts.
        enuWXFonts = wx.FontEnumerator()
        enuWXFonts.EnumerateFacenames()
        WX_fonts = enuWXFonts.GetFacenames()

        # 2. Remove the word separators from the font names, making 
        #    abbreviations. So:
        #    "Bitstream-Vera-Sans-Mono" becomes "BitstreamVeraSansMono" (IM)
        #    "Bitstream Vera Sans Mono" becomes "BitstreamVeraSansMono" (wx)
        abbr_name_re = re.compile("-|_| ")
        IM_abbr = [abbr_name_re.sub('', font) for font in IM_fonts]
        WX_abbr = [abbr_name_re.sub('', font) for font in WX_fonts]

        # 3. Make a dictionary map between the abbreviated name and the 
        #    original The keys are the abbreviated names, and the values are 
        #    the originals.
        #    eg:   'BitstreamVeraSansMono': 'Bitstream-Vera-Sans-Mono' (IM)
        #          'BitstreamVeraSansMono': 'Bitstream Vera Sans Mono' (wx)
        IM_dict = dict( [(IM_abbr[i], IM_fonts[i]) 
            for i in range(len(IM_fonts))] )
        WX_dict = dict( [(WX_abbr[i], WX_fonts[i]) 
            for i in range(len(WX_fonts))] )

        # 4. Find the common keys between both dicts. Make each dict's keys 
        #    a set (thereby removing any duplicate entries) and find their 
        #    intersection.
        shared_fonts = set(WX_dict.keys()).intersection(set(IM_dict.keys()))
        shared_fonts = list(shared_fonts)

        # 5. Make a dictionary that maps wx fonts to IM fonts. Using the common
        #    keys, build a dictionary that maps original wx font names to 
        #    original IM font names.
        #    eg:                   'wx_name': 'IM_name'
        #         'Bitstream Vera Sans Mono': 'Bitstream-Vera-Sans-Mono'
        WX_IM_dict = dict( [(WX_dict[font], IM_dict[font]) 
            for font in shared_fonts] )

        # Add IM's 'default' font, and return the font map
        if 'Bitstream Vera Sans' in WX_IM_dict.keys():
            WX_IM_dict['Default'] = WX_IM_dict['Bitstream Vera Sans']
        elif 'Dingbats' in WX_IM_dict.keys():
            WX_IM_dict['Default'] = WX_IM_dict['Dingbats']
        else:
            WX_IM_dict['Default'] = 'Helvetica'
        self.wx_IM_FontMap = WX_IM_dict

    def UseLanguage(self, lang):
        self.trans[ lang ].install()
    
    def InitLocales(self):
        self.trans = {}
    
        try:
            self.trans['en'] = gettext.translation('tovidgui', '.', ['en'])
            #self.trans['de'] = gettext.translation('tovidgui', '.', ['de'])
        except IOError:
            print "Couldn't initialize translations"


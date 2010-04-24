#! /usr/bin/env python
# -=- encoding: latin-1 -=-
# License: GPL
# Author: Alexandre Bourget <wackysalut@bourget.cc>
# Copyright: 2006

"""Module that implements a set of classes which aid in creation of a valid
dvdauthor-formatted .xml file.

A dvdauthor .xml file describes the contents and playback behavior of a DVD.
The MPEG video files to be included, as well as any interactive menus, are
included here. (See the dvdauthor manual page for its full capabilities.) A
typical .xml file looks something like this:

    <dvdauthor>
        <vmgm>
            <menus> ... </menus>
        </vmgm>
        <titleset>
            <menus> ... </menus>
            <titles> ... </titles>
        </titleset>
    </dvdauthor>

The purpose of this module is to encapsulate dvdauthor's XML syntax into Python
classes, and make it easier to create such .xml files automatically.

Using this module's classes, the above XML becomes:

    Disc
    |-- VMGM
    |   `-- Menu(s)
    `-- Titleset(s)
        |-- Menu(s)
        `-- Title(s)


Adding a Titleset in the Disc object, or adding a Button to a Menu is done
in a consistent manner across the different object types. For example:

    Disc.add_titleset(Titleset)

    Titleset.add_menu(Menu)

    Menu.add_video_file('myfile.mpg')
    
etc.

Note that a VMGM menu is a subclass of a Titleset (more restricted), and a
Menu object is a subclass of a Title, extended only by the fact that it can
have buttons.

You must be aware of the inner restrictions of `commands` inside a Menu or a
Title object. These are restrictions imposed by the dvdauthor software itself.
Read the man pages for more details.

Cross-referencing is done with IDs. Each object, be it Titleset, Menu, Title or
VMGM, has its own randomly-generated ID (stored in object.id). You must use
these in the commands to jump from a title to another, or when you call a menu,
for example:

  command = "jump titleset %s title %s" % (mytitleset.id, thistitle.id)

When rendering, the engine will replace the IDs with the actual number values of
the menus or titles you specified. This enables dynamic creation of DVD, and
even 'menu driven interactive DVD', without having to worry of the references
if you change the order of your story, or insert a new title/titleset somewhere.

Note you can also use a short form, which will expand to the full location of
the menu/title:

  command = "jump f:%s" %(mytitle.id)

which will be expanded to:

  "jump titleset 2 title 1"

depending on where it's placed in the Disc hierarchy. Note the 'f:' in front of
'%s', which stands for 'full addressing'.

Notes

* Consider having Disc() construct mandatory parts automatically (discs must
    have one VMGM section, and at least one titleset.) That way, user can get
    a basic "empty disc" just by calling Disc().

"""

version = '0.1'

import random # for random()
import cgi    # for escape()
import os     # for system()

__all__ = ['Disc', 'VMGM', 'Titleset', 'Title', 'Menu']
  
class Disc:
    """dvdauthor XML file generator.

    This is the highest level object in the tree. See module documentation."""
    def __init__(self, name=None):
        """Highest level object, which includes all others.

        name -- Just a name for you to remember. It will be inserted as a
                comment in the .XML file
        """
        self.id = _gen_id()
        self.titlesets = []
        self.jumppad = True
        self.vmgm = None
        self.name = name

    def add_titleset(self, titleset):
        """Add the Titleset"""
        self.titlesets.append(titleset)

    def xml(self, output_dir='dvd'):
        """Return XML file as a string

        output_dir -- specifies where to output the project
        """
        add = ''
        if self.jumppad:
            add += ' jumppad="yes"'
        xml = '<dvdauthor dest="%s"%s>\n' % (output_dir, add)

        # Deal with VMGM
        if self.vmgm:
            xml += _indent(2, self.vmgm._xml())
        # Deal with Titlesets
        for titleset in self.titlesets:
            xml += _indent(2, titleset._xml())

        xml += '</dvdauthor>\n'

        xml = self._check_crossref(xml)

        return xml

    def _check_crossref(self, xml):
        """This functions scans the .xml file for any IDs, in the form:
        [ID:xxxxxxxx] and replaces it with the position of the title or
        titleset, for buttons referencing.

        See set_pre_commands() for more information.
        """
        # TODO: Eventually, this could return a full location, in the form:
        #   titleset 2 title 1
        #   vmgm menu 2
        # so we could use: "jump %s" % menu2.id
        # and everything would be solved.
        # but this doesn't help if we want to jump to the title1 no matter
        # which titleset we're in.

        for i in range(0, len(self.titlesets)):
            t = self.titlesets[i]
            xml = xml.replace(t.id, str(i+1))

            for j in range(0, len(t.menus)):
                m = t.menus[j]
                xml = xml.replace('f:%s' % m.id,
                                  "titleset %d menu %d" % (i+1, j+1))
                xml = xml.replace(m.id, str(j+1))
            for j in range(0, len(t.titles)):
                l = t.titles[j]
                xml = xml.replace('f:%s' % l.id,
                                  "titleset %d title %d" % (i+1, j+1))
                xml = xml.replace(l.id, str(j+1))

        if self.vmgm:
            v = self.vmgm
            
            for j in range(0, len(v.menus)):
                m = v.menus[j]
                xml = xml.replace('f:%s' % m.id,
                                  "vmgm menu %d" % (j+1))
                xml = xml.replace(m.id, str(j+1))
            # No titles in a VMGM
            
        # Check if any unresolved IDs still exist, if so, raise error.
        if xml.find('[ID:') != -1:
            raise ReferenceError, "Unresolved menu reference in commands parsing. Have you added all your titles/menus to titlesets/vmgm structs ?"

        return xml

    def dvdauthor_execute(self, output_dir,
                          xml_file='/tmp/dvdauthor.xml'):
        """Writes the XML file to disk and run dvdauthor on it to produce the
        desired output.

        output_dir -- specifies where to output the project
        xml_file -- specifies the location of the output xml file

        This function calls xml()
        """
        f = open(xml_file, 'w')
        f.write(self.xml(output_dir))
        f.close()
        os.system('dvdauthor -x "%s"' % xml_file)

    def set_jumppad(self, jumppad=True):
        """Set dvdauthor jumpad tag.

        jumppad -- bool.

        If you do not call this function with a True value, the jumppad is
        by default disabled.
        """
        self.jumppad = jumppad

    def set_vmgm(self, vmgm):
        """Set the VMGM menu for the disc.

        NOTE: we use the 'set_' prefix, as opposed to 'add_', because there
              is only one VMGM menu by disc.
        """
        self.vmgm = vmgm


class Titleset:
    """Represent a Titleset on the DVD.

    You can add Title(s), and Menu(s) (including buttons) to a Titleset.

    Note that this is just a container for menus and titles, and has not itself
    video files associated. It's the way the DVD structure works. Read on about
    official DVD specs to learn more.
  
    """

    def __init__(self, name=None):
        """Create a Titleset instance.

        name -- Just a name for you to remember. It will be inserted as a
                comment in the .XML file
        """
        self.id = _gen_id()
        self.name = name
        self.menus = []
        self.titles = []      # shouldn't change if we're a VMGM
        self.audio_langs = []
        self.subpictures = [] # shouldn't change if we're a Titleset
        self.menulang = None  # shouldn't change if we're a Titleset
    
    def add_menu(self, menu):
        """Add a menu to the Titleset.

        You can only add menus that have no 'entry' field or where their 'entry'
        field is one of:

            root
            subtitle
            audio
            angle
            ptt
        """
        entries = [None, 'root', 'subtitle', 'audio', 'angle', 'ptt']
        if menu.entry not in entries:
            raise AttributeError, "Menu should have entry in the following: root, subtitle, audio, angle, ptt. Not: %s" % menu.entry
        self.menus.append(menu)

    def add_title(self, title):
        """Add a title to the Titleset."""
        self.titles.append(title)

    def add_audio_lang(self, lang):
        """Set the language for the next audio track in the video files of the
        Title(s) you've added, or you're going to add.

        The language codes must be one in the list you'll find at:

            http://sunsite.berkeley.edu/amher/iso_639.html

        Validation is done in the function call to ensure you specify something
        that exists.
        """
        self.audio_langs.append(_verify_lang(lang))

    def _xml(self, block='titleset'):
        """Return the dvdauthor XML string for this Titleset."""
        xml = '<!-- %s: %s -->\n' % (self.__class__, self.name)

        xml += '<%s>\n' % block

        if len(self.menus):
            # Deal with MENUS blocks, and language-code
            add = ''
            if self.menulang:
                add += ' lang="%s"' % self.menulang
            xml += '  <menus%s>\n' % add

            # Deal with the video block
            #           '    <video />'
            # Deal with audio language block(s)
            for audio_lang in self.audio_langs:
                xml += '    <audio lang="%s" />\n' % audio_lang
            # Deal with subpictures blocks
            for subpicture in self.subpictures:
                xml += '    <subpicture lang="%s" />\n' % subpicture
            # List all menus
            for menu in self.menus:
                xml += _indent(4, menu._xml())

            xml += '  </menus>\n'


        if len(self.titles):
            # Deal with TITLES blocks
            xml += '  <titles>\n'
            
            # Deal with the video block
            #           '    <video />'
            # Deal with audio language block(s)
            for audio_lang in self.audio_langs:
                xml += '    <audio lang="%s" />\n' % audio_lang
            # Deal with subpictures blocks
            # `--> UNUSED by dvdauthor docs ?
            #for subpicture in self.subpictures:
            #    xml += '    <subpicture lang="%s" />\n' % subpicture
            # List all titles
            for title in self.titles:
                xml += _indent(4, title._xml())

            xml += '  </titles>\n'

        xml += '</%s>\n' % block

        return xml


class VMGM(Titleset):
    """Represent the VMGM menu structure on the DVD.

    Note that this is just a container for menus, and has not itself video files
    associated.

    Differences with the Titleset and the 'entry' fields in the Menus it
    includes that cannot have the same values.
    """
    
    def __init__(self, name=None, lang=None):
        """Create the VMGM menu instance (top level menu) for the DVD.

        name -- Just a name for you to remember. It will be inserted as a
                comment in the .XML file
        """
        Titleset.__init__(self, name)
        self.menulang = _verify_lang(lang)
        self.id = 'vmgm' # no need for a fancy id, since there is only one VMGM

    def add_menu(self, menu):
        """Add a menu to the VMGM top-level menu.
        
        You can only add menus that have no 'entry' field or where their 'entry'
        field is one of:

            title
        """
        entries = [None, 'title']
        if menu.entry not in entries:
            raise AttributeError, "Title should have entry = 'title', or None. Not: %s" % menu.entry
        self.menus.append(menu)

    def add_title(self, title):
        """You shouldn't add a title to a VMGM menu."""
        raise(NotImplementedError, "You shouldn't call add_title() on a VMGM object. VMGM menu sets don't have titles.")

    def add_subpicture_lang(self, lang):
        """Add the language definitions for the subtitles in the videos.

        The language codes must be one in the list you'll find at:

            http://dvdauthor.sourceforge.net/doc/languages.html

        Validation is done in the function call to ensure you specify something
        that exists.

        NOTE: I still don't know if this is valid only for VMGM. Could someone
              point me to some documentation ?
        """
        self.subpictures.append(_verify_lang(lang))

    def _xml(self):
        """Return the dvdauthor XML string for this VMGM."""
        # Use the Titleset rendering engine, which does the job for both
        # of us (VMGM and Titleset)
        return Titleset._xml(self, 'vmgm')

        

class Title:
    """Represent a Title on the DVD. This includes one or more .vob (or .mpg)
    files.
    """

    def __init__(self, name=None, pause=None, video_files=[]):
        """Create a Title instance.

        name -- Just a name for you to remember. It will be inserted as a
                comment in the .XML file
        pause -- = None, if you don't want the video to pause after having
                   played all the .vob (or .mpg) files in the Title
                 = 1 to 254, in seconds, if you want to pause for that number
                   of seconds after the Title
                 = 'inf', if you want to pause indefinitely, or until someone
                   presses the 'Next' button on the DVD remote control.
        video_files -- Array of strings (or string) containing the
                       video files for this Title.
        """
        self.id = _gen_id()
        self.name = name
        self.pause = pause
        self.video_files = []
        self.cells = []
        self.pre_cmds = None
        self.post_cmds = None
        self.entry = None # shouldn't change if we're still a Title obj.
        self.buttons = [] # idem.

        # Add video files if specified.
        if isinstance(video_files, str):
            self.add_video_file(video_files)
        elif isinstance(video_files, list):
            for x in video_files:
                self.add_video_file(x)

    def add_video_file(self, file, chapters=None, pause=None):
        """Add a .vob (or .mpg) file to the Title.

        chapters -- A string as understood by dvdauthor. Example:
                   "00:00:00.000,00:01:00.001" or "12:26,15:42"
        pause -- A time in seconds (ranging from 0 (no pause, default)
                 to 254. Use 'inf' if you want it to stop indefinitely.
        """
        self.video_files.append({'file': file, 'chapters': chapters,
                                'pause': pause})

    def add_cell(self, start_stamp, end_stamp, chapter=False, program=False,
                 pause=None):
        """Add a cell definition.

        start_stamp -- see dvdauthor documentation (quite undocumented)
        end_stamp -- idem.
        chapter -- bool (see docs?)
        program -- bool (see docs?)
        pause -- see Title.__init__() for documentation
        """
        self.cells.append({'start': start_stamp, 'end': end_stamp,
                           'chapter': chapter, 'program': program,
                           'pause': pause})
    
    def set_pre_commands(self, commands):
        """Set the commands executed before the Title plays.

        See dvdauthor's man page for a detailed explanation of the language
        used herein.

        commands -- this is a string which contains commands and optionally
                    location IDs (menu.id, title.id, titleset.id). Check
                    module's documentation for example or the test suite.
        """
        self.pre_cmds = commands

    def set_post_commands(self, commands):
        """Set the commands executed after the Title has played.

        commands -- see Title.set_pre_commands() for documentation
        """
        self.post_cmds = commands

    def _xml(self):
        """Return the dvdauthor XML string for this Title."""

        # It is possible to have a no-video menu, with only a <pre>
        # (so it seems!)
        #if not len(self.video_files):
        #    raise ValueError, 'VideoFiles needed for Title named: "%s"' % \
        #          self.name
        
        xml =  "<!-- %s: %s -->\n" % (self.__class__, self.name)
        
        # Deal with head
        add = ''
        if self.entry != None:
            add += ' entry="%s"' % self.entry
        if self.pause != None:
            add += ' pause="%s"' % self.pause
        xml +=  "<pgc%s>\n" % add
        
        # Deal with pre commands
        if self.pre_cmds:
            xml += "  <pre> %s </pre>\n" % _xmlentities(self.pre_cmds)
            
        # Deal with all vob files
        for videofile in self.video_files:
            add = ''
            if videofile['chapters'] != None:
                add += ' chapters="%s"' % videofile['chapters']
            if videofile['pause'] != None:
                add += ' pause="%s"' % videofile['pause']
            xml += "  <vob file=\"%s\"%s />\n" % (videofile['file'], add)
            
        # Deal with all buttons if they exist
        for button in self.buttons:
            add = ''
            if button[0] != None:
                add += ' name="%s"' % button[0]
            xml += "  <button%s> %s </button>\n" % (add,
                                                    _xmlentities(button[1]))
        # Deal with post commands
        if self.post_cmds:
            xml += "  <post> %s </post>\n" % _xmlentities(self.post_cmds)

        # Just add it!
        xml += "</pgc>\n"

        return xml


class Menu(Title):
    """Represent a Menu on the DVD. This includes one or more .vob (or .mpg)
    files.
    """

    def __init__(self, name=None, entry=None, pause=None, video_files=[]):
        """Create a Menu instance.
        
        name -- Just a name for you to remember. It will be inserted as a
                comment in the .XML file
        entry -- one of:
                      root, subtitle, audio, angle, ptt
                 if you intend to add it to a Titleset object, or one of:
                      title
                 if you intend to add it to a VMGM object.
        pause -- See the Title.__init__() documentation
        video_files -- Array of strings (or string) containing the
                       video files for this Menu.
        """
        Title.__init__(self, name, pause, video_files)
        # TODO: deal with entry only here, because Title doesn't have anything
        #       to do with entry points.
        entries = [None, 'root', 'subtitle', 'audio', 'angle', 'ptt', 'title']
        if entry not in entries:
            raise KeyError, "entry must be one of: root, subtitle, audio, angle, ptt, title"
        self.entry = entry
        self.buttons = []
    
    def set_button_commands(self, commands, button=None):
        """Set the commands executed when a button is pressed in the menu.

        commands -- see Title.set_pre_commands() for documentation
        button -- leave to None for automatic numbering. Otherwise, specify
                  a string which must have the same reference in the video
                  files you're going to add to the menu.

        If you specify the button name, then you can overwrite it's value in
        the course of your program. If you do not specify it's value, you
        cannot modify what was previously entered (unless you dive into the
        dvdauthor module code :).
        """
        if button == None:
            self.buttons.append([None, commands])
        else:
            # Go set the right button's value
            nowset = False
            for x in self.buttons:
                if (x[0] == button):
                    x[1] = commands
                    nowset = True
            if not nowset:
                self.buttons.append([button, commands])


    def _xml(self):
        """Return the dvdauthor XML string for this Menu."""
        return Title._xml(self)


###
### Helper functions
###


def _xmlentities(text):
    """Return the given text with <, >, and & characters escaped (replaced
    by corresponding SGML entities)."""
    return cgi.escape(text)

def _indent(spaces, text):
    """Indents each line in the text by the given number of spaces"""
    new_text = ''
    for line in text.splitlines():
        new_text += (' ' * spaces) + line + "\n"
    return new_text


def _gen_id():
    """Generates a random ID, which will be used in the commands strings
    for 'jump' and 'call' cross-referencing.
    """
    # This ID won't be transformed by the _xmlentities() func, so we're okay
    # with it :)
    return "[ID:%08x]" % random.randint(0, 65535*65535)


def _verify_lang(lang):
    if lang == None:
        return None
    
    nlang = lang.upper()
    if not language_codes.has_key(nlang):
        raise KeyError, "Language codes must be one in the list found at: "\
              "http://sunsite.berkeley.edu/amher/iso_639.html"

    return (lang.lower(), language_codes[nlang])




############################### DATA ################################

### Language codes definitions, from:
### http://sunsite.berkeley.edu/amher/iso_639.html
###
language_codes = {'AA': 'AFAR',
                  'AB': 'ABKHAZIAN',
                  'AF': 'AFRIKAANS',
                  'AM': 'AMHARIC',
                  'AR': 'ARABIC',
                  'AS': 'ASSAMESE',
                  'AY': 'AYMARA',
                  'AZ': 'AZERBAIJANI',
                  'BA': 'BASHKIR',
                  'BE': 'BYELORUSSIAN',
                  'BG': 'BULGARIAN',
                  'BH': 'BIHARI',
                  'BI': 'BISLAMA',
                  'BN': 'BENGALI;BANGLA',
                  'BO': 'TIBETAN',
                  'BR': 'BRETON',
                  'CA': 'CATALAN',
                  'CO': 'CORSICAN',
                  'CS': 'CZECH',
                  'CY': 'WELSH',
                  'DA': 'DANISH',
                  'DE': 'GERMAN',
                  'DZ': 'BHUTANI',
                  'EL': 'GREEK',
                  'EN': 'ENGLISH',
                  'EO': 'ESPERANTO',
                  'ES': 'SPANISH',
                  'ET': 'ESTONIAN',
                  'EU': 'BASQUE',
                  'FA': 'PERSIAN (farsi)',
                  'FI': 'FINNISH',
                  'FJ': 'FIJI',
                  'FO': 'FAROESE',
                  'FR': 'FRENCH',
                  'FY': 'FRISIAN',
                  'GA': 'IRISH',
                  'GD': 'SCOTS GAELIC',
                  'GL': 'GALICIAN',
                  'GN': 'GUARANI',
                  'GU': 'GUJARATI',
                  'HA': 'HAUSA',
                  'HI': 'HINDI',
                  'HR': 'CROATIAN',
                  'HU': 'HUNGARIAN',
                  'HY': 'ARMENIAN',
                  'IA': 'INTERLINGUA',
                  'IE': 'INTERLINGUE',
                  'IK': 'INUPIAK',
                  'IN': 'INDONESIAN',
                  'IS': 'ICELANDIC',
                  'IT': 'ITALIAN',
                  'IW': 'HEBREW',
                  'JA': 'JAPANESE',
                  'JI': 'YIDDISH',
                  'JV': 'JAVANESE',
                  'KA': 'GEORGIAN',
                  'KK': 'KAZAKH',
                  'KL': 'GREENLANDIC',
                  'KM': 'CAMBODIAN',
                  'KN': 'KANNADA',
                  'KO': 'KOREAN',
                  'KS': 'KASHMIRI',
                  'KU': 'KURDISH',
                  'KY': 'KIRGHIZ',
                  'LA': 'LATIN',
                  'LN': 'LINGALA',
                  'LO': 'LAOTHIAN',
                  'LT': 'LITHUANIAN',
                  'LV': 'LATVIAN;LETTISH',
                  'MG': 'MALAGASY',
                  'MI': 'MAORI',
                  'MK': 'MACEDONIAN',
                  'ML': 'MALAYALAM',
                  'MN': 'MONGOLIAN',
                  'MO': 'MOLDAVIAN',
                  'MR': 'MARATHI',
                  'MS': 'MALAY',
                  'MT': 'MALTESE',
                  'MY': 'BURMESE',
                  'NA': 'NAURU',
                  'NE': 'NEPALI',
                  'NL': 'DUTCH',
                  'NO': 'NORWEGIAN',
                  'OC': 'OCCITAN',
                  'OM': 'AFAN (OROMO',
                  'OR': 'ORIYA',
                  'PA': 'PUNJABI',
                  'PL': 'POLISH',
                  'PS': 'PASHTO;PUSHTO',
                  'PT': 'PORTUGUESE',
                  'QU': 'QUECHUA',
                  'RM': 'RHAETO-ROMANCE',
                  'RN': 'KURUNDI',
                  'RO': 'ROMANIAN',
                  'RU': 'RUSSIAN',
                  'RW': 'KINYARWANDA',
                  'SA': 'SANSKRIT',
                  'SD': 'SINDHI',
                  'SG': 'SANGHO',
                  'SH': 'SERBO-CROATIAN',
                  'SI': 'SINGHALESE',
                  'SK': 'SLOVAK',
                  'SL': 'SLOVENIAN',
                  'SM': 'SAMOAN',
                  'SN': 'SHONA',
                  'SO': 'SOMALI',
                  'SQ': 'ALBANIAN',
                  'SR': 'SERBIAN',
                  'SS': 'SISWATI',
                  'ST': 'SESOTHO',
                  'SU': 'SUNDANESE',
                  'SV': 'SWEDISH',
                  'SW': 'SWAHILI',
                  'TA': 'TAMIL',
                  'TE': 'TELUGU',
                  'TG': 'TAJIK',
                  'TH': 'THAI',
                  'TI': 'TIGRINYA',
                  'TK': 'TURKMEN',
                  'TL': 'TAGALOG',
                  'TN': 'SETSWANA',
                  'TO': 'TONGA',
                  'TR': 'TURKISH',
                  'TS': 'TSONGA',
                  'TT': 'TATAR',
                  'TW': 'TWI',
                  'UK': 'UKRAINIAN',
                  'UR': 'URDU',
                  'UZ': 'UZBEK',
                  'VI': 'VIETNAMESE',
                  'VO': 'VOLAPUK',
                  'WO': 'WOLOF',
                  'XH': 'XHOSA',
                  'YO': 'YORUBA',
                  'ZH': 'CHINESE',
                  'ZU': 'ZULU'}


#! /usr/bin/env python

# ===========================================================
# TDL

import copy
from Globals import strip_indentation

# ===========================================================
__doc__ = \
"""This module contains a definition of the tovid design language (TDL),
including:

    * Valid Element types (i.e., 'Video', 'Menu', 'Disc')
    * Valid options for each type of element
    * Argument format, default value, and documentation
      for each accepted option

Essentially, TDL is a user-interface API for tovid, designed to provide a
generalized interface, which may then be implemented by an actual frontend
(command-line, GUI, text-file input, etc.)


Hacking this module:

This module can do some pretty interesting things on its own, with a little bit
of interaction. Run 'python' to get an interactive shell, and try some of the
following.

First, tell python where to find this module:

    >>> import libtovid.TDL
    >>>

The first thing of interest is what elements are available in TDL:

    >>> for elem in TDL.elements:
    ...     print elem
    ...
    Menu
    Disc
    Video
    >>>

You can see that TDL has three different kinds of element: Menu, Disc, and
Video. What options are available for a Menu element?

    >>> for option in TDL.element_options['Menu']:
    ...     print option
    ...
    highlightcolor
    font
    format
    tvsys
    selectcolor
    textcolor
    fontsize
    background
    audio
    alignment
    linksto
    >>>

Say you want to know the purpose of the Menu 'background' option:

    >>> print TDL.element_options['Menu']['background'].doc
    Use IMAGE (in most any graphic format) as a background.
    >>>

You can also display full usage notes for an option, by using the
usage_string() function:

    >>> print TDL.element_options['Menu']['background'].usage_string()
    -background IMAGE (default None)
        Use IMAGE (in most any graphic format) as a background.
    >>>

To display full usage notes for an element, do like this:

    >>> print TDL.usage('Menu')
    -highlightcolor [#RRGGBB|#RGB|COLORNAME] (default red)
        Undocumented option

    -font FONTNAME (default Helvetica)
        Use FONTNAME for the menu text.

    -format [vcd|svcd|dvd] (default dvd)
        Generate a menu compliant with the specified disc format
    
    (...)

    >>>

Let's create a new Menu element, named "Main menu":

    >>> menu = TDL.Element('Menu', "Main menu")

Behind the scenes, a new element is created, and filled with all the default
options befitting a Menu element. You can check it out by displaying the TDL
string representation of the element, like so:

    >>> print menu.tdl_string()
    Menu "Main menu"
        textcolor white
        format dvd
        tvsys ntsc
        selectcolor green
        highlightcolor red
        fontsize 24
        background None
        font Helvetica
        linksto []
        alignment left
        audio None
    >>>

Let's say you don't like Helvetica, and want to use the "Times" font instead:

    >>> menu.set('font', "Times")
    >>>

And you would like to change the background:

    >>> menu.set('background', "/pub/images/foo.jpg")
    >>>


"""


# ===========================================================
class OptionDef:
    """An option, its default value, and notes on usage and purpose.
    
    For example:
        
        opt = OptionDef(
            'debug',
            '[no|some|all]',
            'some',
            "Amount of debugging information to display"
           )

    This defines a 'debug' option, along with a human-readable string showing
    expected argument formatting, a default value, and a string documenting the
    purpose of the 'debug' option."""

    def __init__(self, name, argformat, default, doc = "Undocumented option"):
        """Create a new option definition with the given attributes."""
        self.name = name
        self.argformat = argformat
        self.default = default
        self.doc = strip_indentation(doc)

        
    def num_args(self):
        """Return the number of arguments expected by this option, or -1 if
        unlimited."""
        if self.default.__class__ == bool:
            # Boolean: no argument
            return 0
        elif self.default.__class__ == list:
            # List: unlimited arguments
            return -1
        else:
            # Unary: one argument
            return 1

    def usage_string(self):
        """Return a string containing "usage notes" for this option."""
        usage = "-%s %s (default %s)\n" % \
                (self.name, self.argformat, self.default)
        usage += "    %s\n" % self.doc
        return usage



# ===========================================================
"""Dictionary of TDL options, categorized by element tag

TODO: Expand to include all currently-supported tovid suite
options, where feasible. Document all options.
"""
element_options = {
# Disc element definition
# Options pertaining to high-level disc structure
    'Disc': { 
        'format':
            OptionDef('format', '[vcd|svcd|dvd]', 'dvd',
            """Create a disc of the specified format."""),
        'tvsys':
            OptionDef('tvsys', '[pal|ntsc]', 'ntsc',
            """Make the disc for the specified TV system."""),
        'topmenu':
            OptionDef('topmenu', 'MENUNAME', None,
            """Use MENUNAME for the top-level menu on the disc.""")

    },

    # Menu element definition
    # Options pertaining to generating a video disc menu
    'Menu': {
        'format': OptionDef('format', '[vcd|svcd|dvd]', 'dvd',
            """Generate a menu compliant with the specified disc format"""),
        'tvsys': OptionDef('tvsys', '[pal|ntsc]', 'ntsc',
            """Make the menu for the specified TV system"""),

        'linksto': OptionDef('linksto', '"TITLE" [, "TITLE"]', [],
            """Comma-separated list of quoted titles; these are the
            titles that will be displayed (and linked) from the menu."""),
        'background': OptionDef('background', 'IMAGE', None,
            """Use IMAGE (in most any graphic format) as a background."""),
        'audio': OptionDef('audio', 'AUDIOFILE', None,
            """Use AUDIOFILE for background music while the menu plays."""),
        'font':
            OptionDef('font', 'FONTNAME', 'Helvetica',
            """Use FONTNAME for the menu text."""),
        'fontsize':
            OptionDef('fontsize', 'NUM', '24',
            """Use a font size of NUM pixels."""),
        'alignment':
            OptionDef('alignment', '[left|center|right]', 'left'),
        'textcolor':
            OptionDef('textcolor', '[#RRGGBB|#RGB|COLORNAME]', 'white'),
        'highlightcolor':
            OptionDef('highlightcolor', '[#RRGGBB|#RGB|COLORNAME]', 'red'),
        'selectcolor':
            OptionDef('selectcolor', '[#RRGGBB|#RGB|COLORNAME]', 'green')
    },

    # Video element definition
    # Options pertaining to video format and postprocessing
    'Video': {
        # New options to (eventually) replace -vcd, -pal etc.
        'format':
            OptionDef('format', '[vcd|svcd|dvd|half-dvd|dvd-vcd]', 'dvd',
            """Make video compliant with the specified format"""),

        'tvsys':
            OptionDef('tvsys', '[ntsc|pal]', 'ntsc',
            """Make the video compliant with the specified TV system"""),

        # Deprecated options. Need to find a way to
        # mark options as deprecated, so the parser can
        # warn the user.
        'vcd':
            OptionDef('vcd', '', False),
        'svcd':
            OptionDef('svcd', '', False),
        'dvd':
            OptionDef('dvd', '', False),
        'half-dvd':
            OptionDef('half-dvd', '', False),
        'dvd-vcd':
            OptionDef('dvd-vcd', '', False),
        'ntsc':
            OptionDef('ntsc', '', False),
        'ntscfilm':
            OptionDef('ntscfilm', '', False),
        'pal':
            OptionDef('pal', '', False),

        # Other options
        'in':           OptionDef('in', 'FILENAME', None),
        'out':          OptionDef('out', 'FILENAME', None),

        'aspect':       OptionDef('aspect', 'WIDTH:HEIGHT', "4:3",
            """Force the input video to be the given aspect ratio, where WIDTH
            and HEIGHT are integers."""),

        'quality':      OptionDef('quality', '[1-9]', 8,
            """Desired output quality, on a scale of 1 to 10, with 10 giving
            the best quality at the expense of a larger output file. Output
            size can vary by approximately a factor of 4 (that is, -quality 1
            output can be 25% the size of -quality 10 output). Your results may
            vary."""),
        
        'vbitrate':     OptionDef('vbitrate', '[0-9800]', 6000,
            """Maximum bitrate to use for video (in kbits/sec). Must be within
            allowable limits for the given format. Overrides default values.
            Ignored for VCD."""),

        'abitrate':     OptionDef('abitrate', '[0-1536]', 224,
            """Encode audio at NUM kilobits per second.  Reasonable values
            include 128, 224, and 384. The default is 224 kbits/sec, good
            enough for most encodings. The value must be within the allowable
            range for the chosen disc format; Ignored for VCD, which must be
            224."""),

        'safe':         OptionDef('safe', '[0-100]%', "100%",
            """Fit the video within a safe area defined by PERCENT. For
            example, '-safe 90%' will scale the video to 90% of the
            width/height of the output resolution, and pad the edges with a
            black border. Use this if some of the picture is cut off when
            played on your TV."""),

        'interlaced':   OptionDef('interlaced', '', False,
            """Do interlaced encoding of the input video. Use this option if
            your video is interlaced, and you want to preserve as much picture
            quality as possible. Ignored for VCD."""),

        'deinterlace':  OptionDef('deinterlace', '', False,
            """Use this option if your source video is interlaced. You can
            usually tell if you can see a bunch of horizontal lines when you
            pause the video during playback. If you have recorded a video from
            TV or your VCR, it may be interlaced. Use this option to convert to
            progressive (non-interlaced) video. This option is DEPRECATED, and
            will probably be ditched in favor of interlaced encoding, which is
            better in almost every way."""),

        'subtitles':    OptionDef('subtitles', 'FILE', None,
            """Get subtitles from FILE and encode them into the video.
            WARNING: This hard-codes the subtitles into the video, and you
            cannot turn them off while viewing the video. By default, no
            subtitles are loaded. If your video is already compliant with the
            chosen output format, it will be re-encoded to include the
            subtitles."""),

        'normalize':    OptionDef('normalize', '', False,
            """Normalize the volume of the audio. Useful if the audio is too
            quiet or too loud, or you want to make volume consistent for a
            bunch of videos.""")
    }
}


# ===========================================================
"""Convenience variable for listing available elements"""
elements = []
for elem in element_options:
    elements.append(elem)


def usage(elem):
    """Return a string containing usage notes for the given element type."""
    usage_str = ''
    for opt, optdef in element_options[elem].iteritems():
        usage_str += optdef.usage_string() + '\n'
    return usage_str
        
# ===========================================================
class Element:
    """A Disc, Menu, or Video with associated options.

    Create an element by calling Element() with the type of element desired,
    along with an identifying name. For example:

        elem = Element('Menu', "Movie trailers")
    
    The Element is automatically filled with default values for the
    corresponding TDL element ('Menu'); these may then be overridden by
    user-defined values."""

    # TODO: Find a more efficient way to create new Elements filled with default
    # values. (Maybe fill a module-level dictionary once at runtime, then copy it
    # when a new Element is created?)
    
    def __init__(self, tag, name):
        """Create a TDL element of the given type, and with the given (unique)
        name, filled with default values for that element type."""
        self.tag = tag
        self.name = name
        if not element_options.has_key(tag):
            print "TDL.Element(): unknown element '%s'" % tag

        else:
            # Fill a dictionary of options with their default values
            self.options = {}
            for key, optdef in element_options[tag].iteritems():
                self.options[key] = copy.copy(optdef.default)

        self.parents = []
        self.children = []


    def set(self, opt, value):
        """Set the given option (with/without leading '-') to the given value."""
        # Consider: Treat value=='' as resetting to default value?
        self.options[opt.lstrip('-')] = copy.copy(value)
    
    
    def get(self, opt):
        """Get the value of the given option."""
        return self.options[opt]
    

    def tdl_string(self):
        """Format element as a TDL-compliant string and return it."""
        tdl = "%s \"%s\"\n" % (self.tag, self.name)
        for key, value in self.options.iteritems():
            # If value has spaces, quote it
            if value.__class__ == str and ' ' in value:
                tdl += "    %s \"%s\"\n" % (key, value)
            # Otherwise, don't
            else:
                tdl += "    %s %s\n" % (key, value)
        return tdl

    

# Self-test; executed when this module is run as a standalone script
if __name__ == "__main__":
    # Print all element/option definitions
    for elem in element_options:
        print "%s element options:" % elem
        for key, optdef in element_options[elem].iteritems():
            print optdef.usage_string()

    # Create one of each element and display them (to ensure that
    # default values are copied correctly)
    vid = Element('Video', "Test video")
    menu = Element('Menu', "Test menu")
    disc = Element('Disc', "Test disc")
    vid.tdl_string()
    menu.tdl_string()
    disc.tdl_string()



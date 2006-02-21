# ###################################################################
# ###################################################################
#
#
#                             UTIL
#
#
# ###################################################################
# ###################################################################
import threading, wx
from libtovid.gui.constants import id_dict

__all__ = ["_", "ID_to_text", "text_to_ID", "element_to_options", "VER_GetFirstChild", 
            "VideoStatSeeker"]
# Hack until gettext works
def _(str):
    return str

def ID_to_text(idtype, id):
    """Convert widget ID numbers to string representations.
    """
    return id_dict[ idtype ][ id ]

def text_to_ID(txt):
    """Convert internal text identifiers into widget ID numbers
    """
    for idtype, subdict in id_dict.iteritems():
        for id, value in subdict.iteritems():
            if value == txt:
                return id
    print "text_to_ID: Couldn't match '%s'. Returning 0." % txt
    return 0

def element_to_options(element):
    from libtovid.gui.options import DiscOptions, MenuOptions, VideoOptions
    """Takes a TDL element and returns a DiscOptions, MenuOptions,
    or VideoOptions object filled with appropriate values.
    """
    if element.tag == 'Disc':
        opts = DiscOptions()
    elif element.tag == 'Menu':
        opts = MenuOptions()
    elif element.tag == 'Video':
        opts = VideoOptions()
    else:
        print "element_to_options: unknown element.tag %s" % element.tag

    opts.fromElement(element)
    return opts

# ===================================================================
#
# VERSION WORKAROUNDS
# "Macro" functions to work around wx.Widgets/python
# version incompatibilities
#
# ===================================================================

# wx.TreeCtrl.GetFirstChild
def VER_GetFirstChild(obj, item):
    # For wx.Widgets >=2.5, cookie isn't needed
    if wx.MAJOR_VERSION == 2 and wx.MINOR_VERSION >= 5:
        return obj.GetFirstChild(item)
    # For other versions, use a dummy cookie
    else:
        return obj.GetFirstChild(item, 1)

# ===================================================================
#
# CLASS DEFINITION
# Video statistics-seeking thread class. Runs in the
# background determining duration and size of input videos
#
# ===================================================================
class VideoStatSeeker(threading.Thread):
    # ==========================================================
    # Class data (will be used as if it is static)
    # ==========================================================
    # List of VideoOptions objects to gather statistics on
    listVideoOptions = []

    # ==========================================================
    # Initialize VideoStatSeeker and Thread base class
    # ==========================================================
    def __init__(self, vidOptions):
        threading.Thread.__init__(self)

        # Add vidOptions to end of queue; thread will later
        # gather statistics and store them back in vidOptions
        self.listVideoOptions.append(vidOptions)
        self.doneWithStats = False

    # ==========================================================
    # Runs in background to gather and save statistics
    # ==========================================================
    def run(self):
        # For each video in queue, get and save stats
        while len(self.listVideoOptions) > 0:
            curOpts = self.listVideoOptions.pop(0)
            #curStatCmd = os.popen("idvid -terse \"%s\" | grep DURATION | sed -e \"s/DURATION://g\"" % curOpts.inFile, 'r')
            #curOpts.duration = curStatCmd.readline().strip('\n ')
            #curStatCmd.readlines()
            #curStatCmd.close()
            #print "VideoStatSeeker: duration for %s is %s" % (curOpts.inFile, curOpts.duration)

        # Done with current batch of statistics
        self.doneWithStats = True
# ===================================================================
# End VideoStatSeeker
# ===================================================================
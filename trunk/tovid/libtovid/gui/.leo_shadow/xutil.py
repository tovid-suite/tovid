#@+leo-ver=4-thin
#@+node:eric.20090722212922.3069:@shadow util.py
# util.py

import threading, wx
from libtovid.gui.constants import id_dict

__all__ = [\
    '_',
    'ID_to_text',
    'text_to_ID',
    'VER_GetFirstChild',
    'VideoStatSeeker']

# Hack until gettext works
def _(str):
    return str

#@+others
#@+node:eric.20090722212922.3072:ID_to_text
def ID_to_text(idtype, id):
    """Convert widget ID numbers to string representations.
    """
    return id_dict[ idtype ][ id ]

#@-node:eric.20090722212922.3072:ID_to_text
#@+node:eric.20090722212922.3073:text_to_ID
def text_to_ID(txt):
    """Convert internal text identifiers into widget ID numbers
    """
    for idtype, subdict in id_dict.iteritems():
        for id, value in subdict.iteritems():
            if value == txt:
                return id
    print("text_to_ID: Couldn't match '%s'. Returning 0." % txt)
    return 0

#@-node:eric.20090722212922.3073:text_to_ID
#@+node:eric.20090722212922.3074:VER_GetFirstChild
# wx.TreeCtrl.GetFirstChild workaround
def VER_GetFirstChild(obj, item):
    # For wx.Widgets >=2.5, cookie isn't needed
    if wx.MAJOR_VERSION == 2 and wx.MINOR_VERSION >= 5:
        return obj.GetFirstChild(item)
    # For other versions, use a dummy cookie
    else:
        return obj.GetFirstChild(item, 1)

#@-node:eric.20090722212922.3074:VER_GetFirstChild
#@+node:eric.20090722212922.3075:class VideoStatSeeker
class VideoStatSeeker(threading.Thread):
    """Video statistics-seeking thread class. Runs in the background determining
    duration and size of input videos."""
    # List of VideoOptions objects to gather statistics on
    listVideoOptions = []

    #@    @+others
    #@+node:eric.20090722212922.3076:__init__
    def __init__(self, vidOptions):
        threading.Thread.__init__(self)
        # Add vidOptions to end of queue; thread will later
        # gather statistics and store them back in vidOptions
        self.listVideoOptions.append(vidOptions)
        self.doneWithStats = False

    #@-node:eric.20090722212922.3076:__init__
    #@+node:eric.20090722212922.3077:run
    def run(self):
        """Run in background to gather and save statistics."""
        # For each video in queue, get and save stats
        while len(self.listVideoOptions) > 0:
            curOpts = self.listVideoOptions.pop(0)
            #curStatCmd = os.popen("idvid -terse \"%s\" | grep DURATION | sed -e \"s/DURATION://g\"" % curOpts.inFile, 'r')
            #curOpts.duration = curStatCmd.readline().strip('\n ')
            #curStatCmd.readlines()
            #curStatCmd.close()
            #print("VideoStatSeeker: duration for %s is %s" % (curOpts.inFile, curOpts.duration))

        # Done with current batch of statistics
        self.doneWithStats = True
    #@-node:eric.20090722212922.3077:run
    #@-others
#@-node:eric.20090722212922.3075:class VideoStatSeeker
#@-others
#@-node:eric.20090722212922.3069:@shadow util.py
#@-leo

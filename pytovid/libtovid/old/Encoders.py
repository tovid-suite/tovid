#! /usr/bin/env python

# ===========================================================
# RuntimeBehavior,
# ffmpegEncoder, mencoderEncoder
# ===========================================================

import os
from Globals import *
from Filetypes import *
from Standards import *

class RuntimeBehavior:
    parallel = False
    debug = False
    overwrite = False
    

# ffmpeg-based encoder
class ffmpegEncoder:
    "Converts a multimedia file using ffmpeg"

    # Make a given VideoElement compliant with its
    # target specification/standard
    #
    # It is up to this function to handle error conditions, and
    # raise an exception on failed encoding.
    #
    # Returns: nothing yet
    def encode( self, infile, outfile, vstandard, astandard ):

        # Assemble and execute command-line for
        # encoding with ffmpeg.
        cmd = "ffmpeg -y -i " + infile

        keys = vstandard.keywords

        # The following conditionals are poorly-written,
        # and need improvement (especially for robustness;
        # there is no 'else' case)

        # Append TV system, if relevant
        if "pal" in keys:
            cmd += " -target pal-"
        elif "ntsc" in keys:
            cmd += " -target ntsc-"

        # Construct a -target option if appropriate and
        # ffmpeg supports this format
        if "dvd" in keys:
            cmd += "dvd"
        elif "svcd" in keys:
            cmd += "svcd"
        elif "vcd" in keys:
            cmd += "vcd"

        # Convert video codecs to names that ffmpeg understands
        if vstandard.codec == "mpeg1":
            cmd += " -vcodec mpeg1video"
        elif vstandard.codec == "mpeg2":
            cmd += " -vcodec mpeg2video"
        else:
            cmd += " -vcodec %s" % vstandard.codec
        
        cmd += " -s %sx%s" % ( vstandard.width, vstandard.height )
        cmd += " -r %s" % vstandard.fps
        cmd += " -acodec %s" % astandard.codec
        cmd += " " + outfile

        print "Encoding with command:"
        print cmd

        ffmpegout = os.popen( cmd, 'r' )
        for line in ffmpegout.readlines():
            print line

        # Get final video (MultimediaFile) and return it.
        # Temporary hack alert! Optimally, this data
        # will be gathered from known output attributes,
        # obviating the need to re-scan the file)

        # Make sure the output file exists
        if os.path.isfile( outfile ):
            print "---- Output file %s exists." % outfile
            return MultimediaFile( outfile )
        else:
            print "!!!! Output file %s does not exist!" % outfile
            # Probably not the best approach, but just for now...
            return None

class mencoderEncoder:
    "Converts a multimedia file using mencoder"
    
    def encode( self, target ):

        # MPEG output is hardcoded for now; this will need to be
        # more generalized if tovid is to ever encode non-MPEG
        # video formats (not likely in the foreseeable future).
        cmd = "mencoder -oac lavc -ovc lavc -of mpeg"

        # Add relevant mpeg encoding format options
        keys = target.vstandard.keywords
        if "VCD" in keys:
            cmd += " -mpegopts format=mpeg1"
        elif "SVCD" in keys:
            cmd += " -mpegopts format=mpeg2"
        elif "DVD" in keys:
            cmd += " -mpegopts format=dvd"

        # Include vbitrate in -mpegopts for correct muxing
        # cmd += ",vbitrate=X"
        
        cmd += " -vf scale=%s:%s" % ( target.vstandard.width, target.vstandard.height )
        cmd += " -lavcopts vcodec=%s:acodec=%s" % \
            ( target.vstandard.codec, target.astandard.codec )
        cmd += " " + infile
        cmd += " -o " + outfile

        print cmd

# Other Encoder implementations:
# mplayer/mpeg2enc-based




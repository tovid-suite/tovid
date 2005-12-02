#! /usr/bin/env python

# ===========================================================
# Element
# ===========================================================

from copy import *
from TDL import *
from Encoders import *

class Element:
    def __init__( self, tag, name, options = {} ):
        self.tag = tag
        self.name = name
        self.options = copy( options )

    # Generate the element
    # This function is extremely hackish at the moment.
    # Needs to be cleaned up
    def generate( self ):
        # Determine a matching standard for
        # any provided format keywords
        keywords = []
        keywords.append( self.options[ 'format' ] )
        
        # Audio standard doesn't care about tvsys,
        # so match it before adding tvsys
        astandard = matchAudioStandard( keywords )

        keywords.append( self.options[ 'tvsys' ] )
        vstandard = matchVideoStandard( keywords )

        print "Matching target standards:"
        astandard.display()
        vstandard.display()

        infile = self.options['in']
        outfile = self.options['out']

        print "Encoding %s to %s" % ( infile, outfile )

        enc = ffmpegEncoder()
        enc.encode( infile, outfile, vstandard, astandard )

class ElementGenerator:
    """Generate the output defined by an Element:
    
        Video: Getting content from an input video file,
            generate a compliant output video file
        Menu: Getting content from background image/audio
            files and a list of titles, generate a
            video menu
        Disc: Getting content from a list of Elements,
            generate and/or burn a video disc"""

    def __init__( self ):
        pass


class VideoGenerator:
    """Convert a video file to a compliant
    disc format according to options in a given
    Video Element"""

    def __init__( self, element ):
        self.element = element

        # Perform common pre-processing
        pass

    def __init_target( self ):
        # Resolution
        fmt = self.element.options[ 'format' ]
        tvsys = self.element.options[ 'tvsys' ]
        
        self.width, self.height = get_resolution( fmt, tvsys )
        self.fps = get_fps( fmt, tvsys )



#! /usr/bin/env python2.4
# mencoder.py

from libtovid.encoder import Encoder
from libtovid.utils import verify_app

class MencoderEncoder(Encoder):
    def __init__(self, video):
        """Create an mencoder encoder for the given video."""
        Encoder.__init__(self, video)
        verify_app('mencoder')
        
    def encode(self):
        """Encode the input video to the target format."""
        cmd = 'mencoder "%s" -o "%s.mpg"' % (self.video['in'], self.basename)
        cmd += ' -oac lavc -ovc lavc -of mpeg '
        # Format
        if self.video['format'] in ['vcd', 'svcd']:
            cmd += ' -mpegopts format=x%s ' % self.video['format']
        else:
            cmd += ' -mpegopts format=dvd '
        
        # Audio settings
        # Adjust sampling rate if necessary
        if self.infile.audio and self.infile.audio.samprate != self.samprate:
            cmd += ' -srate %s -af lavcresample=%s ' % \
                    (self.samprate, self.samprate)
    
        # Video codec
        if self.video['format'] == 'vcd':
            lavcopts = 'vcodec=mpeg1video'
        else:
            lavcopts = 'vcodec=mpeg2video'
        # Audio codec
        if self.video['format'] in ['vcd', 'svcd']:
            lavcopts += ':acodec=mp2'
        else:
            lavcopts += ':acodec=ac3'

        lavcopts += ':abitrate=%s:vbitrate=%s' % (self.abitrate, self.vbitrate)
        # Maximum video bitrate
        lavcopts += ':vrc_maxrate=%s' % self.vbitrate
        if self.video['format'] == 'vcd':
            lavcopts += ':vrc_buf_size=327'
        elif self.video['format'] == 'svcd':
            lavcopts += ':vrc_buf_size=917'
        else:
            lavcopts += ':vrc_buf_size=1835'
        # Set appropriate target aspect
        if self.widescreen:
            lavcopts += ':aspect=16/9'
        else:
            lavcopts += ':aspect=4/3'
        # Put all lavcopts together
        cmd += ' -lavcopts %s ' % lavcopts
    
        # FPS
        if self.video['tvsys'] == 'pal':
            cmd += ' -ofps 25/1 '
        elif self.video['tvsys'] == 'ntsc':
            cmd += ' -ofps 30000/1001 ' # ~= 29.97
    
        # Scale/expand to fit target frame
        if self.scale:
            cmd += ' -vf scale=%s:%s' % self.scale
        if self.expand:
            cmd += ',expand=%s:%s ' % self.expand
        self.run(cmd)



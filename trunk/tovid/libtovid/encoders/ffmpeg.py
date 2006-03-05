#! /usr/bin/env python2.4
# ffmpeg.py

from libtovid.encoder import Encoder
from libtovid.utils import verify_app

class FfmpegEncoder(Encoder):
    def __init__(self, video):
        """Create an ffmpeg encoder for the given video."""
        Encoder.__init__(self, video)
        verify_app('ffmpeg')
        
    def encode(self):
        """Encode the video with ffmpeg."""
        cmd = 'ffmpeg -i "%s" ' % self.video['in']
        if self.video['format'] in ['vcd', 'svcd', 'dvd']:
            cmd += ' -tvstd %s ' % self.video['tvsys']
            cmd += ' -target %s-%s ' % \
                    (self.video['format'], self.video['tvsys'])
        cmd += ' -r %g ' % self.fps
        cmd += ' -ar %s ' % self.samprate

        # Convert scale/expand to ffmpeg's padding system
        if self.scale:
            cmd += ' -s %sx%s ' % self.scale
        if self.expand:
            e_width, e_height = self.expand
            s_width, s_height = self.scale
            h_pad = (e_width - s_width) / 2
            v_pad = (e_height - s_height) / 2
            if h_pad > 0:
                cmd += ' -padleft %s -padright %s ' % (h_pad, h_pad)
            if v_pad > 0:
                cmd += ' -padtop %s -padbottom %s ' % (v_pad, v_pad)
        if self.widescreen:
            cmd += ' -aspect 16:9 '
        else:
            cmd += ' -aspect 4:3 '

        self.run(cmd)

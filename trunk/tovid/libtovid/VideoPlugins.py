#! /usr/bin/env python
# VideoPlugins.py

__doc__ = \
"""This module implements several backends for encoding a video file to
a standard MPEG format such as (S)VCD or DVD.
"""

__all__ = ['VideoPlugin', 'Mpeg2encEncoder', 'MencoderEncoder']

# TODO: Cleanup/modularize, move stuff to classes, make interface simple

import os
import sys

import libtovid
from libtovid.standards import get_resolution
from libtovid.globals import ratio_to_float
from libtovid.log import Log

log = Log('VideoPlugins.py')

class VideoPlugin:
    """Base plugin class; all encoders inherit from this."""
    def __init__(self, video):
        log.info('Creating a VideoPlugin')
        self.video = video
        # List of commands to be executed
        self.commands = []

        self.preproc()

    def preproc(self):
        """Do preprocessing common to all backends."""

        width, height = get_resolution(self.video['format'], self.video['tvsys'])

        # Convert aspect (ratio) to a floating-point value
        src_aspect = ratio_to_float(self.video['aspect'])
        # Use anamorphic widescreen for any video 16:9 or wider
        # (Only DVD supports this)
        if src_aspect >= 1.7 and self.video['format'] == 'dvd':
            tgt_aspect = 16.0/9.0
        else:
            tgt_aspect = 4.0/3.0

        # If aspect matches target, no letterboxing is necessary
        # (Match within a tolerance of 0.05)
        if abs(src_aspect - tgt_aspect) < 0.05:
            scale = (width, height)
            expand = False
        # If aspect is wider than target, letterbox vertically
        elif src_aspect > tgt_aspect:
            scale = (width, height * tgt_aspect / src_aspect)
            expand = (width, height)
        # Otherwise (rare), letterbox horizontally
        else:
            scale = (width * src_aspect / tgt_aspect, height)
            expand = (width, height)

        # Remember scale/expand sizes and target aspect
        self.scale = scale
        self.expand = expand
        self.tgt_aspect = tgt_aspect


    def run(self):
        """Execute all queued commands, with proper stream redirection and
        verbosity level. Subclasses should override this function if they need
        different runtime behavior."""
        # TODO: Proper stream redirection and verbosity level
        for cmd in self.commands:
            log.info("VideoPlugin: Running the following command:")
            log.info(cmd)
            # TODO: Catch failed execution
            cin, cout = os.popen4(cmd, 1)
            for line in cout.readlines():
                # Strip extra line breaks
                line = line.rstrip('\n\r')
                log.debug(line)


class Mpeg2encEncoder (VideoPlugin):
    def __init__(self, video):
        """Create an mplayer/mpeg2enc/mplex encoder for the given video."""
        VideoPlugin.__init__(self, video)
        # Add appropriate commands to list
        self.get_mplayer_cmd()
        self.get_mpeg2enc_cmd()
        self.get_mplex_cmd()
        
    def get_mplayer_cmd(self):
        """Get mplayer command-line for making a video compliant with the given
        format and tvsys, while applying named custom filters, writing output to
        stream.yuv."""
        
        # TODO: Custom mplayer options, subtitles, interlacing, safe area, corresp.
        # to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE, etc.
        
        # TODO: Determine aspect ratio and scale appropriately (in a separate
        # function, preferably).
    
        cmd = 'mplayer "%s" ' % self.video['in']
        cmd += ' -vo yuv4mpeg -nosound -benchmark -noframedrop '
        # TODO: Support subtitles. For now, use default tovid behavior.
        cmd += ' -noautosub '
        # TODO: Avoid scaling unless necessary
        cmd += ' -vf scale=%s:%s ' % self.scale
        # Filters
        if 'denoise' in self.video['filters']:
            cmd += ' -vf-add hqdn3d '
        if 'contrast' in self.video['filters']:
            cmd += ' -vf-add pp=al:f '
        if 'deblock' in self.video['filters']:
            cmd += ' -vf-add pp=hb/vb '
    
        self.commands.append(cmd)
    
    
    def get_mpeg2enc_cmd(self):
        """Get mpeg2enc command-line suitable for encoding a video stream to the
        given format and TV system, at the given aspect ratio (if the format
        supports it)."""
    
        # TODO: Control over quality (bitrate/quantization) and disc split size,
        # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
        
        # Missing options (compared to tovid)
        # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    
        cmd = 'cat stream.yuv | mpeg2enc '
        if self.video['tvsys'] == 'pal':
            cmd += ' -F 3 -n p '
        elif self.video['tvsys'] == 'ntsc':
            cmd += ' -F 4 -n n '
    
        if self.video['format'] == 'vcd':
            cmd += ' -f 1 '
        elif self.video['format'] == 'svcd':
            cmd += ' -f 4 '
        elif 'dvd' in self.video['format']:
            cmd += ' -f 8 '
    
        if self.video['aspect'] == '4:3':
            cmd += ' -a 2 '
        elif self.video['aspect'] == '16:9':
            cmd += ' -a 3 '
        cmd += ' -o "%s.m2v"' % self.video['out']
    
        self.commands.append(cmd)
    
    
    def get_mplex_cmd(self):
        """Get mplex command-line suitable for muxing streams with the given format
        and TV system."""
    
        cmd = 'mplex '
        if self.video['format'] == 'vcd':
            cmd += '-f 1 '
        elif self.video['format'] == 'dvd-vcd':
            cmd += '-V -f 8 '
        elif self.video['format'] == 'svcd':
            cmd += '-V -f 4 -b 230 '
        elif self.video['format'] == 'half-dvd':
            cmd += '-V -f 8 -b 300 '
        elif self.video['format'] == 'dvd':
            cmd += '-V -f 8 -b 400 '
        # elif format == 'kvcd':
        #   cmd += '-V -f 5 -b 350 -r 10800 '
    
        self.commands.append(cmd)



class MencoderEncoder (VideoPlugin):
    def __init__(self, video):
        """Create an mencoder encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.get_mencoder_cmd()
        
    def get_mencoder_cmd(self):
        """Get mencoder command-line suitable for encoding the given video to
        its target format."""
    
        cmd = 'mencoder "%s" -o "%s.mpg"' % (self.video['in'], self.video['out'])
        cmd += ' -oac lavc -ovc lavc -of mpeg '
        
        if self.video['format'] in ['vcd', 'svcd']:
            cmd += ' -mpegopts format=x%s ' % self.video['format']
        else:
            cmd += ' -mpegopts format=dvd '
    
        # TODO: Move all aspect/scaling stuff into a separate
        # function, so all backends can benefit from it
    
        
        # TODO: Implement safe area calculation
        
        # Audio settings
        # The following cause segfaults on mencoder 1.0pre7try2-3.3.6 (Gentoo)
        # when the input file's audio bitrate already matches.
        # Can anyone confirm?
        if 'dvd' in self.video['format']:
            cmd += ' -srate 48000 -af lavcresample=48000 '
        else:
            cmd += ' -srate 44100 -af lavcresample=44100 '
            pass
    
    
        # Video settings
        # Construct lavcopts
    
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

        # TODO: Preprocessing: Set audio/video bitrates
        # based on target format, quality, or user-defined values

        vbitrate = self.video['vbitrate']
        abitrate = self.video['abitrate']
        
        # Audio and video bitrates
        if self.video['format'] == 'vcd':
            abitrate = 224
            vbitrate = 1152
        else:
            # If user didn't override, use reasonable defaults
            if not vbitrate:
                # TODO: Adjust bitrate based on -quality
                if self.video['format'] in ['svcd', 'dvd-vcd']:
                    vbitrate = 2600
                else:
                    vbitrate = 7000
            if not abitrate:
                abitrate = 224

        lavcopts += ':abitrate=%s:vbitrate=%s' % (abitrate, vbitrate)

        # Maximum video bitrate
        lavcopts += ':vrc_maxrate=%s' % vbitrate
        if self.video['format'] == 'vcd':
            lavcopts += ':vrc_buf_size=327'
        elif self.video['format'] == 'svcd':
            lavcopts += ':vrc_buf_size=917'
        else:
            lavcopts += ':vrc_buf_size=1835'
    
        # Set appropriate target aspect
        if self.tgt_aspect == 16.0/9.0:
            lavcopts += ':aspect=16/9'
        else:
            lavcopts += ':aspect=4/3'
    
        # Put it all together
        cmd += ' -lavcopts %s ' % lavcopts
    
        # FPS
        if self.video['tvsys'] == 'pal':
            cmd += ' -ofps 25/1 '
        else:
            cmd += ' -ofps 30000/1001 ' # ~= 29.97
    
    
        # Scale/expand to fit target frame
        cmd += ' -vf scale=%s:%s' % self.scale
        if self.expand:
            cmd += ',expand=%s:%s ' % self.expand
    
        self.commands.append(cmd)



"""
For DVD:

Filtering: -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup

-lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:

mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg

"""

"""
Notes:


Command-line option variables:

# Filters
mplayer:
SUBTITLES
    -noautosub
    -sub FILE
YUV4MPEG_ILACE
    ''
    :interlaced
    :interlaced_bf
VF_PRE
    ''
    -vf-pre il=d:d

VID_SCALE
    ''
    -vf-add scale=$INNER_WIDTH:$INNER_HEIGHT
+   -vf-add expand=$TGT_WIDTH:$TGT_HEIGHT

VF_POST
    ''
    -vf-pre il=i:i
MPLAYER_OPTS
    (user-defined)

YUVDENOISE
    ''
    yuvdenoise |
ADJUST_FPS
    ''
    yuvfps -s $FORCE_FPSRATIO -r $TGT_FPSRATIO $VERBOSE |
    yuvfps -r $TGT_FPSRATIO $VERBOSE |


mpeg2enc
DISC_SIZE
    ''
    '4500'
    '700'
    (user-defined)

NONVIDEO_BITRATE
MTHREAD

MPEG2_FMT
+   !vcd: -b $VID_BITRATE

MPEG2_QUALITY
    vcd: -4 2 -2 1 -H
    other: -4 2 -2 1 -q $QUANT -H


mencoder command-lines to build upon:

For DVD:

mencoder -oac lavc -ovc lavc -of mpeg -mpegopts format=dvd -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup -srate 48000 -af lavcresample=48000,equalizer=11:11:10:8:8:8:8:10:10:12 -lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:

mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg


"""

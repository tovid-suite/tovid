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
from libtovid.utils import ratio_to_float
from libtovid.log import Log
from libtovid.filetypes import MultimediaFile
from libtovid.utils import which

log = Log('VideoPlugins.py')

class VideoPlugin:
    """Base plugin class; all encoders inherit from this."""
    def __init__(self, video):
        log.info('Creating a VideoPlugin')
        self.video = video
        # List of commands to be executed (in order)
        self.commands = []
        self.identify_infile()
        self.preproc()

    def identify_infile(self):
        """Gather information about the input file and store it locally."""
        log.debug('Creating MultimediaFile for "%s"' % self.video['in'])
        self.infile = MultimediaFile(self.video['in'])
        self.infile.display()
        
    def preproc(self):
        """Do preprocessing common to all backends."""
        width, height = get_resolution(self.video['format'], self.video['tvsys'])
        # Convert aspect (ratio) to a floating-point value
        src_aspect = ratio_to_float(self.video['aspect'])
        # Use anamorphic widescreen for any video 16:9 or wider
        # (Only DVD supports this)
        if src_aspect >= 1.7 and self.video['format'] == 'dvd':
            tgt_aspect = 16.0/9.0
            self.widescreen = True
        else:
            tgt_aspect = 4.0/3.0
            self.widescreen = False
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
        # If infile is already the correct size, don't scale
        if scale == self.infile.video.size:
            scale = False
            log.debug('Infile resolution matches target resolution.')
            log.debug('No scaling will be done.')
        # Remember scale/expand sizes and target aspect
        self.scale = scale
        self.expand = expand
        self.tgt_aspect = tgt_aspect
        # Other commonly-used values
        if 'dvd' in self.video['format']:
            self.samprate = 48000
        else:
            self.samprate = 44100
        if self.video['tvsys'] == 'pal':
            self.fps = '25.0'
        elif self.video['tvsys'] == 'ntsc':
            self.fps = '29.97'

    def verify_app(self, appname):
        """Verify that the given appname is available; if not, log an error
        and exit."""
        app = which(appname)
        if not app:
            # TODO: A more friendly error message
            log.error("Cannot find '%s' in your path." % app)
            log.error("You may need to (re)install it.")
            sys.exit()
            
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


class Mpeg2encEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an mplayer/mpeg2enc/mplex encoder for the given video."""
        VideoPlugin.__init__(self, video)
        # TODO: os.mkfifo("/work/directory/stream.yuv")
        # Add appropriate commands to list
        self.commands.append(self.get_mplayer_cmd())
        self.commands.append(self.get_mpeg2enc_cmd())
        self.commands.append(self.get_mplex_cmd())
        
    def get_mplayer_cmd(self):
        """Get mplayer command-line for making a video compliant with the given
        format and tvsys, while applying named custom filters, writing output to
        stream.yuv."""
        # TODO: Custom mplayer options, subtitles, interlacing, safe area,
        # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
        # etc.
        cmd = 'mplayer "%s" ' % self.video['in']
        cmd += ' -vo yuv4mpeg -nosound -benchmark -noframedrop '
        # TODO: Support subtitles. For now, use default tovid behavior.
        cmd += ' -noautosub '
        # TODO: Avoid scaling unless necessary
        cmd += ' -vf scale=%s:%s ' % self.scale
        cmd += ' -vf-add expand=%s:%s ' % self.expand
        # Filters
        if 'denoise' in self.video['filters']:
            cmd += ' -vf-add hqdn3d '
        if 'contrast' in self.video['filters']:
            cmd += ' -vf-add pp=al:f '
        if 'deblock' in self.video['filters']:
            cmd += ' -vf-add pp=hb/vb '
        return cmd
    
    def get_mpeg2enc_cmd(self):
        """Get mpeg2enc command-line suitable for encoding a video stream to the
        given format and TV system, at the given aspect ratio (if the format
        supports it)."""
        # TODO: Control over quality (bitrate/quantization) and disc split size,
        # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
        # Missing options (compared to tovid)
        # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
        cmd = 'cat stream.yuv | mpeg2enc '
        # TV system
        if self.video['tvsys'] == 'pal':
            cmd += ' -F 3 -n p '
        elif self.video['tvsys'] == 'ntsc':
            cmd += ' -F 4 -n n '
        # Format
        if self.video['format'] == 'vcd':
            cmd += ' -f 1 '
        elif self.video['format'] == 'svcd':
            cmd += ' -f 4 '
        elif 'dvd' in self.video['format']:
            cmd += ' -f 8 '
        # Aspect ratio
        if self.video['aspect'] == '4:3':
            cmd += ' -a 2 '
        elif self.video['aspect'] == '16:9':
            cmd += ' -a 3 '
        cmd += ' -o "%s.m2v"' % self.video['out']
        return cmd
    
    def get_mplex_cmd(self):
        """Get mplex command-line suitable for muxing streams with the given
        format and TV system."""
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
        return cmd


class MencoderEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an mencoder encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.verify_app('mencoder')
        self.commands.append(self.get_mencoder_cmd())
        
    def get_mencoder_cmd(self):
        """Get mencoder command-line suitable for encoding the given video to
        its target format."""
        cmd = 'mencoder "%s" -o "%s.mpg"' % (self.video['in'], self.video['out'])
        cmd += ' -oac lavc -ovc lavc -of mpeg '
        # Format
        if self.video['format'] in ['vcd', 'svcd']:
            cmd += ' -mpegopts format=x%s ' % self.video['format']
        else:
            cmd += ' -mpegopts format=dvd '
        # TODO: Move all aspect/scaling stuff into a separate
        # function, so all backends can benefit from it
        # TODO: Implement safe area calculation
        
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
        return cmd


class FfmpegEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an ffmpeg encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.verify_app('ffmpeg')
        self.commands.append(self.get_ffmpeg_cmd())
        
    def get_ffmpeg_cmd(self):
        """Return ffmpeg command for encoding the current video."""
        cmd = 'ffmpeg -i "%s" ' % self.video['in']
        # Format and TV system
        if self.video['format'] in ['vcd', 'svcd', 'dvd']:
            cmd += ' -tvstd %s ' % self.video['tvsys']
            cmd += ' -target %s-%s ' % \
                    (self.video['format'], self.video['tvsys'])
        # FPS
        if self.video['tvsys'] == 'pal':
            cmd += ' -r 25.00 '
        elif self.video['tvsys'] == 'ntsc':
            cmd += ' -r 29.97 '
        # Audio sampling rate
        if 'dvd' in self.video['format']:
            cmd += ' -ar 48000 '
        else:
            cmd += ' -ar 44100 '

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

        return cmd
    

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

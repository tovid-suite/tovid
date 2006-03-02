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
from subprocess import *

import libtovid
from libtovid.standards import get_resolution
from libtovid.utils import ratio_to_float
from libtovid.log import Log
from libtovid.filetypes import MultimediaFile
from libtovid.utils import which
from libtovid.globals import Config

log = Log('VideoPlugins.py')

class VideoPlugin:
    """Base plugin class; all encoders inherit from this."""
    def __init__(self, video):
        log.info('Creating a VideoPlugin')
        self.video = video
        # Base name for output files
        self.basename = os.path.abspath(video['out'])
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
        # TODO: Calculate safe area
        # Other commonly-used values
        if 'dvd' in self.video['format']:
            samprate = 48000
        else:
            samprate = 44100
        if self.video['tvsys'] == 'pal':
            fps = '25.0'
        elif self.video['tvsys'] == 'ntsc':
            fps = '29.97'
        
        # Set audio/video bitrates based on target format, quality, or
        # user-defined values (if given)
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

        # Everything exported from this function:
        self.abitrate = abitrate
        self.vbitrate = vbitrate
        self.scale = scale
        self.expand = expand
        self.tgt_aspect = tgt_aspect
        self.samprate = samprate
        self.fps = fps

    def verify_app(self, appname):
        """Verify that the given appname is available; if not, log an error
        and exit."""
        app = which(appname)
        if not app:
            # TODO: A more friendly error message
            log.error("Cannot find '%s' in your path." % appname)
            log.error("You may need to (re)install it.")
            sys.exit()
        else:
            log.debug("Found %s" % app)

    def verify_apps(self, applist):
        for app in applist:
            self.verify_app(app)
            
    def run(self, command, wait=True):
        """Execute the given command, with proper stream redirection and
        verbosity. Wait for execution to finish, if wait is True. Subclasses
        should override this function if they need different runtime
        behavior."""
        log.info("VideoPlugin: Running the following command:")
        log.info(command)
        process = Popen(command, shell=True, bufsize=1, \
                stdout=PIPE, stderr=PIPE, close_fds=True)
        if wait:
            for line in process.stdout.readlines():
                log.info(line.rstrip('\n'))
            for line in process.stderr.readlines():
                log.debug(line.rstrip('\n'))
            log.info("Waiting for process to terminate...")
            process.wait()


class Mpeg2encEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an mplayer/mpeg2enc/mplex encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.verify_apps(['mplayer', 'mpeg2enc', 'ffmpeg', 'mp2enc', 'mplex'])
        self.yuvfile = '%s/stream.yuv' % Config().workdir
        if video['format'] in ['vcd', 'svcd']:
            self.asuf = 'mpa'
        else:
            self.asuf = 'ac3'

    def encode(self):
        """Start encoding."""
        try:
            os.remove(self.yuvfile)
        except:
            pass
        os.mkfifo(self.yuvfile)
        self.rip_wav()
        self.encode_wav()
        self.rip_video()
        self.encode_video()
        self.mplex_streams()
        
    def rip_video(self):
        """Rip the input video to yuv4mpeg format, and write to stream.yuv
        pipe."""
        # TODO: Custom mplayer options, subtitles, interlacing,
        # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
        # etc.
        cmd = 'mplayer "%s" ' % self.video['in']
        cmd += ' -vo yuv4mpeg:file=%s ' % self.yuvfile
        cmd += ' -nosound -benchmark -noframedrop '
        # TODO: Support subtitles. For now, use default tovid behavior.
        cmd += ' -noautosub '
        if self.scale:
            cmd += ' -vf scale=%s:%s ' % self.scale
        if self.expand:
            cmd += ' -vf-add expand=%s:%s ' % self.expand
        # Filters
        if 'denoise' in self.video['filters']:
            cmd += ' -vf-add hqdn3d '
        if 'contrast' in self.video['filters']:
            cmd += ' -vf-add pp=al:f '
        if 'deblock' in self.video['filters']:
            cmd += ' -vf-add pp=hb/vb '
        self.run(cmd, wait=False)
    
    def encode_video(self):
        """Encode the yuv4mpeg stream to the given format and TV system."""
        # TODO: Control over quality (bitrate/quantization) and disc split size,
        # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
        # Missing options (compared to tovid)
        # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
        # TODO: Consider using os.pipe?
        cmd = 'cat %s | mpeg2enc ' % self.yuvfile
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
        cmd += ' -o "%s.m2v"' % self.basename
        self.run(cmd)
    
    def generate_silent_wav(self):
        """Generate a silent audio .wav."""
        cmd = 'cat /dev/zero | sox -t raw -c 2 '
        cmd += ' -r %s ' % self.samprate
        cmd += ' -w -s -t wav '
        cmd += ' "%s.wav" ' % self.basename
        # TODO: Use actual video duration
        cmd += ' trim 0 5'
        self.run(cmd)

    def rip_wav(self):
        """Rip a .wav of the audio stream from the input video."""
        cmd = 'mplayer -quiet -vc null -vo null '
        cmd += ' -ao pcm:waveheader:file=%s.wav ' % self.basename
        cmd += ' "%s"' % self.video['in']
        self.run(cmd)

    def encode_wav(self):
        """Encode the audio .wav to the target format."""
        if self.video['format'] in ['vcd', 'svcd']:
            cmd = 'cat "%s.wav" ' % self.basename
            cmd += '| mp2enc -s -V '
            cmd += ' -b %s ' % self.abitrate
            cmd += ' -o "%s.mpa" ' % self.basename
        else:
            cmd = 'ffmpeg -i "%s.wav" ' % self.basename
            cmd += ' -ab %s ' % self.abitrate
            cmd += ' -ar %s ' % self.samprate
            cmd += ' -ac 2 -acodec ac3 -y '
            cmd += ' "%s.%s"' % (self.basename, self.asuf)
        self.run(cmd)

    def mplex_streams(self):
        """Multiplex the audio and video streams."""
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
        cmd += ' "%s.m2v" ' % self.basename
        cmd += ' "%s.%s" ' % (self.basename, self.asuf)
        cmd += ' -o "%s.mpg"' % self.basename
        self.run(cmd)


class MencoderEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an mencoder encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.verify_app('mencoder')
        
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


class FfmpegEncoder(VideoPlugin):
    def __init__(self, video):
        """Create an ffmpeg encoder for the given video."""
        VideoPlugin.__init__(self, video)
        self.verify_app('ffmpeg')
        
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
    

"""
Notes:

For DVD:
Filtering: -vf hqdn3d,crop=624:464:8:8,pp=lb,scale=704:480,harddup
-lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=18:acodec=ac3:abitrate=192:aspect=4/3 -ofps 30000/1001 -o Bill_Linda-DVD.mpg bill.mjpeg

For SVCD:
mencoder 100_0233.MOV  -oac lavc -ovc lavc -of mpeg -mpegopts format=xsvcd  -vf   scale=480:480,harddup -noskip -mc 0 -srate 44100 -af lavcresample=44100 -lavcopts   vcodec=mpeg2video:mbd=2:keyint=18:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224 -ofps 30000/1001   -o movie.mpg


Stuff not yet used in plugins:

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

"""

#! /usr/bin/env python2.4
# mpeg2enc.py

from libtovid.encoder import Encoder
from libtovid.utils import verify_app

class Mpeg2encEncoder(Encoder):
    def __init__(self, video):
        """Create an mplayer/mpeg2enc/mplex encoder for the given video."""
        Encoder.__init__(self, video)
        for app in ['mplayer', 'mpeg2enc', 'ffmpeg', 'mp2enc', 'mplex']:
            verify_app(app)
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


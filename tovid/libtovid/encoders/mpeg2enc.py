#! /usr/bin/env python2.4
# mpeg2enc.py

__all__ = ['encode']

import os

from libtovid.utils import verify_app, run

for app in ['mplayer', 'mpeg2enc', 'ffmpeg', 'mp2enc', 'mplex']:
    verify_app(app)

def encode(infile, options):
    """Encode infile (a MultimediaFile) with mpeg2enc, using the given options."""

    outfile = options['out']
    # YUV raw video FIFO, for piping video from mplayer to mpeg2enc
    yuvfile = '%s.yuv' % outfile
    try:
        os.remove(yuvfile)
    except:
        pass
    os.mkfifo(yuvfile)
    
    # Filenames for intermediate streams (wav/ac3/m2v etc.)
    wavfile = '%s.wav' % outfile
    # Appropriate suffix for audio stream
    if options['format'] in ['vcd', 'svcd']:
        audiofile = '%s.mpa' % outfile
    else:
        audiofile = '%s.ac3' % outfile
    # Appropriate suffix for video stream
    if options['format'] == 'vcd':
        videofile = '%s.m1v' % outfile
    else:
        videofile = '%s.m2v' % outfile
    # Do audio
    rip_wav(outfile, wavfile, options)
    encode_wav(wavfile, audiofile, options)
    # Do video
    rip_video(outfile, yuvfile, options)
    encode_video(yuvfile, videofile, options)
    # Combine audio and video
    mplex_streams(videofile, audiofile, outfile, options)
    
def rip_video(infile, yuvfile, options):
    """Rip the input video to yuv4mpeg format, and write to stream.yuv
    pipe."""
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = 'mplayer "%s" ' % infile
    cmd += ' -vo yuv4mpeg:file=%s ' % yuvfile
    cmd += ' -nosound -benchmark -noframedrop '
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd += ' -noautosub '
    if options['scale']:
        cmd += ' -vf scale=%s:%s ' % options['scale']
    if options['expand']:
        cmd += ' -vf-add expand=%s:%s ' % options['expand']
    # Filters
    filters = options['filters']
    if 'denoise' in filters:
        cmd += ' -vf-add hqdn3d '
    if 'contrast' in filters:
        cmd += ' -vf-add pp=al:f '
    if 'deblock' in filters:
        cmd += ' -vf-add pp=hb/vb '
    run(cmd, "Ripping video to yuv4mpeg format", wait=False)

def encode_video(yuvfile, videofile, options):
    """Encode the yuv4mpeg stream to the given format and TV system."""
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    # TODO: Consider using os.pipe?
    cmd = 'cat "%s" | mpeg2enc ' % yuvfile
    # TV system
    if options['tvsys'] == 'pal':
        cmd += ' -F 3 -n p '
    elif options['tvsys'] == 'ntsc':
        cmd += ' -F 4 -n n '
    # Format
    format = options['format']
    if format == 'vcd':
        cmd += ' -f 1 '
    elif format == 'svcd':
        cmd += ' -f 4 '
    elif 'dvd' in format:
        cmd += ' -f 8 '
    # Aspect ratio
    if options['widescreen']:
        cmd += ' -a 3 '
    else:
        cmd += ' -a 2 '
    cmd += ' -o "%s"' % videofile
    run(cmd, "Encoding yuv4mpeg video stream to MPEG format")

def generate_silent_wav(wavfile, options):
    """Generate a silent audio .wav."""
    cmd = 'cat /dev/zero | sox -t raw -c 2 '
    cmd += ' -r %s ' % options['samprate']
    cmd += ' -w -s -t wav '
    cmd += ' "%s" ' % wavfile
    # TODO: Use actual video duration
    cmd += ' trim 0 5'
    run(cmd, "Generating a silent .wav file")

def rip_wav(infile, wavfile, options):
    """Rip a .wav of the audio stream from the input video."""
    cmd = 'mplayer -quiet -vc null -vo null '
    cmd += ' -ao pcm:waveheader:file=%s ' % wavfile
    cmd += ' "%s"' % infile
    run(cmd, "Ripping audio to .wav format")

def encode_wav(wavfile, audiofile, options):
    """Encode the audio .wav to the target format."""
    if options['format'] in ['vcd', 'svcd']:
        cmd = 'cat "%s" ' % wavfile
        cmd += '| mp2enc -s -V '
        cmd += ' -b %s ' % options['abitrate']
        cmd += ' -o "%s"' % audiofile
        run(cmd, "Encoding .wav to MP2 format")
    else:
        cmd = 'ffmpeg -i "%s" ' % wavfile
        cmd += ' -ab %s ' % options['abitrate']
        cmd += ' -ar %s ' % options['samprate']
        cmd += ' -ac 2 -acodec ac3 -y '
        cmd += ' "%s"' % audiofile
        run(cmd, "Encoding .wav to AC3 format")

def mplex_streams(vstream, astream, outfile, options):
    """Multiplex the audio and video streams."""
    format = options['format']
    cmd = 'mplex '
    if format == 'vcd':
        cmd += '-f 1 '
    elif format == 'dvd-vcd':
        cmd += '-V -f 8 '
    elif format == 'svcd':
        cmd += '-V -f 4 -b 230 '
    elif format == 'half-dvd':
        cmd += '-V -f 8 -b 300 '
    elif format == 'dvd':
        cmd += '-V -f 8 -b 400 '
    # elif format == 'kvcd':
    #   cmd += '-V -f 5 -b 350 -r 10800 '
    cmd += ' "%s" "%s" -o "%s"' % (vstream, astream, outfile)
    run(cmd, "Multiplexing audio and video streams")


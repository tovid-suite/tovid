#! /usr/bin/env python2.4
# mpeg2enc.py

__all__ = ['encode']

import os

from libtovid.cli import Command

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
    rip_wav(infile.filename, wavfile, options)
    encode_wav(wavfile, audiofile, options)
    # Do video
    rip_video(infile.filename, yuvfile, options)
    encode_video(yuvfile, videofile, options)
    # Combine audio and video
    mplex_streams(videofile, audiofile, outfile, options)
    
def rip_video(infile, yuvfile, options):
    """Rip input video to yuv4mpeg format, and write to stream.yuv pipe."""
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = Command('mplayer')
    cmd.append('"%s"' % infile)
    cmd.append('-vo yuv4mpeg:file=%s' % yuvfile)
    cmd.append('-nosound -benchmark -noframedrop')
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd.append('-noautosub')
    if options['scale']:
        cmd.append('-vf scale=%s:%s' % options['scale'])
    if options['expand']:
        cmd.append('-vf-add expand=%s:%s' % options['expand'])
    # Filters
    filters = options['filters']
    if 'denoise' in filters:
        cmd.append('-vf-add hqdn3d')
    if 'contrast' in filters:
        cmd.append('-vf-add pp=al:f')
    if 'deblock' in filters:
        cmd.append('-vf-add pp=hb/vb')
    cmd.purpose = "Ripping video to yuv4mpeg format"
    cmd.run(wait=False)


def encode_video(yuvfile, videofile, options):
    """Encode the yuv4mpeg stream to the given format and TV system."""
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    cmd = Command('mpeg2enc')
    cmd.purpose = "Encoding yuv4mpeg video stream to MPEG format"
    # TV system
    if options['tvsys'] == 'pal':
        cmd.append('-F 3 -n p')
    elif options['tvsys'] == 'ntsc':
        cmd.append('-F 4 -n n')
    # Format
    format = options['format']
    if format == 'vcd':
        cmd.append('-f 1')
    elif format == 'svcd':
        cmd.append('-f 4')
    elif 'dvd' in format:
        cmd.append('-f 8')
    # Aspect ratio
    if options['widescreen']:
        cmd.append('-a 3')
    else:
        cmd.append('-a 2')
    cmd.append('-o "%s"' % videofile)

    # Pipe the .yuv file into mpeg2enc
    cmd.prepend('cat "%s" | ' % yuvfile)
    cmd.run()

def generate_silent_wav(wavfile, options):
    """Generate a silent audio .wav."""
    cmd = Command('sox')
    cmd.purpose = "Generating a silent .wav file"
    cmd.append('sox -t raw -c 2')
    cmd.append('-r %s' % options['samprate'])
    cmd.append('-w -s -t wav')
    cmd.append('"%s"' % wavfile)
    # TODO: Use actual video duration
    cmd.append('trim 0 5')
    # Pipe zero-data into sox to get silence
    cmd.prepend('cat /dev/zero | ')
    cmd.run()

def rip_wav(infile, wavfile, options):
    """Rip a .wav of the audio stream from the input video."""
    cmd = Command('mplayer')
    cmd.purpose = "Ripping audio to .wav format"
    cmd.append('-quiet -vc null -vo null')
    cmd.append('-ao pcm:waveheader:file=%s' % wavfile)
    cmd.append('"%s"' % infile)
    cmd.run()

def encode_wav(wavfile, audiofile, options):
    """Encode the audio .wav to the target format."""
    if options['format'] in ['vcd', 'svcd']:
        cmd = Command('mp2enc')
        cmd.purpose = "Encoding .wav to MP2 format"
        cmd.append('-s -V')
        cmd.append('-b %s' % options['abitrate'])
        cmd.append('-o "%s"' % audiofile)
        # Pipe wav file into mp2enc
        cmd.prepend('cat "%s" | ' % wavfile)
        cmd.run()
    else:
        cmd = Command('ffmpeg')
        cmd.purpose = "Encoding .wav to AC3 format"
        cmd.append('-i "%s"' % wavfile)
        cmd.append('-ab %s ' % options['abitrate'])
        cmd.append('-ar %s ' % options['samprate'])
        cmd.append('-ac 2 -acodec ac3 -y')
        cmd.append('"%s"' % audiofile)
        cmd.run()

def mplex_streams(vstream, astream, outfile, options):
    """Multiplex the audio and video streams."""
    cmd = Command('mplex')
    cmd.purpose = "Multiplexing audio and video streams"
    format = options['format']
    if format == 'vcd':
        cmd.append('-f 1')
    elif format == 'dvd-vcd':
        cmd.append('-V -f 8')
    elif format == 'svcd':
        cmd.append('-V -f 4 -b 230')
    elif format == 'half-dvd':
        cmd.append('-V -f 8 -b 300')
    elif format == 'dvd':
        cmd.append('-V -f 8 -b 400')
    # elif format == 'kvcd':
    #   cmd.append('-V -f 5 -b 350 -r 10800 '
    cmd.append('"%s" "%s" -o "%s"' % (vstream, astream, outfile))
    cmd.run()


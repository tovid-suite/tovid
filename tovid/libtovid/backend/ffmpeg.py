#! /usr/bin/env python
# ffmpeg.py

"""Video encoding and identification using ``ffmpeg``.
"""

__all__ = [
    'encode',
    'encode_audio',
    'identify',
]

import re
from libtovid import log
from libtovid import cli

def encode(source, target, **kw):
    """Encode a multimedia video using ffmpeg.

        source
            Input MediaFile
        target
            Output MediaFile
        kw
            Keyword arguments to customize encoding behavior
    
    Supported keywords:
    
        quant
            Minimum quantization, from 1-31 (1 being fewest artifacts)
        vbitrate
            Maximum video bitrate, in kilobits per second.
        abitrate
            Audio bitrate, in kilobits per second
        interlace
            'top' or 'bottom', to do interlaced encoding with
            top or bottom field first

    For example::
    
        ffmpeg_encode(source, target, quant=4, vbitrate=7000)
    """
    cmd = cli.Command('ffmpeg', '-y', '-i', source.filename)

    # Use format/tvsys that ffmpeg knows about
    if target.format in ['vcd', 'svcd', 'dvd']:
        cmd.add('-tvstd', target.tvsys,
                '-target', '%s-%s' % (target.tvsys, target.format))

    # Interpret keyword arguments
    if 'quant' in kw:
        cmd.add('-qmin', kw['quant'], '-qmax', 31)
    if 'vbitrate' in kw:
        cmd.add('-b', '%dk' % kw['vbitrate'])
    if 'abitrate' in kw:
        cmd.add('-ab', '%dk' % kw['abitrate'])
    if 'interlace' in kw:
        if kw['interlace'] == 'bottom':
            cmd.add('-top', 0, '-flags', '+alt+ildct+ilme')
        elif kw['interlace'] == 'top':
            cmd.add('-top', 1, '-flags', '+alt+ildct+ilme')

    # Frame rate and audio sampling rate
    cmd.add('-r', target.fps,
            '-ar', target.samprate)
    
    # Convert scale/expand to ffmpeg's padding system
    if target.scale:
        cmd.add('-s', '%sx%s' % target.scale)
        # Letterbox if necessary
        if target.expand != target.scale:
            e_width, e_height = target.expand
            s_width, s_height = target.scale
            h_pad = (e_width - s_width) / 2
            v_pad = (e_height - s_height) / 2
            if h_pad > 0:
                cmd.add('-padleft', h_pad, '-padright', h_pad)
            if v_pad > 0:
                cmd.add('-padtop', v_pad, '-padbottom', v_pad)

    # Aspect
    if target.widescreen:
        cmd.add('-aspect', '16:9')
    else:
        cmd.add('-aspect', '4:3')

    cmd.add(target.filename)    
    cmd.run()
    

def encode_audio(source, audiofile, target):
    """Encode the audio stream in a source file to a target format, saving
    to the given filename.

        source
            Input MediaFile
        audiofile
            Filename for encoded audio
        target
            Output MediaFile

    If no audio is present in the source file, encode silence.
    """
    cmd = cli.Command('ffmpeg')

    # If source has audio, encode it
    if source.has_audio:
        cmd.add('-i', source.filename)
    # Otherwise, encode silence (minimum 4 seconds)
    else:
        cmd.add('-f', 's16le', '-i', '/dev/zero')
        if source.length < 4:
            cmd.add('-t', '4.0')
        else:
            cmd.add('-t', '%f' % source.length)

    cmd.add('-vn', '-ac', '2', '-ab', '224k')
    cmd.add('-ar', target.samprate)
    cmd.add('-acodec', target.acodec)
    cmd.add('-y', audiofile)

    cmd.run()


from libtovid.media import MediaFile

def identify(filename):
    """Identify a video file using ffmpeg, and return a MediaFile with
    the video's specifications.
    """
    result = MediaFile(filename)

    cmd = cli.Command('ffmpeg', '-i', filename)
    cmd.run(capture=True)

    # ffmpeg puts its output on stderr
    output = cmd.get_error()

    video_line = re.compile(''
        'Stream (?P<tracknum>[^:]+): Video: ' # Track number (ex. #0.0)
        '(?P<vcodec>[^,]+), '                 # Video codec (ex. mpeg4)
        '(?P<colorspace>[^,]+), '             # Color space (ex. yuv420p)
        '(?P<width>\d+)x(?P<height>\d+), '    # Resolution (ex. 720x480)
        '((?P<vbitrate>\d+) kb/s, )?'         # Video bitrate (ex. 8000 kb/s)
        '(?P<fps>[\d.]+)')                    # FPS (ex. 29.97 fps(r))

    audio_line = re.compile(''
        'Stream (?P<tracknum>[^:]+): Audio: ' # Track number (ex. #0.1)
        '(?P<acodec>[^,]+), '                 # Audio codec (ex. mp3)
        '(?P<samprate>\d+) Hz, '              # Sampling rate (ex. 44100 Hz)
        '(?P<channels>[^,]+), '               # Channels (ex. stereo)
        '(?P<abitrate>\d+) kb/s')             # Audio bitrate (ex. 128 kb/s)
    
    # Parse ffmpeg output and set MediaFile attributes
    for line in output.split('\n'):
        if 'Video:' in line:
            match = video_line.search(line)
            result.vcodec = match.group('vcodec')
            result.scale = (int(match.group('width')),
                            int(match.group('height')))
            result.expand = result.scale
            result.fps = float(match.group('fps'))
            if match.group('vbitrate'):
                result.vbitrate = int(match.group('vbitrate'))

        elif 'Audio:' in line:
            match = audio_line.search(line)
            result.acodec = match.group('acodec')
            result.samprate = int(match.group('samprate'))
            result.abitrate = int(match.group('abitrate'))
            if match.group('channels') == '5.1':
                result.channels = 6
            elif match.group('channels') == 'stereo':
                result.channels = 2
            else:
                result.channels = 1

    return result


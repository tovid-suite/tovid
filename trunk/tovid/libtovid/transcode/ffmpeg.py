#! /usr/bin/env python
# ffmpeg.py

__all__ = [\
    'encode',
    'encode_audio',
    'identify']

from libtovid import log
from libtovid.cli import Command

def encode(source, target, **kw):
    """Encode a multimedia video using ffmpeg.

        source:  Input MediaFile
        target:  Output MediaFile
        kw:      name=value keyword arguments
    
    Supported keywords:
    
        quant:      Minimum quantization, from 1-31 (1 being fewest artifacts)
        vbitrate:   Maximum video bitrate, in kilobits per second.
        abitrate:   Audio bitrate, in kilobits per second
        interlace:  'top' or 'bottom', to do interlaced encoding with
                    top or bottom field first

    For example:
    
        ffmpeg_encode(source, target, quant=4, vbitrate=7000)
    """
    # Build the ffmpeg command
    cmd = Command('ffmpeg')
    cmd.add('-i', source.filename)
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

    # Convert frame rate and audio sampling rate
    cmd.add('-r', target.fps,
            '-ar', target.samprate)
    
    # Convert scale/expand to ffmpeg's padding system
    if target.scale:
        cmd.add('-s', '%sx%s' % target.scale)
        if target.expand != target.scale:
            e_width, e_height = target.expand
            s_width, s_height = target.scale
            h_pad = (e_width - s_width) / 2
            v_pad = (e_height - s_height) / 2
            if h_pad > 0:
                cmd.add('-padleft', h_pad, '-padright', h_pad)
            if v_pad > 0:
                cmd.add('-padtop', v_pad, '-padbottom', v_pad)
    if target.widescreen:
        cmd.add('-aspect', '16:9')
    else:
        cmd.add('-aspect', '4:3')
    # Overwrite existing output files
    cmd.add('-y')
    cmd.add(target.filename)
    
    cmd.run()
    

def encode_audio(source, audiofile, target):
    """Encode the audio stream in a source file to a target format, saving
    to the given filename.

        source:    Input MediaFile
        audiofile: Filename for encoded audio
        target:    Output MediaFile

    If no audio is present in the source file, encode silence.
    """
    cmd = Command('ffmpeg')

    # If source has audio, encode it
    if source.has_audio:
        cmd.add('-i', source.filename)
    # Otherwise, generate 4-second silence
    else:
        # Add silence the length of source length
        ln = source.length
        #print "Source.length: %f" % ln
        if ln < 4:
            # Minimum 4 secs :)
            ln = 4.0
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '%f' % ln)
    cmd.add('-vn', '-ac', '2', '-ab', '224k')
    cmd.add('-ar', target.samprate)
    cmd.add('-acodec', target.acodec)
    cmd.add('-y', audiofile)

    cmd.run()


def identify(filename):
    """
    """


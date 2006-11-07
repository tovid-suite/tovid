#! /usr/bin/env python
# encoders.py

__all__ = [\
    'get_encoder',
    'ffmpeg_encoder',
    'mencoder_encoder',
    'mpeg2enc_encoder']

import os

from libtovid.cli import Script, Command
from libtovid.utils import float_to_ratio
from libtovid import log
import math


def get_encoder(backend):
    """Get an encoder function."""
    if backend == 'ffmpeg':
        return ffmpeg_encoder
    elif backend == 'mencoder':
        return mencoder_encoder
    elif backend == 'mpeg2enc':
        return mpeg2enc_encoder


# ffmpeg


def ffmpeg_encoder(infile, options):
    """Return a Script to encode infile with ffmpeg, using
    the given options.
        infile:  A MediaFile, loaded with an input file
        options: An OptionDict containing user customizations
    """

    script = Script('ffmpeg')

    # Build the ffmpeg command
    cmd = Command('ffmpeg')
    cmd.add('-i', infile.filename)
    if options['format'] in ['vcd', 'svcd', 'dvd']:
        cmd.add('-tvstd', options['tvsys'],
                '-target', '%s-%s' % (options['tvsys'], options['format']))
    
    cmd.add('-r', options['fps'],
            '-ar', options['samprate'])
    # Convert scale/expand to ffmpeg's padding system
    if options['scale']:
        cmd.add('-s', '%sx%s' % options['scale'])
    if options['expand']:
        e_width, e_height = options['expand']
        s_width, s_height = options['scale']
        h_pad = (e_width - s_width) / 2
        v_pad = (e_height - s_height) / 2
        if h_pad > 0:
            cmd.add('-padleft', h_pad, '-padright', h_pad)
        if v_pad > 0:
            cmd.add('-padtop', v_pad, '-padbottom', v_pad)
    if options['widescreen']:
        cmd.add('-aspect', '16:9')
    else:
        cmd.add('-aspect', '4:3')
    # Overwrite existing output files
    cmd.add('-y')
    
    cmd.add(options['out'])

    script.append(cmd)
    return script


# mencoder

def mencoder_encode(infile, options):
    """Return a Script to encode infile (a MediaFile) with mencoder,
    using the given options (an OptionDict)."""

    script = Script('mencoder')

    # Build the mencoder command
    cmd = Command('mencoder')
    cmd.add(infile.filename,
            '-o', options['out'],
            '-oac', 'lavc',
            '-ovc', 'lavc',
            '-of', 'mpeg')
    # Format
    cmd.add('-mpegopts')
    
    if options['format'] in ['vcd', 'svcd']:
        cmd.add('format=x%s' % options['format'])
    else:
        cmd.add('format=dvd')
    
    # TODO: this assumes we only have ONE audio track.
    if infile.audio:
        # Audio settings
        # Adjust sampling rate
        # TODO: Don't resample unless needed
        needed_samprate = standards.get_samprate(options['format'])
        if needed_samprate != infile.audio.samprate:
            log.info("Resampling needed to achieve %d Hz" % needed_samprate)
            cmd.add('-srate', options['samprate'])
            cmd.add('-af', 'lavcresample=%s' % options['samprate'])
        else:
            log.info("No resampling needed, already at %d Hz" % needed_samprate)
        
    else:
        log.info("No audio file, generating silence of %f seconds." % infile.length)
        # Generate silence.
        if options['format'] in ['vcd', 'svcd']:
            audiofile = '%s.mpa' % options['out']
        else:
            audiofile = '%s.ac3' % options['out']
        script.append(encode_audio(infile, audiofile, options))
        # TODO: make this work, it,s still not adding the ac3 file correctly.
        cmd.add('-audiofile', audiofile)
        

    # Video codec
    if options['format'] == 'vcd':
        lavcopts = 'vcodec=mpeg1video'
    else:
        lavcopts = 'vcodec=mpeg2video'
    # Audio codec
    if options['format'] in ['vcd', 'svcd']:
        lavcopts += ':acodec=mp2'
    else:
        lavcopts += ':acodec=ac3'
    lavcopts += ':abitrate=%s:vbitrate=%s' % \
            (options['abitrate'], options['vbitrate'])
    # Maximum video bitrate
    lavcopts += ':vrc_maxrate=%s' % options['vbitrate']
    if options['format'] == 'vcd':
        lavcopts += ':vrc_buf_size=327'
    elif options['format'] == 'svcd':
        lavcopts += ':vrc_buf_size=917'
    else:
        lavcopts += ':vrc_buf_size=1835'
    # Set appropriate target aspect
    if options['widescreen']:
        lavcopts += ':aspect=16/9'
    else:
        lavcopts += ':aspect=4/3'
    # Put all lavcopts together
    cmd.add('-lavcopts', lavcopts)

    # FPS
    if options['tvsys'] == 'pal':
        cmd.add('-ofps', '25/1')
    elif options['tvsys'] == 'ntsc':
        cmd.add('-ofps', '30000/1001') # ~= 29.97

    # Scale/expand to fit target frame
    if options['scale']:
        vfilter = 'scale=%s:%s' % options['scale']
        # Expand is not done unless also scaling
        if options['expand']:
            vfilter += ',expand=%s:%s' % options['expand']
        cmd.add('-vf', vfilter)

    # Add the Command to the Script
    script.append(cmd)
    return script


# mpeg2enc


def encode_audio(infile, audiofile, options):
    """Encode the audio stream in infile to the target format.

    infile -- a MediaFile object
    audiofile -- string to filename
    options -- an OptionDict

    If no audio present, encode silence.
    """
    cmd = Command('ffmpeg')
    if options['format'] in ['vcd', 'svcd']:
        acodec = 'mp2'
    else:
        acodec = 'ac3'

    # If infile was provided, encode it
    if infile.audio:
        cmd.add('-i', infile.filename)
    # Otherwise, generate 4-second silence
    else:
        # Add silence the length of infile.length
        ln = infile.length
        if ln < 4:
            # Minimum 4 secs :)
            ln = 4.0
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '%f' % ln)
    cmd.add_raw('-vn -ac 2 -ab 224')
    cmd.add('-ar', options['samprate'])
    cmd.add('-acodec', acodec)
    cmd.add('-y', audiofile)
    print "CMD: %s" % str(cmd)
    return str(cmd)

def mepg2enc_encode(infile, options):
    """Return a Script to encode infile (a MediaFile) with mpeg2enc,
    using the given options (an OptionDict)."""
    log.warning("This encoder is very experimental, and may not work.")

    script = Script('mpeg2enc')

    outname = options['out']
    # YUV raw video FIFO, for piping video from mplayer to mpeg2enc
    yuvfile = '%s.yuv' % outname
    try:
        os.remove(yuvfile)
    except:
        pass
    os.mkfifo(yuvfile)
    
    # Filenames for intermediate streams (ac3/m2v etc.)
    # Appropriate suffix for audio stream
    if options['format'] in ['vcd', 'svcd']:
        audiofile = '%s.mpa' % outname
    else:
        audiofile = '%s.ac3' % outname
    # Appropriate suffix for video stream
    if options['format'] == 'vcd':
        videofile = '%s.m1v' % outname
    else:
        videofile = '%s.m2v' % outname
    # Do audio
    script.append(encode_audio(infile, audiofile, options))
    # Do video
    script.append(rip_video(infile, yuvfile, options))
    script.append(encode_video(infile, yuvfile, videofile, options))
    # Combine audio and video
    script.append(mplex_streams(videofile, audiofile, outname, options))
    return script
    
def rip_video(infile, yuvfile, options):
    """Rip input video to yuv4mpeg format, and write to yuvfile."""
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = Command('mplayer')
    cmd.add(infile.filename)
    cmd.add('-vo', 'yuv4mpeg:file=%s' % yuvfile)
    cmd.add('-nosound', '-benchmark', '-noframedrop')
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd.add('-noautosub')
    if options['scale']:
        cmd.add('-vf', 'scale=%s:%s' % options['scale'])
    if options['expand']:
        cmd.add('-vf-add', 'expand=%s:%s' % options['expand'])
    # Do ripping in background
    cmd.bg = True
    return cmd


def encode_video(infile, yuvfile, videofile, options):
    """Encode the yuv4mpeg stream to the given format and TV system."""
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    cmd = Command('mpeg2enc')
    # TV system
    if options['tvsys'] == 'pal':
        cmd.add('-F', '3', '-n', 'p')
    elif options['tvsys'] == 'ntsc':
        cmd.add('-F', '4', '-n', 'n')
    # Format
    format = options['format']
    if format == 'vcd':
        cmd.add('-f', '1')
    elif format == 'svcd':
        cmd.add('-f', '4')
    elif 'dvd' in format:
        cmd.add('-f', '8')
    # Aspect ratio
    if options['widescreen']:
        cmd.add('-a', '3')
    else:
        cmd.add('-a', '2')
    cmd.add('-o', videofile)

    # Adjust framerate if necessary
    if infile.video.fps != options['fps']:
        log.info("Adjusting framerate")
        yuvcmd = Command('yuvfps')
        yuvcmd.add('-r', float_to_ratio(options['fps']))
        cmd.pipe_to(yuvcmd)
    cat = Command('cat')
    cat.add(yuvfile)
    cat.pipe_to(cmd)
    return cat

def encode_audio(infile, audiofile, options):
    """Encode the audio stream in infile to the target format."""
    cmd = Command('ffmpeg')
    if options['format'] in ['vcd', 'svcd']:
        acodec = 'mp2'
    else:
        acodec = 'ac3'
    # If infile was provided, encode it
    if infile:
        cmd.add('-i', infile.filename)
    # Otherwise, generate 4-second silence
    else:
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '4')
    cmd.add('-ac', '2',
            '-ab', '224',
            '-ar', options['samprate'],
            '-acodec', acodec,
            '-y', audiofile)
    return cmd

def mplex_streams(vstream, astream, outfile, options):
    """Multiplex the audio and video streams."""
    cmd = Command('mplex')
    format = options['format']
    if format == 'vcd':
        cmd.add('-f', '1')
    elif format == 'dvd-vcd':
        cmd.add('-V', '-f', '8')
    elif format == 'svcd':
        cmd.add('-V', '-f', '4', '-b', '230')
    elif format == 'half-dvd':
        cmd.add('-V', '-f', '8', '-b', '300')
    elif format == 'dvd':
        cmd.add('-V', '-f', '8', '-b', '400')
    # elif format == 'kvcd':
    #   cmd += ' -V -f 5 -b 350 -r 10800 '
    cmd.add(vstream, astream, '-o', outfile)
    return cmd



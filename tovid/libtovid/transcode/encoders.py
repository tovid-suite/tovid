#! /usr/bin/env python
# encoders.py

__all__ = [\
    'get_encoder',
    'ffmpeg_encoder',
    'mencoder_encoder',
    'mpeg2enc_encoder']

import os

from libtovid.cli import Command
from libtovid.utils import float_to_ratio
from libtovid import log
import math


def get_encoder(backend):
    """Get an encoding function."""
    if backend == 'ffmpeg':
        return ffmpeg_encode
    elif backend == 'mencoder':
        return mencoder_encode
    elif backend == 'mpeg2enc':
        return mpeg2enc_encode


# --------------------------------------------------------------------------
#
# ffmpeg backend
#
# --------------------------------------------------------------------------

def ffmpeg_encode(infile, outfile, target):
    """Use ffmpeg to encode infile with ffmpeg, using the given Target.
        infile:  A MediaFile, loaded with an input file
        target:  Encoding Target
    """
    # Build the ffmpeg command
    cmd = Command('ffmpeg')
    cmd.add('-i', infile.filename)
    if target.format in ['vcd', 'svcd', 'dvd']:
        cmd.add('-tvstd', target.tvsys,
                '-target', '%s-%s' % (target.tvsys, target.format))
    
    cmd.add('-r', target.fps,
            '-ar', target.samprate)
    # Convert scale/expand to ffmpeg's padding system
    if target.scale:
        cmd.add('-s', '%sx%s' % target.scale)
    if target.expand:
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
    cmd.add(outfile)
    
    # Run the command to do the encoding
    cmd.run()



# --------------------------------------------------------------------------
#
# mencoder backend
#
# --------------------------------------------------------------------------

def mencoder_encode(infile, outfile, target):
    """Use mencoder to encode infile (a MediaFile) to the given output
    filename, using the given Target."""

    # Build the mencoder command
    cmd = Command('mencoder')
    cmd.add(infile.filename,
            '-o', outfile,
            '-oac', 'lavc',
            '-ovc', 'lavc',
            '-of', 'mpeg')
    # Format
    cmd.add('-mpegopts')
    
    if target.format in ['vcd', 'svcd']:
        cmd.add('format=x%s' % target.format)
    else:
        cmd.add('format=dvd')
    
    # TODO: this assumes we only have ONE audio track.
    if infile.audio:
        # Audio settings
        # Adjust sampling rate
        # TODO: Don't resample unless needed
        needed_samprate = target.samprate
        if needed_samprate != infile.audio.samprate:
            log.info("Resampling needed to achieve %d Hz" % needed_samprate)
            cmd.add('-srate', target.samprate)
            cmd.add('-af', 'lavcresample=%s' % target.samprate)
        else:
            log.info("No resampling needed, already at %d Hz" % needed_samprate)
        
    else:
        log.info("No audio file, generating silence of %f seconds." % infile.length)
        # Generate silence.
        if target.format in ['vcd', 'svcd']:
            audiofile = '%s.mpa' % outfile
        else:
            audiofile = '%s.ac3' % outfile
        encode_audio(infile, audiofile, target)
        # TODO: make this work, it,s still not adding the ac3 file correctly.
        cmd.add('-audiofile', audiofile)
        

    # Video codec
    if target.format == 'vcd':
        lavcopts = 'vcodec=mpeg1video'
    else:
        lavcopts = 'vcodec=mpeg2video'
    # Audio codec
    if target.format in ['vcd', 'svcd']:
        lavcopts += ':acodec=mp2'
    else:
        lavcopts += ':acodec=ac3'
    lavcopts += ':abitrate=%s:vbitrate=%s' % \
            (target.abitrate, target.vbitrate)
    # Maximum video bitrate
    lavcopts += ':vrc_maxrate=%s' % target.vbitrate
    if target.format == 'vcd':
        lavcopts += ':vrc_buf_size=327'
    elif target.format == 'svcd':
        lavcopts += ':vrc_buf_size=917'
    else:
        lavcopts += ':vrc_buf_size=1835'
    # Set appropriate target aspect
    if target.widescreen:
        lavcopts += ':aspect=16/9'
    else:
        lavcopts += ':aspect=4/3'
    # Put all lavcopts together
    cmd.add('-lavcopts', lavcopts)

    # FPS
    if target.tvsys == 'pal':
        cmd.add('-ofps', '25/1')
    elif target.tvsys == 'ntsc':
        cmd.add('-ofps', '30000/1001') # ~= 29.97

    # Scale/expand to fit target frame
    if target.scale:
        vfilter = 'scale=%s:%s' % target.scale
        # Expand is not done unless also scaling
        if target.expand:
            vfilter += ',expand=%s:%s' % target.expand
        cmd.add('-vf', vfilter)

    # Run the command to do the encoding
    cmd.run()

# --------------------------------------------------------------------------
#
# mpeg2enc backend
#
# --------------------------------------------------------------------------


def mpeg2enc_encode(infile, outfile, target):
    """Use mplayer|yuvfps|mpeg2enc to encode infile (a MediaFile) to the
    given output filename, using the given Target.
    """
    log.warning("This encoder is very experimental, and may not work.")

    outname = outfile
    # YUV raw video FIFO, for piping video from mplayer to mpeg2enc
    yuvfile = '%s.yuv' % outname
    try:
        os.remove(yuvfile)
    except:
        pass
    os.mkfifo(yuvfile)
    
    # Filenames for intermediate streams (ac3/m2v etc.)
    # Appropriate suffix for audio stream
    if target.format in ['vcd', 'svcd']:
        audiofile = '%s.mp2' % outname
    else:
        audiofile = '%s.ac3' % outname
    # Appropriate suffix for video stream
    if target.format == 'vcd':
        videofile = '%s.m1v' % outname
    else:
        videofile = '%s.m2v' % outname
    # Do audio
    encode_audio(infile, audiofile, target)
    # Do video
    rip_video(infile, yuvfile, target)
    encode_video(infile, yuvfile, videofile, target)
    # Combine audio and video
    mplex_streams(videofile, audiofile, outname, target)


def encode_audio(infile, audiofile, target):
    """Encode the audio stream in infile to the target format.

    infile:    Input MediaFile
    audiofile: Filename for encoded audio
    target:    A Target

    If no audio present, encode silence.
    """
    cmd = Command('ffmpeg')
    if target.format in ['vcd', 'svcd']:
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
    cmd.add('-ar', target.samprate)
    cmd.add('-acodec', acodec)
    cmd.add('-y', audiofile)
    # Run the command to encode the audio
    cmd.run()


def rip_video(infile, yuvfile, target):
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
    if target.scale:
        cmd.add('-vf', 'scale=%s:%s' % target.scale)
    if target.expand:
        cmd.add('-vf-add', 'expand=%s:%s' % target.expand)
    # Do ripping in background
    cmd.bg = True
    # Run the command to rip the video
    cmd.run()


def encode_video(infile, yuvfile, videofile, target):
    """Encode the yuv4mpeg stream to the given format and TV system.
        infile:    The original input MediaFile
        yuvfile:   Filename of .yuv stream coming from mplayer
        videofile: Filename of .m[1|2]v to write encoded video stream to
        target:    Encoding Target
    """
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    cmd = Command('mpeg2enc')
    # TV system
    if target.tvsys == 'pal':
        cmd.add('-F', '3', '-n', 'p')
    elif target.tvsys == 'ntsc':
        cmd.add('-F', '4', '-n', 'n')
    # Format
    format = target.format
    if format == 'vcd':
        cmd.add('-f', '1')
    elif format == 'svcd':
        cmd.add('-f', '4')
    elif 'dvd' in format:
        cmd.add('-f', '8')
    # Aspect ratio
    if target.widescreen:
        cmd.add('-a', '3')
    else:
        cmd.add('-a', '2')
    cmd.add('-o', videofile)

    # Adjust framerate if necessary
    if infile.video.fps != target.fps:
        log.info("Adjusting framerate")
        yuvcmd = Command('yuvfps')
        yuvcmd.add('-r', float_to_ratio(target.fps))
        cmd.pipe_to(yuvcmd)
    cat = Command('cat')
    cat.add(yuvfile)
    cat.pipe_to(cmd)
    # Run the pipeline to encode the video stream
    cat.run()

def encode_audio(infile, audiofile, target):
    """Encode the audio stream in infile to the target format."""
    cmd = Command('ffmpeg')
    if target.format in ['vcd', 'svcd']:
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
            '-ar', target.samprate,
            '-acodec', acodec,
            '-y', audiofile)
    # Run the command to encode the audio
    cmd.run()

def mplex_streams(vstream, astream, outfile, target):
    """Multiplex the audio and video streams."""
    cmd = Command('mplex')
    format = target.format
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
    # Run the command to multiplex the streams
    cmd.run()



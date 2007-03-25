#! /usr/bin/env python
# encode.py

"""This module provides several video-encoding backends. It provides one
high-level function:

    encode(infile, outfile, format, tvsys, method)

For example:

    encode('/video/foo.avi', '/video/bar.mpg', 'dvd', 'ntsc', 'mencoder')

This will encode '/video/foo.avi' to NTSC DVD form using mencoder, saving
the result as '/video/bar.mpg'.

Each backend implements a top-level function:

    ffmpeg_encode(source, target)
    mencoder_encode(source, target)
    mpeg2enc_encode(source, target)

The source and target are MediaFile objects from libtovid.media, containing
profiles of the input and output videos.
"""

__all__ = [\
    'encode',
    'get_encoder',
    'ffmpeg_encode',
    'mencoder_encode',
    'mpeg2enc_encode']

import os
import math
import copy
import glob
from libtovid.cli import Command, Pipe
from libtovid.utils import float_to_ratio, ratio_to_float
from libtovid.transcode import rip
from libtovid.media import *
from libtovid.standard import fps
from libtovid import log


# --------------------------------------------------------------------------
#
# Primary interface
#
# --------------------------------------------------------------------------

def encode(infile, outfile, format='dvd', tvsys='ntsc', method='ffmpeg'):
    """Encode a multimedia file according to a target profile, saving the
    encoded file to outfile.
    
        infile:  Input filename
        outfile: Desired output filename (.mpg implied)
        format:  One of 'vcd', 'svcd', 'dvd' (case-insensitive)
        tvsys:   One of 'ntsc', 'pal' (case-insensitive)
        method:  Encoding backend: 'ffmpeg', 'mencoder', or 'mpeg2enc'

    """
    source = load_media(infile)
    # Add .mpg to outfile if not already present
    if not outfile.endswith('.mpg'):
        outfile += '.mpg'
    # Get an appropriate encoding target
    target = standard_media(format, tvsys)
    # TODO: User-defined aspect ratio; hardcoded 4:3 for now
    target = correct_aspect(source, target, '4:3')
    target.filename = outfile
    
    # Get the appropriate encoding backend and encode
    encoder = get_encoder(method)
    encoder(source, target)

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

def ffmpeg_encode(source, target):
    """Encode a multimedia video using ffmpeg.

        source:  Input MediaFile
        target:  Output MediaFile
    
    """
    # Build the ffmpeg command
    cmd = Command('ffmpeg')
    cmd.add('-i', source.filename)
    if target.format in ['vcd', 'svcd', 'dvd']:
        cmd.add('-tvstd', target.tvsys,
                '-target', '%s-%s' % (target.tvsys, target.format))
    
    cmd.add('-r', target.fps,
            '-ar', target.samprate)
    # Convert scale/expand to ffmpeg's padding system
    if target.scale:
        cmd.add('-s', '%sx%s' % target.scale)
    if target.expand > target.scale:
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
    
    # Run the command to do the encoding
    cmd.run()


# --------------------------------------------------------------------------
#
# mencoder backend
#
# --------------------------------------------------------------------------

def mencoder_encode(source, target):
    """Encode a multimedia video using mencoder.

        source:  Input MediaFile
        target:  Output MediaFile
    
    """

    # Build the mencoder command
    cmd = Command('mencoder')
    cmd.add(source.filename,
            '-o', target.filename,
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
    if source.has_audio:
        # Audio settings
        # Adjust sampling rate
        # TODO: Don't resample unless needed
        if source.samprate != target.samprate:
            log.info("Resampling needed to achieve %d Hz" % target.samprate)
            cmd.add('-srate', target.samprate)
            cmd.add('-af', 'lavcresample=%s' % target.samprate)
        else:
            log.info("No resampling needed, already at %d Hz" % target.samprate)
        
    else:
        log.info("No audio file, generating silence of %f seconds." % \
                 source.length)
        # Generate silence.
        if target.format in ['vcd', 'svcd']:
            audiofile = '%s.mpa' % target.filename
        else:
            audiofile = '%s.ac3' % target.filename
        encode_audio(source, audiofile, target)
        # TODO: make this work, it,s still not adding the ac3 file correctly.
        cmd.add('-audiofile', audiofile)

    # Video codec
    if target.format == 'vcd':
        lavcopts = 'vcodec=mpeg1video'
    else:
        lavcopts = 'vcodec=mpeg2video'
    # Audio codec
    lavcopts += ':acodec=%s' % target.acodec
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
        if target.expand > target.scale:
            vfilter += ',expand=%s:%s' % target.expand
        cmd.add('-vf', vfilter)

    # Run the command to do the encoding
    cmd.run()

# --------------------------------------------------------------------------
#
# mpeg2enc backend
#
# --------------------------------------------------------------------------


def mpeg2enc_encode(source, target):
    """Encode a multimedia video using mplayer|yuvfps|mpeg2enc.
    
        source:  Input MediaFile
        target:  Output MediaFile

    """
    log.warning("This encoder is very experimental, and may not work.")

    outname = target.filename
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
    encode_audio(source, audiofile, target)
    # Do video
    rip.rip_video(source, yuvfile, target)
    encode_video(source, yuvfile, videofile, target)
    # Combine audio and video
    mplex_streams(videofile, audiofile, target)


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
        if ln < 4:
            # Minimum 4 secs :)
            ln = 4.0
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '%f' % ln)
    cmd.add_raw('-vn -ac 2 -ab 224')
    cmd.add('-ar', target.samprate)
    cmd.add('-acodec', target.acodec)
    cmd.add('-y', audiofile)
    # Run the command to encode the audio
    cmd.run()


def encode_video(source, yuvfile, videofile, target):
    """Encode a yuv4mpeg stream to an MPEG video stream.
    
        source:    Input MediaFile
        yuvfile:   Filename of .yuv stream coming from mplayer
        videofile: Filename of .m[1|2]v to write encoded video stream to
        target:    Output MediaFile
        
    """
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    pipe = Pipe()

    # Feed the .yuv file into the pipeline
    cat = Command('cat', yuvfile)
    pipe.add(cat)

    # Adjust framerate if necessary by piping through yuvfps
    if source.fps != target.fps:
        log.info("Adjusting framerate")
        yuvfps = Command('yuvfps')
        yuvfps.add('-r', float_to_ratio(target.fps))
        pipe.add(yuvfps)

    # Encode the resulting .yuv stream by piping into mpeg2enc
    mpeg2enc = Command('mpeg2enc')
    # TV system
    if target.tvsys == 'pal':
        mpeg2enc.add('-F', '3', '-n', 'p')
    elif target.tvsys == 'ntsc':
        mpeg2enc.add('-F', '4', '-n', 'n')
    # Format
    format = target.format
    if format == 'vcd':
        mpeg2enc.add('-f', '1')
    elif format == 'svcd':
        mpeg2enc.add('-f', '4')
    elif 'dvd' in format:
        mpeg2enc.add('-f', '8')
    # Aspect ratio
    if target.widescreen:
        mpeg2enc.add('-a', '3')
    else:
        mpeg2enc.add('-a', '2')
    mpeg2enc.add('-o', videofile)
    pipe.add(mpeg2enc)
    
    # Run the pipeline to encode the video stream
    pipe.run()


def encode_audio(source, audiofile, target):
    """Encode an audio stream to AC3 or MP2 format.
    
        source:    Input MediaFile
        audiofile: File to put encoded audio in
        target:    Output MediaFile
        
    """
    cmd = Command('ffmpeg')
    # If source file has audio, encode it
    if source.has_audio:
        cmd.add('-i', source.filename)
    # Otherwise, generate 4-second silence
    else:
        cmd.add('-f', 's16le', '-i', '/dev/zero', '-t', '4')
    # Add other necessary qualifiers
    cmd.add('-ac', '2',
            '-ab', '224',
            '-ar', target.samprate,
            '-acodec', target.acodec,
            '-y', audiofile)
    # Run the command to encode the audio
    cmd.run()


def mplex_streams(vstream, astream, target):
    """Multiplex audio and video stream files to the given target.
    
        vstream:  Filename of MPEG video stream
        astream:  Filename of MP2/AC3 audio stream
        target:   Profile of output file
        
    """
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
    cmd.add(vstream, astream, '-o', target.filename)
    # Run the command to multiplex the streams
    cmd.run()

# --------------------------------------------------------------------------
#
# Frame encoder
#
# --------------------------------------------------------------------------

def encode_frames(imagedir, outfile, format, tvsys, aspect, interlaced=False):
    """Convert an image sequence in the given directory to match a target
    MediaFile, putting the output stream in outfile.

        imagedir:   Directory containing images (and only images)
        outfile:    Filename for output.
        tvsys:      TVsys desired for output (to deal with FPS)
        aspect:     Aspect ratio ('4:3', '16:9')
        interlaced: Frames are interlaced material.
        
    Currently supports JPG and PNG images; input images must already be
    at the desired target resolution.
    """
    #
    # Trying to implement interlaced in encoding failed with:
    #    ++ WARN: [mpeg2enc] Frame height won't split into two equal field pictures...
    #    ++ WARN: [mpeg2enc] forcing encoding as progressive video
    # in all cases. Setting -Ip -L1 with pnv2yuv and -I2 in mpeg2enc, etc..
    # The option is still there, so that compatibility continues, but it
    # currently does nothing.
    #
    
    # Use absolute path name
    imagedir = os.path.abspath(imagedir)
    print "Creating video stream from image sequence in %s" % imagedir
    # Determine image type
    images = glob.glob("%s/*" % imagedir)
    extension = images[0][-3:]
    if extension not in ['jpg', 'png']:
        raise ValueError, "Image format '%s' isn't currently supported to "\
              "render video from still frames" % extension
    # Make sure remaining image files have the same extension
    for img in images:
        if not img.endswith(extension):
            raise RuntimeWarning, "%s does not have a .%s extension" %\
                  (img, extension)

    pipe = Pipe()

    # Use jpeg2yuv/png2yuv to stream images
    if extension == 'jpg':
        jpeg2yuv = Command('jpeg2yuv')
        
        jpeg2yuv.add('-Ip') # Progressive
            
        jpeg2yuv.add('-f', '%.3f' % fps(tvsys),
                     '-j', '%s/%%08d.%s' % (imagedir, extension))
        pipe.add(jpeg2yuv)
    elif extension == 'png':
        #ls = Command('sh', '-c', 'ls %s/*.png' % imagedir)
        #xargs = Command('xargs', '-n1', 'pngtopnm')
        png2yuv = Command('png2yuv')

        png2yuv.add('-Ip') # Progressive
            

        png2yuv.add('-f', '%.3f' % fps(tvsys),
                    '-j', '%s/%%08d.png' % (imagedir))
        
        pipe.add(png2yuv)

        #pipe.add(ls, xargs, png2yuv)
        #cmd += 'pnmtoy4m -Ip -F %s %s/*.png' % standard.fpsratio(tvsys)

    # TODO: Scale to correct target size using yuvscaler or similar
    
    # Pipe image stream into mpeg2enc to encode
    mpeg2enc = Command('mpeg2enc')

    # Anyways.
    mpeg2enc.add('-I 0') # Progressive
    
    mpeg2enc.add('-v', '0',
                 '-q' '3',
                 '-o' '%s' % outfile)
    # Format
    if format == 'vcd':
        mpeg2enc.add('--format', '1')
    elif format == 'svcd':
        mpeg2enc.add('--format', '4')
    else:
        mpeg2enc.add('--format', '8')
    # Aspect ratio
    if aspect == '16:9':
        mpeg2enc.add('-a', '3')
    elif aspect == '4:3':
        mpeg2enc.add('-a', '2')

    pipe.add(mpeg2enc)

    pipe.run(capture=True)
    pipe.get_output() # and wait :)

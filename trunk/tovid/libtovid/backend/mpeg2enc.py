#! /usr/bin/env python
# mpeg2enc.py

"""Video and frame encoding using ``mpeg2enc``.
"""

__all__ = [
    'encode',
    'encode_video',
    'encode_frames',
]

# TODO: Filter out some of the inter-backend dependencies

import os, glob
from libtovid import log
from libtovid import util
from libtovid import cli
from libtovid.backend import mplex, mplayer, ffmpeg

def encode(source, target, **kw):
    """Encode a multimedia video using mplayer|yuvfps|mpeg2enc.
    
        source
            Input MediaFile
        target
            Output MediaFile
        **kw
            Keyword arguments to customize encoding behavior

    Supported keywords:

        None yet

    """
    log.warning("This encoder is very experimental, and may not work.")

    outname = target.filename
    # YUV raw video FIFO, for piping video from mplayer to mpeg2enc
    yuvfile = '%s.yuv' % outname
    if os.path.exists(yuvfile):
        os.remove(yuvfile)
    
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
    ffmpeg.encode_audio(source, audiofile, target)
    # Do video
    mplayer.rip_video(source, yuvfile, target)
    encode_video(source, yuvfile, videofile, target)
    # Combine audio and video
    mplex.mux(videofile, audiofile, target)
    


def encode_video(source, yuvfile, videofile, target):
    """Encode a yuv4mpeg stream to an MPEG video stream.
    
        source
            Input MediaFile
        yuvfile
            Filename of .yuv stream coming from mplayer
        videofile
            Filename of .m[1|2]v to write encoded video stream to
        target
            Output MediaFile
        
    """
    # TODO: Control over quality (bitrate/quantization) and disc split size,
    # corresp. to $VID_BITRATE, $MPEG2_QUALITY, $DISC_SIZE, etc.
    # Missing options (compared to tovid)
    # -S 700 -B 247 -b 2080 -v 0 -4 2 -2 1 -q 5 -H -o FILE
    pipe = cli.Pipe()

    # Feed the .yuv file into the pipeline
    cat = cli.Command('cat', yuvfile)
    pipe.add(cat)

    # Adjust framerate if necessary by piping through yuvfps
    if source.fps != target.fps:
        log.info("Adjusting framerate")
        yuvfps = cli.Command('yuvfps')
        yuvfps.add('-r', util.float_to_ratio(target.fps))
        pipe.add(yuvfps)

    # Encode the resulting .yuv stream by piping into mpeg2enc
    mpeg2enc = cli.Command('mpeg2enc')
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


# --------------------------------------------------------------------------
#
# Frame encoder
#
# --------------------------------------------------------------------------
from libtovid import standard

def encode_frames(imagedir, outfile, format, tvsys, aspect, interlaced=False):
    """Convert an image sequence in the given directory to match a target
    MediaFile, putting the output stream in outfile.

        imagedir
            Directory containing images (and only images)
        outfile
            Filename for output.
        tvsys
            TVsys desired for output (to deal with FPS)
        aspect
            Aspect ratio ('4:3', '16:9')
        interlaced
            Frames are interlaced material
        
    Currently supports JPG and PNG images; input images must already be
    at the desired target resolution.
    """
    
    # Use absolute path name
    imagedir = os.path.abspath(imagedir)
    print "Creating video stream from image sequence in %s" % imagedir
    # Determine image type
    images = glob.glob("%s/*" % imagedir)
    extension = images[0][-3:]
    if extension not in ['jpg', 'png']:
        raise ValueError("Image format '%s' isn't currently supported to "
              "render video from still frames" % extension)
    # Make sure remaining image files have the same extension
    for img in images:
        if not img.endswith(extension):
            raise ValueError("%s does not have a .%s extension" %
                  (img, extension))

    pipe = cli.Pipe()

    # Use jpeg2yuv/png2yuv to stream images
    if extension == 'jpg':
        jpeg2yuv = cli.Command('jpeg2yuv')
        
        jpeg2yuv.add('-Ip') # Progressive

        jpeg2yuv.add('-f', '%.3f' % standard.fps(tvsys),
                     '-j', '%s/%%08d.%s' % (imagedir, extension))
        pipe.add(jpeg2yuv)
    elif extension == 'png':
        #ls = cli.Command('sh', '-c', 'ls %s/*.png' % imagedir)
        #xargs = cli.Command('xargs', '-n1', 'pngtopnm')
        png2yuv = cli.Command('png2yuv')

        png2yuv.add('-Ip') # Progressive
            

        png2yuv.add('-f', '%.3f' % standard.fps(tvsys),
                    '-j', '%s/%%08d.png' % (imagedir))
        
        pipe.add(png2yuv)

        #pipe.add(ls, xargs, png2yuv)
        #cmd += 'pnmtoy4m -Ip -F %s %s/*.png' % standard.fpsratio(tvsys)

    # TODO: Scale to correct target size using yuvscaler or similar
    
    # Pipe image stream into mpeg2enc to encode
    mpeg2enc = cli.Command('mpeg2enc')

    # Anyways.
    mpeg2enc.add('-I 0') # Progressive

    # Bottom-first, determined in render/drawing.py::interlace_drawings()
    if (interlaced):
        mpeg2enc.add('--playback-field-order', 'b')  # Bottom-first field order
        # conforming to drawing.py::interlace_drawings()
    
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


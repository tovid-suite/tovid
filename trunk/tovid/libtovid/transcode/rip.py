#! /usr/bin/env python
# rip.py

"""Python video (audio, subtitle) ripping interface.

Currently provides:

    rip_frames:  Rip video frames from a MediaFile
    rip_video:   Rip a yuv4mpeg video stream from a MediaFile

May someday also provide:

    rip_title:    Rip video title(s) from DVD
    rip_audio:    Rip audio stream(s) from a MediaFile
    rip_subtitle: Rip subtitle(s) from a MediaFile

etc.
"""
__all__ = [\
    'rip_video',
    'rip_frames']

import os
import glob
from libtovid.cli import Command
from libtovid import log

def rip_video(source, yuvfile, target):
    """Rip video to the given yuv4mpeg file.
    
        source:  Input MediaFile
        yuvfile: File to put ripped video in
        target:  Output MediaFile
        
    """
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = Command('mplayer')
    cmd.add(source.filename)
    cmd.add('-vo', 'yuv4mpeg:file=%s' % yuvfile)
    cmd.add('-nosound', '-benchmark', '-noframedrop')
    # TODO: Support subtitles. For now, use default tovid behavior.
    cmd.add('-noautosub')
    if target.scale:
        cmd.add('-vf', 'scale=%s:%s' % target.scale)
    if target.expand > target.scale:
        cmd.add('-vf-add', 'expand=%s:%s' % target.expand)
    # Run the command to rip the video
    cmd.run(background=True)


def rip_frames(media, out_dir, frames='all', size=(0, 0)):
    """Extract frame images from a MediaFile and return a list of frame image
    files.
    
        media:    MediaFile to extract images from
        out_dir:  Directory where output images should be stored; images
                  are saved in a subdirectory of out_dir named after the
                  input filename
        frames:   Which frames to rip: 'all' for all frames, 15 to rip frame
                  15; [30, 90] to rip frames 30 through 90, etc.
        size:     Resolution of frame images (default: original size), used
                  for prescaling
        
    """
    out_dir = os.path.abspath(out_dir)
    try:
        os.mkdir(out_dir)
    except:
        log.warn("Temp directory: %s already exists. Overwriting." % out_dir)
        os.system('rm -rf "%s"' % out_dir)
        os.mkdir(out_dir)

    # TODO: use tcdemux to generate a nav index, like:
    # tcdemux -f 29.970 -W -i "$FILE" > "$NAVFILE"
    
    # Use transcode to rip frames
    cmd = Command('transcode',
                  '-i', '%s' % media.filename)
    # Resize
    if size != (0, 0):
        cmd.add('-Z', '%sx%s' % size)
    # Encode selected frames
    if frames == 'all':
        start = 0
    elif isinstance(frames, int):
        cmd.add('-c', '%s-%s' % (frames, frames))
        start = frames
    elif isinstance(frames, list):
        start = frames[0]
        cmd.add('-c', '%s-%s' % (frames[0], frames[-1]))
    cmd.add('-y', 'jpg,null')
    cmd.add('-o', '%s/frame_' % out_dir)
    log.info("Creating image sequence from %s" % media.filename)
    cmd.run()

    # Return a list of ripped files
    return glob.glob('%s/frame_*.jpg' % out_dir)

#! /usr/bin/env python
# mplayer.py

"""Video encoding, ripping, and identification using ``mplayer``.
"""

__all__ = [
    'encode',
    'identify',
    'rip_video',
]

from libtovid import log
from libtovid import cli
from libtovid.media import MediaFile
from libtovid.backend import ffmpeg

def encode(source, target, **kw):
    """Encode a multimedia video using mencoder.

        source
            Input MediaFile
        target
            Output MediaFile
        kw
            Keyword arguments to customize encoding behavior
    
    Supported keywords:

        None yet

    """
    cmd = cli.Command('mencoder')
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
    
    # FIXME: This assumes we only have ONE audio track.
    if source.has_audio:
        # Adjust audio sampling rate if necessary
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
        ffmpeg.encode_audio(source, audiofile, target)
        # TODO: make this work, it's still not adding the ac3 file correctly.
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
    # Pass all lavcopts together
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
        if target.expand != target.scale:
            vfilter += ',expand=%s:%s' % target.expand
        cmd.add('-vf', vfilter)

    cmd.run()
    

def identify(filename):
    """Identify a video file using mplayer, and return a MediaFile with
    the video's specifications.
    """
    # TODO: Raise an exception if the file couldn't be identified
    # TODO: Infer aspect ratio

    media = MediaFile(filename)
   
    mp_dict = {}
    # Use mplayer
    cmd = cli.Command('mplayer',
                  '-identify',
                  '%s' % filename,
                  '-vo', 'null',
                  '-ao', 'null',
                  '-frames', '1',
                  '-channels', '6')
    cmd.run(capture=True)
    
    # Look for mplayer's "ID_..." lines and include each assignment in mp_dict
    for line in cmd.get_output().splitlines():
        log.debug(line)
        if line.startswith("ID_"):
            left, right = line.split('=')
            mp_dict[left] = right.strip()

    # Check for existence of streams
    if 'ID_VIDEO_ID' in mp_dict:
        media.has_video = True
    else:
        media.has_video = False
    if 'ID_AUDIO_ID' in mp_dict:
        media.has_audio = True
    else:
        media.has_audio = False

    # Parse the dictionary and set appropriate values
    for left, right in mp_dict.iteritems():
        if left == "ID_VIDEO_WIDTH":
            media.scale = (int(right), media.scale[1])
        elif left == "ID_VIDEO_HEIGHT":
            media.scale = (media.scale[0], int(right))
        elif left == "ID_VIDEO_FPS":
            media.fps = float(right)
        elif left == "ID_VIDEO_FORMAT":
            media.vcodec = right
        elif left == "ID_VIDEO_BITRATE":
            media.vbitrate = int(right) / 1000
        elif left == "ID_AUDIO_CODEC":
            media.acodec = right
        elif left == "ID_AUDIO_FORMAT":
            pass
        elif left == "ID_AUDIO_BITRATE":
            media.abitrate = int(right) / 1000
        elif left == "ID_AUDIO_RATE":
            media.samprate = int(right)
        elif left == "ID_AUDIO_NCH":
            media.channels = right
        elif left == 'ID_LENGTH':
            media.length = float(right)
    media.expand = media.scale
    
    # Fix mplayer's audio codec naming for ac3 and mp2
    if media.acodec == "8192":
        media.acodec = "ac3"
    elif media.acodec == "80":
        media.acodec = "mp2"
    # Fix mplayer's video codec naming for mpeg1 and mpeg2
    if media.vcodec == "0x10000001":
        media.vcodec = "mpeg1"
    elif media.vcodec == "0x10000002":
        media.vcodec = "mpeg2"
    return media




def rip_video(source, yuvfile, target):
    """Rip video to the given yuv4mpeg file.
    
        source
            Input MediaFile
        yuvfile
            File to put ripped video in
        target
            Output MediaFile
        
    """
    # TODO: Custom mplayer options, subtitles, interlacing,
    # corresp.  to $MPLAYER_OPT, $SUBTITLES, $VF_PRE/POST, $YUV4MPEG_ILACE,
    # etc.
    cmd = cli.Command('mplayer')
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


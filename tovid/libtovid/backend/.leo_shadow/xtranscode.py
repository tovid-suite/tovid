#@+leo-ver=4-thin
#@+node:eric.20090722212922.2538:@shadow transcode.py
"""Video frame ripping and video identification using ``transcode``.
"""

#@+at
# Sample output from tcprobe:
# 
# [tcprobe] RIFF data, AVI video
# [avilib] V: 24.000 fps, codec=DIVX, frames=15691, width=1024, height=576
# [avilib] A: 48000 Hz, format=0x2000, bits=0, channels=5, bitrate=448 kbps,
# [avilib]    10216 chunks, 36614144 bytes, CBR
# [tcprobe] summary for Elephants_1024.avi, (*) = not default, 0 = not 
# detected
# import frame size: -g 1024x576 [720x576] (*)
#        frame rate: -f 24.000 [25.000] frc=0 (*)
#       audio track: -a 0 [0] -e 48000,0,5 [48000,16,2] -n 0x2000 [0x2000] (*)
#                    bitrate=448 kbps
#            length: 15691 frames, frame_time=41 msec, duration=0:10:53.790
#@-at
#@@c

__all__ = [
    'identify',
    'rip_frames',
]

import os, re, glob
from libtovid import log
from libtovid import cli
from libtovid.media import MediaFile

#@+others
#@+node:eric.20090722212922.2540:identify
def identify(filename):
    """Identify a video file using transcode (tcprobe), and return a MediaFile
    with the video's specifications.
    """
    result = MediaFile(filename)

    cmd = cli.Command('tcprobe', '-i', filename)
    cmd.run(capture=True)
    output = cmd.get_output()

    video_line = re.compile('V: '
        '(?P<fps>[\d.]+) fps, '
        'codec=(?P<vcodec>[^,]+), '
        'frames=\d+, '
        'width=(?P<width>\d+), '
        'height=(?P<height>\d+)')

    audio_line = re.compile('A: '
        '(?P<samprate>\d+) Hz, '
        'format=(?P<acodec>[^,]+), '
        'bits=\d+, '
        'channels=(?P<channels>[^,]+), '
        'bitrate=(?P<abitrate>\d+) kbps')

    for line in output.split('\n'):
        if 'V: ' in line:
            match = video_line.search(line)
            result.fps = float(match.group('fps'))
            result.vcodec = match.group('vcodec')
            result.scale = (int(match.group('width')),
                            int(match.group('height')))
            result.expand = result.scale

        elif 'A: ' in line:
            match = audio_line.search(line)
            result.acodec = match.group('acodec')
            result.samprate = int(match.group('samprate'))
            result.abitrate = int(match.group('abitrate'))
            result.channels = int(match.group('channels'))

    return result


#@-node:eric.20090722212922.2540:identify
#@+node:eric.20090722212922.2541:rip_frames
def rip_frames(media, out_dir, frames='all', size=(0, 0)):
    """Extract frame images from a MediaFile and return a list of frame image
    files.

        media
            MediaFile to extract images from
        out_dir
            Directory where output images should be stored; images are saved
            in a subdirectory of out_dir named after the input filename
        frames
            Which frames to rip: 'all' for all frames, 15 to rip frame 15;
            [30, 90] to rip frames 30 through 90, etc.
        size
            Resolution of frame images (default: original size), used
            for prescaling

    """
    out_dir = os.path.abspath(out_dir)
    if os.path.exists(out_dir):
        log.warning("Temp directory: %s already exists. Overwriting." % out_dir)
        os.system('rm -rf "%s"' % out_dir)
    os.mkdir(out_dir)

    # TODO: use tcdemux to generate a nav index, like:
    # tcdemux -f 29.970 -W -i "$FILE" > "$NAVFILE"

    # Use transcode to rip frames
    cmd = cli.Command('transcode',
                  '-i', '%s' % media.filename)
    # Resize
    if size != (0, 0):
        cmd.add('-Z', '%sx%s' % size)
    # Encode selected frames
    if frames == 'all':
        # transcode does all by default
        pass
    elif isinstance(frames, int):
        # rip a single frame
        cmd.add('-c', '%s-%s' % (frames, frames))
    elif isinstance(frames, list):
        # rip a range of frames
        cmd.add('-c', '%s-%s' % (frames[0], frames[-1]))
    cmd.add('-y', 'jpg,null')
    cmd.add('-o', '%s/frame_' % out_dir)
    log.info("Creating image sequence from %s" % media.filename)
    cmd.run()

    # Return a list of ripped files
    return glob.glob('%s/frame_*.jpg' % out_dir)
#@-node:eric.20090722212922.2541:rip_frames
#@-others
#@-node:eric.20090722212922.2538:@shadow transcode.py
#@-leo

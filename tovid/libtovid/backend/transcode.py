#! /usr/bin/env python
# transcode.py

from libtovid.cli import Command
from libtovid.media import MediaFile
import re

"""
Sample output from tcprobe:

[tcprobe] RIFF data, AVI video
[avilib] V: 24.000 fps, codec=DIVX, frames=15691, width=1024, height=576
[avilib] A: 48000 Hz, format=0x2000, bits=0, channels=5, bitrate=448 kbps,
[avilib]    10216 chunks, 36614144 bytes, CBR
[tcprobe] summary for Elephants_Dream_1024.avi, (*) = not default, 0 = not detected
import frame size: -g 1024x576 [720x576] (*)
       frame rate: -f 24.000 [25.000] frc=0 (*)
      audio track: -a 0 [0] -e 48000,0,5 [48000,16,2] -n 0x2000 [0x2000] (*)
                   bitrate=448 kbps
           length: 15691 frames, frame_time=41 msec, duration=0:10:53.790
"""


def identify(filename):
    """Identify a video file using transcode (tcprobe), and return a MediaFile
    with the video's specifications.
    """
    result = MediaFile(filename)
    
    cmd = Command('tcprobe', '-i', filename)
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

import unittest
import math
# Fetch in subdir
import sys
import os
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing
from libtovid.render.flipbook import Flipbook
from libtovid.render import layer
from libtovid.backend import mplayer
from libtovid import standard

class TestFlipbook(unittest.TestCase):
    """Test the Flipbook class"""
    def setUp(self):
        if not os.path.isfile('/tmp/save_image.png'):
            self.test_save_an_image()

    def test_save_an_image(self):
        # Save image to /tmp/save_image.[png|jpg]
        d = Drawing(250, 250)
        d.stroke_width(10)
        d.circle((125,125), 120)
        d.stroke('red')
        d.save_png('/tmp/save_image.png')
        d.save_jpg('/tmp/save_image.jpg')
        del(d)

    def test_flip_save_video(self):
        """First test drive for Flipbook"""
        fb = Flipbook(1, 'dvd', 'ntsc')

        thumb = layer.Thumb('/tmp/save_image.png', (100,100), (250, 250),
                            'My image')
        fb.add(thumb)
        # Export '/tmp/testclip.m2v' ...
        fb.render_video('/tmp/testflip')

    def test_flip_video_in(self):
        """Try the ThumbGrid"""
        global VIDEO_FILE
        fb = Flipbook(2, 'dvd', 'ntsc')

        # Add frames
        mf = mplayer.identify('/tmp/testflip.m2v')
        mf.rip_frames([0, 10])

        # Add a video also
        lst = mf.frame_files
        lst.append(VIDEO_FILE)

        print("LIST %s" % lst)

        thumbgrid = layer.ThumbGrid(lst)

        fb.add(thumbgrid)

        fb.render_video('/tmp/finalvideo')

global VIDEO_FILE

if __name__ == '__main__':
    global VIDEO_FILE
    if len(sys.argv) < 2:
        print("Please a video file as argument")
        sys.exit()
    VIDEO_FILE = sys.argv.pop()

    unittest.main()


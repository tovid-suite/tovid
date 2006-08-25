import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.cairo_ import Drawing
from flipbook import Flipbook
from media import MediaFile
import layer
import standards

class TestFlipbook(unittest.TestCase):
    """Test the Flipbook class"""
    
    def test_save_an_image(self):
        # Save image to /tmp/save_image.[png|jpg]
        d = Drawing((250, 250))
        d.color_stroke('red')
        d.stroke_width(10)
        d.circle_rad((125,125), 120)
        d.stroke()
        d.save_png('/tmp/save_image.png')
        d.save_jpg('/tmp/save_image.jpg')
        del(d)
    
    def test_flip_save_video(self):
        """First test drive for Flipbook"""
        size = standards.get_resolution('dvd', 'ntsc')
        fb = Flipbook(10, size)

        thumb = layer.Thumb('/tmp/save_image.png', (100,100), 'My image')
        fb.add(thumb)
        # Export '/tmp/testclip.m2v' ...
        fb.render_video('/tmp/testflip', 'dvd', 'ntsc')

    def test_flip_video_in(self):
        """Try the ThumbGrid"""
        global VIDEO_FILE
        size = standards.get_resolution('dvd', 'ntsc')
        fb = Flipbook(20, size)

        # Add frames
        mf = MediaFile()
        mf.load('/tmp/testflip.m2v')
        mf.rip_frames([0, 10])

        # Add a video also
        lst = mf.frame_files
        lst.append(VIDEO_FILE)

        print "LIST", lst

        thumbgrid = layer.ThumbGrid(lst)

        fb.add(thumbgrid)

        fb.render_video('/tmp/finalvideo', 'dvd', 'ntsc')
        
global VIDEO_FILE

if __name__ == '__main__':
    global VIDEO_FILE
    VIDEO_FILE = '/home/wacky/Desktop/VIDEO_SATURNE-2006-07-27-jour9.mpg'
    
    unittest.main()


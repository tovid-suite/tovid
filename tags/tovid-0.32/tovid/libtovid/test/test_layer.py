import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing
from libtovid.render import layer
from libtovid.render.animation import Keyframe

class TestLayer(unittest.TestCase):
    """Test the Layer class"""
    def test_layer(self):
        pass

    def test_draw_layers(self):
        # Test Layer class instantiation
        print("Creating a Thumb Layer")
        thumb = layer.Thumb('test.png', (50, 35), title='Oh yeah')
        print("Creating a Thumbgrid Layer")
        files = ['test.png']*3
        thumb_grid = layer.ThumbGrid(files, files, (600, 400))
        print("Creating a SafeArea Layer")
        safe_area = layer.SafeArea(93, 'yellow')
        print("Creating an InterpolationGraph Layer")
        keys = [Keyframe(0, 0), Keyframe(90, 100)]
        interpolation_graph = layer.InterpolationGraph(keys)
        print("Creating a ColorBars Layer")
        color_bars = layer.ColorBars((320, 240), (150, 150))

        # Test drawing
        pic = Drawing()
        thumb.draw(pic, 1)
        thumb_grid.draw(pic, 1)
        safe_area.draw(pic, 1)
        color_bars.draw(pic, 1)
        pic.display()

if __name__ == '__main__':
    unittest.main()


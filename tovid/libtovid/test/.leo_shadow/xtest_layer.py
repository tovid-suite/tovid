#@+leo-ver=4-thin
#@+node:eric.20090722212922.3374:@shadow test_layer.py
#@+others
#@+node:eric.20090722212922.3375:test_layer declarations
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing
from libtovid.render import layer
from libtovid.render.animation import Keyframe

#@-node:eric.20090722212922.3375:test_layer declarations
#@+node:eric.20090722212922.3376:class TestLayer
class TestLayer(unittest.TestCase):
    """Test the Layer class"""
    #@    @+others
    #@+node:eric.20090722212922.3377:test_layer
    def test_layer(self):
        pass

    #@-node:eric.20090722212922.3377:test_layer
    #@+node:eric.20090722212922.3378:test_draw_layers
    def test_draw_layers(self):
        # Test Layer class instantiation
        print("Creating a Thumb Layer")
        thumb = layer.Thumb('test.png', (50, 35), title='Oh yeah')
        print("Creating a Thumbgrid Layer")
        thumb_grid = layer.ThumbGrid(['test.png', 'test.png', 'test.png'],
                             (600, 400))
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

    #@-node:eric.20090722212922.3378:test_draw_layers
    #@-others
#@-node:eric.20090722212922.3376:class TestLayer
#@-others
if __name__ == '__main__':
    unittest.main()

#@-node:eric.20090722212922.3374:@shadow test_layer.py
#@-leo

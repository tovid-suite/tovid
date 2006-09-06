import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.cairo_ import Drawing
import layer
from libtovid.animation import Keyframe

class TestLayer(unittest.TestCase):
    """Test the Layerk class"""
    
    def test_layer(self):
        pass

    def test_instantiate_layers(self):

        # Good instantiations
        l1 = layer.Thumb('test.png', (50, 35), title='Oh yeah')
        l2 = layer.ThumbGrid(['test.png', 'test.png', 'test.png'],
                             (600, 400))
        l3 = layer.SafeArea(93, 'yellow')
        l4 = layer.TitleSafeArea('yellow')
        l5 = layer.ActionSafeArea('white')

        k = [Keyframe(0, 0), Keyframe(90, 100)]
        l6 = layer.InterpolationGraph(k)

        l7 = layer.ColorBars((320, 240), (50, 50)) # At a given pos.


if __name__ == '__main__':
    unittest.main()


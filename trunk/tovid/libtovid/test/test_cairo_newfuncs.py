# -=- encoding: latin-1 -=-
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing
import cairo

class TestCairoRenderer(unittest.TestCase):
    def setUp(self):
        """Set up a new drawing"""
        self.d = Drawing(640, 480)

    def tearDown(self):
        """Delete the drawing"""
        del(self.d)

    def test_init(self):
        """Blank test"""
        pass

    def test_set_source(self):
        p = cairo.SolidPattern(1, 1, 1, 0.5)
        # Image as source
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 480)
        # Create a gradient.
        g = cairo.LinearGradient(0, 0, 640, 480)
        g.add_color_stop_rgb(0, 1, 1, 1)
        g.add_color_stop_rgb(1, 0, 0, 0)

        # At each step, make sure a source going in, can be extracted
        # (get_source) and then put back into set_source()

        # Try some of the ImageColor
        self.d.set_source('rgb(255,255,255)')
        source = self.d.get_source()
        self.d.set_source(source)

        # Try solid pattern...
        self.d.set_source(p)
        source = self.d.get_source()
        self.d.set_source(source)

        # Try image surface
        self.d.set_source(s)
        source = self.d.get_source()
        self.d.set_source(source)

        # Try gradient
        self.d.set_source(g)
        source = self.d.get_source()
        self.d.set_source(source)

    def test_group(self):
        self.d.push_group()
        self.d.pop_group_to_source()

    def test_paints(self):
        self.d.paint()
        self.d.paint_with_alpha(0.5)


if __name__ == '__main__':
    unittest.main()


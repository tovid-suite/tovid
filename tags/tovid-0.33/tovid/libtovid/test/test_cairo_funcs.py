# -=- encoding: latin-1 -=-
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing, save_image
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

    def test_bezier(self):
        """Test bezier points checker"""
        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2), (2,2)],
               [(3,3), (3,3), (3,3)]]

        self.d.bezier(pts)

        pts = [[(1,1), (1,1)],
               [(2,2), (2,2), (2,2)],
               [(3,3), (3,3), (3,3)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2)],
               [(3,3), (3,3), (3,3)]]

        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2), (2,2)],
               [(3,3), (3,3)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1), (1,1)],
               [(2,2), (2,2)],
               [(3,3), (3,3), (3)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2), (2,2)],
               [(3,3), (3,3), (3,3,3,4,5)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2,5,6), (2,2)],
               [(3,3), (3,3), (3,3)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1)],
               [(2,2), (2,2), (2,2)],
               [(3,3), (3,3), (3,3)],
               [(1,1), (1), (1,1)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1)],
               [(2,2), (2,2)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1), (1,1), (1,1), (1,1)],
               [(2,2), (2,2), (2,2), (2,2)],
               [(3,3), (3,3), (3,3), (3,3)]]

        self.assertRaises(AssertionError, self.d.bezier, pts)

        pts = [[(1,1)],
               [(2,2)],
               [(3,3)]]

        # This one okay, because control points will be the same as the
        # specified points.
        self.d.bezier(pts)

    def test_polyschlaft(self):
        """Test polyline and polygon"""
        self.d.polygon([(0,0),
                        (100, 0),
                        (100, 100),
                        (0, 100),
                        (0,0)])
        self.d.polyline([(0,0),
                        (100, 0),
                        (100, 100),
                        (0, 100),
                        (0,0)])


    def test_draw_funcs(self):
        """Test drive drawing functions

        We still need to verify the output visually to make sure it's okay
        """
        # bezier is tested in test_bezier()
        self.d.stroke_width(5)

        self.d.affine(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        self.d.arc(25, 25, 15, 0, 270)
        self.d.arc_rad(125, 125, 50, 0, 1)
        self.d.circle(55, 55, 30)
        self.d.circle(250, 250, 20)

        self.d.line(25, 25, 125, 125)
        self.d.line(125, 125, 55, 55)
        self.d.line(55, 55, 250, 250)

    def test_stroke_styles(self):
        self.assertRaises(KeyError, self.d.stroke_linecap, 'gurda')
        self.d.stroke_linecap('butt')
        self.d.stroke_linecap('round')
        self.d.stroke_linecap('square')

        self.assertRaises(KeyError, self.d.stroke_linejoin, 'pou')
        self.d.stroke_linejoin('miter')
        self.d.stroke_linejoin('bevel')
        self.d.stroke_linejoin('round')


    def test_scale_translate(self):
        self.d.save()
        self.d.translate(-200, 0)
        self.d.scale(1.5, 1.5)  # Scaling is done from (0,0) as reference.
        self.d.scale_centered(50, 50, 1.5, 1.5)
        self.d.circle(500, 100, 50) # same radius as others
        self.d.stroke()
        self.d.restore()

    def test_push_n_rotate(self):
        self.d.save()
        self.d.rotate(180)
        self.d.rotate_deg(180)
        self.d.rotate_rad(math.pi)
        self.d.restore()

    def test_colors(self):
        self.d.set_source('black')

    def test_new_fill_n_stroke(self):
        # Check that the new fill and stroke accept colors.
        self.d.set_source('rgb(255,255,255)', 1.0)

        # We use these also for the 'text' function.
        self.d.text('ahuh', 10,50)
        self.d.text_path('ahuh', 10, 1000)
        self.d.fill('blue')

        # When we call fill() and stroke() with no parameters, the last used
        # parameters are applied.
        self.d.fill()
        self.d.stroke()

    def test_operator(self):
        self.assertRaises(KeyError, self.d.operator, 'bad_arg')
        methods = [
            'clear',  'source', 'over', 'in', 'out', 'atop',
            'dest', 'dest_over', 'dest_in', 'dest_out', 'dest_atop',
            'xor', 'add', 'saturate',
        ]
        # Test all methods
        for method in methods:
            self.d.operator(method)

    def test_fill_funcs(self):
        self.assertRaises(KeyError, self.d.fill_rule, 'invalid')
        self.d.fill_rule('evenodd')
        # Don't feed it a tuple, but a 'color' now...
        self.d.fill()

    def test_font_stuff(self):
        self.d.font('Times')
        self.d.font_size(24)
        self.d.font_stretch(2.0)
        self.d.font_stretch(2.0, 2.0)
        self.d.font_rotate(90)
        self.d.font_rotate(180)
        self.d.font_rotate(0)

    def test_text_stuff(self):
        self.d.text("Test of text string", 15, 15)

    def test_antialias_stuff(self):
        self.d.stroke_antialias(True)
        self.d.stroke_antialias(False)

    def test_rectangle_stuff(self):
        self.d.rectangle(20, 20, 200, 200)
        self.d.rectangle_corners(20, 20, 230, 230)
        self.d.roundrectangle(10, 445, 610, 470, 5, 5)


    def test_dash_stuff(self):
        self.d.stroke_dash([1.0, 2.0, 3.0], 1.0)

    def test_render(self):
        """Test drive rendering mechanism"""
        self.d.stroke_width(8)
        self.d.circle(250, 250, 50)
        self.d.stroke_width(2)
        self.d.circle(250, 250, 80)

        save_image(self.d, '/tmp/my.png')




if __name__ == '__main__':
    unittest.main()


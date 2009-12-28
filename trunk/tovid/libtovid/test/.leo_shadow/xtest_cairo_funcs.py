# -=- encoding: latin-1 -=-
#@+leo-ver=4-thin
#@+node:eric.20090722212922.3324:@shadow test_cairo_funcs.py
#@@first
#@+others
#@+node:eric.20090722212922.3325:test_cairo_funcs declarations
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing, save_image
import cairo

#@-node:eric.20090722212922.3325:test_cairo_funcs declarations
#@+node:eric.20090722212922.3326:class TestCairoRenderer
class TestCairoRenderer(unittest.TestCase):
    #@    @+others
    #@+node:eric.20090722212922.3327:setUp
    def setUp(self):
        """Set up a new drawing"""
        self.d = Drawing(640, 480)

    #@-node:eric.20090722212922.3327:setUp
    #@+node:eric.20090722212922.3328:tearDown
    def tearDown(self):
        """Delete the drawing"""
        del(self.d)

    #@-node:eric.20090722212922.3328:tearDown
    #@+node:eric.20090722212922.3329:test_init
    def test_init(self):
        """Blank test"""
        pass

    #@-node:eric.20090722212922.3329:test_init
    #@+node:eric.20090722212922.3330:test_bezier
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

    #@-node:eric.20090722212922.3330:test_bezier
    #@+node:eric.20090722212922.3331:test_polyschlaft
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


    #@-node:eric.20090722212922.3331:test_polyschlaft
    #@+node:eric.20090722212922.3332:test_draw_funcs
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

    #@-node:eric.20090722212922.3332:test_draw_funcs
    #@+node:eric.20090722212922.3333:test_stroke_styles
    def test_stroke_styles(self):
        self.assertRaises(KeyError, self.d.stroke_linecap, 'gurda')
        self.d.stroke_linecap('butt')
        self.d.stroke_linecap('round')
        self.d.stroke_linecap('square')

        self.assertRaises(KeyError, self.d.stroke_linejoin, 'pou')
        self.d.stroke_linejoin('miter')
        self.d.stroke_linejoin('bevel')
        self.d.stroke_linejoin('round')


    #@-node:eric.20090722212922.3333:test_stroke_styles
    #@+node:eric.20090722212922.3334:test_scale_translate
    def test_scale_translate(self):
        self.d.save()
        self.d.translate(-200, 0)
        self.d.scale(1.5, 1.5)  # Scaling is done from (0,0) as reference.
        self.d.scale_centered(50, 50, 1.5, 1.5)
        self.d.circle(500, 100, 50) # same radius as others
        self.d.stroke()
        self.d.restore()

    #@-node:eric.20090722212922.3334:test_scale_translate
    #@+node:eric.20090722212922.3335:test_push_n_rotate
    def test_push_n_rotate(self):
        self.d.save()
        self.d.rotate(180)
        self.d.rotate_deg(180)
        self.d.rotate_rad(math.pi)
        self.d.restore()

    #@-node:eric.20090722212922.3335:test_push_n_rotate
    #@+node:eric.20090722212922.3336:test_colors
    def test_colors(self):
        self.d.set_source('black')

    #@-node:eric.20090722212922.3336:test_colors
    #@+node:eric.20090722212922.3337:test_new_fill_n_stroke
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

    #@-node:eric.20090722212922.3337:test_new_fill_n_stroke
    #@+node:eric.20090722212922.3338:test_operator
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

    #@-node:eric.20090722212922.3338:test_operator
    #@+node:eric.20090722212922.3339:test_fill_funcs
    def test_fill_funcs(self):
        self.assertRaises(KeyError, self.d.fill_rule, 'invalid')
        self.d.fill_rule('evenodd')
        # Don't feed it a tuple, but a 'color' now...
        self.d.fill()

    #@-node:eric.20090722212922.3339:test_fill_funcs
    #@+node:eric.20090722212922.3340:test_font_stuff
    def test_font_stuff(self):
        self.d.font('Times')
        self.d.font_size(24)
        self.d.font_stretch(2.0)
        self.d.font_stretch(2.0, 2.0)
        self.d.font_rotate(90)
        self.d.font_rotate(180)
        self.d.font_rotate(0)

    #@-node:eric.20090722212922.3340:test_font_stuff
    #@+node:eric.20090722212922.3341:test_text_stuff
    def test_text_stuff(self):
        self.d.text("Test of text string", 15, 15)

    #@-node:eric.20090722212922.3341:test_text_stuff
    #@+node:eric.20090722212922.3342:test_antialias_stuff
    def test_antialias_stuff(self):
        self.d.stroke_antialias(True)
        self.d.stroke_antialias(False)

    #@-node:eric.20090722212922.3342:test_antialias_stuff
    #@+node:eric.20090722212922.3343:test_rectangle_stuff
    def test_rectangle_stuff(self):
        self.d.rectangle(20, 20, 200, 200)
        self.d.rectangle_corners(20, 20, 230, 230)
        self.d.roundrectangle(10, 445, 610, 470, 5, 5)


    #@-node:eric.20090722212922.3343:test_rectangle_stuff
    #@+node:eric.20090722212922.3344:test_dash_stuff
    def test_dash_stuff(self):
        self.d.stroke_dash([1.0, 2.0, 3.0], 1.0)

    #@-node:eric.20090722212922.3344:test_dash_stuff
    #@+node:eric.20090722212922.3345:test_render
    def test_render(self):
        """Test drive rendering mechanism"""
        self.d.stroke_width(8)
        self.d.circle(250, 250, 50)
        self.d.stroke_width(2)
        self.d.circle(250, 250, 80)

        save_image(self.d, '/tmp/my.png')




    #@-node:eric.20090722212922.3345:test_render
    #@-others
#@-node:eric.20090722212922.3326:class TestCairoRenderer
#@-others
if __name__ == '__main__':
    unittest.main()

#@-node:eric.20090722212922.3324:@shadow test_cairo_funcs.py
#@-leo

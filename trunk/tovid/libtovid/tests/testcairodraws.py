import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.cairo_ import Drawing
import cairo
import os

class TestCairoDraws(unittest.TestCase):
    """Test several drawings, and view them"""
    
    def setUp(self):
        """Set up a new drawing"""
        print self
        self.d = Drawing((640, 480))

    def tearDown(self):
        """Delete the drawing"""
        self.d.render()
        os.system("display /tmp/my.png")
        del(self.d)
        
    def _test_defunc_cmds(self):
        """Test commands that should send an assertion error"""
        self.assertRaises(AssertionError, self.d.goto, 1)
        self.assertRaises(AssertionError, self.d.goto_end)
        self.assertRaises(AssertionError, self.d.append, 'str')
        self.assertRaises(AssertionError, self.d.insert, 'str')
        self.assertRaises(AssertionError, self.d.remove, 1)
        self.assertRaises(AssertionError, self.d.extend, self.d)
        self.assertRaises(AssertionError, self.d.undo)
        self.assert_(self.d.code() == '')

    def txt(self, txt):
        #self.d.rectangle_size((15, 445), (610, 20))
        self.d.push()
        self.d.color_stroke('black')
        self.d.color_fill('black', 0.3)
        self.d.roundrectangle((10, 440), (620, 470), (5, 5))
        self.d.fill_n_stroke()
        self.d.color_text('white')
        self.d.font_size(16)
        self.d.text((15, 460), txt)
        self.d.pop()

#    def test_font_rotate(self):
#        self.d.source_r


    def test_circle_stroke_fill(self):
        """Test whether the stroke goes over the fill and vice-versa"""
        self.txt(u"Red circle filled with white-50%")
        # Set colors
        self.d.color_fill('white', 0.5)
        self.d.color_stroke('red', 1.0)
        # Set width
        self.d.stroke_width(15)

        # Define a circle (left-most)
        self.d.circle_rad((100, 100), 50)
        self.d.stroke()
        self.d.fill()

        # Define a second circle (centered)
        self.d.circle_rad((300, 100), 50)
        self.d.fill()
        self.d.stroke()

        # Define a third circle (rightmost), and scale+translate it.
        self.d.push()
        self.d.translate((-200, 0))
        self.d.scale((1.5, 1.5))  # Scaling is done from (0,0) as reference.
        self.d.circle_rad((500, 100), 50) # same radius as others
        self.d.stroke()
        self.d.pop()
        
        
    def test_round_rectangle(self):
        """Test bezier points placement to make a round rectangle."""
        self.txt(u"We should see here a round rectangle")

        self.d.stroke_width(10)
        self.d.color_fill('red')
        self.d.roundrectangle((20, 20), (400, 400), (20, 20))
        self.d.fill()
        

    def test_scaling(self):
        """Test the scale() and scale_centered() functions."""
        self.txt(u"Three circles. Red: scaled from (0,0), green, "\
                 "scaled_centered")

        self.d.auto_stroke(True)

        # Black circle
        self.d.push()
        self.d.stroke_width(10)
        self.d.color_stroke('black')
        self.d.circle_rad((100, 100), 30)
        self.d.pop()

        # Red circle
        self.d.push()
        self.d.stroke_width(10)
        self.d.scale((2.0, 2.0))
        self.d.color_stroke('red')
        self.d.circle_rad((100, 100), 30)
        self.d.pop()

        # Green circle
        self.d.push()
        self.d.stroke_width(10)
        self.d.scale_centered((100, 100), (2.0, 2.0))
        self.d.color_stroke('green')
        self.d.circle_rad((100, 100), 30)
        self.d.pop()


            
    def _test_draw_funcs(self):
        """Test drive drawing functions

        We still need to verify the output visually to make sure it's okay
        """
        # bezier is tested in test_bezier()
        self.d.stroke_width(5)
        
        self.d.affine(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        self.d.arc((25,25), 15, (0, 270))
        self.d.arc_rad((125, 125), 50, (0, 1))
        self.d.circle((55, 55), (100, 50))
        self.d.circle_rad((250, 250), 20)
        
        self.d.line((25,25), (125,125))
        self.d.line((125,125), (55,55))
        self.d.line((55,55), (250,250))


    def _test_stroke_styles(self):
        self.assertRaises(KeyError, self.d.stroke_linecap, 'gurda')
        self.d.stroke_linecap('butt')
        self.d.stroke_linecap('round')
        self.d.stroke_linecap('square')

        self.assertRaises(KeyError, self.d.stroke_linejoin, 'pou')
        self.d.stroke_linejoin('miter')
        self.d.stroke_linejoin('bevel')
        self.d.stroke_linejoin('round')

        self.d.scale((2, 2))

    def _test_push_n_rotate(self):
        self.d.push()
        self.d.rotate(180)
        self.d.rotate_deg(180)
        self.d.rotate_rad(math.pi)
        self.d.pop()

    def _test_set_color(self):
        self.d.source_color('#112233')
        self.d.source_rgb((1,2,3))
        self.d.source_rgba((1,2,3), 0.9)
        self.d.opacity(0.8)
        
    def _test_fill_funcs(self):
        self.d.fill_opacity(0.8)
        self.assertRaises(KeyError, self.d.fill_rule, 'invalid')
        self.d.fill_rule('evenodd')

    def _test_font_stuff(self):
        self.d.font('Times')
        self.d.font_family('')
        self.d.font_family()
        self.d.font_size(24)
        self.d.font_stretch(2.0)
        self.d.font_stretch(2.0, 2.0)
        self.d.font_rotate(90)
        self.assertRaises(KeyError, self.d.font_slant, 'invalid_key')
        self.d.font_slant('italic')
        self.assertRaises(KeyError, self.d.font_weight, 'invalid_key')
        self.d.font_weight('bold')

    def _test_antialias_stuff(self):
        self.d.stroke_antialias(True)
        self.assert_(self.d.cr.get_antialias() == cairo.ANTIALIAS_GRAY)
        self.d.stroke_antialias(False)
        self.assert_(self.d.cr.get_antialias() == cairo.ANTIALIAS_NONE)
        
    def _test_dash_stuff(self):
        self.d.stroke_dash([1.0, 2.0, 3.0], 1.0)
        self.d.stroke_dasharray([1.0, 2.0, 3.0])
        self.d.stroke_dashoffset(5.0)

    def _test_render(self):
        """Test drive rendering mechanism"""
        self.d.stroke_width(8)
        self.d.circle((250, 250), (300, 300))
        self.d.stroke_width(2)
        self.d.circle_rad((250, 250), 80)

        self.d.render()

        
        


if __name__ == '__main__':
    unittest.main()


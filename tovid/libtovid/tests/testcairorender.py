import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.cairo import Drawing


class TestCairoRenderer(unittest.TestCase):
    def setUp(self):
        """Set up a new drawing"""
        self.d = Drawing((640, 480))

    def tearDown(self):
        """Delete the drawing"""
        del(self.d)
        
    def test_init(self):
        """Blank test"""
        pass

    def test_defunc_cmds(self):
        """Test commands that should send an assertion error"""
        self.assertRaises(AssertionError, self.d.goto, 1)
        self.assertRaises(AssertionError, self.d.goto_end)
        self.assertRaises(AssertionError, self.d.append, 'str')
        self.assertRaises(AssertionError, self.d.insert, 'str')
        self.assertRaises(AssertionError, self.d.remove, 1)
        self.assertRaises(AssertionError, self.d.extend, self.d)
        self.assertRaises(AssertionError, self.d.undo)
        self.assert_(self.d.code() == '')
        
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

        self.assertRaises(AssertionError, self.d.bezier, pts)
            
    def test_draw_funcs(self):
        """Test drive drawing functions

        We still need to verify the output visually to make sure it's okay
        """
        # bezier is tested in test_bezier()
        self.d.stroke_width(5)
        
        self.d.affine(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        self.d.arc((5,5), 5, (0, 270))
        self.d.arc_rad((5, 5), 5, (0, 1))
        self.d.circle((5, 5), (1, 1))
        self.d.circle_rad((5, 5), 5)

        self.assertRaises(KeyError, self.d.stroke_linecap, 'gurda')
        self.d.stroke_linecap('butt')
        self.d.stroke_linecap('round')
        self.d.stroke_linecap('square')

        self.assertRaises(KeyError, self.d.stroke_linejoin, 'pou')
        self.d.stroke_linejoin('miter')
        self.d.stroke_linejoin('bevel')
        self.d.stroke_linejoin('round')

        self.d.scale((2, 2))

        self.d.rotate(180)
        self.d.rotate_deg(180)
        self.d.rotate_rad(math.pi)

        self.d.source_rgb((1,2,3))
        self.d.source_rgba((1,2,3), 0.9)
        self.d.opacity(0.8)
        self.d.fill_opacity(0.8)

    def test_render(self):
        """Test drive rendering mechanism"""
        self.d
        self.d.stroke_width(25)
        self.d.circle((25, 25), (250, 250))
        self.d.circle_rad((25, 25), 80)

        #print "This should show up a window with a circle somewhere"
        self.d.render()

        
        


if __name__ == '__main__':
    unittest.main()


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
        self.d = Drawing((640, 480))

    def tearDown(self):
        """Delete the drawing"""
        self.d.render()
        os.system("display /tmp/my.png")
        del(self.d)
        
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

    ################ Tests start here ###########

    def test_image_load(self):
        """Draws an image into the buffer"""
        self.txt("Four red circles (first black bg), in a line, always bigger.")
        # Save a temp image to disk...
        im = Drawing((50,50))
        im.stroke_width(5)
        im.color_stroke('red')
        im.circle_rad((25,25), 20)
        im.stroke()
        im.circle_rad((25,25), 10)
        im.save_jpg('/tmp/img.jpg')
        im.save_png('/tmp/img.png')

        # Load it with the image() function.
        self.d.image((5,5), (25, 25), '/tmp/img.jpg')
        self.d.image((50, 50), (35,35), '/tmp/img.png')
        self.d.image((100, 100), (50, 50), '/tmp/img.png')
        self.d.rectangle_size((150, 150), (150, 100))
        self.d.stroke()
        self.d.image((150, 150), (150, 100), im.surface)

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

        self.d.stroke_width(1)
        self.d.color_fill('red', 0.5)
        self.d.color_stroke('black')
        self.d.roundrectangle((20, 20), (400, 400), (20, 20))
        self.d.fill_n_stroke()


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


if __name__ == '__main__':
    unittest.main()


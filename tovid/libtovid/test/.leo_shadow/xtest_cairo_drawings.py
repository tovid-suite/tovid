#@+leo-ver=4-thin
#@+node:eric.20090722212922.3306:@shadow test_cairo_drawings.py
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.render.drawing import Drawing, display, save_jpg, save_png, interlace_drawings
import libtovid
import cairo
import os

#@+others
#@+node:eric.20090722212922.3308:class TestCairoDraws
class TestCairoDraws(unittest.TestCase):
    """Test several drawings, and view them"""
    #@    @+others
    #@+node:eric.20090722212922.3309:setUp
    def setUp(self):
        """Set up a new drawing"""
        self.d = Drawing(640, 480)

    #@-node:eric.20090722212922.3309:setUp
    #@+node:eric.20090722212922.3310:tearDown
    def tearDown(self):
        """Delete the drawing"""
        display(self.d)
        del(self.d)

    #@-node:eric.20090722212922.3310:tearDown
    #@+node:eric.20090722212922.3311:txt
    def txt(self, txt):
        #self.d.rectangle(15, 445, 610, 20)
        self.d.save()
        self.d.roundrectangle(10, 440, 620, 470, 5, 5)
        self.d.stroke('black')
        self.d.fill('black', 0.3)
        self.d.font_size(16)
        self.d.set_source('white') 
        self.d.text(txt, 15, 460)
        self.d.restore()

    #@-node:eric.20090722212922.3311:txt
    #@-others

#@-node:eric.20090722212922.3308:class TestCairoDraws
#@+node:eric.20090722212922.3312:class TestInterlaceDrawings
class TestInterlaceDrawings(TestCairoDraws):
    #@    @+others
    #@+node:eric.20090722212922.3313:test_interlace_drawings
    def test_interlace_drawings(self):
        """Test interlace_drawings function"""
        self.txt("Show an interlaced 200x200 image of blue and red.")

        # Save a temp image to disk...
        im1 = Drawing(200, 200)
        im1.image(0,0,200,200, 'bleu.png')
        im2 = Drawing(200, 200)
        im2.image(0,0,200,200, 'rouge.png')

        mix = interlace_drawings(im1, im2)

        save_png(mix, '/tmp/img.png', mix.w, mix.h)

        # Show in the test showcase.
        self.d.image(0, 0, 200, 200, '/tmp/img.png')


    #@-node:eric.20090722212922.3313:test_interlace_drawings
    #@-others
#@-node:eric.20090722212922.3312:class TestInterlaceDrawings
#@+node:eric.20090722212922.3314:class TestImageLoad
class TestImageLoad(TestCairoDraws):
    #@    @+others
    #@+node:eric.20090722212922.3315:test_image_load
    def test_image_load(self):
        """Draws an image into the buffer"""
        self.txt("Four red circles (first black bg), in a line, always bigger.")
        # Save a temp image to disk...
        im = Drawing(50, 50)
        im.stroke_width(5)
        im.circle(25, 25, 20)
        im.stroke('red')
        im.circle(25, 25, 10)
        im.stroke()
        save_jpg(im, '/tmp/img.jpg')
        save_png(im, '/tmp/img.png')

        # Load it with the image() function.
        self.d.image(5, 5, 25, 25, '/tmp/img.jpg')
        self.d.image(50, 50, 35, 35, '/tmp/img.png')
        self.d.image(100, 100, 50, 50, '/tmp/img.png')
        self.d.rectangle(150, 150, 150, 100)
        self.d.stroke()
        self.d.image(150, 150, 150, 100, im.surface)

    #@-node:eric.20090722212922.3315:test_image_load
    #@-others
#@-node:eric.20090722212922.3314:class TestImageLoad
#@+node:eric.20090722212922.3316:class TestCircleStrokeFill
class TestCircleStrokeFill(TestCairoDraws):
    #@    @+others
    #@+node:eric.20090722212922.3317:test_circle_stroke_fill
    def test_circle_stroke_fill(self):
        """Test whether the stroke goes over the fill and vice-versa"""
        self.txt(u"Red circle filled with white-50%")
        # Set colors
        fc = self.d.create_source('white', 0.5) # fill color
        sc = self.d.create_source('red', 1.0)   # stroke color
        # Set width
        self.d.stroke_width(15)

        # Define a circle (left-most)
        self.d.circle(100, 100, 50)
        self.d.stroke(sc)
        self.d.fill(fc)

        # Define a second circle (centered)
        self.d.circle(300, 100, 50)
        self.d.fill(fc)
        self.d.stroke(sc)

        # Define a third circle (rightmost), and scale+translate it.
        self.d.save()
        self.d.translate(-200, 0)
        self.d.scale(1.5, 1.5)  # Scaling is done from (0,0) as reference.
        self.d.circle(500, 100, 50) # same radius as others
        self.d.stroke(sc)
        self.d.restore()

    #@-node:eric.20090722212922.3317:test_circle_stroke_fill
    #@-others
#@-node:eric.20090722212922.3316:class TestCircleStrokeFill
#@+node:eric.20090722212922.3318:class TestRoundRectangle
class TestRoundRectangle(TestCairoDraws):        
    #@    @+others
    #@+node:eric.20090722212922.3319:test_round_rectangle
    def test_round_rectangle(self):
        """Test bezier points placement to make a round rectangle."""
        self.txt(u"We should see here a round rectangle")

        self.d.stroke_width(1)
        self.d.roundrectangle(20, 20, 400, 400, 20, 20) 
        self.d.fill('red', 0.5)
        self.d.stroke('black')

    #@-node:eric.20090722212922.3319:test_round_rectangle
    #@-others
#@-node:eric.20090722212922.3318:class TestRoundRectangle
#@+node:eric.20090722212922.3320:class TestTextAlign
class TestTextAlign(TestCairoDraws):
    #@    @+others
    #@+node:eric.20090722212922.3321:test_text_align
    def test_text_align(self):
        """Test the different align="" values for .text()"""
        self.txt(u"Tries align='left', 'center' and 'right'")
        self.d.set_source('white')
        self.d.font_size(18)
        self.d.text('Placed at (320, 100), aligned: left',
                    320, 100, align='left')
        self.d.text('Placed at (320, 150), aligned: center',
                    320, 150, align='center')
        self.d.text('Placed at (320, 200), aligned: right',
                    320, 200, align='right')

    #@-node:eric.20090722212922.3321:test_text_align
    #@-others
#@-node:eric.20090722212922.3320:class TestTextAlign
#@+node:eric.20090722212922.3322:class TestScaling
class TestScaling(TestCairoDraws):
    #@    @+others
    #@+node:eric.20090722212922.3323:test_scaling
    def test_scaling(self):
        """Test the scale() and scale_centered() functions."""
        self.txt(u"Three circles. Red: scaled from (0,0), green, "\
                 "scaled_centered")

        # Black circle
        self.d.save()
        self.d.stroke_width(10)
        self.d.circle(100, 100, 30)
        self.d.stroke('black')
        self.d.restore()

        # Red circle
        self.d.save()
        self.d.stroke_width(10)
        self.d.scale(2.0, 2.0)
        self.d.circle(100, 100, 30)
        self.d.stroke('red')
        self.d.restore()

        # Green circle
        self.d.save()
        self.d.stroke_width(10)
        self.d.scale_centered(100, 100, 2.0, 2.0)
        self.d.circle(100, 100, 30)
        self.d.stroke('green')
        self.d.restore()


    #@-node:eric.20090722212922.3323:test_scaling
    #@-others
#@-node:eric.20090722212922.3322:class TestScaling
#@-others
if __name__ == '__main__':
    unittest.main()

#@-node:eric.20090722212922.3306:@shadow test_cairo_drawings.py
#@-leo

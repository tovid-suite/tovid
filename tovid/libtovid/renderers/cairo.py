#! /usr/bin/env python
# -=- encoding: latin-1 -=-
# cairo.py


"""A Python interface to the Cairo library.

Run this script standalone for a demonstration:

    $ python libtovid/cairo.py

To build your own Cairo vector image using this module, fire up your Python
interpreter:

    $ python

And do something like this:

    >>> from libtovid.cairo import Drawing
    >>> drawing = Drawing((800, 600))

This creates an image (drawing) at 800x600 display resolution. Drawing has a
wealth of draw functions.

Example usage:

    >>> drawing.fill('blue')
    >>> drawing.rectangle((0, 0), (800, 600))
    >>> drawing.fill('white')
    >>> drawing.rectangle((320, 240), (520, 400))

If you want to preview what you have so far, call drawing.render().

You can keep drawing on the image, calling render() at any time to display the
rendered image.


References:
[1] http://www.cairegraphics.org

"""

__all__ = ['Drawing']

import os
import sys
import commands
from math import pi, sqrt
import cairo

class Drawing:
    """A Cairo image context, ready to be drawn.

    Drawing functions are mostly identical to their MVG counterparts, e.g.
    these two are equivalent:

        rectangle 100,100 200,200       # MVG command
        rectangle((100,100), (200,200)) # Drawing function

    The only exception is MVG commands that are hyphenated. For these, use an
    underscore instead:

        font-family "Serif"      # MVG command
        font_family("Serif")     # Drawing function

    """
    def __init__(self, size=(720, 480)):
        self.size = size
        self.width, self.height = size
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width,
                                     self.height)
        self.cr = cairo.Context(self.surface)
 
    #
    # Cairo drawing commands
    #

    def affine(self, scale_x, rot_x, rot_y, scale_y, translate_x, translate_y):
        """Define a 3x3 transformation matrix:
            
            [ scale_x  rot_y    translate_x ]
            [ rot_x    scale_y  translate_y ]
            [ 0        0        1           ]

        This is scaling, rotation, and translation in a single matrix,
        so it's a compact way to represent any transformation.
        
        See [http://www.w3.org/TR/SVG11/coords.html] for more on
        these matrices and how to use them.
        """
        mtx = cairo.Matrix(scale_x, rot_x, rot_y, scale_y,
                           translate_x, translate_y)
        self.cr.set_matrix(mtx)

    def arc(self, (x, y), radius, (start_deg, end_deg)):
        """Draw an arc from (x, y), with the specified radius, starting at degree
        start_deg and ending at end_deg.
        """
        # Convert deg. to rad.
        self.cr.arc(x, y, radius, start_deg * pi/180, end_deg * pi/180)
        self.cr.stroke()

    def arc_rad(self, (x, y), radius, (start_rad, end_rad)):
        """Draw an arc from (x, y), with the specified radius, starting at radian
        start_rad and ending at end_rad.
        """
        # Convert deg. to rad.
        self.cr.arc(x, y, radius, start_rad, end_rad)
        self.cr.stroke()

    def bezier(self, pt_list):
        """Create a Bézier curve.

        pt_list should look like:
            [[(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
             [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
             [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)]]
        where (x0, y0) are the point coordinates, and x_ctl* are the control
        points coordinates.

        """
        assert len(pt_list) > 1, "You need at least two points"
        for x in pt_list:
            assert len(x) == 3, "You need to specify three tuples for each point"
            for y in x:
                assert isinstance(y, tuple), "You need to specify two " \
                                              "values-tuple"
                assert len(y) == 2, "Each point must have two coordinates"
                
        # Move to the first x,y in the first point
        self.cr.move_to(pt_list[0][0][0], pt_list[0][0][1])
        for pt in pt_list:
            self.cr.curve_to(pt[2][0], pt[2][1],
                             pt[0][0], pt[0][1],
                             pt[1][0], pt[1][1])

    def circle(self, (center_x, center_y), (perimeter_x, perimeter_y)):
        """Draw a circle defined by center and perimeter points."""

        # distance between x1y1, and x2y2
        rad = sqrt( (perimeter_x - center_x) ** 2 -
                    (perimeter_y - center_y) ** 2 )
        
        self.cr.arc(center_x, center_y, rad, 0, 0)
        self.cr.stroke()
                    
    def circle_rad(self, (center_x, center_y), radius):
        """Draw a circle defined by center point and radius."""
        self.cr.arc(center_x, center_y, radius, 0, 0)
        self.cr.stroke()

    def clip_path(self, url):
        self.insert('clip-path url(%s)' % url)

    def clip_rule(self, rule):
        # rule in [evenodd, nonzero]
        self.insert('clip-rule %s' % rule)

    def clip_units(self, units):
        # May be: userSpace, userSpaceOnUse, objectBoundingBox
        self.insert('clip-units %s' % units)

    def color(self, (x, y), method='floodfill'):
        """Define a coloring method. method may be 'point', 'replace',
        'floodfill', 'filltoborder', or 'reset'.
        (Anyone know what (x, y) are?)"""
        self.insert('color %s,%s %s' % (x, y, method))
    
    def decorate(self, decoration):
        """Decorate text(?) with the given style, which may be 'none',
        'line-through', 'overline', or 'underline'."""
        self.insert('decorate %s' % decoration)

    def ellipse(self, (center_x, center_y), (radius_x, radius_y),
                (arc_start, arc_stop)):
        # Draw arc, transform matrix, etc...
        
        self.insert('ellipse %s,%s %s,%s %s,%s' % \
                (center_x, center_y, radius_x, radius_y, arc_start, arc_stop))


    def source_color(self, color, opacity=1.0):
        """Set the RGB values, #AABBCC triplet, or named color.

            http://www.imagemagick.org/script/color.php
        """
        # TODO: complete this function
        pass
    
    def source_rgb(self, (r,g,b)):
        """Set the source color for the next drawing operations.

        If you want to add transparency, use source_rgba() instead.
        """
        self.rgb = (r,g,b)
        self.cr.set_source_rgb(r, g, b)

    def source_rgba(self, (r,g,b), a):
        """Set the source color and opacity for the next drawing
        operations.
        """
        self.rgb = (r,g,b)
        self.cr.set_source_rgba(r, g, b, a)

    def opacity(self, opacity):
        """Set the opacity of the next operations.

        It's basically just a shorthand to source_rgba() using the
        latest used colors."""
        self.source_rgba(self.rgb, opacity)

    def fill_opacity(self, opacity):
        """Define fill opacity, from fully transparent (0.0) to fully
        opaque (1.0).

        Alias for opacity()."""
        self.opacity(opacity)
    
    def fill(self, color):
        """Fill the current path with the source color
        
        
        WARNING: Cairo and MVG backends don't handle 'fill' the same way.
                 Cairo will paint with a 'fill' command, whereas MVG will
                 set the color to be used in the next drawing operations.
        """
        self.insert('fill "%s"' % color)

    def fill_rgb(self, (r, g, b)):
        """Set the fill color to an RGB value."""
        self.fill('rgb(%s, %s, %s)' % (r, g, b))
    
    def fill_rule(self, rule):
        """Set the fill rule to one of:
        evenodd, nonzero
        http://www.w3.org/TR/SVG/painting.html#FillRuleProperty
        """
        self.insert('fill-rule %s' % rule)
    
    def font(self, name):
        """Set the current font, by name."""
        self.insert('font "%s"' % name)
    
    def font_family(self, family):
        """Set the current font, by family name."""
        self.insert('font-family "%s"' % family)
    
    def font_size(self, pointsize):
        """Set the current font size in points."""
        self.insert('font-size %s' % pointsize)
    
    def font_stretch(self, stretch_type):
        """Set the font stretch type to one of:
        all, normal,
        semi-condensed, condensed, extra-condensed, ultra-condensed,
        semi-expanded, expanded, extra-expanded, ultra-expanded
        """
        self.insert('font-stretch %s' % stretch_type)
    
    def font_style(self, style):
        """Set the font style to one of:
        all, normal, italic, oblique
        """
        self.insert('font-style %s' % style)
    
    def font_weight(self, weight):
        """Set the font weight to one of:
        all, normal, bold, 100, 200, ... 800, 900
        """
        self.insert('font-weight %s' % weight)
    
    def gradient_units(self, units):
        """Set gradient units to one of:
        userSpace, userSpaceOnUse, objectBoundingBox
        """
        self.insert('gradient-units %s' % units)
    
    def gravity(self, direction):
        """Set the gravity direction to one of:
        
            NorthWest, North, NorthEast,
            West, Center, East,
            SouthWest, South, SouthEast
            
        Note: gravity is known to affect text and images; it does not affect
        points, lines, circles, rectangles, roundrectangles, polylines or
        polygons.
        """
        self.insert('gravity %s' % direction)
    
    def image(self, compose, (x, y), (width, height), filename):
        """Draw an image centered at (x, y), scaled to the given width and
        height. compose may be:
            Add, Minus, Plus, Multiply, Difference, Subtract,
            Copy, CopyRed, CopyGreen, CopyBlue, CopyOpacity,
            Atop, Bumpmap, Clear, In, Out, Over, Xor

        See: 
            http://www.imagemagick.org/script/magick-vector-graphics.php
        under 'image', for more ops.
        """
        self.insert('image %s %s,%s %s,%s "%s"' % \
                    (compose, x, y, width, height, filename))
    
    def line(self, (x0, y0), (x1, y1)):
        """Draw a line from (x0, y0) to (x1, y1). Note: Line color is defined
        by the 'fill' command."""
        self.insert('line %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def matte(self, (x, y), method='floodfill'):
        # method may be: point, replace, floodfill, filltoborder, reset
        # (What do x, y mean?)
        self.insert('matte %s,%s %s' % (x, y, method))

    def offset(self, offset):
        self.insert('offset %s' % offset)

    def path(self, path_data):
        """Draw a path. path_data is a list of instructions and coordinates,
        e.g. ['M', (100,100), 'L', (200,200), ...]
        Instructions are M (moveto), L (lineto), A (arc), Z (close path)
        For more on using paths (and a complete list of commands), see:
        http://www.cit.gu.edu.au/~anthony/graphics/imagick6/draw/#paths
        http://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
        """
        command = 'path'
        for token in path_data:
            if isinstance(token, tuple):
                command += ' %s,%s' % token
            else:
                command += ' %s' % token
        self.insert(command)

    def point(self, (x, y)):
        """Draw a point at position (x, y)."""
        self.insert('point %s,%s' % (x, y))

    def polygon(self, point_list):
        """Draw a filled polygon defined by (x, y) points in the given list."""
        command = 'polygon'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)
    
    def polyline(self, point_list):
        """Draw an unfilled polygon defined by (x, y) points in the given list."""
        command = 'polyline'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)
    
    def rectangle(self, (x0, y0), (x1, y1)):
        """Draw a rectangle from (x0, y0) to (x1, y1)."""
        self.insert('rectangle %s,%s %s,%s' % (x0, y0, x1, y1))

    def rotate(self, degrees):
        """Map to rotate_deg()"""
        self.rotate_deg(degrees)
        
    def rotate_deg(self, degrees):
        """Rotate by the given number of degrees."""
        m = self.cr.get_matrix()
        m.rotate(degrees * 180./pi)
        self.cr.set_matrix(m)

    def rotate_rad(self, rad):
        """Rotate by the given number of radians."""
        m = self.cr.get_matrix()
        m.rotate(rad)
        self.cr.set_matrix(m)

    def roundrectangle(self, (x0, y0), (x1, y1), (bevel_width, bevel_height)):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        a bevel size of (bevel_width, bevel_height)."""
        self.insert('roundrectangle %s,%s %s,%s %s,%s' % \
                (x0, y0, x1, y1, bevel_width, bevel_height))

    def scale(self, (dx, dy)):
        """Set scaling in x and y to (dx, dy)."""
        m = self.cr.get_matrix()
        m.scale(dx, dy)
        self.cr.set_matrix(m)

    def skewX(self, angle):
        self.insert('skewX %s' % angle)
    
    def skewY(self, angle):
        self.insert('skewY %s' % angle)

    def stop_color(self, color, offset):
        self.insert('stop-color %s %s' % (color, offset))
        
    def stroke(self, color):
        """Set the current stroke color, or 'none' for transparent."""
        self.insert('stroke %s' % color)

    def stroke_antialias(self, do_antialias):
        """Turn stroke antialiasing on (True) or off (False)."""
        if do_antialias:
            self.insert('stroke-antialias 1')
        else:
            self.insert('stroke-antialias 0')

    def stroke_dasharray(self, array):
        """Set the stroke dash style, as defined by the given array. For
        example, stroke_dasharray([5, 3]) draws dashed-line strokes with
        (roughly) 5-pixel dashes separated by 3-pixel spaces. Pass None or
        [] to draw solid-line strokes."""
        if array == None or array == []:
            self.insert('stroke-dasharray none')
        else:
            cmd = 'stroke-dasharray'
            for length in array:
                cmd += ' %s' % length
            self.insert(cmd)
        
    def stroke_dashoffset(self, offset):
        self.insert('stroke-dashoffset %s' % offset)

    def stroke_linecap(self, cap_type):
        """Set the type of line-cap to use. cap_type may be 'butt', 'round',
        or 'square'."""
        dic = {'butt': cairo.LINE_CAP_BUTT,
               'round': cairo.LINE_CAP_ROUND,
               'square': cairo.LINE_CAP_SQUARE}
        
        self.cr.set_line_cap(dic[cap_type])

    def stroke_linejoin(self, join_type):
        """Set the type of line-joining to do. join_type may be 'bevel',
        'miter', or 'round'."""
        dic = {'bevel': cairo.LINE_JOIN_BEVEL,
               'miter': cairo.LINE_JOIN_MITER,
               'round': cairo.LINE_JOIN_ROUND}
        self.cr.set_line_join(dic[join_type])

    def stroke_opacity(self, opacity):
        """Set the stroke opacity. opacity may be decimal (0.0-1.0)
        or percentage (0-100)%."""
        self.insert('stroke-opacity %s' % opacity)

    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        self.cr.set_line_width(width)
    
    def text(self, (x, y), text_string):
        """Draw the given text string, with lower-left corner at (x, y)."""
        # TODO: Escape special characters in text string
        self.insert('text %s,%s "%s"' % (x, y, text_string))
    
    def text_antialias(self, do_antialias):
        """Turn text antialiasing on (True) or off (False)."""
        if do_antialias:
            self.insert('text-antialias 1')
        else:
            self.insert('text-antialias 0')

    def text_undercolor(self, color):
        self.insert('text-undercolor %s' % color)

    def translate(self, (x, y)):
        """Do a translation by (x, y) pixels."""
        self.insert('translate %s,%s' % (x, y))
    
    def viewbox(self, (x0, y0), (x1, y1)):
        """Define a rectangular viewing area from (x0, y0) to (x1, y1)."""
        self.insert('viewbox %s,%s %s,%s' % (x0, y0, x1, y1))
    
    def push(self, context='graphic-context', *args, **kwargs):
        """Save state, and begin a new context. context may be:
        'clip-path', 'defs', 'gradient', 'graphic-context', or 'pattern'.
        """
        # TODO: Accept varying arguments depending on context, e.g.
        #    push('graphic-context')
        # or push('pattern', id, radial, x, y, width,height)
        self.insert('push %s' % context)
        self.indent += 1

    def pop(self, context='graphic-context'):
        """Restore the previously push()ed context. context may be:
        'clip-path', 'defs', 'gradient', 'graphic-context', or 'pattern'.
        """
        self.indent -= 1
        self.insert('pop %s' % context)
    
    def comment(self, text):
        """Add a comment to the drawing's code.

        NOTE: Unused in Cairo context"""
        pass

    #
    # Editor interface/interactive functions
    #

    def load(self, filename):
        """Load MVG from the given file."""
        self.clear()
        infile = open(filename, 'r')
        for line in infile.readlines():
            cleanline = line.lstrip(' \t').rstrip(' \n\r')
            # Convert all single-quotes to double-quotes
            cleanline = cleanline.replace("'", '"')
            self.append(cleanline)
        infile.close()

    def save(self, filename):
        """Save to the given MVG file."""
        self.filename = os.path.abspath(filename)
        outfile = open(filename, 'w')
        for line in self.data:
            outfile.write("%s\n" % line)
        outfile.close()

    def code(self, editing=True):
        """Return complete MVG text for the Drawing.
        
        NOTE: Unused in Cairo context"""
        return ''

    def render(self):
        """Render the .mvg with ImageMagick, and display it."""
        self.surface.write_to_png('/tmp/my.png')
        #print commands.getoutput("display /tmp/my.png")

    def save_image(self, img_filename):
        """Render the drawing to a .jpg, .png or other image."""
        self.save(self.filename)
        cmd = "convert -size %sx%s " % self.size
        cmd += "%s %s" % (self.filename, img_filename)
        print "Rendering drawing to: %s" % img_filename
        print commands.getoutput(cmd)


    def goto(self, line_num):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use goto() method"

    def goto_end(self):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use goto_end() method"

    def append(self, mvg_string):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use append() method"

    def insert(self, mvg_string, at_line=0):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use insert() method"

    def remove(self, from_line, to_line=None):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use remove() method"

    def extend(self, drawing):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use extend() method"

    def undo(self, steps=1):
        """Command used in the MVG backend, shouldn't be used in the Cairo backend.
        """
        assert 0, "Shouldn't use undo() method"


# Demo functions

def draw_fontsize_demo(drawing):
    """Draw font size samples on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.push()
    
    # Draw white text in a range of sizes
    drawing.fill('white')
    for size in [12,16,20,24,28,32]:
        ypos = size * size / 5
        drawing.font('Helvetica')
        drawing.font_size(size)
        drawing.text((0, ypos), "%s pt: The quick brown fox" % size)
    
    # Restore context
    drawing.pop()

def draw_font_demo(drawing):
    """Draw samples of different fonts on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.push()

    fontsize = 48
    drawing.font_size(fontsize)
    fonts = ['Helvetica', 'NimbusSans', 'Tahoma', 'Times']
    ypos = 0
    for font in fonts:
        drawing.font(font)
        # Transparent shadow
        drawing.fill('darkblue')
        drawing.fill_opacity(0.4)
        drawing.text((3, ypos+3), font)
        # White text
        drawing.fill('white')
        drawing.fill_opacity(1.0)
        drawing.text((0, ypos), font)
        ypos += fontsize

    # Restore context
    drawing.pop()

def draw_shape_demo(drawing):
    """Draw shape samples on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.push()

    # Large orange circle with black stroke
    drawing.push()
    drawing.stroke('black')
    drawing.stroke_width(12)
    drawing.fill('orange')
    # Circle at (500, 200), with radius 200
    drawing.circle_rad((500, 200), 200)
    drawing.pop()

    # Grey-stroked blue circles
    drawing.push()
    drawing.stroke('grey')
    drawing.stroke_width(2)
    drawing.fill('#8080FF')
    drawing.circle_rad((65, 50), 15)
    drawing.fill('#2020F0')
    drawing.circle_rad((60, 100), 10)
    drawing.fill('#0000A0')
    drawing.circle_rad((55, 150), 5)
    drawing.pop()

    # Semitransparent green rectangles
    drawing.push()
    drawing.translate((50, 400))
    drawing.fill('lightgreen')
    for scale in [0.2, 0.4, 0.7, 1.1, 1.6, 2.2, 2.9, 3.7]:
        drawing.push()
        drawing.translate((scale * 70, scale * -50))
        drawing.scale((scale, scale))
        drawing.fill_opacity(scale / 5.0)
        drawing.stroke_width(scale)
        drawing.stroke('black')
        drawing.roundrectangle((-30, -30), (30, 30), (8, 8))
        drawing.pop()
    drawing.pop()

    # Restore context
    drawing.pop()


def draw_stroke_demo(drawing):
    """Draw a stroke/strokewidth demo on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.push()

    for width in [1, 2, 4, 6, 8, 10, 12, 14, 16]:
        drawing.stroke_width(width)
        rgb = ((255 - width * 8), (120 - width * 5), 0)
        drawing.stroke('rgb(%s,%s,%s)' % rgb)
        offset = width * 10
        drawing.line((0, offset), (-offset, offset))

    # Restore context
    drawing.pop()


def draw_pattern_demo(drawing):
    """Draw a pattern demo on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.push()

    # Define a pattern of blue and green squares
    drawing.push('defs')
    drawing.push('pattern', 'squares', (10, 10), (20, 20))
    drawing.push()
    drawing.fill('blue')
    drawing.rectangle((5, 5), (15, 15))
    drawing.pop()
    drawing.push()
    drawing.fill('green')
    drawing.rectangle((10, 10), (20, 20))
    drawing.pop()
    drawing.pop('pattern')
    drawing.pop('defs')
    # Draw a rectangle filled with the pattern
    drawing.push()
    drawing.fill('url(#squares)')
    drawing.rectangle((0, 0), (80, 80))
    drawing.pop()
    
    # Restore context
    drawing.pop()

if __name__ == '__main__':
    drawing = Drawing((720, 480))

    # Start a new
    drawing.push()
    drawing.viewbox((0, 0), (720, 480))

    # Add a background fill
    drawing.comment("Background")
    drawing.fill('darkgrey')
    drawing.rectangle((0, 0), (720, 480))

    # Shape demo
    drawing.comment("Shape demo")
    drawing.push()
    draw_shape_demo(drawing)
    drawing.pop()

    # Font size demo
    drawing.comment("Font size demo")
    drawing.push()
    drawing.translate((20, 20))
    draw_fontsize_demo(drawing)
    drawing.pop()

    # Font face demo
    drawing.comment("Font face demo")
    drawing.push()
    drawing.translate((20, 300))
    draw_font_demo(drawing)
    drawing.pop()

    # Stroke demo
    drawing.comment("Stroke demo")
    drawing.push()
    drawing.translate((600, 200))
    draw_stroke_demo(drawing)
    drawing.pop()

    #drawing.push()
    #drawing.translate((100, 300))
    #draw_pattern_demo(drawing)
    #drawing.pop()

    # Close out the MVG file
    drawing.pop()

    # Display the MVG text, then show the generated image
    print drawing.code()
    drawing.render()

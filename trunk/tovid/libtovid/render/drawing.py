#! /usr/bin/env python
# -=- encoding: latin-1 -=-
# drawing.py

"""A Python interface to the Cairo library.

Run this script standalone for a demonstration:

    $ python libtovid/render/drawing.py

To use this module from your Python interpreter, run:

    $ python
    >>> from libtovid.render.drawing import *
    
This module provides a 2D vector drawing interface in a class called Drawing.
To use it, simply provide a resolution and aspect ratio:

    >>> drawing = Drawing(800, 600, (4, 3))   # width, height, aspect

You can now draw shapes on the drawing, fill and stroke them:

    >>> drawing.circle(500, 300, 150)        # (x, y, radius)
    >>> drawing.fill('blue', 0.8)            # color name with optional alpha
    >>> drawing.stroke('rgb(0, 128, 255)')   # rgb values 0-255

Then add more shapes:

    >>> drawing.rectangle(25, 25, 320, 240)  # x, y, width, height
    >>> drawing.fill('rgb(40%, 80%, 10%)')   # rgb percentages
    >>> drawing.stroke('#FF0080', 0.5)       # rgb hex notation with an alpha

To see what the drawing looks like so far, do:

    >>> display(drawing)                     # display at existing size
    >>> display(drawing, 720, 480)           # display at different size
    >>> display(drawing, fix_aspect=True)    # display in correct aspect ratio

You may then decide to add more to the drawing:

    >>> drawing.set_source('white')
    >>> drawing.text("Dennis", 50, 100)      # text, x, y

And preview again:

    >>> display(drawing)

Once you finish your beautiful painting, save it as a nice high-res PNG!

    >>> save_png(drawing, "my.png", 1600, 1200)
    
Cairo references:

    [1] http://www.cairographics.org
    [2] http://tortall.net/mu/wiki/CairoTutorial

"""

__all__ = [
    'Drawing',
    'render',
    'display',
    'save_png',
    'save_jpg',
    'save_image']

import os
import sys
import time
import commands
from copy import copy
from math import pi, sqrt
import cairo
import Image      # for JPG export
import ImageColor # for getrgb, getcolor
from libtovid import log
from libtovid.utils import to_unicode


def get_surface(width, height, surface_type='image'):
    """Get a cairo surface at the given dimensions.
    """
    if type(width) != int or type(height) != int:
        log.warning("Surface width and height should be integers."\
                    " Converting to int.")
    # TODO: Support other surface types
    if surface_type == 'image':
        return cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                  int(width), int(height))


def function_string(func):
    """Return a formatted string describing the given function object.
    """
    # TODO: Find a way to print more info (local variables?)
    # Backtrace ?!
    return "%s" % func.__name__


# Drawing class notes:
#
# The Drawing class has a number of methods (circle, rectangle, fill, stroke
# and many others) that need to operate on a Cairo surface. But we'd like to
# delay execution of actually drawing on that surface--otherwise, we can't
# easily render a given Drawing to a custom resolution.
#
# Closures save the day here--that is, functions without "free variables".
# Anytime you "paint" on the Drawing, what's actually happening is a new
# function is getting created, whose sole purpose in life is to carry out
# that specific paint operation. These tiny, single-purpose functions are
# then added to a list of commands (self.commands) that will actually be
# executed at rendering-time (i.e., when you do display() or save_png).
#
# This not only lets us render a Drawing to different resolutions, but allows
# the possibility of rendering to different Cairo surfaces.

class Drawing:
    def __init__(self, width=800, height=600, aspect=(4, 3)):
        """Create a blank drawing at the given size.
        
            width, height: Dimensions of the drawable region.
            aspect:        Aspect ratio, as a (width, height) tuple
            
        """
        self.size = (width, height)
        self.aspect = aspect
        # Sequence of drawing commands
        self.commands = []
        # "Dummy" surface/context at the original resolution;
        # should not be drawn on
        self.surface = get_surface(width, height, 'image')
        self.cr = cairo.Context(self.surface)


    ### -----------------------------------------------------------------
    ### Drawing commands
    ### -----------------------------------------------------------------

    def affine(self, rot_x, rot_y, scale_x, scale_y, translate_x, translate_y):
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
        def _affine(cr):
            cr.set_matrix(mtx)
        self.commands.append(_affine)


    def arc(self, x, y, radius, start_deg, end_deg):
        """Draw an arc from (x, y), with the specified radius, starting at
        degree start_deg and ending at end_deg.
        """
        def _arc(cr):
            cr.arc(x, y, radius, start_deg * pi/180., end_deg * pi/180.)
        self.commands.append(_arc)


    def arc_rad(self, x, y, radius, start_rad, end_rad):
        """Draw an arc from (x, y), with the specified radius, starting at
        radian start_rad and ending at end_rad.
        """
        def _arc_rad(cr):
            cr.arc(x, y, radius, start_rad, end_rad)
        self.commands.append(_arc_rad)


    # TODO: Rewrite/cleanup bezier function
    def bezier(self, points, rel=False, close_path=False):
        """Create a Bézier curve.

            points should look like:
            
            points = [[(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0)],
                      ]
             
        where (x0, y0) are the point coordinates, and x_ctl* are the control
        points coordinates.

            *ctl1 - control from last point
            *ctl2 - control to next point

        The last line would specify that control points
        are at the same place (x0, y0), drawing straight lines.

            rel -- when this is True, the x_ctl and y_ctl become relatives
                   to the (x0, y0) points
            close_path -- set this to True to call cr.close_path() before
                          stroking.

        """
        assert len(points) > 1, "You need at least two points"
        for pt in points:
            # If only one point is specified, copy it for control points
            if len(pt) == 1:
                pt.append(pt[0])       # add the two identical
                pt.append(pt[0])       # control points
            assert len(pt) == 3, "You need to specify three tuples for each point, or one single"
            for y in pt:
                assert isinstance(y, tuple) and len(y) == 2, "You need "\
                       "to specify two-values tuples"
        # Map relative stuff to absolute, when rel=True
        if rel:
            for x in range(0,len(points)):
                pt = points[x]
                assert len(pt) == 3, "In relative mode, you must "\
                       "specify control points"
                # Render relative values to absolute values.
                npt = []
                #             #  x      #  y
                npt.append([pt[0][0], pt[0][1]]) # x0, y0
                npt.append([pt[0][0] + pt[1][0], pt[0][1] + pt[1][1]])
                npt.append([pt[0][0] + pt[2][0], pt[0][1] + pt[2][1]])
                points[x] = npt
                    
        # Define the actual drawing function
        def _bezier(cr):
            # Move to the first x,y in the first point
            cr.new_path()
            cr.move_to(points[0][0][0], points[0][0][1])
            for pt in points:
                cr.curve_to(pt[2][0], pt[2][1],
                            pt[0][0], pt[0][1],
                            pt[1][0], pt[1][1])
            if close_path:
                cr.close_path()
        self.commands.append(_bezier)


    def circle(self, center_x, center_y, radius):
        """Draw a circle defined by center point and radius."""
        def _circle(cr):
            cr.new_path()
            cr.arc(center_x, center_y, radius, 0, 2*pi)
        self.commands.append(_circle)

    # TODO: add clip stuff...


    def fill(self, source=None, opacity=None):
        """Fill the current (closed) path with an optionally given color.

        If arguments are present, they are passed to set_source()
        before filling.
        """

        # Optionally set fill color, and save it.
        if source is not None:
            print "SOURCE in FILL: %s" % source
            self.set_source(source, opacity)

        def _fill(cr):
            cr.fill_preserve()
        self.commands.append(_fill)


    def fill_rule(self, rule):
        """Set the fill rule to one of:
        
            evenodd, winding (nonzero)

        This determines which parts of an overlapping path polygon will
        be filled with the fill() command.
            
        http://www.w3.org/TR/SVG/painting.html#FillRuleProperty
        """
        tr = {'evenodd': cairo.FILL_RULE_EVEN_ODD,
              'winding': cairo.FILL_RULE_WINDING}

        # Test value
        tr[rule]
        
        def _fill_rule(cr):
            cr.set_fill_rule(tr[rule])
        self.commands.append(_fill_rule)


    def font(self, name, slant='normal', weight='normal'):
        """Set the current font, by name.

        name -- name of the Font, or family (sans-serif, serif)
        slant -- one of: italic, normal, oblique
        weight -- one of: normal, bold
        """
        sl = {'italic': cairo.FONT_SLANT_ITALIC,
              'normal': cairo.FONT_SLANT_NORMAL,
              'oblique': cairo.FONT_SLANT_OBLIQUE}
        wg = {'normal': cairo.FONT_WEIGHT_NORMAL,
              'bold': cairo.FONT_WEIGHT_BOLD}
        def _font(cr):
            cr.select_font_face(name, sl[slant], wg[weight])
        self.commands.append(_font)


    def font_size(self, pointsize):
        """Set the current font size in points."""
        def _font_size(cr):
            cr.set_font_size(pointsize)
        self.commands.append(_font_size)


    def font_stretch(self, x=1.0, y=1.0):
        """Set the font stretch type in both directions to one of:

        = 1.0 -- normal
        > 1.0 -- strench
        < 1.0 -- shrink

        """
        def _font_stretch(cr):
            m = cr.get_font_matrix()
            m.scale(x, y)
            cr.set_font_matrix(m)
        self.commands.append(_font_stretch)


    def font_rotate(self, degrees):
        """Set the font rotation, in degrees.
        """
        def _font_rotate(cr):
            m = cr.get_font_matrix()
            m.rotate(degrees * pi/180.)
            cr.set_font_matrix(m)
        self.commands.append(_font_rotate)

    def image_surface(self, x, y, width, height, surface):
        """Draw a given cairo.ImageSurface centered at (x, y), at the given
        width and height.
        """
        # Calculate centering and scaling
        add_x, add_y = (0, 0)
        dw = float(width) / float(surface.get_width())
        dh = float(height) / float(surface.get_height())
        if (dw > dh):
            scale = dh
            add_x = (width - dh * float(surface.get_width())) / 2
        else:
            scale = dw
            add_y = (height - dw * float(surface.get_height())) / 2
        
        # Save context and get the surface to right dimensions
        self.save()
        self.translate(x + add_x, y + add_y)
        self.scale(scale, scale)

        # Create and append the drawing function
        def _image_surface(cr):
            cr.set_source_surface(surface)
            cr.paint()
        self.commands.append(_image_surface)

        self.restore()
    

    def image(self, x, y, width, height, source):
        """Draw an image centered at (x, y), scaled to the given width and
        height. Return the corresponding cairo.ImageSurface object.

        source -- a .png filename (quicker and alpha present),
                  a cairo.ImageSurface object, which is even better,
                  a file object
                  a filename - any file supported by python-imaging,
                               a.k.a PIL [1]

        Ref:
          [1] http://www.pythonware.com/library/pil/handbook/formats.htm

        You can apply some operator() to manipulation how the image is going
        to show up. See operator()
        """
        # Determine what type of source was given, and make it into
        # a cairo.ImageSurface
        if isinstance(source, cairo.ImageSurface):
            surface = source
        # PNG files can be added directly
        elif isinstance(source, str) and source.endswith('.png'):
            surface = cairo.ImageSurface.create_from_png(source)
        # Other formats must be converted to PNG
        else:
            infile = Image.open(source)
            outfile = open('/tmp/export.png', 'wb+')
            infile.save(outfile, 'PNG')
            outfile.seek(0)
            surface = cairo.ImageSurface.create_from_png(outfile)
            outfile.close()
        # Let someone else do the dirty work
        self.image_surface(x, y, width, height, surface)


    def line(self, x0, y0, x1, y1):
        """Set new path as a line from (x0, y0) to (x1, y1).

        Don't forget to stroke()
        """
        def _line(cr):
            cr.new_path()
            cr.move_to(x0, y0)
            cr.line_to(x1, y1)
        self.commands.append(_line)



    def operator(self, operator='clear'):
        """Set the operator mode.

        operator -- One of: clear
                            source, over, in, out, atop
                            dest, dest_over, dest_in, dest_out, dest_atop
                            xor, add, saturate

        """
        ops = {'clear': cairo.OPERATOR_CLEAR,
               'source': cairo.OPERATOR_SOURCE,
               'over': cairo.OPERATOR_OVER,
               'in': cairo.OPERATOR_IN,
               'out': cairo.OPERATOR_OUT,
               'atop': cairo.OPERATOR_ATOP,
               'dest': cairo.OPERATOR_DEST,
               'dest_over': cairo.OPERATOR_DEST_OVER,
               'dest_in': cairo.OPERATOR_DEST_IN,
               'dest_out': cairo.OPERATOR_DEST_OUT,
               'dest_atop': cairo.OPERATOR_DEST_ATOP,
               'xor': cairo.OPERATOR_XOR,
               'add': cairo.OPERATOR_ADD,
               'saturate': cairo.OPERATOR_SATURATE,
               }

        # Test bad value
        ops[operator]

        def _operator(cr):
            cr.set_operator(ops[operator])
        self.commands.append(_operator)


    def paint(self):
        """Paint the current source everywhere within the current clip
        region."""
        def _paint(cr):
            cr.paint()
        self.commands.append(_paint)


    def paint_with_alpha(self, alpha):
        """Paints the current source everywhere within the current clip
        region using a mask of constant alpha value alpha.

        The effect is similar to paint(), but the drawing is faded out
        using the alpha value."""
        def _paint_with_alpha(cr):
            cr.paint_with_alpha(alpha)
        self.commands.append(_paint_with_alpha)

    def polygon(self, points, close_path=True):
        """Define a polygonal path defined by (x, y) points in the given
        list.

            points = [(x0, y0),
                       (x1, y1),
                       (x2, y2)]

        Draw strokes and filling yourself, with fill() and stroke().
        """
        nlist = []
        for tup in points:
            nlist.append([tup])
        self.bezier(nlist, False, close_path)

    
    def polyline(self, points, close_path=True):
        """Draw a polygon defined by (x, y) points in the given list.

        This is a short- (or long-) hand for polygon. In Cairo, you draw
        your filling (fill()), or strokes (stroke()) yourself, so
        having polyline and polygon is basiclly useless.
        """
        self.polygon(points, close_path)

    
    def rectangle_corners(self, x0, y0, x1, y1):
        """Draw a rectangle defined by opposite corners (x0, y0) and (x1, y1).
        """
        def _rectangle_corners(cr):
            cr.new_path()
            cr.rectangle(x0, y0, x1-x0, y1-y0)
        self.commands.append(_rectangle_corners)


    def rectangle(self, x, y, width, height):
        """Draw a rectangle with top-left corner at (x, y), and (width x height)
        in size.
        """
        def _rectangle(cr):
            cr.new_path()
            cr.rectangle(x, y, width, height)
        self.commands.append(_rectangle)


    def rotate_deg(self, degrees):
        """Rotate by the given number of degrees."""
        def _rotate_deg(cr):
            m = cr.get_matrix()
            m.rotate(degrees * pi/180.)
            cr.set_matrix(m)
        self.commands.append(_rotate_deg)

    rotate = rotate_deg


    def rotate_rad(self, rad):
        """Rotate by the given number of radians."""
        def _rotate_rad(cr):
            m = cr.get_matrix()
            m.rotate(rad)
            cr.set_matrix(m)
        self.commands.append(_rotate_rad)


    def roundrectangle(self, x0, y0, x1, y1, bevel_width, bevel_height):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        a bevel size of (bevel_width, bevel_height)."""
        bw = bevel_width
        bh = bevel_height
        # Add bezier points
        # Top left corner:
        tl1 = [(x0, y0 + bh), (0,0), (0,0)]
        tl2 = [(x0 + bw, y0), (0,0), (-bw,0)]
        tr1 = [(x1 - bw, y0), (0,0), (-bw,0)]
        tr2 = [(x1, y0 + bh), (0,0), (0,-bw)]
        br1 = [(x1, y1 - bh), (0,0), (0,-bh)]
        br2 = [(x1 - bw, y1), (0,0), (+bw,0)]
        bl1 = [(x0 + bw, y1), (0,0), (+bw,0)]
        bl2 = [(x0, y1 - bh), (0,0), (0,+bh)]
        end = [(x0, y0 + bh), (0,0), (0,0)]
        # Call in relative mode bezier control points.
        mylst = [tl1, tl2, tr1, tr2, br1, br2, bl1, bl2, end]
        # Let bezier do the work
        self.bezier(mylst, True)


    def set_source(self, source, opacity=None):
        """
        source -- One of the following color formats as a string or a tuple
                  (see below), another Surface or Surface-derivative object,
                  or a Pattern object (and its derivatives).
        opacity -- Opacity ranging from 0.0 to 1.0. Defaults to None. If
                   you specify a 'string' or 'tuple' RGB-like code as
                   source, opacity defaults to 1.0

        You can use the following *tuple* format to specify color:
        * (red, green, blue) -- with colors ranging from 0.0 to 1.0, like
                                Cairo wants them.

        You can use the following *string* formats to specify color:
        
        * Hexadecimal color specifiers, given as '#rgb' or '#rrggbb'.
          For example, '#ff0000' specifies pure red.
        * RGB functions, given as 'rgb(red, green, blue)' where the colour
          values are integers in the range 0 to 255. Alternatively, the color
          values can be given as three percentages (0% to 100%). For example,
          'rgb(255,0,0)' and 'rgb(100%,0%,0%)' both specify pure red.
        * Hue-Saturation-Lightness (HSL) functions, given as:
          'hsl(hue, saturation%, lightness%)' where hue is the colour given as
          an angle between 0 and 360 (red=0, green=120, blue=240), saturation
          is a value between 0% and 100% (gray=0%, full color=100%), and
          lightness is a value between 0% and 100% (black=0%, normal=50%,
          white=100%). For example, 'hsl(0,100%,50%)' is pure red.
        * Common HTML colour names. The ImageColor module provides some 140
          standard colour names, based on the colors supported by the X
          Window system and most web browsers. Colour names are case
          insensitive. For example, 'red' and 'Red' both specify pure red.
         
        """
        mysource = self.create_source(source, opacity)
        def _set_source(cr):
            print "INSIDE set_source function: %s" % mysource
            cr.set_source(mysource)
        self.commands.append(_set_source)


    def create_source(self, source, opacity=None):
        """Return a source pattern (solid, gradient, image surface)
        with anything fed into it.

        See the set_source() documentation for more details on inputs.

        You can feed anything returned by this function into set_source()
        """
        if isinstance(source, cairo.Pattern):
            return source
        # A string--color name, rgb(), hsv(), or hexadecimal
        elif isinstance(source, str):
            (r, g, b) = ImageColor.getrgb(source)
            alpha = 1.0
            if opacity is not None:
                alpha = opacity
            return cairo.SolidPattern(r / 255.0, g / 255.0,
                                      b / 255.0, alpha)
        # An (r, g, b) tuple
        elif isinstance(source, tuple):
            assert len(source) == 3
            (r, g, b) = source
            alpha = 1.0
            if opacity is not None:
                alpha = opacity
            return cairo.SolidPattern(r, g, b, alpha)
        # A cairo Gradient
        elif isinstance(source, cairo.Gradient):
            return source
        # A cairo Surface
        elif isinstance(source, cairo.Surface):
            return cairo.SurfacePattern(source)
        else:
            raise TypeError, "source must be one of: str, tuple, "\
                  "cairo.Pattern, cairo.Gradient or cairo.Surface"


    def get_source(self):
        """Return the actually used source pattern

        This returns either of these:

            cairo.SolidPattern (RGB or RGBA color)
            cairo.SurfacePattern (some other image)
            cairo.LinearGradient (linear gradient :)
            cairo.RadialGradient (radial gradient :)

        You can then use this source in set_source(), to use the same
        pattern for fill()ing or stroke()ing.
        """
        # TODO: Fix or remove this function
        return self.cr.get_source()


    def scale(self, factor_x, factor_y):
        """Set scaling to (factor_x, factor_y), where 1.0 means no scaling.

        Note that the center point for scaling is (0,0); to scale from a
        different center point, use scale_centered()
        """
        def _scale(cr):
            m = cr.get_matrix()
            m.scale(factor_x, factor_y)
            cr.set_matrix(m)
        self.commands.append(_scale)


    def scale_centered(self, center_x, center_y, factor_x, factor_y):
        """Set scaling to (dx, dy), where dx and dy are horizontal and
        vertical ratios (floats).

        scale_centered() will keep the (center_x, center_y) in the middle
        of the scaling, operating a translation in addition to scaling.
        """
        def _scale_centered(cr):
            m = cr.get_matrix()
            # Ouch, we want to keep the center x,y at the same place?!
            m.translate(-(center_x * factor_x - center_x),
                        -(center_y * factor_y - center_y))
            m.scale(factor_x, factor_y)
            cr.set_matrix(m)
        self.commands.append(_scale_centered)


    def stroke(self, source=None, opacity=None):
        """Stroke the current shape.

        See fill() documentation for parameter explanation. They are the
        same.
        """

        def _stroke(cr):
            # Optionally set fill color, and save it.
            if source is not None:
                print "SET SOURCE inside stroke: %s" % source
                self.set_source(source, opacity)
            cr.stroke_preserve()
        self.commands.append(_stroke)


    def stroke_antialias(self, do_antialias=True):
        """Enable/disable antialiasing for strokes.

            do_antialias: True, False, 'none', 'default', or 'gray'
        
        This does not affect text. See text_antialias() for more info
        on text antialiasing.
        """
        if do_antialias:
            aa_type = cairo.ANTIALIAS_GRAY
        else:
            aa_type = cairo.ANTIALIAS_NONE
            
        def _stroke_antialias(cr):
            cr.set_antialias(aa_type)
        self.commands.append(_stroke_antialias)


    def stroke_dash(self, array, offset=0.0):
        """Set the dash style.

            array:  A list of floats, alternating between ON and OFF for
                    each value
            offset: An offset into the dash pattern at which the stroke
                    should start
        
        For example:
        
            >>> stroke_dash([5.0, 3.0])

        alternates between 5 pixels on, and 3 pixels off.
        """
        def _stroke_dash(cr):
            cr.set_dash(array, offset)
        self.commands.append(_stroke_dash)


    def stroke_linecap(self, cap_type):
        """Set the type of line cap to use for stroking.

            cap_type:  One of 'butt', 'round', or 'square'
        """
        dic = {'butt': cairo.LINE_CAP_BUTT,
               'round': cairo.LINE_CAP_ROUND,
               'square': cairo.LINE_CAP_SQUARE}

        # Test value
        dic[cap_type]
        
        def _stroke_linecap(cr):
            cr.set_line_cap(dic[cap_type])
        self.commands.append(_stroke_linecap)


    def stroke_linejoin(self, join_type):
        """Set the type of line-joining to do for stroking.

            join_type:  One of 'bevel', 'miter', or 'round'.
        """
        dic = {'bevel': cairo.LINE_JOIN_BEVEL,
               'miter': cairo.LINE_JOIN_MITER,
               'round': cairo.LINE_JOIN_ROUND}

        # Test value
        dic[join_type]
        
        def _stroke_linejoin(cr):
            cr.set_line_join(dic[join_type])
        self.commands.append(_stroke_linejoin)


    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        def _stroke_width(cr):
            cr.set_line_width(width)
        self.commands.append(_stroke_width)


    def text(self, text_string, x, y, align='left'):
        """Draw the given text string.

            text_string: utf8 encoded text string
            (x, y):      lower-left corner position
        
        Set the text's color with set_source() before calling text().
        """
        text_string = to_unicode(text_string)

        #self.save()
        def _text(cr):
            (dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
            if align == 'right':
                nx = x - w
            elif align == 'center':
                nx = x - w / 2
            else:
                nx = x
            # TODO: Fix, the center thing is *not really* centered..
            # maybe all those scalings, rescalings and scalings again mess
            # things up.
            cr.move_to(nx, y)
            cr.show_text(text_string)
        self.commands.append(_text)
        #self.restore()


    def text_path(self, text_string, x, y):
        """Same as text(), but sets a path and doesn't draw anything.
        Call stroke() or fill() yourself.

        Has the parameters and returns the same values as text().

        Beware that text() calls the Cairo function show_text() which
        caches glyphs, so is more efficient when dealing with large
        texts.
        """
        if not isinstance(text_string, unicode):
            text_string = unicode(text_string.decode('latin-1'))
        def _text_path(cr):
            cr.move_to(x, y)
            cr.text_path(text_string)
        self.commands.append(_text_path)


    def text_extents(self, text):
        """Returns the dimensions of the to-be-drawn text.

        Call this before calling text() if you want to place it well,
        according to the dimensions of the text rectangle to be drawn.

        See text()'s return value for details.

        Returns:
            (x_bearing, y_bearing, width, height, x_advance, y_advance)
        """
        # TODO: Fix this
        text = to_unicode(text)
        return self.cr.text_extents(text)


    def translate(self, dx, dy):
        """Do a translation by (dx, dy) pixels."""
        def _translate(cr):
            m = cr.get_matrix()
            m.translate(dx, dy)
            cr.set_matrix(m)
        self.commands.append(_translate)


    def push_group(self):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.

        The redirection lasts until the group is completed by a call
        to pop_group() or pop_group_to_source(). These calls provide
        the result of any drawing to the group as a pattern, (either
        as an explicit object, or set as the source pattern).
        """
        def _push_group(cr):
            cr.push_group()
        self.commands.append(_push_group)


    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to push_group() and
        installs the resulting pattern as the source pattern in the current
        cairo context.
        """
        def _pop_group_to_source(cr):
            cr.pop_group_to_source()
        self.commands.append(_pop_group_to_source)


    def save(self):
        """Save state for Cairo and local contexts.

        You can save in a nested manner, and calls to restore() will pop
        the latest saved context.
        """
        def _save(cr):
            cr.save()
        self.commands.append(_save)


    def restore(self):
        """Restore the previously saved context."""
        def _restore(cr):
            cr.restore()
        self.commands.append(_restore)


    ### ----------------------------------------------------------------
    ### Unfinished methods
    ### ----------------------------------------------------------------
    
    
    #def font_style(self, style):
    #    """Set the font style to one of:
    #    all, normal, italic, oblique
    #
    #    Alias to font_slant()
    #    """
    #    self.font_slant(style)


    #def font_slant(self, style):
    #    """Set the font slant. Use one of:
    #
    #       normal, italic, oblique
    #    """
    #    tr = {'italic': cairo.FONT_SLANT_ITALIC,
    #          'normal': cairo.FONT_SLANT_NORMAL,
    #          'oblique': cairo.FONT_SLANT_OBLIQUE}
    #    self.cr.set_slant(tr[style])
   

    #def font_weight(self, weight):
    #    """Set the font weight to one of:
    #    
    #        normal, bold
    #    """
    #    tr = {'normal': cairo.FONT_WEIGHT_NORMAL,
    #          'bold': cairo.FONT_WEIGHT_BOLD}
    #    self.cr.set_font_weight(tr[weight])


    #def font_family(self, family):
    #    """Set the current font, by family name."""
    #    self.cr.select_font_face(family)


    #def gradient_units(self, units):
    #    """Set gradient units to one of:
    #    userSpace, userSpaceOnUse, objectBoundingBox
    #    """
    #    self.insert('gradient-units %s' % units)


    #def gravity(self, direction):
    #    """Set the gravity direction to one of:
    #    
    #        NorthWest, North, NorthEast,
    #        West, Center, East,
    #        SouthWest, South, SouthEast
    #        
    #    Note: gravity is known to affect text and images; it does not affect
    #    points, lines, circles, rectangles, roundrectangles, polylines or
    #    polygons.
    #    """
    #    self.insert('gravity %s' % direction)


    #def matte(self, (x, y), method='floodfill'):
    #    # method may be: point, replace, floodfill, filltoborder, reset
    #    # (What do x, y mean?)
    #    self.insert('matte %s,%s %s' % (x, y, method))


    #def offset(self, offset):
    #    self.insert('offset %s' % offset)


    #def path(self, path_data):
    #    """Draw a path. path_data is a list of instructions and coordinates,
    #    e.g. ['M', (100,100), 'L', (200,200), ...]
    #    Instructions are M (moveto), L (lineto), A (arc), Z (close path)
    #    For more on using paths (and a complete list of commands), see:
    #    http://www.cit.gu.edu.au/~anthony/graphics/imagick6/draw/#paths
    #    http://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
    #    """
    #    command = 'path'
    #    for token in path_data:
    #        if isinstance(token, tuple):
    #            command += ' %s,%s' % token
    #        else:
    #            command += ' %s' % token
    #    self.insert(command)


    #def text_align(self, text_string, x, y, align='left'):
        #"""Draw the given text string.

            #text_string: utf8 encoded text string
            #(x, y):      lower-left corner position
            #align:       'left', 'center', 'right'. This only changes the
                         #alignment in 'x', and 'y' stays the baseline.

        #Set the text's color with set_source() before calling text().
        #"""
        ## TODO: Somehow determine extents of text without needing self.cr
        #(dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        #w = 0
        #if align == 'right':
            #x = x - w
        #elif align == 'center':
            #x = x - w / 2
        #else: # 'left'
            #x = x
        ## Let text() do the drawing
        #self.text(text_string, x, y)


    #def text_path_align(self, x, y, text_string, centered=False):
        #"""Same as text_align(), but sets a path and doesn't draw anything.
        #Call stroke() or fill() yourself.
        #"""
        ## TODO: Somehow determine extents of text without needing self.cr
        
        #(dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        #if centered:
            #x = x - w / 2
            #y = y + h / 2
        #self.text_path(text_string, x, y)


    #def point(self, (x, y), size):
    #    """Draw a point at position (x, y)"""
    #    self.insert('point %s,%s' % (x, y))



### --------------------------------------------------------------------
### Exported functions
### --------------------------------------------------------------------

def render(drawing, width=None, height=None):
    """Render a Drawing at the given size to a new surface, and
    return the surface and context.
    """

    # Take original size if not specified
    if not width:
        width = drawing.size[0]
    if not height:
        height = drawing.size[1]
        
    # Create a new surface/context at the given size
    surface = get_surface(width, height, 'image')
    cr = cairo.Context(surface)
    log.debug("render()--surface, cr: %s, %s" % (surface, cr))
    
    # Scale from the original size
    scale_x = float(width) / drawing.size[0]
    scale_y = float(height) / drawing.size[1]
    drawing.scale(scale_x, scale_y)
    # Sneaky bit--scaling needs to happen before everything else
    drawing.commands.insert(0, drawing.commands.pop(-1))
    
    # Execute all draw commands
    for command in drawing.commands:
        log.debug("Draw function: %s" % function_string(command))
        command(cr)

    # Remove scaling function
    drawing.commands.pop(0)
    
    return surface, cr


def display(drawing, width=None, height=None, fix_aspect=False):
    """Render and display the given Drawing at the given size.
    
        drawing:    A Drawing object to display
        width:      Pixel width of displayed image,
                    or 0 to use the given Drawing's size
        height:     Pixel height of displayed image,
                    or 0 to use the given Drawing's size
        fix_aspect: True to adjust height to make the image
                    appear in the correct aspect ratio
    """
    if not width:
        width = drawing.size[0]
    if not height:
        height = drawing.size[1]
        
    # Adjust height to fix aspect ratio if desired
    if fix_aspect:
        x, y = drawing.aspect
        height = width * y / x
    # Render and display a .png
    png_file = '/tmp/drawing.png'
    save_png(drawing, png_file, width, height)
    print "Displaying", png_file, "at %sx%s" % (width, height)
    print "(press 'q' in image window to continue)"
    print commands.getoutput('display %s' % png_file)


def save_png(drawing, filename, width=None, height=None):
    """Saves a drawing to PNG, keeping alpha channel intact.

    This is the quickest, since Cairo itself exports directly to .png"""
    surface, cr = render(drawing, width, height)
    print "Saving", filename
    surface.write_to_png(filename)
    del cr
    del surface
    

def save_jpg(drawing, filename, width=None, height=None):
    """Saves a drawing to JPG, losing alpha channel information.
    """
    f = open('/tmp/export.png', 'wb+')
    save_png(drawing, f, width, height)
    f.seek(0)
    im = Image.open(f)
    im.save(filename)
    del(im)
    f.close()


def save_image(drawing, img_filename, width=None, height=None):
    """Render drawing to a .jpg, .png or other image."""
    log.info("Saving Drawing to %s" % img_filename)
    if img_filename.endswith('.png'):
        save_png(drawing, img_filename, width, height)
    elif img_filename.endswith('.jpg'):
        save_jpg(drawing, img_filename, width, height)
    else:
        log.debug("Creating temporary .png")
        temp_png = '/tmp/%s.png' % img_filename
        save_png(drawing, temp_png, width, height)
        log.debug("Converting temporary png to %s" % img_filename)
        cmd = "convert -size %sx%s " % drawing.size
        cmd += "%s %s" % (temp_png, img_filename)
        print commands.getoutput(cmd)


def display_xlib(drawing, width=0, height=0):
    """Display the given Drawing using Xlib.
    
        drawing:    A Drawing object to display
        width:      Pixel width of displayed image,
                    or 0 to use the given Drawing's size
        height:     Pixel height of displayed image,
                    or 0 to use the given Drawing's size
    """
    pass


### --------------------------------------------------------------------
### Demo functions
### --------------------------------------------------------------------

def draw_fontsize_demo(drawing):
    """Draw font size samples on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    drawing.scale(1.0/720, 1.0/480)
    
    # Draw white text in a range of sizes
    drawing.set_source('white')
    
    for size in [12,16,20,24,28,32]:
        ypos = size * size / 5
        drawing.font('Helvetica')
        drawing.font_size(size)
        drawing.text(u"%s pt: The quick brown fox" % size, 0, ypos)
    
    # Restore context
    drawing.restore()


def draw_font_demo(drawing):
    """Draw samples of different fonts on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    drawing.scale(1.0/720, 1.0/480)

    fontsize = 48
    drawing.font_size(fontsize)
    fonts = [u'Helvetica', u'NimbusSans', u'Tahoma', u'Times']
    ypos = 0
    for font in fonts:
        drawing.font(font)
        # Transparent shadow
        drawing.set_source('darkblue', 0.4)
        drawing.text(font, 3, ypos+3)
        # White text
        drawing.set_source('white', 1.0)
        drawing.text(font, 0, ypos)
        ypos += fontsize

    # Restore context
    drawing.restore()


def draw_shape_demo(drawing):
    """Draw shape samples on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    drawing.scale(1.0/720, 1.0/480)

    # Large orange circle with black stroke
    drawing.save()
    drawing.stroke_width(12)
    # Circle at (500, 200), with radius 200
    drawing.circle(500, 200, 200)
    drawing.stroke('black')
    drawing.fill('orange')
    drawing.restore()

    # Grey-stroked blue circles
    drawing.save()
    # TODO:
    # All circles have the same stroke width and color (and, in other cases,
    # might all have the same fill style as well). A simpler interface is
    # called for, e.g.:
    # drawing.set_style(fill='#8080FF', stroke='#777', stroke_width=2)
    # drawing.circle((65, 50), 15)
    # drawing.circle((65, 100), 10)
    # drawing.circle((65, 150), 5)
    # drawing.set_style(fill='black') # stroke stays the same as before
    # drawing.rectangle((40, 30), (50, 150))
    
    drawing.stroke_width(2)
    drawing.circle(65, 50, 15)
    drawing.fill('#8080FF')
    drawing.stroke('#777')
    
    drawing.circle(60, 100, 10)
    drawing.fill('#2020F0')
    drawing.stroke('#777')
    
    drawing.circle(55, 150, 5)
    drawing.fill('#0000A0')
    drawing.stroke('#777')
    drawing.restore()

    # Semitransparent green rectangles
    drawing.save()
    drawing.translate(50, 400)
    for scale in [0.2, 0.4, 0.7, 1.1, 1.6, 2.2, 2.9, 3.7]:
        drawing.save()
        drawing.translate(scale * 70, scale * -50)
        drawing.scale(scale, scale)
        drawing.stroke_width(scale)
        # roundrectangle broken?
        drawing.roundrectangle(-30, -30, 30, 30, 8, 8)
        #drawing.rectangle(-30, -30, 30, 30)
        drawing.fill('lightgreen', scale / 5.0)
        drawing.stroke('black')
        drawing.restore()
    drawing.restore()

    # Restore context
    drawing.restore()


def draw_stroke_demo(drawing):
    """Draw a stroke/strokewidth demo on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    drawing.scale(1.0/720, 1.0/480)
    
    for width in [1, 2, 4, 6, 8, 10, 12, 14, 16]:
        drawing.stroke_width(width)
        rgb = ((255 - width * 8), (120 - width * 5), 0)
        offset = width * 10
        drawing.line(0, offset, -offset, offset)
        drawing.stroke('rgb(%s,%s,%s)' % rgb)

    # Restore context
    drawing.restore()

import logging
log.setLevel(logging.INFO)

if __name__ == '__main__':
    mytime = time.time() # Benchmark

    drawing = Drawing(1, 1, (4, 3))

    # Start a new
    drawing.save()
    #drawing.viewbox((0, 0), (720, 480))

    # Add a background fill
    #->Background
    drawing.set_source('darkgray')
    drawing.rectangle(0, 0, 1.0, 1.0)
    drawing.fill()

    # Shape demo
    drawing.save()
    draw_shape_demo(drawing)
    drawing.restore()

    # Font size demo
    drawing.save()
    drawing.translate(0.03, 0.04)
    draw_fontsize_demo(drawing)
    drawing.restore()

    # Font face demo
    drawing.save()
    drawing.translate(0.03, 0.6)
    draw_font_demo(drawing)
    drawing.restore()

    # Stroke demo
    drawing.save()
    drawing.translate(0.8, 0.4)
    draw_stroke_demo(drawing)
    drawing.restore()

    # Close out the Cairo rendering...
    drawing.restore()

    print "Took %f seconds" % (time.time() - mytime)

    # Render and display the Drawing at several different sizes
    resolutions = [(352, 240), (352, 480), (720, 480)]
    #resolutions = [(720, 480)]
    for w, h in resolutions:
        display(drawing, w, h)
   


#! /usr/bin/env python
# -=- encoding: latin-1 -=-
# drawing.py
#
# Cairo backend, by Alexandre Bourget <wackysalut@bourget.cc>
#

# TODO: Rewrite docstring
"""A Python interface to the Cairo library.

Run this script standalone for a demonstration:

    $ python libtovid/render/cairo.py

Please note the leading '_' after 'cairo'. This is to prevent conflicts with
the 'official' cairo binding class.

To start off with Cairo, read (a must!):

    http://tortall.net/mu/wiki/CairoTutorial

To build your own Cairo vector image using this module, fire up your Python
interpreter:

    $ python

And do something like this:

    >>> from libtovid.render.drawing import Drawing
    >>> drawing = Drawing((800, 600))

This creates an image (drawing) at 800x600 display resolution. Drawing has a
wealth of draw functions.

Follow the Cairo-way of drawing:

    - Draw a shape, create a path, with several functions (text_path,
      circle_rad, circle, rectangle, etc...)
    - fill([color], [alpha]) or stroke([color], [alpha]) as wanted

You can optionally set the 'Auto-stroke' and 'Auto-fill' behavior, which
will use the latest fill() and stroke() colors set. You can set these
colors with calls to set_fill_color() and set_stroke_color() too.

Main difference with the MVG backend. Example MVG usage:

    >>> drawing.fill('blue')
    >>> drawing.rectangle((0, 0), (800, 600))
    >>> drawing.fill('white')
    >>> drawing.rectangle((320, 240), (200, 100))

Example Cairo usage:

    >>> drawing.set_source('rgb(255,255,80)')
    >>> drawing.rectangle((0, 0), (800, 600))
    >>> drawing.fill()
    >>> drawing.set_source(1, 1, 0.5)
    >>> drawing.rectangle((320, 240), (200, 100))
    >>> drawing.stroke('white')

Notice how you set the colors first in Cairo, and that you call the fill() and
stroke() methods afterwards. This is because Cairo creates paths, and then you
can choose to fill() them or not, and to stroke() the outline or not.

Note also that MVG confuses fill() with stroke(). When calling mvg's fill(),
you will in fact stroke the outline. [insert here how does MVG handle filling]

References:

    [1] http://www.cairographics.org
    [2] http://tortall.net/mu/wiki/CairoTutorial

"""

"""Interface ideas:

Strip drawing interface to the minimal set of features needed by tovid apps.
e.g.:

Text rendering (font, size, fill, placement)
Image rendering (size, mask, placement)
Basic shape rendering (lines, rectangles, circles, polygons)
Translation (scaling, rotation)

Thin glue between Drawing and Layer.

Use a dictionary for specifying gradient color stops (instead of repeated
calls to add_color_stop_rgba)

grad1 = {0: 'red', 1: 'blue'}
grad2 = {0.0: 'transparent',
         0.5: '#00FF0080',
         1.0: 'green'}

drawing.gradient('linear', grad1)
drawing.gradient('radial', grad2)

(plus additional coordinate information as needed)


"""

__all__ = ['Drawing']

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

class Drawing:
    def __init__(self, width=800, height=600, aspect=(4, 3)):
        """Create a blank drawing at the given size.
        
            width, height: Dimensions of the drawable region.

        The given size should have the intended display aspect ratio, assuming
        "square pixels". That is, if your Drawing will be displayed at 4:3
        aspect, it should have size (400, 300), (800, 600) or similar.
        """
        self.size = (width, height)
        self.aspect = aspect
        # Sequence of drawing commands
        self.commands = []

        # This'll catch some bugs...
        self.cr = None
        
        # TODO: Move this part to rendering function(s)
        #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        #self.cr = cairo.Context(self.surface)


    ###
    ### Cairo drawing commands
    ###

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
        def _affine():
            mtx = cairo.Matrix(scale_x, rot_x, rot_y, scale_y,
                               translate_x, translate_y)
            self.cr.set_matrix(mtx)
        self.commands.append(_affine)

    def arc(self, x, y, radius, start_deg, end_deg):
        """Draw an arc from (x, y), with the specified radius, starting at
        degree start_deg and ending at end_deg.
        """
        def _arc():
            self.cr.arc(x, y, radius, start_deg * pi/180., end_deg * pi/180.)
        self.commands.append(_arg)


    def arc_rad(self, x, y, radius, start_rad, end_rad):
        """Draw an arc from (x, y), with the specified radius, starting at
        radian start_rad and ending at end_rad.
        """
        def _arc_rad():
            self.cr.arc(x, y, radius, start_rad, end_rad)
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
        def _bezier():
            # Move to the first x,y in the first point
            self.cr.new_path()
            self.cr.move_to(points[0][0][0], points[0][0][1])
            for pt in points:
                self.cr.curve_to(pt[2][0], pt[2][1],
                                 pt[0][0], pt[0][1],
                                 pt[1][0], pt[1][1])
            if close_path:
                self.cr.close_path()
        self.commands.append(_bezier)


    def circle(self, center_x, center_y, radius):
        """Draw a circle defined by center point and radius."""
        def _circle():
            self.cr.new_path()
            self.cr.arc(center_x, center_y, radius, 0, 2*pi)
        self.commands.append(_circle)

    # TODO: add clip stuff...


    def fill(self, source=None, opacity=None):
        """Fill the current (closed) path with an optionally given color.

        If arguments are present, they are passed to set_source()
        before filling.
        """
        # Optionally set fill color, and save it.
        if source is not None:
            self.set_source(source, opacity)

        def _fill():
            self.cr.fill_preserve()
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
        def _fill_rule():
            self.cr.set_fill_rule(tr[rule])
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
        def _font():
            self.cr.select_font_face(name, sl[slant], wg[weight])
        self.commands.append(_font)


    #def font_family(self, family):
    #    """Set the current font, by family name."""
    #    self.cr.select_font_face(family)


    def font_size(self, pointsize):
        """Set the current font size in points."""
        def _font_size():
            self.cr.set_font_size(pointsize)
        self.commands.append(_font_size)


    def font_stretch(self, x=1.0, y=1.0):
        """Set the font stretch type in both directions to one of:

        = 1.0 -- normal
        > 1.0 -- strench
        < 1.0 -- shrink

        """
        def _font_stretch():
            m = self.cr.get_font_matrix()
            m.scale(x, y)
            self.cr.set_font_matrix(m)
        self.commands.append(_font_stretch)


    def font_rotate(self, degrees):
        """Set the font rotation, in degrees.

        Addition to Cairo backend."""
        def _font_rotate():
            m = self.cr.get_font_matrix()
            m.rotate(degrees * pi/180.)
            self.cr.set_font_matrix(m)
        self.commands.append(_font_rotate)
    
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
        def _image_surface():
            self.cr.set_source_surface(surface)
            self.cr.paint()
        self.commands.append(_image_surface())

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
        self.image_surface(x, y, width, height, img)


    def line(self, x0, y0, x1, y1):
        """Set new path as a line from (x0, y0) to (x1, y1).

        Don't forget to stroke()
        """
        def _line():
            self.cr.new_path()
            self.cr.move_to(x0, y0)
            self.cr.line_to(x1, y1)
        self.commands.append(_line)
    
    #def matte(self, (x, y), method='floodfill'):
    #    # method may be: point, replace, floodfill, filltoborder, reset
    #    # (What do x, y mean?)
    #    self.insert('matte %s,%s %s' % (x, y, method))

    #def offset(self, offset):
    #    self.insert('offset %s' % offset)


    def operator(self, operator='clear'):
        """Set the operator mode.

        operator -- One of: clear
                            source, over, in, out, atop
                            dest, dest_over, dest_in, dest_out, dest_atop
                            xor, add, saturate

        """
        def _operator():
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
            self.cr.set_operator(ops[operator])
        self.commands.append(_operator)

    def paint(self):
        """Paint the current source everywhere within the current clip
        region."""
        def _paint():
            self.cr.paint()
        self.commands.append(_paint)


    def paint_with_alpha(self, alpha):
        """Paints the current source everywhere within the current clip
        region using a mask of constant alpha value alpha.

        The effect is similar to paint(), but the drawing is faded out
        using the alpha value."""
        def _paint_with_alpha():
            self.cr.paint_with_alpha(alpha)
        self.commands.append(_paint_with_alpha)


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

    #def point(self, (x, y), size):
    #    """Draw a point at position (x, y)"""
    #    self.insert('point %s,%s' % (x, y))

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
        def _rectangle_corners():
            self.cr.new_path()
            self.cr.rectangle(x0, y0, x1-x0, y1-y0)
        self.commands.append(_rectangle_)


    def rectangle(self, x, y, width, height):
        """Draw a rectangle with top-left corner at (x, y), and (width x height)
        in size.
        """
        def _rectangle():
            self.cr.new_path()
            self.cr.rectangle(x, y, width, height)
        self.commands.append(_rectangle)


    def rotate_deg(self, degrees):
        """Rotate by the given number of degrees."""
        def _rotate_deg():
            m = self.cr.get_matrix()
            m.rotate(degrees * pi/180.)
            self.cr.set_matrix(m)
        self.commands.append(_rotate_deg)

    # Map rotate() to rotate_deg()
    rotate = rotate_deg


    def rotate_rad(self, rad):
        """Rotate by the given number of radians."""
        def _rotate_rad():
            m = self.cr.get_matrix()
            m.rotate(rad)
            self.cr.set_matrix(m)
        self.commands.append(_rotate_rad)


    def roundrectangle(self, x0, y0, x1, y1, bevel_width, bevel_height):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        a bevel size of (bevel_width, bevel_height)."""
        def _roundrectangle():
            bw = bevel_width
            bh = bevel_height
            # Add bezier points...
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
            self.bezier(mylst, True)
        self.commands.append(_roundrectangle)


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
        def _set_source():
            self.cr.set_source(mysource)
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
        return self.cr.get_source()


    def scale(self, factor_x, factor_y):
        """Set scaling to (factor_x, factor_y), where 1.0 means no scaling.

        Note that the center point for scaling is (0,0); to scale from a
        different center point, use scale_centered()
        """
        def _scale():
            m = self.cr.get_matrix()
            m.scale(factor_x, factor_y)
            self.cr.set_matrix(m)
        self.commands.append(_scale)


    def scale_centered(self, center_x, center_y, factor_x, factor_y):
        """Set scaling to (dx, dy), where dx and dy are horizontal and
        vertical ratios (floats).

        scale_centered() will keep the (center_x, center_y) in the middle
        of the scaling, operating a translation in addition to scaling.
        """
        def _scale_centered():
            m = self.cr.get_matrix()
            # Ouch, we want to keep the center x,y at the same place?!
            m.translate(-(center_x * factor_x - center_x),
                        -(center_y * factor_y - center_y))
            m.scale(factor_x, factor_y)
            self.cr.set_matrix(m)
        self.commands.append(_scale_centered)


    def stroke(self, source=None, opacity=None):
        """Stroke the current shape.

        See fill() documentation for parameter explanation. They are the
        same.
        """
        # Optionally set fill color, and save it.
        if source is not None:
            self.set_source(source, opacity)

        def _stroke():
            self.cr.stroke_preserve()
        self.commands.append(_stroke)


    def stroke_antialias(self, do_antialias=True):
        """Enable/disable antialiasing for strokes.

            do_antialias: True, False, 'none', 'default', or 'gray'
        
        This does not affect text. See text_antialias() for more info
        on text antialiasing.
        """
        def _stroke_antialias():
            if do_antialias:
                self.cr.set_antialias(cairo.ANTIALIAS_GRAY)
            else:
                self.cr.set_antialias(cairo.ANTIALIAS_NONE)
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
        def _stroke_dash():
            self.cr.set_dash(array, offset)
        self.commands.append(_stroke_dash)


    def stroke_linecap(self, cap_type):
        """Set the type of line cap to use for stroking.

            cap_type:  One of 'butt', 'round', or 'square'
        """
        def _stroke_linecap():
            dic = {'butt': cairo.LINE_CAP_BUTT,
                   'round': cairo.LINE_CAP_ROUND,
                   'square': cairo.LINE_CAP_SQUARE}
            self.cr.set_line_cap(dic[cap_type])
        self.commands.append(_stroke_linecap)


    def stroke_linejoin(self, join_type):
        """Set the type of line-joining to do for stroking.

            join_type:  One of 'bevel', 'miter', or 'round'.
        """
        def _stroke_linejoin():
            dic = {'bevel': cairo.LINE_JOIN_BEVEL,
                   'miter': cairo.LINE_JOIN_MITER,
                   'round': cairo.LINE_JOIN_ROUND}
            self.cr.set_line_join(dic[join_type])
        self.commands.append(_stroke_linejoin)


    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        def _stroke_width():
            self.cr.set_line_width(width)
        self.commands.append(_stroke_width)


    def text(self, text_string, x, y):
        """Draw the given text string.

            text_string: utf8 encoded text string
            (x, y):      lower-left corner position
        
        Set the text's color with set_source() before calling text().
        """
        # Convert text to unicode
        if not isinstance(text_string, unicode):
            text_string = unicode(str(text_string).decode('latin-1'))

        self.save()
        def _text():
            self.cr.move_to(x, y)
            self.cr.show_text(text_string)
        self.commands.append(_text)
        self.restore()


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
        def _text_path():
            self.cr.move_to(x, y)
            self.cr.text_path(text_string)
        self.commands.append(_text_path)


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


    def text_extents(self, text_string):
        """Returns the dimensions of the to-be-drawn text.

        Call this before calling text() if you want to place it well,
        according to the dimensions of the text rectangle to be drawn.

        See text()'s return value for details.

        Returns:
            (x_bearing, y_bearing, width, height, x_advance, y_advance)
        """
        if not isinstance(text_string, unicode):
            text_string = unicode(text_string.decode('latin-1'))
        return self.cr.text_extents(text_string)


    def translate(self, dx, dy):
        """Do a translation by (dx, dy) pixels."""
        def _translate():
            m = self.cr.get_matrix()
            m.translate(dx, dy)
            self.cr.set_matrix(m)
        self.commands.append(_translate)


    def push_group(self):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.

        The redirection lasts until the group is completed by a call
        to pop_group() or pop_group_to_source(). These calls provide
        the result of any drawing to the group as a pattern, (either
        as an explicit object, or set as the source pattern).
        """
        def _push_group():
            self.cr.push_group()
        self.commands.append(_push_group)


    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to push_group() and
        installs the resulting pattern as the source pattern in the current
        cairo context.
        """
        def _pop_group_to_source():
            self.cr.pop_group_to_source()
        self.commands.append(_pop_group_to_source)


    def save(self):
        """Save state for Cairo and local contexts.

        You can save in a nested manner, and calls to restore() will pop
        the latest saved context.
        """
        def _save():
            # Save Cairo context
            self.cr.save()
        self.commands.append(_save)


    def restore(self):
        """Restore the previously saved context."""
        def _restore():
            # Restore Cairo context
            self.cr.restore()
        self.commands.append(_restore)


    ###
    ### Important function alert!
    ###

    def render(self, width, height):
        """Render the Drawing at the given size to the current surface.
        """
        # Create a surface at the given size
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.cr = cairo.Context(self.surface)
        # Scale from the original size
        scale_x = float(width) / self.size[0]
        scale_y = float(height) / self.size[1]
        self.scale(scale_x, scale_y)
        # Sneaky bit--scaling needs to happen before everything else
        self.commands.insert(0, self.commands.pop(-1))
        # Execute all draw commands
        for command in self.commands:
            log.debug("Rendering function: %s" % command)
            command()

    ###
    ### Editor interface/interactive functions
    ###

    def save_png(self, filename, width, height):
        """Saves current drawing to PNG, keeping alpha channel intact.

        This is the quickest, since Cairo itself exports directly to .png"""
        self.render(width, height)
        print "Saving", filename
        self.surface.write_to_png(filename)


    def save_jpg(self, filename):
        """Saves current drawing to JPG, losing alpha channel information.
        """
        f = open('/tmp/export.png', 'wb+')
        self.surface.write_to_png(f)
        f.seek(0)
        im = Image.open(f)
        im.save(filename)
        del(im)
        f.close()


    def display(self, width, height):
        """Render and display the Drawing."""
        # Display image at the intended aspect ratio
        png_file = '/tmp/drawing.png'
        self.save_png(png_file, width, height)
        print "Displaying", png_file
        print "(press 'q' in image window to continue)"
        print commands.getoutput('display %s' % png_file)


    def save_image(self, img_filename):
        """Render drawing to a .jpg, .png or other image."""
        log.info("Saving Drawing to %s" % img_filename)
        if img_filename.endswith('.png'):
            self.save_png(img_filename)
        elif img_filename.endswith('.jpg'):
            self.save_jpg(img_filename)
        else:
            log.debug("Creating temporary .png")
            temp_png = '/tmp/%s.png' % img_filename
            self.save_png(temp_png)
            log.debug("Converting temporary png to %s" % img_filename)
            cmd = "convert -size %sx%s " % self.size
            cmd += "%s %s" % (temp_png, img_filename)
            print commands.getoutput(cmd)


###
### Demo functions
###

def draw_fontsize_demo(drawing):
    """Draw font size samples on the given drawing."""
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    
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
        #drawing.roundrectangle(-30, -30, 30, 30, 8, 8)
        drawing.rectangle(-30, -30, 30, 30)
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

    for width in [1, 2, 4, 6, 8, 10, 12, 14, 16]:
        drawing.stroke_width(width)
        rgb = ((255 - width * 8), (120 - width * 5), 0)
        offset = width * 10
        drawing.line(0, offset, -offset, offset)
        drawing.stroke('rgb(%s,%s,%s)' % rgb)

    # Restore context
    drawing.restore()



if __name__ == '__main__':
    mytime = time.time() # Benchmark

    drawing = Drawing(720, 480)

    # Start a new
    drawing.save()
    #drawing.viewbox((0, 0), (720, 480))

    # Add a background fill
    #->Background
    drawing.set_source('darkgray')
    drawing.rectangle(0, 0, 720, 480)
    drawing.fill()

    # Shape demo
    drawing.save()
    draw_shape_demo(drawing)
    drawing.restore()

    # Font size demo
    drawing.save()
    drawing.translate(20, 20)
    draw_fontsize_demo(drawing)
    drawing.restore()

    # Font face demo
    drawing.save()
    drawing.translate(20, 300)
    draw_font_demo(drawing)
    drawing.restore()

    # Stroke demo
    drawing.save()
    drawing.translate(600, 200)
    draw_stroke_demo(drawing)
    drawing.restore()

    # Close out the Cairo rendering...
    drawing.restore()

    print "Took %f seconds" % (time.time() - mytime)

    # Render and display the Drawing at several different sizes
    resolutions = [(720, 480), (352, 480), (352, 240)]
    #resolutions = [(720, 480)]
    for w, h in resolutions:
        print "Displaying Drawing at %sx%s" % (w, h)
        drawing.display(w, h)
   


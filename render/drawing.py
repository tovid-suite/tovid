# -=- encoding: latin-1 -=-

# Run this script standalone for a demonstration:
#    $ python libtovid/render/drawing.py

# To use this module from your Python interpreter, run:
#    $ python
#    >>> from libtovid.render.drawing import *

"""Interactive vector drawing and rendering interface.

This module provides a class called Drawing, which provides a blank canvas
that can be painted with vector drawing functions, and later rendered to
a raster image file (.png, .jpg etc.) at any desired resolution.

To create a new, blank Drawing::

    >>> d = Drawing(800, 600)          # width, height

Here, (800, 600) defines two things:

    - On-screen display size, in pixels (800px x 600px)
    - Intended viewing aspect ratio (800:600 or 4:3)

Note that you are still doing vector drawing, so whatever size you pick here
has no bearing on your final target resolution--it's mostly intended for a
convenient "preview" size while doing interactive drawing.

Back on topic: you can now add shapes to the drawing, fill and stroke them::

    >>> d.circle(500, 300, 150)        # (x, y, radius)
    >>> d.fill('blue', 0.8)            # color name with optional alpha
    >>> d.stroke('rgb(0, 128, 255)')   # rgb values 0-255

Then add more shapes::

    >>> d.rectangle(25, 25, 320, 240)  # x, y, width, height
    >>> d.fill('rgb(40%, 80%, 10%)')   # rgb percentages
    >>> d.stroke('#FF0080', 0.5)       # rgb hex notation with an alpha

To see what the drawing looks like so far, do::

    >>> display(d)                     # display at existing size
    >>> display(d, 720, 480)           # display at different size
    >>> display(d, fix_aspect=True)    # display in correct aspect ratio

You may then decide to add more to the drawing::

    >>> d.set_source('white')
    >>> d.text("Dennis", 50, 100)      # text, x, y

And preview again::

    >>> display(d)

Once you finish your beautiful painting, save it as a nice high-res PNG::

    >>> save_png(d, "my.png", 1600, 1200)

Cairo references:

    [1] http://www.cairographics.org
    [2] http://tortall.net/mu/wiki/CairoTutorial

"""

__all__ = [
    'Drawing',
    'render',
    'display',
    'save_image',
    'save_jpg',
    'save_pdf',
    'save_png',
    'save_ps',
    'save_svg',
    'write_ppm',
]

import os
import sys
import time
import commands
from copy import copy
from math import pi, sqrt
import cairo
import Image      # for JPG export
import ImageColor # for getrgb, getcolor
import ImageFile  # for write_png()
from libtovid import log
from libtovid.util import to_unicode

def get_surface(width, height, surface_type='image', filename=''):
    """Get a cairo surface at the given dimensions.
    """
    if type(width) != int or type(height) != int:
        log.warning("Surface width and height should be integers."\
                    " Converting to int.")

    if surface_type == 'image':
        return cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                  int(width), int(height))
    elif surface_type == 'svg':
        return cairo.SVGSurface(filename, width, height)
    elif surface_type == 'pdf':
        return cairo.PDFSurface(filename, width, height)
    elif surface_type == 'ps':
        return cairo.PSSurface(filename, width, height)



### --------------------------------------------------------------------
### Classes
### --------------------------------------------------------------------
class Step:
    """An atomic drawing procedure, consisting of a closed function that
    draws on a given cairo surface, and human-readable information about
    what parameters were given to it.
    """
    def __init__(self, function, *args):
        self.function = function
        self.name = function.__name__.lstrip('_')
        self.args = args
    def __str__(self):
        return "%s%s" % (self.name, self.args)


# Drawing class notes
#
# The Drawing class has a number of methods (circle, rectangle, fill, stroke
# and many others) that need to operate on a Cairo surface. But we'd like to
# delay execution of actually drawing on that surface--otherwise, we can't
# easily render a given Drawing to a custom resolution.
#
# Closures save the day here--that is, functions without "free variables".
# Anytime you "paint" on the Drawing, what's actually happening is a new
# function is getting created, whose sole purpose in life is to carry out that
# specific paint operation. These tiny, single-purpose functions are then
# added to a list of steps (self.steps) that will actually be executed at
# rendering-time (i.e., when you do display() or save_png).
#
# This not only lets us render a Drawing to different resolutions, but allows
# the possibility of rendering to different Cairo surfaces.

class Drawing:

    tk = None # tkinter widget to send redraws to

    def __init__(self, width=800, height=600, autodraw=False):
        """Create a blank drawing at the given size.

            width, height
                Dimensions of the drawable region, in arbitrary units
            autodraw
                Redraw a preview image after each drawing operation
        """
        self.size = (width, height)
        self.w = width
        self.h = height
        self.aspect = float(width) / height
        self.autodraw = autodraw
        #self.commands = []
        self.steps = []
        # "Dummy" surface/context at the original resolution;
        # should not be drawn on
        self.surface = get_surface(width, height, 'image')
        self.cr = cairo.Context(self.surface)


    def addStep(self, func, *args):
        """Add a Step to self.steps using the given function and args."""
        step = Step(func, *args)
        self.steps.append(step)
        if self.autodraw and step.name in ['fill', 'stroke']:
            display(self, 640, 480, True)


    def doStep(self, func, *args):
        """Add the given Step, and execute it."""
        self.addStep(func, *args)
        func(self.cr)


    def history(self):
        """Return a formatted string of all steps in this Drawing."""
        result = ''
        for number, step in enumerate(self.steps):
            result += '%d. %s\n' % (number, step)
        return result


    def affine(self, rot_x, rot_y, scale_x, scale_y, translate_x, translate_y):
        """Define a 3x3 transformation matrix::

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
        self.doStep(_affine, rot_x, rot_y, scale_x, scale_y,
                     translate_x, translate_y)


    def arc(self, x, y, radius, start_deg, end_deg):
        """Draw an arc from (x, y), with the specified radius, starting at
        degree start_deg and ending at end_deg.
        """
        def _arc(cr):
            cr.arc(x, y, radius, start_deg * pi/180., end_deg * pi/180.)
        self.doStep(_arc, x, y, radius, start_deg, end_deg)


    def arc_rad(self, x, y, radius, start_rad, end_rad):
        """Draw an arc from (x, y), with the specified radius, starting at
        radian start_rad and ending at end_rad.
        """
        def _arc_rad(cr):
            cr.arc(x, y, radius, start_rad, end_rad)
        self.doStep(_arc_rad, x, y, radius, start_rad, end_rad)


    # TODO: Rewrite/cleanup bezier function
    def bezier(self, points, rel=False, close_path=False):
        """Create a Bezier curve.

        Points should look like::

            points = [[(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
                      [(x0, y0)],
                      ]

        where (x0, y0) are the point coordinates, and x_ctl* are the control
        points coordinates.

            - ctl1 - control from last point
            - ctl2 - control to next point

        The last line would specify that control points
        are at the same place (x0, y0), drawing straight lines.

            rel
                when this is True, the x_ctl and y_ctl become relatives
                to the (x0, y0) points
            close_path
                set this to True to call cr.close_path() before stroking.

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
            for x in range(0, len(points)):
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
        self.doStep(_bezier, points, rel, close_path)


    def circle(self, center_x, center_y, radius):
        """Draw a circle defined by center point and radius."""
        def _circle(cr):
            cr.new_path()
            cr.arc(center_x, center_y, radius, 0, 2*pi)
        self.doStep(_circle, center_x, center_y, radius)


    def fill(self, source=None, opacity=None):
        """Fill the current (closed) path with an optionally given color.

        If arguments are present, they are passed to set_source()
        before filling. Note that this source will be applied to further
        fill()ings or stroke()ings or text() calls.
        """
        # Optionally set fill color, and save it.
        if source is not None:
            self.set_source(source, opacity)

        def _fill(cr):
            cr.fill_preserve()
        self.doStep(_fill, source, opacity)


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
        self.doStep(_fill_rule, rule)


    def font(self, name, slant='normal', weight='normal'):
        """Set the current font.

            name
                name of the Font, or family (sans-serif, serif)
            slant
                one of: italic, normal, oblique
            weight
                one of: normal, bold
        """
        sl = {'italic': cairo.FONT_SLANT_ITALIC,
              'normal': cairo.FONT_SLANT_NORMAL,
              'oblique': cairo.FONT_SLANT_OBLIQUE}
        wg = {'normal': cairo.FONT_WEIGHT_NORMAL,
              'bold': cairo.FONT_WEIGHT_BOLD}
        def _font(cr):
            cr.select_font_face(name, sl[slant], wg[weight])
        self.doStep(_font, name, slant, weight)


    def font_size(self, pointsize):
        """Set the current font size in points.
        """
        def _font_size(cr):
            cr.set_font_size(pointsize)
        self.doStep(_font_size, pointsize)


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
        self.doStep(_font_stretch, x, y)


    def font_rotate(self, degrees):
        """Set the font rotation, in degrees.
        """
        def _font_rotate(cr):
            m = cr.get_font_matrix()
            m.rotate(degrees * pi/180.)
            cr.set_font_matrix(m)
        self.doStep(_font_rotate, degrees)


    def image_surface(self, x, y, width, height, surface, mask=None):
        """Draw a given cairo.ImageSurface centered at (x, y), at the given
        width and height.

        If you specify mask, it must be a cairo ImageSurface.
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
        if (mask):
            def _image_surface(cr):
                cr.set_source_surface(surface)
                cr.mask_surface(mask)
            self.doStep(_image_surface, x, y, width, height, surface, mask)
        else:
            def _image_surface(cr):
                cr.set_source_surface(surface)
                cr.paint()
            self.doStep(_image_surface, x, y, width, height, surface, mask)

        self.restore()


    def image(self, x, y, width, height, source):
        """Draw an image centered at (x, y), scaled to the given width and
        height. Return the corresponding cairo.ImageSurface object.

            source
                - a .png filename (quicker and alpha present),
                - a cairo.ImageSurface object, which is even better,
                - a file object
                - a filename - any file supported by python-imaging,
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

        return surface


    def line(self, x0, y0, x1, y1):
        """Set new path as a line from (x0, y0) to (x1, y1).

        Don't forget to stroke()
        """
        def _line(cr):
            cr.new_path()
            cr.move_to(x0, y0)
            cr.line_to(x1, y1)
        self.doStep(_line, x0, y0, x1, y1)


    def operator(self, operator='clear'):
        """Set the operator mode.

            operator
                One of: clear, source, over, in, out, atop, dest,
                dest_over, dest_in, dest_out, dest_atop, xor, add, saturate

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
        self.doStep(_operator, operator)


    def paint(self):
        """Paint the current source everywhere within the current clip
        region.
        """
        def _paint(cr):
            cr.paint()
        self.doStep(_paint)


    def paint_with_alpha(self, alpha):
        """Paints the current source everywhere within the current clip
        region using a mask of constant alpha value alpha.

        The effect is similar to paint(), but the drawing is faded out
        using the alpha value.
        """
        def _paint_with_alpha(cr):
            cr.paint_with_alpha(alpha)
        self.doStep(_paint_with_alpha, alpha)


    def point(self, x, y):
        """Draw a point at (x, y).
        """
        # Circle radius 1/1000 the drawing width
        radius = float(self.size[0]) / 1000
        def _point(cr):
            cr.new_path()
            cr.arc(x, y, radius, 0, 2*pi)
        self.doStep(_point, x, y)


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
        self.doStep(_rectangle_corners, x0, y0, x1, y1)


    def rectangle(self, x, y, width, height):
        """Draw a rectangle with top-left corner at (x, y), and (width x height)
        in size.
        """
        def _rectangle(cr):
            cr.new_path()
            cr.rectangle(x, y, width, height)
        self.doStep(_rectangle, x, y, width, height)


    def rotate_deg(self, degrees):
        """Rotate by the given number of degrees.
        """
        def _rotate_deg(cr):
            m = cr.get_matrix()
            m.rotate(degrees * pi/180.)
            cr.set_matrix(m)
        self.doStep(_rotate_deg, degrees)

    rotate = rotate_deg
    def rotate_rad(self, rad):
        """Rotate by the given number of radians.
        """
        def _rotate_rad(cr):
            m = cr.get_matrix()
            m.rotate(rad)
            cr.set_matrix(m)
        self.doStep(_rotate_rad, rad)


    def roundrectangle(self, x0, y0, x1, y1, bevel_width, bevel_height):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        a bevel size of (bevel_width, bevel_height).
        """
        bw = bevel_width
        bh = bevel_height
        # Add bezier points
        tl1 = [(x0, y0 + bh), (0, 0), (0, 0)]
        tl2 = [(x0 + bw, y0), (0, 0), (-bw, 0)]
        tr1 = [(x1 - bw, y0), (0, 0), (-bw, 0)]
        tr2 = [(x1, y0 + bh), (0, 0), (0, -bw)]
        br1 = [(x1, y1 - bh), (0, 0), (0, -bh)]
        br2 = [(x1 - bw, y1), (0, 0), (+bw, 0)]
        bl1 = [(x0 + bw, y1), (0, 0), (+bw, 0)]
        bl2 = [(x0, y1 - bh), (0, 0), (0, +bh)]
        end = [(x0, y0 + bh), (0, 0), (0, 0)]
        # Call in relative mode bezier control points.
        mylst = [tl1, tl2, tr1, tr2, br1, br2, bl1, bl2, end]
        # Let bezier do the work
        self.bezier(mylst, True)


    def set_source(self, source, opacity=None):
        """Set the source.

            source
                One of the following color formats as a string or a tuple
                (see below), another Surface or Surface-derivative object,
                or a Pattern object (and its derivatives).
            opacity
                Opacity ranging from 0.0 to 1.0. Defaults to None. If
                you specify a 'string' or 'tuple' RGB-like code as
                source, opacity defaults to 1.0

        You can use the following *tuple* format to specify color:

        - (red, green, blue) with colors ranging from 0.0 to 1.0,
          like Cairo wants them

        You can use the following *string* formats to specify color:

        - Hexadecimal color specifiers, given as '#rgb' or '#rrggbb'.
          For example, '#ff0000' specifies pure red.
        - RGB functions, given as 'rgb(red, green, blue)' where the colour
          values are integers in the range 0 to 255. Alternatively, the color
          values can be given as three percentages (0% to 100%). For example,
          'rgb(255,0,0)' and 'rgb(100%,0%,0%)' both specify pure red.
        - Hue-Saturation-Lightness (HSL) functions, given as:
          'hsl(hue, saturation%, lightness%)' where hue is the colour given as
          an angle between 0 and 360 (red=0, green=120, blue=240), saturation
          is a value between 0% and 100% (gray=0%, full color=100%), and
          lightness is a value between 0% and 100% (black=0%, normal=50%,
          white=100%). For example, 'hsl(0,100%,50%)' is pure red.
        - Common HTML colour names. The ImageColor module provides some 140
          standard colour names, based on the colors supported by the X
          Window system and most web browsers. Colour names are case
          insensitive. For example, 'red' and 'Red' both specify pure red.

        """
        mysource = self.create_source(source, opacity)
        def _set_source(cr):
            cr.set_source(mysource)
        # Only do the step if the source could be created
        if mysource:
            self.doStep(_set_source, source, opacity)


    def create_source(self, source, opacity=None):
        """Return a source pattern (solid, gradient, image surface)
        with anything fed into it. Returns None if the source could not
        be created successfully.

        See the set_source() documentation for more details on inputs.

        You can feed anything returned by this function into set_source()
        """
        if isinstance(source, cairo.Pattern):
            return source
        # A string--color name, rgb(), hsv(), or hexadecimal
        elif isinstance(source, str):
            try:
                (r, g, b) = ImageColor.getrgb(source)
            except ValueError, err:
                log.error(err)
                return None
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
        self.doStep(_scale, factor_x, factor_y)


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
        self.doStep(_scale_centered, center_x, center_y, factor_x, factor_y)


    def stroke(self, source=None, opacity=None):
        """Stroke the current shape.

        See fill() documentation for parameter explanation. They are the
        same.
        """
        # Optionally set stroke color, and save it.
        if source is not None:
            self.set_source(source, opacity)

        def _stroke(cr):
            # Optionally set fill color, and save it.
            cr.stroke_preserve()
        self.doStep(_stroke, source, opacity)


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
        self.doStep(_stroke_antialias, do_antialias)


    def stroke_dash(self, array, offset=0.0):
        """Set the dash style.

            array
                A list of floats, alternating between ON and OFF for
                each value
            offset
                An offset into the dash pattern at which the stroke
                should start

        For example::

            >>> stroke_dash([5.0, 3.0])

        alternates between 5 pixels on, and 3 pixels off.
        """
        def _stroke_dash(cr):
            cr.set_dash(array, offset)
        self.doStep(_stroke_dash, array, offset)


    def stroke_linecap(self, cap_type):
        """Set the type of line cap to use for stroking.

            cap_type
                'butt', 'round', or 'square'
        """
        dic = {'butt': cairo.LINE_CAP_BUTT,
               'round': cairo.LINE_CAP_ROUND,
               'square': cairo.LINE_CAP_SQUARE}

        # Test value
        dic[cap_type]

        def _stroke_linecap(cr):
            cr.set_line_cap(dic[cap_type])
        self.doStep(_stroke_linecap, cap_type)


    def stroke_linejoin(self, join_type):
        """Set the type of line-joining to do for stroking.

            join_type
                'bevel', 'miter', or 'round'
        """
        dic = {'bevel': cairo.LINE_JOIN_BEVEL,
               'miter': cairo.LINE_JOIN_MITER,
               'round': cairo.LINE_JOIN_ROUND}

        # Test value
        dic[join_type]

        def _stroke_linejoin(cr):
            cr.set_line_join(dic[join_type])
        self.doStep(_stroke_linejoin, join_type)


    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        def _stroke_width(cr):
            cr.set_line_width(width)
        self.doStep(_stroke_width, width)


    def text(self, text_string, x, y, align='left'):
        """Draw the given text string.

            text_string
                utf8 encoded text string
            x, y
                lower-left corner position

        Set the text's color with set_source() before calling text().
        """
        text_string = to_unicode(text_string)

        def _text(cr):
            (dx, dy, w, h, ax, ay) = cr.text_extents(text_string)
            if align == 'right':
                nx = x - w
            elif align == 'center':
                nx = x - w / 2
            else:
                nx = x
            cr.move_to(nx, y)
            cr.show_text(text_string)
        self.doStep(_text, text_string, x, y, align)


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
        self.doStep(_text_path, text_string, x, y)


    def text_extents(self, text):
        """Returns the dimensions of the to-be-drawn text.

        Call this before calling text() if you want to place it well,
        according to the dimensions of the text rectangle to be drawn.

        See text()'s return value for details.

        Returns:
            (x_bearing, y_bearing, width, height, x_advance, y_advance)
        """
        text = to_unicode(text)
        return self.cr.text_extents(text)


    def translate(self, dx, dy):
        """Do a translation by (dx, dy) pixels."""
        def _translate(cr):
            m = cr.get_matrix()
            m.translate(dx, dy)
            cr.set_matrix(m)
        self.doStep(_translate, dx, dy)


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
        self.doStep(_push_group)


    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to push_group() and
        installs the resulting pattern as the source pattern in the current
        cairo context.
        """
        def _pop_group_to_source(cr):
            cr.pop_group_to_source()
        self.doStep(_pop_group_to_source)


    def save(self):
        """Save state for Cairo and local contexts.

        You can save in a nested manner, and calls to restore() will pop
        the latest saved context.
        """
        def _save(cr):
            cr.save()
        self.doStep(_save)

    BEGIN = save
    def restore(self):
        """Restore the previously saved context.
        """
        def _restore(cr):
            cr.restore()
        self.doStep(_restore)

    END = restore
    def font_family(self, family):
        """Set the current font, by family name."""
        def _font_family(cr):
            cr.select_font_face(family)
        self.doStep(_font_family, family)

    font_face = font_family
    def text_align(self, text_string, x, y, align='left'):
        """Draw the given text string.

            text_string
                UTF-8 encoded text string
            x, y
                Lower-left corner position
            align
                'left', 'center', 'right'. This only changes the
                alignment in 'x', and 'y' stays the baseline.

        Set the text's color with set_source() before calling text().
        """
        (dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        w = 0
        if align == 'right':
            x = x - w
        elif align == 'center':
            x = x - w / 2
        else: # 'left'
            x = x
        # Let text() do the drawing
        self.text(text_string, x, y)


    def text_path_align(self, x, y, text_string, centered=False):
        """Same as text_align(), but sets a path and doesn't draw anything.
        Call stroke() or fill() yourself.
        """
        (dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        if centered:
            x = x - w / 2
            y = y + h / 2
        # Let text_path() do the drawing
        self.text_path(text_string, x, y)


### --------------------------------------------------------------------
### Exported functions
### --------------------------------------------------------------------
# Cached masks, rendered only once.
interlace_fields = None


def interlace_drawings(draw1, draw2):
    """Merge two drawings into one, using interlacing fields.

    This method interlaces with the BOTTOM-FIRST field order.
    """
    global interlace_fields

    dr = Drawing(draw1.w, draw1.h)

    # create masks (only once)
    if (not interlace_fields):
        fields = [0, 1]
        for f in range(0, 2):
            img = cairo.ImageSurface(cairo.FORMAT_ARGB32, draw1.w, draw1.h)
            cr = cairo.Context(img)
            cr.set_antialias(cairo.ANTIALIAS_NONE)
            cr.set_source_rgba(0.5, 0.5, 0.5, 1)
            cr.set_line_width(1)

            for x in range(0, draw1.h / 2):
                # x*2 + f = top field first.., each two lines..
                # -1 à draw1.w +1 -> pour être sur de couvrir aussi les bouts.
                cr.move_to(-1, x*2 + f)
                cr.line_to(draw1.w + 1, x*2 + f)
                cr.stroke()

            fields[f] = img
        interlace_fields = fields
    else:
        fields = interlace_fields

    # For bottom first, use fields[0] first, and fields[1] after.
    # For top-first, use draw1 with fields[1] and draw2 with fields[0]
    # paint first image
    dr.image_surface(0, 0, dr.w, dr.h, draw1.surface, fields[0])
    # paint second image
    dr.image_surface(0, 0, dr.w, dr.h, draw2.surface, fields[1])

    return dr



def render(drawing, context, width, height):
    """Render a Drawing to the given cairo context at the given size.
    """
    # Scale from the original size
    scale_x = float(width) / drawing.size[0]
    scale_y = float(height) / drawing.size[1]
    drawing.scale(scale_x, scale_y)
    # Sneaky bit--scaling needs to happen before everything else
    drawing.steps.insert(0, drawing.steps.pop(-1))

    # Execute all draw commands
    for step in drawing.steps:
        log.debug("Drawing step: %s" % step)
        step.function(context)

    # Remove scaling function
    drawing.steps.pop(0)


def display(drawing, width=None, height=None, fix_aspect=False):
    """Render and display the given Drawing at the given size.

        drawing
            A Drawing object to display
        width
            Pixel width of displayed image,
            or 0 to use the given Drawing's size
        height
            Pixel height of displayed image,
            or 0 to use the given Drawing's size
        fix_aspect
            True to adjust height to make the image
            appear in the correct aspect ratio
    """
    if not width:
        width = drawing.size[0]
    if not height:
        height = drawing.size[1]

    # Adjust height to fix aspect ratio if desired
    if fix_aspect:
        height = width / drawing.aspect
    # Render and display a .png
    png_file = '/tmp/drawing.png'
    save_png(drawing, png_file, width, height)
    print("Displaying %s at %sx%s" % (png_file, width, height))
    print("(press 'q' in image window to continue)")
    print(commands.getoutput('display %s' % png_file))


def write_ppm(drawing, pipe, width, height, workdir=None):
    """Write image as a PPM file to a file-object

      workdir
        Unused in this context, just to have parallel parameters
        with write_png().

    Useful to pipe directly in ppmtoy4m and to pipe directly to mpeg2enc.
    """
    # Timing
    start = time.time()
    if (width, height) == drawing.size:
        #print("Not re-rendering")
        surface = drawing.surface
    else:
        surface = get_surface(width, height, 'image')
        context = cairo.Context(surface)
        render(drawing, context, width, height)

    buf = surface.get_data()
    # Assumes surface is cairo.FORMAT_ARGB32
    im = Image.frombuffer('RGBA', (surface.get_width(),  surface.get_height()),
                          buf)
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    im.save(pipe, 'ppm')

    #print("write_ppm took %s seconds" % (time.time() - start))


def write_png(drawing, pipe, width, height, workdir):
    """Write image as a PPM file to a file-object

    Useful to pipe directly in::

        pngtopnm -mix -background=rgb:00/00/00 | ppmtoy4m | mpeg2enc.
    """
    # Timing
    start = time.time()
    if (width, height) == drawing.size:
        #print("Not re-rendering")
        surface = drawing.surface
    else:
        surface = get_surface(width, height, 'image')
        context = cairo.Context(surface)
        render(drawing, context, width, height)

    surface.write_to_png('%s/tmp.png' % workdir)
    im = Image.open('%s/tmp.png' % workdir)
    im.load()
    im.save(pipe, 'ppm')

    #print("write_png took %s seconds" % (time.time() - start))


def save_png(drawing, filename, width, height):
    """Saves a drawing to PNG, keeping alpha channel intact.

    This is the quickest, since Cairo itself exports directly to .png
    """
    # Timing
    start = time.time()
    if (width, height) == drawing.size:
        #print("Not re-rendering")
        surface = drawing.surface
    else:
        surface = get_surface(width, height, 'image')
        context = cairo.Context(surface)
        render(drawing, context, width, height)
    surface.write_to_png(filename)
    #print("save_png took %s seconds" % (time.time() - start))


def save_jpg(drawing, filename, width, height):
    """Saves a drawing to JPG, losing alpha channel information.
    """
    f = open('/tmp/export.png', 'wb+')
    save_png(drawing, f, width, height)
    f.seek(0)
    im = Image.open(f)
    im.save(filename)
    del(im)
    f.close()


def save_image(drawing, img_filename, width, height):
    """Render drawing to a .jpg, .png or other image.
    """
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
        print(commands.getoutput(cmd))


def save_svg(drawing, filename, width, height):
    """Render drawing to an SVG file.
    """
    surface = get_surface(width, height, 'svg', filename)
    context = cairo.Context(surface)
    render(drawing, context, width, height)
    context.show_page()
    surface.finish()
    print("Saved SVG to %s" % filename)


def save_pdf(drawing, filename, width, height):
    """Render drawing to a PDF file.
    """
    surface = get_surface(width, height, 'pdf', filename)
    context = cairo.Context(surface)
    render(drawing, context, width, height)
    context.show_page()
    surface.finish()
    print("Saved PDF to %s" % filename)


def save_ps(drawing, filename, width, height):
    """Render drawing to a PostScript file.
    """
    surface = get_surface(width, height, 'ps', filename)
    context = cairo.Context(surface)
    render(drawing, context, width, height)
    context.show_page()
    surface.finish()
    print("Saved PostScript to %s" % filename)


### --------------------------------------------------------------------
### Demo functions
### --------------------------------------------------------------------
def draw_fontsize_demo(drawing):
    """Draw font size samples on the given drawing.
    """
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    # TODO: Remove this scaling hack
    drawing.scale(800.0/720, 600.0/480)

    # Draw white text in a range of sizes
    drawing.set_source('white')

    for size in [12, 16, 20, 24, 28, 32]:
        ypos = size * size / 5
        drawing.font('Nimbus Sans')
        drawing.font_size(size)
        drawing.text("%s pt: The quick brown fox" % size, 700, ypos, 'right')

    # Restore context
    drawing.restore()


def draw_font_demo(drawing):
    """Draw samples of different fonts on the given drawing.
    """
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    # TODO: Remove this scaling hack
    drawing.scale(800.0/720, 600.0/480)

    fontsize = 24
    drawing.font_size(fontsize)
    fonts = [
        'Arial',
        'Baskerville',
        'Dragonwick',
        'Georgia',
        'Helvetica',
        'Linotext',
        'Luxi Mono',
        'Nimbus Sans',
        'Old-Town',
        'Sharktooth',
        'Tahoma',
        'Times']
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
    """Draw shape samples on the given drawing.
    """
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    # TODO: Remove this scaling hack
    drawing.scale(800.0/720, 600.0/480)

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
    """Draw a stroke/strokewidth demo on the given drawing.
    """
    assert isinstance(drawing, Drawing)

    # Save context
    drawing.save()
    # TODO: Remove this scaling hack
    drawing.scale(800.0/720, 600.0/480)

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

    drawing = Drawing(800, 600)

    # Start a new
    drawing.save()

    # Add a background fill
    #->Background
    drawing.set_source('darkgray')
    drawing.rectangle(0, 0, 800, 600)
    drawing.fill()

    # Shape demo
    drawing.save()
    draw_shape_demo(drawing)
    drawing.restore()

    # Font size demo
    drawing.save()
    draw_fontsize_demo(drawing)
    drawing.restore()

    # Stroke demo
    drawing.save()
    drawing.translate(680, 240)
    draw_stroke_demo(drawing)
    drawing.restore()

    # Font face demo
    drawing.save()
    drawing.translate(60, 160)
    draw_font_demo(drawing)
    drawing.restore()

    # Close out the Cairo rendering...
    drawing.restore()

    print("Took %f seconds" % (time.time() - mytime))

    # Render and display the Drawing at several different sizes
    resolutions = [(352, 240), (352, 480), (720, 480), (800, 600)]
    #resolutions = [(720, 480)]
    for w, h in resolutions:
        display(drawing, w, h)

    #save_svg(drawing, "/tmp/drawing.svg", 400, 300)
    #save_pdf(drawing, "/tmp/drawing.pdf", 400, 300)
    #save_ps(drawing, "/tmp/drawing.ps", 400, 300)

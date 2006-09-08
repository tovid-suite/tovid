#! /usr/bin/env python
# -=- encoding: latin-1 -=-
# cairo_.py
#
# Cairo backend, by Alexandre Bourget <wackysalut@bourget.cc>
#

"""A Python interface to the Cairo library.

Run this script standalone for a demonstration:

    $ python libtovid/render/cairo_.py

Please note the leading '_' after 'cairo'. This is to prevent conflicts with
the 'official' cairo binding class.

To start off with Cairo, read (a must!):

    http://tortall.net/mu/wiki/CairoTutorial

To build your own Cairo vector image using this module, fire up your Python
interpreter:

    $ python

And do something like this:

    >>> from libtovid.render.cairo_ import Drawing
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
    >>> drawing.rectangle((320, 240), (520, 400))

Example Cairo usage:

    >>> drawing.set_source('rgb(255,255,80)')
    >>> drawing.rectangle((0, 0), (800, 600))
    >>> drawing.fill()
    >>> drawing.set_source(1, 1, 0.5)
    >>> drawing.rectangle((320, 240), (520, 400))
    >>> drawing.stroke('white')

Notice how you set the colors first in Cairo, and that you call the fill() and
stroke() methods afterwards. This is because Cairo creates paths, and then you
can choose to fill() them or not, and to stroke() the outline or not.

Note also that MVG confuses fill() with stroke(). When calling mvg's fill(),
you will in fact stroke the outline. [insert here how does MVG handle filling]

If you want to preview what you have so far, call drawing.render().

You can keep drawing on the image, calling render() at any time to display the
rendered image.

References:

    [1] http://www.cairographics.org
    [2] http://tortall.net/mu/wiki/CairoTutorial

"""

__all__ = ['Drawing']

import os
import sys
import time
import commands
from math import pi, sqrt
import cairo
import Image      # for JPG export
import ImageColor # for getrgb, getcolor

class Drawing:
    """A Cairo image context, ready to be drawn.

    Drawing functions are mostly identical to their MVG counterparts, e.g.
    these two are equivalent:

        rectangle 100,100 200,200       # MVG command
        rectangle((100,100), (200,200)) # Drawing function

    """
    def __init__(self, size=(720, 480)):
        # Use self.size and self.width + self.height instead of
        # calling the cairo functions, because actualy values
        # can change according to base_scaling, when dealing with
        # different aspect ratios.
        self.size = size
        self.width, self.height = size
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width,
                                     self.height)
        self.cr = cairo.Context(self.surface)
        # Default values
        self.family = 'sans'
        # Default dash array
        self.dash_array = []
        self.dash_offset = 0.0
        # Default colors..
        self.text_rgb = (0, 0, 0)
        self.text_alpha = 1.0
        self.fill_rgb = (0, 0, 0)
        self.fill_alpha = 0.0
        self.stroke_rgb = (0, 0, 0)
        self.stroke_alpha = 1.0
        # Overall opacity
        self.global_opacity = 1.0
        # Automatic behavior (auto_fill, auto_stroke)
        self.auto_fill_val = False
        self.auto_stroke_val = False
        # Push/pop stack
        self.stack = []

    def cry(self, mstr = ''):
        """Just complain about deprecated functions

        Calls to this functions should all be removed before releasing.
        """
        raise AssertionError, "Use of deprecated function. %s" % mstr

    #
    # Setup commands (auto-stuff)
    #
    def auto_fill(self, value=True):
        """Sets the auto-fill behavior to ON. Accepts a bool value.

        After calls to fillable elements, fill() will automatically
        be called. Make sure to set the color first, unless you like
        the defaults.

        Auto-fill default to being disabled.

        In fact, cairo::fill_preserve() will be called, so that you can
        stroke it after.
        """
        self.auto_fill_val = value

    def auto_stroke(self, value=True):
        """Sets the auto-stroke behavior to ON. Accepts a bool value.

        After calls to strokable elements, stroke() will automatically
        be called. Make sure to set the color first, unless you like
        the defaults.

        Auto-stroke default to being disabled.

        In fact, cairo::stroke_preserve() will be called, so that you can
        fill it after.
        """
        self.auto_stroke_val = value

    def _go_auto_fill(self):
        """Fill the path if auto_fill is enabled.

        See auto_fill()"""
        if self.auto_fill_val:
            self.fill()
            
    def _go_auto_stroke(self):
        """Stroke the path if auto_stroke is enabled.

        See auto_stroke()"""
        if self.auto_stroke_val:
            self.stroke()

    def _go_auto_all(self):
        """Run all the auto_fill and auto_stroke commands if enabled"""
        self._go_auto_fill()
        self._go_auto_stroke()
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
        self.cr.arc(x, y, radius, start_deg * pi/180., end_deg * pi/180.)
        self._go_auto_all()

    def arc_rad(self, (x, y), radius, (start_rad, end_rad)):
        """Draw an arc from (x, y), with the specified radius, starting at radian
        start_rad and ending at end_rad.
        """
        # Convert deg. to rad.
        self.cr.arc(x, y, radius, start_rad, end_rad)
        self._go_auto_all()

    def bezier(self, pt_list, rel=False, close_path=False):
        """Create a Bézier curve.

            pt_list should look like:
            
            pt_list = [[(x0, y0), (x_ctl1, y_ctl1), (x_ctl2, y_ctl2)],
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
        assert len(pt_list) > 1, "You need at least two points"
        for x in pt_list:
            if (len(x) == 1):
                x.append(x[0])       # add the two identical
                x.append(x[0])       # control points
            assert len(x) == 3, "You need to specify three tuples for each point, or one single"
            for y in x:
                assert isinstance(y, tuple) and len(y) == 2, "You need "\
                       "to specify two-values tuples"
        # Map relative stuff to absolute, when rel=True
        if rel:
            for x in range(0,len(pt_list)):
                pt = pt_list[x]
                assert len(pt) == 3, "In relative mode, you must "\
                       "specify control points"
                # Render relative values to absolute values.
                npt = []
                #             #  x      #  y
                npt.append([pt[0][0], pt[0][1]]) # x0, y0
                npt.append([pt[0][0] + pt[1][0], pt[0][1] + pt[1][1]])
                npt.append([pt[0][0] + pt[2][0], pt[0][1] + pt[2][1]])
                pt_list[x] = npt
                    
        # Move to the first x,y in the first point
        self.cr.new_path()
        self.cr.move_to(pt_list[0][0][0], pt_list[0][0][1])

        for pt in pt_list:
            self.cr.curve_to(pt[2][0], pt[2][1],
                             pt[0][0], pt[0][1],
                             pt[1][0], pt[1][1],
                             )
        if close_path:
            self.cr.close_path()

        self._go_auto_all()

    def circle(self, (center_x, center_y), (perimeter_x, perimeter_y)):
        """Draw a circle defined by center and perimeter points."""

        # distance between x1y1, and x2y2
        rad = sqrt( (perimeter_x - center_x) ** 2 +
                    (perimeter_y - center_y) ** 2 )
        self.cr.new_path()
        self.cr.arc(center_x, center_y, rad, 0, 2*pi)

        self._go_auto_all()
                    
    def circle_rad(self, (center_x, center_y), radius):
        """Draw a circle defined by center point and radius."""
        self.cr.new_path()
        self.cr.arc(center_x, center_y, radius, 0, 2*pi)

        self._go_auto_all()


    # TODO: add clip stuff...

    def _getrgb(self, color):
        """Wrapper around ImageColor, to support (r,g,b) tuple as well

        Deals with str and tuple objects.
        """
        self.cry()

    def color_fill(self, color, opacity=1.0):
        """Define color for fill() operations

        This module uses ImageColor to translate 'color' into RGB values:

        DEPRECATED, see fill()
        
        opacity -- 0.0 to 1.0, or None, to leave opacity untouched.
        """

        self.cry()
                
    def color_stroke(self, color, opacity=1.0):
        """Define color for line stroke() operations.

        See color_fill() for details on how to specify 'color'
        """
        self.cry()
        

    def color_text(self, color, opacity=1.0):
        """Define color for text() operations.

        See color_fill() for details on how to specify 'color'
        """
        self.cry()
        
    def color_all(self, color, opacity=1.0):
        """Define all three color_stroke(), color_fill(), color_text()
        in one single shot.

        See color_fill() for details on how to specify 'color'
        """
        self.cry()

    def _go_stroke_color(self):
        self.cry()
        
        r,g,b = self.stroke_rgb
        self.cr.set_source_rgba(r,g,b, float(self.stroke_alpha * self.global_opacity))

    def _go_text_color(self):
        self.cry()
        
        r,g,b = self.text_rgb
        self.cr.set_source_rgba(r,g,b, float(self.text_alpha * self.global_opacity))

    def _go_fill_color(self):
        self.cry()
        
        r,g,b = self.fill_rgb
        self.cr.set_source_rgba(r,g,b, float(self.fill_alpha * self.global_opacity))

    #def decorate(self, decoration):
    #    """Decorate text(?) with the given style, which may be 'none',
    #    'line-through', 'overline', or 'underline'."""
    #    self.insert('decorate %s' % decoration)

    #def ellipse(self, (center_x, center_y), (radius_x, radius_y),
    #            (arc_start, arc_stop)):
    #    # Draw arc, transform matrix, etc...
    #    
    #    self.insert('ellipse %s,%s %s,%s %s,%s' % \
    #            (center_x, center_y, radius_x, radius_y, arc_start, arc_stop))

    def fill_opacity(self, opacity):
        self.cry()

    def set_fill_opacity(self, opacity):
        """Define fill opacity, from fully transparent (0.0) to fully
        opaque (1.0).
    
        NOTE: this doesn't paint anything on the canvas.
        """
        self.fill_alpha = opacity
    
    def fill(self, source=None, opacity=None):
        """Fill the current (closed) path with an optionally given color.

        If arguments are present, they are passed to set_source()
        before filling.

        WARNING: Cairo and MVG backends don't handle 'fill' the same way.
                 Cairo will paint with a 'fill' command, whereas MVG will
                 set the color to be used in the next drawing operations.
        """
        # Optionally set fill color, and save it.
        if source is not None:
            self.set_source(source, opacity)
                
        # Optionally set opacity level, and save it.
        self.cr.fill_preserve()

    def fill_n_stroke(self):
        """Combines fill() and stroke() commands in a single call.

        fill() is called first so that the outline drawn by stroke() will
        not appear over the filling.
        """
        self.cry()
        
    def fill_rule(self, rule):
        """Set the fill rule to one of:
        
            evenodd, winding (nonzero)

        This determines which parts of an overlapping path polygon will
        be filled with the fill() command.
            
        http://www.w3.org/TR/SVG/painting.html#FillRuleProperty
        """
        tr = {'evenodd': cairo.FILL_RULE_EVEN_ODD,
              'winding': cairo.FILL_RULE_WINDING}
        self.cr.set_fill_rule(tr[rule])
    
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
        self.cr.select_font_face(name, sl[slant], wg[weight])

    #def font_family(self, family):
    #    """Set the current font, by family name."""
    #    self.cr.select_font_face(family)
    
    def font_size(self, pointsize):
        """Set the current font size in points."""
        self.cr.set_font_size(pointsize)
    
    def font_stretch(self, x=1.0, y=1.0):
        """Set the font stretch type in both directions to one of:

        = 1.0 -- normal
        > 1.0 -- strench
        < 1.0 -- shrink

        In MVG, these values are used:

            all, normal, semi-condensed, condensed, extra-condensed,
            ultra-condensed, semi-expanded, expanded, extra-expanded,
            ultra-expanded
        """
        m = self.cr.get_font_matrix()
        m.scale(x, y)
        self.cr.set_font_matrix(m)

    def font_rotate(self, degrees):
        """Set the font rotation, in degrees.

        Addition to Cairo backend."""
        m = self.cr.get_font_matrix()
        m.rotate(degrees * pi/180.)
        self.cr.set_font_matrix(m)
        
    
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
    
    def image(self, (x, y), (width, height), source):
        """Draw an image centered at (x, y), scaled to the given width and
        height.

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
        # Create new image
        im = None
        if isinstance(source, cairo.ImageSurface):
            im = source
        elif isinstance(source, str) and source.endswith('.png'):
            im = cairo.ImageSurface.create_from_png(source)
        else:
            mim = Image.open(source)
            f = open('/tmp/export.png', 'wb+')
            mim.save(f, 'PNG')
            del(mim)
            f.seek(0)
            im = cairo.ImageSurface.create_from_png(f)
            f.close()
            del(f)

        # Centering and scaling algo
        add_x, add_y = (0, 0)
        dw = float(width) / float(im.get_width())
        dh = float(height) / float(im.get_height())
        if (dw > dh):
            scal = dh
            add_x = (width - dh * float(im.get_width())) / 2
        else:
            scal = dw
            add_y = (height - dw * float(im.get_height())) / 2
        self.save()
        self.translate((x + add_x, y + add_y))
        self.scale((scal, scal))
        self.cr.set_source_surface(im)
        self.cr.paint()
        self.restore()
    
    def line(self, (x0, y0), (x1, y1)):
        """Set new path as a line from (x0, y0) to (x1, y1).

        Don't forget to stroke()
        """
        self.cr.new_path()
        self.cr.move_to(x0, y0)
        self.cr.line_to(x1, y1)
    
    #def matte(self, (x, y), method='floodfill'):
    #    # method may be: point, replace, floodfill, filltoborder, reset
    #    # (What do x, y mean?)
    #    self.insert('matte %s,%s %s' % (x, y, method))

    #def offset(self, offset):
    #    self.insert('offset %s' % offset)

    def opacity(self, opacity=1.0):
        """Sets global opacity for the next functions
    
        opacity -- ranges from 0.0 (transparent) to 1.0 (fully opaque)
    
        NOTE: Make sure to call opacity() before you call any color(),
        functions, because in certain situations, it might not be applied
        correctly.
        """
        self.global_opacity = opacity
        

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
        self.cr.set_operator(ops[operator])
               
    def paint(self):
        """Paint the current source everywhere within the current clip
        region."""
        self.cr.paint()

    def paint_with_alpha(self, alpha):
        """Paints the current source everywhere within the current clip
        region using a mask of constant alpha value alpha.

        The effect is similar to paint(), but the drawing is faded out
        using the alpha value."""
        self.cr.paint_with_alpha(alpha)

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

    def polygon(self, pt_list, close_path=True):
        """Define a polygonal path defined by (x, y) points in the given
        list.

            pt_list = [(x0, y0),
                       (x1, y1),
                       (x2, y2)]

        Draw strokes and filling yourself, with fill(), stroke(), and
        fill_n_stroke().
        """
        nlist = []
        for tup in pt_list:
            nlist.append([tup])
            
        self.bezier(nlist, False, close_path)
        
    
    def polyline(self, pt_list, close_path=True):
        """Draw a polygon defined by (x, y) points in the given list.

        This is a short- (or long-) hand for polygon. In Cairo, you draw
        your filling (fill()), or strokes (stroke()) yourself, so
        having polyline and polygon is basiclly useless.
        """
        self.polygon(pt_list, close_path)

    
    def rectangle(self, (x0, y0), (x1, y1)):
        """Draw a rectangle from (x0, y0) to (x1, y1)."""
        self.cr.new_path()
        self.cr.rectangle(x0, y0,
                          x1 - x0, y1 - y0)
        
        self._go_auto_all() # Draw or not

    def rectangle_size(self, (x, y), (w, h)):
        """Draw a "w x h" rectangle from top-left corner x,y"""
        self.cr.new_path()
        self.cr.rectangle(x, y, w, h)
        
        self._go_auto_all()

    def rotate(self, degrees):
        """Map to rotate_deg()"""
        self.rotate_deg(degrees)
        
    def rotate_deg(self, degrees):
        """Rotate by the given number of degrees."""
        m = self.cr.get_matrix()
        m.rotate(degrees * pi/180.)
        self.cr.set_matrix(m)

    def rotate_rad(self, rad):
        """Rotate by the given number of radians."""
        m = self.cr.get_matrix()
        m.rotate(rad)
        self.cr.set_matrix(m)

    def roundrectangle(self, (x0, y0), (x1, y1), (bevel_width, bevel_height)):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        a bevel size of (bevel_width, bevel_height)."""
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

    def set_source(self, source, opacity=None):
        """
        source -- One of the following color formats as a string or a tuple
                  (see below), another Surface or Surface-derivative object,
                  or a Pattern object (and it's derivatives).
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

        self.cr.set_source(mysource)
            
    def create_source(self, source, opacity=None):
        """Return a source pattern (solid, gradient, image surface)
        with anything fed into it.

        See the set_source() documentation for more details on inputs.

        You can feed anything returned by this function into set_source()
        """
        if isinstance(source, cairo.Pattern):
            return source
        
        elif isinstance(source, str):
            (r,g,b) = ImageColor.getrgb(source)
            alpha = 1.0
            if opacity is not None:
                alpha = opacity
                
            return cairo.SolidPattern(r / 255.0, g / 255.0,
                                      b / 255.0, alpha)
        
        elif isinstance(source, tuple):
            if len(source) != 3:
                raise ValueError, "Color must be specified as a 3 floats tuple, each ranging from 0.0 to 1.0"
            (r,g,b) = source
            alpha = 1.0
            if opacity is not None:
                alpha = opacity
                
            return cairo.SolidPattern(r,g,b,alpha)
        
        elif isinstance(source, cairo.Gradient):
            return source
        
        elif isinstance(source, cairo.Surface):
            return cairo.SurfacePattern(source)
        
        else:
            raise TypeError, "source must be one of: str, tuple, cairo.Pattern, cairo.Gradient or cairo.Surface"


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

    def base_scaling(self, (dx, dy)):
        """Set base_scaling, to deal with different aspect ratios.

        Changes values of self.size, self.width and self.height.

        Use these values for correct values of the output image.
        """
        self.scale((dx, dy))
        self.width = int(self.width / dx)
        self.height = int(self.height / dy)
        self.size = (self.width, self.height)
        
        
    def scale(self, (dx, dy)):
        """Set scaling to (dx, dy).

        Note that the center point for scaling is (0,0), unless otherwise
        specified. See scale_centered()
        """
        m = self.cr.get_matrix()
        m.scale(dx, dy)
        self.cr.set_matrix(m)

    def scale_centered(self, (center_x, center_y), (dx, dy)):
        """Set scaling to (dx, dy), where dx and dy are horizontal and
        vertical ratios (floats).

        scale_centered() will keep the (center_x, center_y) in the middle
        of the scaling, operating a translation in addition to scaling.
        """
        m = self.cr.get_matrix()
        # Ouch, we want to keep the center x,y at the same place?!
        m.translate(-(center_x * dx - center_x), -(center_y * dy - center_y))
        m.scale(dx, dy)
        self.cr.set_matrix(m)

    #def skewX(self, angle):
    #    # Is that a / / shift of an object ?
    #    self.insert('skewX %s' % angle)
    
    #def skewY(self, angle):
    #    self.insert('skewY %s' % angle)

    # Gradient stuff.. ? People can use the cairo lib directly for that.
    #def stop_color(self, color, offset):
    #    self.insert('stop-color %s %s' % (color, offset))
        
    def stroke(self, source=None, opacity=None):
        """Stroke the current shape.

        See fill() documentation for parameter explanation. They are the
        same.
        """
        # Optionally set fill color, and save it.
        if source is not None:
            self.set_source(source, opacity)
            
        # Optionally set opacity level, and save it.
        self.cr.stroke_preserve()

    def stroke_antialias(self, do_antialias=True):
        """Enable/disable antialiasing for strokes. This does not affect
        text. See text_antialias() for more info on text antialiasing.

        do_antialias -- bool (True/False)can be: 'none', 'default', 'gray'
        """
        if do_antialias:
            self.cr.set_antialias(cairo.ANTIALIAS_GRAY)
        else:
            self.cr.set_antialias(cairo.ANTIALIAS_NONE)

    def stroke_dash(self, array, offset=0.0):
        """Set the dash style.

        array -- an array of floats, alternating between ON and OFF for
                 each value.
        offset -- an offset into the dash pattern at which the stroke
                  should start

        >>> stroke_dash([5.0, 3.0])

        would alternate between 5 pixels on, and 3 pixels off.
        """
        self.dash_array = array
        self.dash_offset = offset
        self.cr.set_dash(array, offset)
        

    def stroke_dasharray(self, array):
        """Shorthand for stroke_dash(), except it doesn't change the offset.

        DEPRECATED: you should use stroke_dash() instead.
        """
        self.stroke_dash(array, self.dash_offset)
        
    def stroke_dashoffset(self, offset):
        """Shorthand for stroke_dash(), except it leaves the dash_array
        untouched.

        DEPRECATED: you should use stroke_dash() instead."""
        self.stroke_dash(self.dash_array, offset)

    def stroke_linecap(self, cap_type):
        """Set the type of line-cap to use (line edges).

        cap_type -- may be 'butt', 'round', or 'square'
        """
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
        self.cry()

    def set_stroke_opacity(self, opacity):
        """Define stroke opacity, from fully transparent (0.0) to fully
        opaque (1.0).

        NOTE: this doesn't paint anything on the canvas.
        """
        self.cry()
        self.stroke_alpha = opacity

    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        self.cr.set_line_width(width)
    
    def text(self, (x, y), text_string, centered=False):
        """Draw the given text string.

            (x, y) -- lower-left corner position
            text_string -- utf8 encoded text string
            centered -- if True, text_string will be centered at the
                        given (x, y) coordinates.

        Set the text's color with set_source() before calling text().

        Returned value:
            (x_bearing, y_bearing, width, height, x_advance, y_advance)
        where:
            x_bearing -- the horizontal distance from the origin to the
                         leftmost part of the glyphs as drawn. Positive
                         if the glyphs lie entirely to the right of the
                         origin.
            y_bearing -- the vertical distance from the origin to the topmost
                         part of the glyphs as drawn. Positive only if the
                         glyphs lie completely below the origin; will usually
                         be negative.
            width -- width of the glyphs as drawn
            height -- height of the glyphs as drawn
            x_advance -- distance to advance in the X direction after drawing
                         these glyphs
            y_advance -- distance to advance in the Y direction after drawing
                         these glyphs. Will typically be zero except for
                         vertical text layout as found in East-Asian languages.
            
        See:
            http://www.cairographics.org/manual/cairo-Scaled-Fonts.html#cairo-text-extents-t
        """
        # NOTE: It will be possible to use pangocairo wrapper around
        #       the cairo class, for all the text-related stuff! hey Pango
        #       at the tips of our fingers :P woah!
        #
        if not isinstance(text_string, unicode):
            text_string = unicode(text_string.decode('latin-1'))

        self.save()
        (dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        if centered:
            x = x - w / 2
            y = y + h / 2
        self.cr.move_to(x, y)
        self.cr.show_text(text_string)
        self.restore()

        return (dx, dy, w, h, ax, ay)

    def text_path(self, (x,y), text_string, centered=False):
        """Same as text(), but sets a path and doesn't draw anything.

        You can, after a call to text_path(), call stroke() or fill()
        yourself.

        Has the parameters and returns the same values as text().

        Beware that text() calls the Cairo function show_text() which
        caches glyphs, so is more efficient when dealing with large
        texts.
        """
        if not isinstance(text_string, unicode):
            text_string = unicode(text_string.decode('latin-1'))

        (dx, dy, w, h, ax, ay) = self.cr.text_extents(text_string)
        if centered:
            x = x - w / 2
            y = y + h / 2
        self.cr.move_to(x, y)
        self.cr.text_path(text_string)

        return (dx, dy, w, h, ax, ay)
    
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
      

    # Old MVG stuff, TODO: Implement using Cairo
    #def text_antialias(self, do_antialias):
    #    """Turn text antialiasing on (True) or off (False)."""
    #    if do_antialias:
    #        self.insert('text-antialias 1')
    #    else:
    #        self.insert('text-antialias 0')

    def text_opacity(self, opacity):
        """Set the text opacity.

            opacity -- 0.0 = transparent, 1.0 = opaque

        Alias for color_text(None, opacity)
        """
        self.cry('Use fill_opacity instead')

    def translate(self, (dx, dy)):
        """Do a translation by (x, y) pixels."""
        m = self.cr.get_matrix()
        m.translate(dx, dy)
        self.cr.set_matrix(m)
    
    def push(self):
        self.cry()

    def push_group(self):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.

        The redirection lasts until the group is completed by a call
        to pop_group() or pop_group_to_source(). These calls provide
        the result of any drawing to the group as a pattern, (either
        as an explicit object, or set as the source pattern).
        """
        self.cr.push_group()

    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to push_group() and
        installs the resulting pattern as the source pattern in the current
        cairo context."""
        self.cr.pop_group_to_source()
    
    def save(self):
        """Save state for Cairo and local contexts. You can save
        in a nested manner, and calls to restore() will pop the latest
        save()'d context.

        This was called push() before.
        """
        # Save local context
        self.stack.append({'tr': self.text_rgb,
                         'ta': self.text_alpha,
                         'fr': self.fill_rgb,
                         'fa': self.fill_alpha,
                         'sr': self.stroke_rgb,
                         'sa': self.stroke_alpha,
                         'go': self.global_opacity,
                         'afv': self.auto_fill_val,
                         'asv': self.auto_stroke_val})
        # Save Cairo context
        self.cr.save()

    def pop(self):
        self.cry()

    def restore(self):
        """Restore the previously save()'d context.

        This was called pop() before.
        """
        # Restore local context
        st = self.stack.pop()
        self.text_rgb = st['tr']
        self.text_alpha = st['ta']
        self.fill_rgb = st['fr']
        self.fill_alpha = st['fa']
        self.stroke_rgb = st['sr']
        self.stroke_alpha = st['sa']
        self.global_opacity = st['go']
        self.auto_fill_val = st['afv']
        self.auto_stroke_val = st['asv']

        # Restore Cairo context
        self.cr.restore()

    
    #
    # Editor interface/interactive functions
    #

    def load(self, filename):
        """DEPRECATED: Load MVG from the given file.

        Unused in Cairo backend"""
        self.cry()


    def code(self, editing=True):
        """Return complete MVG text for the Drawing.
        
        NOTE: Unused in Cairo context"""
        self.cry()

    def save_png(self, filename):
        """Saves current drawing to PNG, keeping alpha channel intact.

        This is the quickest, since Cairo itself exports directly to .png"""
        self.surface.write_to_png(filename)
        
    def save_jpg(self, filename):
        """Saves current drawing to JPG, losing alpha channel information."""
        
        f = open('/tmp/export.png', 'wb+')
        self.surface.write_to_png(f)
        f.seek(0)
        im = Image.open(f)
        im.save(filename)
        del(im)
        f.close()

    def render(self, filename='/tmp/my.png'):
        """Render the .mvg with ImageMagick, and display it."""
        self.surface.write_to_png(filename)
        # TODO: when rendering series of .png, we can make a PNGLIST
        #       that would be ready for importation as a video in
        #       Cinelerra, the video editing suite.

    def save_image(self, img_filename):
        """Render the drawing to a .jpg, .png or other image."""
        self.save(self.filename)
        cmd = "convert -size %sx%s " % self.size
        cmd += "%s %s" % (self.filename, img_filename)
        print "Rendering drawing to: %s" % img_filename
        print commands.getoutput(cmd)




# Demo functions

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
        drawing.text((0, ypos), u"%s pt: The quick brown fox" % size)
    
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
        drawing.text((3, ypos+3), font)
        # White text
        drawing.set_source('white', 1.0)
        drawing.text((0, ypos), font)
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
    drawing.circle_rad((500, 200), 200)
    drawing.stroke('black')
    drawing.fill('orange')
    drawing.restore()

    # Grey-stroked blue circles
    drawing.save()
    drawing.stroke_width(2)
    drawing.circle_rad((65, 50), 15)
    drawing.fill('#8080FF')
    drawing.stroke('#777')
    
    drawing.circle_rad((60, 100), 10)
    drawing.fill('#2020F0')
    drawing.stroke('#777')
    
    drawing.circle_rad((55, 150), 5)
    drawing.fill('#0000A0')
    drawing.stroke('#777')
    drawing.restore()

    # Semitransparent green rectangles
    drawing.save()
    drawing.translate((50, 400))
    for scale in [0.2, 0.4, 0.7, 1.1, 1.6, 2.2, 2.9, 3.7]:
        drawing.save()
        drawing.translate((scale * 70, scale * -50))
        drawing.scale((scale, scale))
        drawing.stroke_width(scale)
        drawing.roundrectangle((-30, -30), (30, 30), (8, 8))
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
        drawing.line((0, offset), (-offset, offset))
        drawing.stroke('rgb(%s,%s,%s)' % rgb)

    # Restore context
    drawing.restore()



if __name__ == '__main__':
    mytime = time.time() # Benchmark
    
    drawing = Drawing((720, 480))

    # Start a new
    drawing.save()
    #drawing.viewbox((0, 0), (720, 480))

    # Add a background fill
    #->Background
    drawing.set_source('darkgray')
    drawing.rectangle((0, 0), (720, 480))
    drawing.fill()

    # Shape demo
    drawing.save()
    draw_shape_demo(drawing)
    drawing.restore()

    # Font size demo
    drawing.save()
    drawing.translate((20, 20))
    draw_fontsize_demo(drawing)
    drawing.restore()

    # Font face demo
    drawing.save()
    drawing.translate((20, 300))
    draw_font_demo(drawing)
    drawing.restore()

    # Stroke demo
    drawing.save()
    drawing.translate((600, 200))
    draw_stroke_demo(drawing)
    drawing.restore()

    # Close out the Cairo rendering...
    drawing.restore()

    # Test JPG output
    #print "Output to: /tmp/cairo.jpg"
    #drawing.save_jpg('/tmp/cairo.jpg')
    
    # Test PNG output
    print "Output to: /tmp/cairo.png"
    drawing.save_png('/tmp/cairo.png')
    
    print "SECONDS: %f" % (time.time() - mytime)


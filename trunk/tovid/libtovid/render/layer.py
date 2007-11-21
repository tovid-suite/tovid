#! /usr/bin/env python
# layer.py

"""This module provides a Layer class and several derivatives. A Layer
is a graphical overlay that may be composited onto an image canvas.

Run this script standalone for a demonstration:

    $ python libtovid/layer.py

Layer subclasses may combine graphical elements, including other Layers,
into a single interface for drawing and customizing those elements. Layers may
exhibit animation, through the use of keyframed drawing commands, or through
use of the Effect class (and its subclasses, as defined in libtovid/effect.py).

Each Layer subclass provides (at least) an __init__ function, and a draw
function. For more on how to use Layers, see the Layer class definition and
template example below.
"""

__all__ = [\
    'Layer',
    'Background',
    'Text',
    'ShadedText',
    'TextBox',
    'Label',
    'VideoClip',
    'Image',
    'Thumb',
    'ThumbGrid',
    'SafeArea',
    'Scatterplot',
    'InterpolationGraph',
    'ColorBars']

import os
import sys
import math
import commands
from libtovid.utils import get_file_type
from libtovid.render.drawing import Drawing, save_image
from libtovid.render.effect import Effect
from libtovid.render.animation import Keyframe, Tween
from libtovid.media import MediaFile
from libtovid.transcode import rip
from libtovid import log

log.level = 'info'

class Layer:
    """A visual element, or a composition of visual elements. Conceptually
    similar to a layer in the GIMP or Photoshop, with support for animation
    effects and sub-Layers.
    """
    def __init__(self):
        """Initialize the layer. Extend this in derived classes to accept
        configuration settings for drawing the layer; call this function
        from any derived __init__ functions."""
        self.effects = []
        self.sublayers = []
        self._parent_flipbook = None
        self._parent_layer = None

    ###
    ### Child-parent initialization
    ###
    def _init_childs(self):
        """Give access to all descendant layers and effects to their parents.

        In layers, you can access your parent layer (if sublayed) with:
            layer._parent_layer
        and to the top Flipbook object with:
            layer._parent_flipbook
        """
        for x in range(0, len(self.effects)):
            self.effects[x]._init_parent_flipbook(self._parent_flipbook)
            self.effects[x]._init_parent_layer(self)
        for x in range(0, len(self.sublayers)):
            self.sublayers[x][0]._init_parent_flipbook(self._parent_flipbook)
            self.sublayers[x][0]._init_parent_layer(self)
            self.sublayers[x][0]._init_childs(self)

    def _init_parent_flipbook(self, flipbook):
        self._parent_flipbook = flipbook

    def _init_parent_layer(self, layer):
        self._parent_layer = layer


    ###
    ### Derived-class interface
    ###
    
    def draw(self, drawing, frame):
        """Draw the layer and all sublayers onto the given Drawing. Override
        this function in derived layers."""
        assert isinstance(drawing, Drawing)

    ###
    ### Sublayer and effect interface
    ###
    
    def add_sublayer(self, layer, position=(0, 0)):
        """Add the given Layer as a sublayer of this one, at the given position.
        Sublayers are drawn in the order they are added; each sublayer may have
        its own effects, but the parent Layer's effects apply to all sublayers.
        """
        assert isinstance(layer, Layer)
        self.sublayers.append((layer, position))

    def draw_sublayers(self, drawing, frame):
        """Draw all sublayers onto the given Drawing for the given frame."""
        assert isinstance(drawing, Drawing)
        for sublayer, position in self.sublayers:
            drawing.save()
            drawing.translate(position)
            sublayer.draw(drawing, frame)
            drawing.restore()

    def add_effect(self, effect):
        """Add the given Effect to this Layer. A Layer may have multiple effects
        applied to it; all effects apply to the current layer, and all sublayers.
        """
        assert isinstance(effect, Effect)
        self.effects.append(effect)

    def draw_with_effects(self, drawing, frame):
        """Render the entire layer, with all effects applied.
        
            drawing: A Drawing object to draw the Layer on
            frame:   The frame number that is being drawn
            
        """
        # Do preliminary effect rendering
        for effect in self.effects:
            effect.pre_draw(drawing, frame)
        # Draw the layer and sublayers
        self.draw(drawing, frame)
        # Close out effect rendering, in reverse (nested) order
        for effect in reversed(self.effects):
            effect.post_draw(drawing, frame)


# ============================================================================
# Layer template
# ============================================================================
# Copy and paste the following code to create your own Layer.
#
# Layer subclasses should define two things:
#
#     __init__():  How to initialize the layer with parameters
#     draw():   How do draw the layer on a Drawing
#
# First, declare the layer class name. Include (Layer) to indicate that your
# class is a Layer.
class MyLayer (Layer):
    """Overlapping semitransparent rectangles.
    (Modify this documentation string to describe what's in your layer)"""

    # Here's the class initialization function, __init__. Define here any
    # parameters that might be used to configure your layer's behavior or
    # appearance in some way (along with default values, if you like). Here,
    # we're allowing configuration of the fill and stroke colors, with default
    # values of 'blue' and 'black', respectively:

    def __init__(self, fill_color='blue', stroke_color='black'):
        """Create a MyLayer with the given fill and stroke colors."""
        # Initialize the base Layer class. Always do this.
        Layer.__init__(self)
        # Store the given colors, for later use
        self.fill_color = fill_color
        self.stroke_color = stroke_color

    # The draw() function is responsible for rendering the contents of the
    # layer onto a Drawing. It will use the configuration given to __init__
    # (in this case, fill and stroke colors) to render something onto a Drawing
    # associated with a particular frame number:

    def draw(self, drawing, frame):
        """Draw MyLayer contents onto the given drawing, at the given frame
        number."""

        # For safety's sake, make sure you really have a Drawing object:
        assert isinstance(drawing, Drawing)

        # Save the drawing context. This prevents any upcoming effects or
        # style changes from messing up surrounding layers in the Drawing.
        drawing.save()

        # Get a Cairo pattern source for the fill and stroke colors
        # (TODO: Make this easier, or use a simpler example)
        fc = drawing.create_source(self.fill_color, 0.6)
        sc = drawing.create_source(self.stroke_color)

        # And a stroke width of 1, say:
        drawing.stroke_width(1)

        # Now, draw something. Here, a couple of pretty semitransparent
        # rectangles, using the fill and stroke color patterns created earlier:
        drawing.rectangle(0, 0,  50, 20)
        drawing.fill(fc)
        drawing.stroke(sc)
        drawing.rectangle(15, 12,  45, 28)
        drawing.fill(fc)
        drawing.stroke(sc)

        # Be sure to restore the drawing context afterwards:
        drawing.restore()

    # That's it! Your layer is ready to use. See the Demo section at the end of
    # this file for examples on how to create and render Layers using Python.

# ============================================================================
# End of Layer template
# ============================================================================


class Background (Layer):
    """A background that fills the frame with a solid color, or an image."""
    def __init__(self, color='black', filename=''):
        Layer.__init__(self)
        self.color = color
        self.filename = filename
        
    def draw(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Background")
        width, height = drawing.size
        drawing.save()
        # Fill drawing with an image
        if self.filename is not '':
            drawing.image(0, 0, width, height, self.filename)
        # Fill drawing with a solid color
        elif self.color:
            drawing.rectangle(0, 0, width, height)
            drawing.fill(self.color)
        drawing.restore()


### --------------------------------------------------------------------

class Image (Layer):
    """A rectangular image, scaled to the given size.

    image_source -- can be anything Drawing::image() can accept.
                    See documentation in render/drawing.py.
    """
    def __init__(self, image_source, (x, y), (width, height)):
        Layer.__init__(self)
        self.size = (width, height)
        self.image_source = image_source
        self.position = (x, y)


    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Image")
        drawing.save()
        # Save the source for future calls to draw, so no further
        # processing will be necessary. And other effects can be done
        # without interferring with the original source.
        self.image_source = drawing.image(self.position[0], self.position[1],
                                          self.size[0], self.size[1],
                                          self.image_source)
        drawing.restore()


### --------------------------------------------------------------------

class VideoClip (Layer):
    """A rectangular video clip, scaled to the given size.

    TODO: num_frames should accept a range [first, end], an int (1-INT) and
    rip frames accordingly. For now, it only accepts an INT for the range 1-INT
    """
    def __init__(self, filename, (width, height), position=(0,0), num_frames=120):
        Layer.__init__(self)
        self.filename = filename
        self.mediafile = MediaFile(filename)
        self.size = (width, height)
        # List of filenames of individual frames
        self.frame_files = []
        # TODO: be able to change hardcoded default values
        self.rip_frames(1, num_frames)
        # Set (x,y) position
        assert(isinstance(position, tuple))
        self.position = position

    def rip_frames(self, start, end):
        """Rip frames from the video file, from start to end frames."""
        log.info("VideoClip: Ripping frames %s to %s" % (start, end))
        outdir = '/tmp/%s_frames' % self.filename
        self.frame_files = rip.rip_frames(self.mediafile, outdir,
                                          [start, end])

    def draw(self, drawing, frame=1):
        """Draw ripped video frames to the given drawing. For now, it's
        necessary to call rip_frames() before calling this function.
        
        Video is looped.
        """
        assert isinstance(drawing, Drawing)
        log.debug("Drawing VideoClip")
        if len(self.frame_files) == 0:
            log.error("VideoClip: need to call rip_frames() before drawing.")
            sys.exit(1)
        drawing.save()
        # Loop frames (modular arithmetic)
        if frame >= len(self.frame_files):
            frame = frame % len(self.frame_files)
        filename = self.frame_files[frame-1]
        drawing.image(self.position, self.size, filename)
        drawing.restore()


### --------------------------------------------------------------------

class Text (Layer):
    """A simple text string, with size, color and font.

    text -- UTF8 encoded string.
    """
    def __init__(self, text, position=(0, 0), color='white', fontsize=20, \
                 font='Helvetica', align='left'):
        Layer.__init__(self)
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.font = font
        self.align = align
        # Set (x,y) position
        self.position = position

    # TODO: This is gonna be pretty broken...
    def extents(self, drawing):
        """Return the extents of the text as a (x0, y0, x1, y1) tuple."""
        assert isinstance(drawing, Drawing)
        drawing.save()
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        x_bearing, y_bearing, width, height, x_adv, y_adv = \
                 drawing.text_extents(self.text)
        drawing.restore()
        # Add current layer's position to the (x,y) bearing of extents
        x0 = int(self.position[0] + x_bearing)
        y0 = int(self.position[1] + y_bearing)
        x1 = int(x0 + width)
        y1 = int(y0 + height)
        return (x0, y0, x1, y1)

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Text")
        # Drop in debugger
        drawing.save()
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        if self.color is not None:
            drawing.set_source(self.color)
        # TODO: DO something with the align !!
        drawing.text(self.text, self.position[0], self.position[1], self.align)
        drawing.restore()


### --------------------------------------------------------------------

class ShadedText (Layer):
    """A simple text string, with size, color and font.

    text -- UTF8 encoded string.
    """
    def __init__(self, text, position=(0, 0), offset=(5, 5),
                 color='white', shade_color='gray', fontsize=20,
                 font='Nimbus Sans', align='left'):
        Layer.__init__(self)
        shade_position = (position[0] + offset[0],
                          position[1] + offset[1])
        self.under = Text(text, shade_position, shade_color,
                          fontsize, font, align)
        self.over = Text(text, position, color, fontsize, font, align)

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Text")
        drawing.save()
        self.under.draw(drawing, frame)
        self.over.draw(drawing, frame)
        drawing.restore()


### --------------------------------------------------------------------

class Label (Text):
    """A text string with a rectangular background.

    You can access Text's extents() function from within here too."""
    def __init__(self, text, position=(0,0), color='white', bgcolor='#555',
                 fontsize=20, font='NimbusSans'):
        Text.__init__(self, text, position, color, fontsize, font)
        self.bgcolor = bgcolor
        # Set (x,y) position
        assert(isinstance(position, tuple))
        self.position = position

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Label")
        #(dx, dy, w, h, ax, ay) = self.extents(drawing)
        (x0, y0, x1, y1) = self.extents(drawing)
        # Save context
        drawing.save()

        # Calculate rectangle dimensions from text size/length
        width = x1 - x0
        height = y1 - y0
        # Padding to use around text
        pad = self.fontsize / 3
        # Calculate start and end points of background rectangle
        start = (-pad, -height - pad)
        end = (width + pad, pad)

        # Draw a stroked round rectangle
        drawing.save()
        drawing.stroke_width(1)
        drawing.roundrectangle(start[0], start[1], end[0], end[1], pad, pad)
        drawing.stroke('black')
        drawing.fill(self.bgcolor, 0.3)
        drawing.restore()

        # Call base Text class to draw the text
        Text.draw(self, drawing, frame)

        # Restore context
        drawing.restore()


### --------------------------------------------------------------------

class Thumb (Layer):
    """A thumbnail image or video."""
    def __init__(self, filename, (width, height), position=(0,0), title=''):
        Layer.__init__(self)
        self.filename = filename
        self.size = (width, height)
        self.title = title or os.path.basename(filename)
        # Set (x,y) position
        assert(isinstance(position, tuple))
        self.position = position

        # Determine whether file is a video or image, and create the
        # appropriate sublayer
        filetype = get_file_type(filename)
        if filetype == 'video':
            self.add_sublayer(VideoClip(filename, self.size, self.position))
        elif filetype == 'image':
            self.add_sublayer(Image(filename, self.size, self.position))
        self.lbl = Label(self.title, fontsize=15)
        self.add_sublayer(self.lbl, self.position)

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Thumb")
        drawing.save()
        (x0, y0, x1, y1) = self.lbl.extents(drawing)
        drawing.translate(0, x1-x0)
        self.draw_sublayers(drawing, frame)
        drawing.restore()


### --------------------------------------------------------------------

class ThumbGrid (Layer):
    """A rectangular array of thumbnail images or videos."""
    def __init__(self, files, titles=None, (width, height)=(600, 400),
                 (columns, rows)=(0, 0), aspect=(4,3)):
        """Create a grid of thumbnail images or videos from a list of files,
        fitting in a space no larger than the given size, with the given number
        of columns and rows. Use 0 to auto-layout columns or rows, or both 
        (default).
        """
        assert files != []
        if titles:
            assert len(files) == len(titles)
        else:
            titles = files
        Layer.__init__(self)
        self.size = (width, height)
        # Auto-dimension (using desired rows/columns, if given)
        self.columns, self.rows = \
            self._fit_items(len(files), columns, rows, aspect)
        # Calculate thumbnail size, keeping aspect
        w = (width - self.columns * 16) / self.columns
        h = w * aspect[1] / aspect[0]
        thumbsize = (w, h)

        # Calculate thumbnail positions
        positions = []
        for row in range(self.rows):
            for column in range(self.columns):
                x = column * (width / self.columns)
                y = row * (height / self.rows)
                positions.append((x, y))

        # Add Thumb sublayers
        for file, title, position in zip(files, titles, positions):
            title = os.path.basename(file)
            self.add_sublayer(Thumb(file, thumbsize, (0, 0), title), position)

    def _fit_items(self, num_items, columns, rows, aspect=(4, 3)):
        # Both fixed, nothing to calculate
        if columns > 0 and rows > 0:
            # Make sure num_items will fit (columns, rows)
            if num_items < columns * rows:
                return (columns, rows)
            # Not enough room; auto-dimension both
            else:
                log.warning("ThumbGrid: Can't fit %s items" % num_items +\
                            " in (%s, %s) grid;" % (columns, rows) +\
                            " doing auto-dimensioning instead.")
                columns = rows = 0
        # Auto-dimension to fit num_items
        if columns == 0 and rows == 0:
            # TODO: Take aspect ratio into consideration to find an optimal fit
            root = int(math.floor(math.sqrt(num_items)))
            return ((1 + num_items / root), root)
        # Rows fixed; use enough columns to fit num_items
        if columns == 0 and rows > 0:
            return ((1 + num_items / rows), rows)
        # Columns fixed; use enough rows to fit num_items
        if rows == 0 and columns > 0:
            return (columns, (1 + num_items / columns))

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing ThumbGrid")
        drawing.save()
        self.draw_sublayers(drawing, frame)
        drawing.restore()


### --------------------------------------------------------------------

class SafeArea (Layer):
    """Render a safe area box at a given percentage.
    """
    def __init__(self, percent, color):
        self.percent = percent
        self.color = color
        
    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing SafeArea")
        # Calculate rectangle dimensions
        scale = float(self.percent) / 100.0
        width, height = drawing.size
        topleft = ((1.0 - scale) * width / 2,
                  (1.0 - scale) * height / 2)
        # Save context
        drawing.save()
        drawing.translate(topleft[0], topleft[1])
        # Safe area box
        drawing.stroke_width(3)
        drawing.rectangle(0, 0,  width * scale, height * scale)
        drawing.stroke(self.color)
        # Label
        drawing.font_size(18)
        drawing.set_source(self.color)
        drawing.text(u"%s%%" % self.percent, 10, 20)
        # Restore context
        drawing.restore()


### --------------------------------------------------------------------

class Scatterplot (Layer):
    """A 2D scatterplot of data.
    """
    def __init__(self, xy_dict, width=240, height=80, x_label='', y_label=''):
        """Create a scatterplot using data in xy_dict, a dictionary of
        lists of y-values, indexed by x-value.
        """
        self.xy_dict = xy_dict
        self.width, self.height = (width, height)
        self.x_label = x_label
        self.y_label = y_label

    def draw(self, drawing, frame):
        """Draw the scatterplot."""
        assert isinstance(drawing, Drawing)
        log.debug("Drawing Scatterplot")
        width, height = (self.width, self.height)
        x_vals = self.xy_dict.keys()
        max_y = 0
        for x in x_vals:
            largest = max(self.xy_dict[x] or [0])
            if largest > max_y:
                max_y = largest
        # For numeric x, scale by maximum x-value
        x_is_num = isinstance(x_vals[0], int) or isinstance(x_vals[0], float)
        if x_is_num:
            x_scale = float(width) / max(x_vals)
        # For string x, scale by number of x-values
        else:
            x_scale = float(width) / len(x_vals)
        # Scale y according to maximum value
        y_scale = float(height) / max_y

        # Save context
        drawing.save()
        drawing.rectangle(0, 0, width, height)
        drawing.fill('white', 0.75)
        
        # Draw axes
        #->comment("Axes of scatterplot")
        drawing.save()
        drawing.stroke_width(2)
        drawing.line(0, 0, 0, height)
        drawing.stroke('black')
        drawing.line(0, height, width, height)
        drawing.stroke('black')
        drawing.restore()

        # Axis labels
        drawing.save()
        drawing.set_source('blue')

        drawing.save()
        for i, x in enumerate(x_vals):
            drawing.save()
            if x_is_num:
                drawing.translate(x * x_scale, height + 15)
            else:
                drawing.translate(i * x_scale, height + 15)
            drawing.rotate(30)
            drawing.text(x, 0, 0)
            drawing.restore()

        drawing.font_size(20)
        drawing.text(self.x_label, width/2, height+40)
        drawing.restore()

        drawing.save()
        drawing.text(max_y, -30, 0)
        drawing.translate(-25, height/2)
        drawing.rotate(90)
        drawing.text(self.y_label, 0, 0)
        drawing.restore()

        drawing.restore()

        # Plot all y-values for each x (as small circles)
        #->comment("Scatterplot data")
        drawing.save()
        for i, x in enumerate(x_vals):
            if x_is_num:
                x_coord = x * x_scale
            else:
                x_coord = i * x_scale
            # Shift x over slightly
            x_coord += 10
            # Plot all y-values for this x
            for y in self.xy_dict[x]:
                y_coord = height - y * y_scale
                drawing.circle(x_coord, y_coord, 3)
                drawing.fill('red', 0.2)
        drawing.restore()
        
        # Restore context
        drawing.restore()


### --------------------------------------------------------------------

class InterpolationGraph (Layer):
    # TODO: Support graphing of tuple data
    """A graph of an interpolation curve, defined by a list of Keyframes and
    an interpolation method."""
    def __init__(self, keyframes, size=(240, 80), method='linear'):
        """Create an interpolation graph of the given keyframes, at the given
        size, using the given interpolation method."""
        Layer.__init__(self)
                
        self.keyframes = keyframes
        self.size = size
        self.method = method
        # Interpolate keyframes
        self.tween = Tween(keyframes, method)

    def draw(self, drawing, frame):
        """Draw the interpolation graph, including frame/value axes,
        keyframes, and the interpolation curve."""
        assert isinstance(drawing, Drawing)
        log.debug("Drawing InterpolationGraph")
        data = self.tween.data
        # Calculate maximum extents of the graph
        width, height = self.size
        x_scale = float(width) / len(data)
        y_scale = float(height) / max(data)

        #->drawing.comment("InterpolationGraph Layer")

        # Save context
        drawing.save()

        # Draw axes
        #->drawing.comment("Axes of graph")
        drawing.save()
        drawing.stroke_width(3)
        drawing.polyline([(0, 0), (0, height), (width, height)], False)
        drawing.stroke('#ccc')
        drawing.restore()

        # Create a list of (x, y) points to be graphed
        curve = []
        x = 1
        while x <= len(self.tween.data):
            # y increases downwards; subtract from height to give a standard
            # Cartesian-oriented graph (so y increases upwards)
            point = (int(x * x_scale), int(height - data[x-1] * y_scale))
            curve.append(point)
            x += 1
        drawing.save()
        # Draw the curve
        drawing.stroke_width(2)
        drawing.polyline(curve, False)
        drawing.stroke('blue')
        drawing.restore()

        # Draw Keyframes as dotted vertical lines
        drawing.save()
        # Vertical dotted lines
        drawing.set_source('red')
        drawing.stroke_width(2)
        for key in self.keyframes:
            x = int(key.frame * x_scale)
            drawing.line(x, 0,   x, height)
            drawing.stroke('red')
            
        # Draw Keyframe labels
        drawing.set_source('white')
        for key in self.keyframes:
            x = int(key.frame * x_scale)
            y = int(height - key.data * y_scale - 3)
            drawing.text(u"(%s,%s)" % (key.frame, key.data), x, y)

        drawing.restore()

        # Draw a yellow dot for current frame
        #->drawing.comment("Current frame marker")
        drawing.save()
        pos = (frame * x_scale, height - data[frame-1] * y_scale)
        drawing.circle(pos[0], pos[1], 2)
        drawing.fill('yellow')
        drawing.restore()

        # Restore context
        drawing.restore()


### --------------------------------------------------------------------

class ColorBars (Layer):
    """Standard SMPTE color bars
    (http://en.wikipedia.org/wiki/SMPTE_color_bars)
    """
    def __init__(self, size, position=(0,0)):
        """Create color bars in a region of the given size and position.
        """
        Layer.__init__(self)
        self.size = size
        # Set (x,y) position
        assert(isinstance(position, tuple))
        self.position = position

    def draw(self, drawing, frame=1):
        assert isinstance(drawing, Drawing)
        log.debug("Drawing ColorBars")
        x, y = self.position
        width, height = self.size

        drawing.save()
        # Get to the right place and size
        drawing.translate(x, y)
        drawing.scale(width, height)
        # Video-black background
        drawing.rectangle(0, 0, 1, 1)
        drawing.fill('rgb(16, 16, 16)')

        # Top 67% of picture: Color bars at 75% amplitude
        top = 0
        bottom = 2.0 / 3
        seventh = 1.0 / 7
        size = (seventh, bottom)
        bars = [(0, top, seventh, bottom, 'rgb(191, 191, 191)'),
                (seventh, top, seventh, bottom, 'rgb(191, 191, 0)'),
                (2*seventh, top, seventh, bottom, 'rgb(0, 191, 191)'),
                (3*seventh, top, seventh, bottom, 'rgb(0, 191, 0)'),
                (4*seventh, top, seventh, bottom, 'rgb(191, 0, 191)'),
                (5*seventh, top, seventh, bottom, 'rgb(191, 0, 0)'),
                (6*seventh, top, seventh, bottom, 'rgb(0, 0, 191)')]

        # Next 8% of picture: Reverse blue bars
        top = bottom
        bottom = 0.75
        height = bottom - top
        bars.extend([(0, top, seventh, height, 'rgb(0, 0, 191)'),
                (seventh, top, seventh, height, 'rgb(16, 16, 16)'),
                (2*seventh, top, seventh, height, 'rgb(191, 0, 191)'),
                (3*seventh, top, seventh, height, 'rgb(16, 16, 16)'),
                (4*seventh, top, seventh, height, 'rgb(0, 191, 191)'),
                (5*seventh, top, seventh, height, 'rgb(16, 16, 16)'),
                (6*seventh, top, seventh, height, 'rgb(191, 191, 191)')])

        # Lower 25%: Pluge signal
        top = bottom
        bottom = 1.0
        sixth = 1.0 / 6
        height = bottom - top
        bars.extend([(0, top, 1.0, height, 'rgb(16, 16, 16)'),
                (0, top, sixth, height, 'rgb(0, 29, 66)'),
                (sixth, top, sixth, height, 'rgb(255, 255, 255)'),
                (2*sixth, top, sixth, height, 'rgb(44, 0, 92)'),
                # Sub- and super- black narrow bars
                (4*sixth, top, 0.33*sixth, height, 'rgb(7, 7, 7)'),
                (4.33*sixth, top, 0.33*sixth, height,'rgb(16, 16, 16)'),
                (4.66*sixth, top, 0.33*sixth, height, 'rgb(24, 24, 24)')])

        # Draw and fill all bars
        for x, y, width, height, color in bars:
            drawing.rectangle(x, y, width, height)
            drawing.fill(color)

        drawing.restore()



if __name__ == '__main__':
    images = None
    # Get arguments, if any
    if len(sys.argv) > 1:
        # Use all args as image filenames to ThumbGrid
        images = sys.argv[1:]

    # A Drawing to render Layer demos to
    drawing = Drawing(800, 600)
    
    # Draw a background layer
    bgd = Background(color='#7080A0')
    bgd.draw(drawing, 1)

    # Draw color bars
    bars = ColorBars((320, 240), (400, 100))
    bars.draw(drawing, 1)

    # Draw a label
    drawing.save()
    drawing.translate(460, 200)
    label = Label("tovid loves Linux")
    label.draw(drawing, 1)
    drawing.restore()

    # Draw a text layer, with position.
    text = Text("Jackdaws love my big sphinx of quartz",
                (82, 62), '#bbb')
    text.draw(drawing, 1)

    # Draw a text layer
    drawing.save()
    drawing.translate(80, 60)
    text = Text("Jackdaws love my big sphinx of quartz")
    text.draw(drawing, 1)
    drawing.restore()

    # Draw a template layer (overlapping semitransparent rectangles)
    template = MyLayer('white', 'darkblue')
    # Scale and translate the layer before drawing it
    drawing.save()
    drawing.translate(50, 100)
    drawing.scale(3.0, 3.0)
    template.draw(drawing, 1)
    drawing.restore()

    # Draw a safe area test (experimental)
    safe = SafeArea(93, 'yellow')
    safe.draw(drawing, 1)

    # Draw a thumbnail grid (if images were provided)
    if images:
        drawing.save()
        drawing.translate(350, 300)
        thumbs = ThumbGrid(images, (320, 250))
        thumbs.draw(drawing, 1)
        drawing.restore()

    # Draw an interpolation graph
    drawing.save()
    drawing.translate(60, 400)
    # Some random keyframes to graph
    keys = [Keyframe(1, 25), Keyframe(10, 5), Keyframe(30, 35),
            Keyframe(40, 35), Keyframe(45, 20), Keyframe(60, 40)]
    interp = InterpolationGraph(keys, (400, 120), method="cosine")
    interp.draw(drawing, 25)
    drawing.restore()

    # Draw a scatterplot
    drawing.save()
    xy_data = {
        5: [2, 4, 6, 8],
        10: [3, 5, 7, 9],
        15: [5, 9, 13, 17],
        20: [8, 14, 20, 26]}
    drawing.translate(550, 350)
    #drawing.scale(200, 200)
    plot = Scatterplot(xy_data, 200, 200, "Spam", "Eggs")
    plot.draw(drawing, 1)
    drawing.restore()
    
    log.info("Output to /tmp/my.png")
    save_image(drawing, '/tmp/my.png', 800, 600)

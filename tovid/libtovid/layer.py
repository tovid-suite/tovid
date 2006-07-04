#! /usr/bin/env python
# layer.py

"""This module provides the Layer class and several of its derivatives. A Layer
is a graphical overlay that may be composited onto an image canvas.

Run this script standalone for a demonstration:

    $ python libtovid/layer.py

Layer subclasses may combine many graphical elements, including other Layers,
into a single interface for customizing and drawing those elements. Layers may
exhibit animation, through the use of keyframed drawing commands, or through
use of the Effect class (and its subclasses, as defined in libtovid/effect.py).

Each class provides (at least) an initialization function, and a draw_on
function. For more on how to use Layers, see the Layer class definition and
template example below.
"""

__all__ = [\
    'Layer',
    'Background',
    'Text',
    'Label',
    'VideoClip',
    'Image',
    'Thumb',
    'ThumbGrid',
    'SafeArea',
    'InterpolationGraph'
]

import os
import sys
import math
import commands
from libtovid.utils import get_file_type
from libtovid.mvg import Drawing
from libtovid.effect import Effect
from libtovid.animation import Keyframe, Tween
from libtovid.media import MediaFile

class Layer:
    """A visual element, or a composition of visual elements. Conceptually
    similar to a layer in the GIMP or Photoshop, plus support for animation
    effects and sub-Layers.
    """
    def __init__(self):
        self.effects = []
        self.sublayers = []

    def add_effect(self, effect):
        assert isinstance(effect, Effect)
        self.effects.append(effect)

    def add_sublayer(self, layer, position=(0, 0)):
        """Add the given Layer as a sublayer of this one, at the given position.
        Sublayers are drawn in the order they are added; each sublayer may have
        its own effects, but the parent Layer's effects apply to all sublayers.
        """
        assert isinstance(layer, Layer)
        self.sublayers.append((layer, position))

    def draw_on(self, drawing, frame):
        """Draw the layer onto the given Drawing. Override this function in
        derived layers."""
        assert isinstance(drawing, Drawing)

    def draw_effects(self, drawing, frame):
        """Draw all effects onto the given Drawing for the given frame."""
        assert isinstance(drawing, Drawing)
        if self.effects != []:
            drawing.comment("Drawing effects")
            for effect in self.effects:
                effect.draw_on(drawing, frame)

    def draw_sublayers(self, drawing, frame):
        """Draw all sublayers onto the given Drawing for the given frame."""
        assert isinstance(drawing, Drawing)
        if self.sublayers != []:
            drawing.comment("Drawing sublayers")
            for sublayer, position in self.sublayers:
                drawing.push()
                drawing.translate(position)
                sublayer.draw_on(drawing, frame)
                drawing.pop()


# ============================================================================
# Layer template
# ============================================================================
# Copy and paste the following code to create your own Layer.
#
# Layer subclasses should define two things:
#
#     __init__():  How to initialize the layer with parameters
#     draw_on():   How do draw the layer on a Drawing
#
# First, declare the layer class name. Include (Layer) to indicate that your
# class is a Layer.
class MyLayer (Layer):
    """Overlapping semitransparent rectangles.
    (Modify this documentation string to describe what's in your layer)"""

    # Here's the class initialization function, __init__. Define here any
    # parameters that might be used to configure your layer's behavior or
    # appearance in some way (along with default values, if you like):

    def __init__(self, fill_color='blue', stroke_color='black'):
        """Draw stroked shapes using the given colors."""
        # Initialize the base Layer class
        Layer.__init__(self)
        # Store the given fill and stroke color
        self.fill_color = fill_color
        self.stroke_color = stroke_color

    # The draw_on() function is responsible for rendering the contents of the
    # layer onto a Drawing.
    def draw_on(self, drawing, frame):
        """Draw MyLayer contents onto the given drawing, at the given frame
        number."""

        # Make sure the drawing is really a Drawing
        assert isinstance(drawing, Drawing)

        # Save context. This isolates the upcoming effects or style changes
        # from any surrounding layers in the Drawing.
        drawing.push()

        # Draw the layer. You can use pretty much any Drawing commands you want
        # here; the world is your oyster! Let's start by using the user-set
        # variables from __init__:
        drawing.fill(self.fill_color)
        drawing.stroke(self.stroke_color)

        # Now, draw something, say, a couple of semitransparent rectangles
        drawing.fill_opacity(0.6)
        drawing.rectangle((0, 0), (50, 20))
        drawing.rectangle((15, 12), (60, 40))

        # Restore context
        drawing.pop()

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
    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.comment("Background Layer")
        drawing.push()
        self.draw_effects(drawing, frame)
        # Fill drawing with an image
        if self.filename is not '':
            drawing.image('over', (0, 0), drawing.size, self.filename)
        # Fill drawing with a solid color
        elif self.color:
            drawing.fill(self.color)
            drawing.rectangle((0, 0), drawing.size)
        drawing.pop()


class Image (Layer):
    """A rectangular image, scaled to the given size."""
    def __init__(self, filename, (width, height)):
        Layer.__init__(self)
        self.size = (width, height)
        # Remember original image filename
        self.original_filename = filename
        # Prescale image file
        self.prescaled_filename = self._prescale(filename)

    def __del__(self):
        """Clean up temporary files."""
        os.remove(self.prescaled_filename)

    def _prescale(self, filename):
        """Convert and rescale the image to the target size, to save time in
        compositing."""
        dir, base = os.path.split(filename)
        if dir is not '':
            scaled_filename = "%s/tmp_%s" % (dir, base)
        else:
            scaled_filename = "tmp_%s" % base
        cmd = 'convert -size %sx%s' % self.size
        cmd += ' %s' % filename
        cmd += ' -resize %sx%s' % self.size
        cmd += ' %s' % scaled_filename
        print "Prescaling Image: '%s' to temporary file: '%s'" % \
              (filename, scaled_filename)
        print commands.getoutput(cmd)
        return scaled_filename

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.comment("Image Layer")
        drawing.push()
        self.draw_effects(drawing, frame)
        drawing.image('over', (0, 0), self.size, self.prescaled_filename)
        drawing.pop()


class VideoClip (Layer):
    """A rectangular video clip, scaled to the given size."""
    def __init__(self, filename, (width, height)):
        Layer.__init__(self)
        self.filename = filename
        self.mediafile = MediaFile(filename)
        self.size = (width, height)
        # List of filenames of individual frames
        self.frames = []
        self.rip_frames(1, 120)

    def rip_frames(self, start, end):
        """Rip frames from the video file, from start to end frames."""
        print "VideoClip: Ripping frames %s to %s" % (start, end)
        self.mediafile.rip_frames([start, end])
        self.frames.extend(self.mediafile.framefiles)

    def draw_on(self, drawing, frame):
        """Draw ripped video frames to the given drawing. For now, it's
        necessary to call rip_frames() before calling this function.
        Video is looped.
        """
        assert isinstance(drawing, Drawing)
        if len(self.frames) == 0:
            print "VideoClip error: need to call rip_frames() before drawing."
            sys.exit(1)
        drawing.comment("VideoClip Layer")
        drawing.push()
        self.draw_effects(drawing, frame)
        # Loop frames (modular arithmetic)
        if frame > len(self.frames):
            frame = frame % len(self.frames)
        filename = self.frames[frame]
        drawing.image('over', (0, 0), self.size, filename)
        drawing.pop()


class Text (Layer):
    """A simple text string, with size, color and font."""
    def __init__(self, text, color='white', fontsize=20, \
                 font='Helvetica'):
        Layer.__init__(self)
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.font = font
    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.comment("Text Layer")
        drawing.push()
        drawing.fill(self.color)
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        self.draw_effects(drawing, frame)
        drawing.text((0, 0), self.text)
        drawing.pop()



class Label (Text):
    """A text string with a rectangular background."""
    def __init__(self, text, color='black', bgcolor='grey',
                 fontsize=20, font='NimbusSans'):
        Text.__init__(self, text, color, fontsize, font)
        self.bgcolor = bgcolor
    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)

        drawing.comment("Label Layer")
        # Save context
        drawing.push()

        # Calculate rectangle dimensions from text size/length
        width = self.fontsize * len(self.text) / 2
        height = self.fontsize
        # Padding to use around text
        pad = self.fontsize / 3
        # Calculate start and end points of background rectangle
        start = (-pad, -height - pad)
        end = (width + pad, pad)

        # Draw a stroked round rectangle
        drawing.push()
        drawing.stroke(self.color)
        drawing.fill(self.bgcolor)
        drawing.roundrectangle(start, end, (pad, pad))
        drawing.pop()

        # Call base Text class to draw the text
        Text.draw_on(self, drawing, frame)

        # Restore context
        drawing.pop()
        

class TextBox (Text):
    """A text box containing paragraphs, and support for simple formatting
    markup in HTML-like syntax.
    
    Formatting elements are <p>...</p>, <b>...</b>, and <i>...</i>.
    """
    def __init__(self, text, (width, height), color='white',
                 fontsize=20, font='Times'):
        """Formatted text contained in a box of the given size."""
        Text.__init__(self, text, color, fontsize, font)
        self.size = (width, height)
        # TODO: Determine max number of characters that will fit in given
        # width, and break marked-up text into lines (breaking at word
        # boundaries)

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.comment("TextBox Layer")
        drawing.push()

        # TODO: Wrap text!

        # Draw font and effects for the whole text box
        drawing.fill(self.color)
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        self.draw_effects(drawing, frame)

        # Start reading text at position 0
        # TODO: For text-wrapping purposes, cursor will be the position on
        # the current line
        cursor = 0
        # Start drawing in upper left-hand corner
        draw_loc = (0, 0)
        
        finished = False
        while not finished:
            # Find the next tag after cursor
            tag_start = self.text.find('<', cursor)
            
            # If no tag was found, draw remaining text and finish up
            if tag_start == -1:
                drawing.text(draw_loc, self.text[cursor:])
                finished = True

            # Otherwise, parse and render tags
            else:
                # Draw text from cursor up to (but not including) the '<'
                drawing.text(draw_loc, self.text[cursor:tag_start])
                chars_written = tag_start - cursor
    
                # Adjust draw_loc
                (x, y) = draw_loc
                # Badly-hacked horizontal positioning
                x += int(self.fontsize / 2 * chars_written)
                # Line-height is double fontsize (Disabled for now)
                # y = y + 2 * self.fontsize
                draw_loc = (x, y)

                # Get the full tag <..>
                tag_end = self.text.find('>', tag_start) + 1
                tag = self.text[tag_start:tag_end]
                # Position the cursor after the tag
                cursor = tag_end
    
                # For any opening tag, start a new drawing context
                if not tag.startswith('</'):
                    drawing.push()
    
                # Paragraph
                if tag == '<p>':
                    # TODO
                    pass
                # Bold text
                elif tag == '<b>':
                    drawing.font_weight('bold')
                # Italic text
                elif tag == '<i>':
                    drawing.font_style('italic')
                # For any closing tag, close the current drawing context
                if tag.startswith('</'):
                    drawing.pop()
        drawing.pop()

    

class Thumb (Layer):
    """A thumbnail image or video."""
    def __init__(self, filename, (width, height), title=''):
        Layer.__init__(self)
        self.filename = filename
        self.size = (width, height)
        self.title = title or os.path.basename(filename)
        # Determine whether file is a video or image, and create the
        # appropriate sublayer
        filetype = get_file_type(filename)
        if filetype == 'video':
            self.add_sublayer(VideoClip(filename, self.size))
        elif filetype == 'image':
            self.add_sublayer(Image(filename, self.size))
        self.add_sublayer(Label(self.title), (0, 0))

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        self.draw_effects(drawing, frame)
        self.draw_sublayers(drawing, frame)


class ThumbGrid (Layer):
    """A rectangular array of thumbnail images or videos."""
    def __init__(self, files, (width, height)=(600, 400),
                 (columns, rows)=(0, 0), aspect=(4,3)):
        """Create a grid of thumbnail images or videos from a list of files,
        fitting in a space no larger than the given size, with the given number
        of columns and rows. Use 0 to auto-layout columns or rows, or both 
        (default).
        """
        assert files != []
        Layer.__init__(self)
        self.size = (width, height)
        print "Creating a thumbnail grid of %s media files" % len(files)
        # Auto-dimension (using desired rows/columns, if given)
        self.columns, self.rows = \
            self._fit_items(len(files), columns, rows)
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
        for file, position in zip(files, positions):
            title = os.path.basename(file)
            self.add_sublayer(Thumb(file, thumbsize), position)

    def _fit_items(self, num_items, columns, rows):
        # Both fixed, nothing to calculate
        if columns > 0 and rows > 0:
            # Make sure num_items will fit (columns, rows)
            if num_items < columns * rows:
                return (columns, rows)
            # Not enough room; auto-dimension both
            else:
                print "ThumbGrid: Can't fit %s items in (%s, %s) grid;" % \
                      (num_items, columns, rows)
                print "doing auto-dimensioning instead."
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

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.comment("ThumbGrid Layer")
        drawing.push()
        self.draw_effects(drawing, frame)
        self.draw_sublayers(drawing, frame)
        drawing.pop()


class SafeArea (Layer):
    """Render a safe area box at a given percentage.
    """
    def __init__(self, percent, color):
        self.percent = percent
        self.color = color
        
    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        # Calculate rectangle dimensions
        scale = float(self.percent) / 100.0
        width, height = drawing.size
        topleft = ((1.0 - scale) * width / 2,
                  (1.0 - scale) * height / 2)
        drawing.comment("SafeArea Layer")
        # Save context
        drawing.push()
        drawing.translate(topleft)
        # Safe area box
        drawing.fill(None)
        drawing.stroke(self.color)
        drawing.stroke_width(3)
        drawing.rectangle((0, 0), (width * scale, height * scale))
        # Label
        drawing.fill(self.color)
        drawing.stroke(None)
        drawing.font_size(20)
        drawing.text((10, 20), "%s%%" % self.percent)
        # Restore context
        drawing.pop()


class InterpolationGraph (Layer):
    # TODO: Support graphing of tuple data
    """A graph of an interpolation curve, defined by a list of Keyframes and
    an interpolation method."""
    def __init__(self, keyframes, size=(240, 80), method='linear'):
        """Create an interpolation graph of the given keyframes, at the given
        size, using the given interpolation method."""
        self.keyframes = keyframes
        self.size = size
        self.method = method
        # Interpolate keyframes
        self.tween = Tween(keyframes, method)

    def draw_on(self, drawing, frame):
        """Draw the interpolation graph, including frame/value axes,
        keyframes, and the interpolation curve."""
        assert isinstance(drawing, Drawing)
        data = self.tween.data
        # Calculate maximum extents of the graph
        width, height = self.size
        x_scale = float(width) / len(data)
        y_scale = float(height) / max(data)

        drawing.comment("InterpolationGraph Layer")

        # Save context
        drawing.push()
        drawing.fill(None)

        # Draw axes
        drawing.comment("Axes of graph")
        drawing.push()
        drawing.stroke('grey')
        drawing.stroke_width(3)
        drawing.polyline([(0, 0), (0, height), (width, height)])
        drawing.pop()

        # Create a list of (x, y) points to be graphed
        curve = []
        x = 1
        while x <= len(self.tween.data):
            # y increases downwards; subtract from height to give a standard
            # Cartesian-oriented graph (so y increases upwards)
            point = (int(x * x_scale), int(height - data[x-1] * y_scale))
            curve.append(point)
            x += 1
        drawing.comment("Interpolation curve")
        drawing.push()
        # Draw the curve
        drawing.stroke('blue')
        drawing.stroke_width(2)
        drawing.polyline(curve)
        drawing.pop()

        # Draw Keyframes as dotted vertical lines
        drawing.comment("Keyframes and labels")
        drawing.push()
        drawing.stroke_dasharray([4, 4])
        # Vertical dotted lines
        drawing.fill(None)
        drawing.stroke('red')
        drawing.stroke_width(2)
        for key in self.keyframes:
            x = int(key.frame * x_scale)
            drawing.line((x, 0), (x, height))
        # Draw Keyframe labels
        drawing.stroke(None)
        drawing.fill('white')
        for key in self.keyframes:
            x = int(key.frame * x_scale)
            y = int(height - key.data * y_scale - 3)
            drawing.text((x, y), "(%s,%s)" % (key.frame, key.data))
        drawing.pop()

        # Draw a yellow dot for current frame
        drawing.comment("Current frame marker")
        drawing.push()
        drawing.stroke(None)
        drawing.fill('yellow')
        pos = (frame * x_scale, height - data[frame-1] * y_scale)
        drawing.circle_rad(pos, 2)
        drawing.pop()

        # Restore context
        drawing.pop()

# ============================================================================
# Demo
# ============================================================================
if __name__ == '__main__':
    images = None
    # Get arguments, if any
    if len(sys.argv) > 1:
        # Use all args as image filenames to ThumbGrid
        images = sys.argv[1:]

    # A Drawing to render Layer demos to
    drawing = Drawing()
    
    # Draw a background layer
    bgd = Background(color='#7080A0')
    bgd.draw_on(drawing, 1)

    # Draw a text layer
    drawing.push()
    drawing.translate((80, 60))
    text = Text("Jackdaws love my big sphinx of quartz")
    text.draw_on(drawing, 1)
    drawing.pop()

    # Draw a template layer (overlapping semitransparent rectangles)
    template = MyLayer('white', 'darkblue')
    # Scale and translate the layer before drawing it
    drawing.push()
    drawing.translate((50, 100))
    drawing.scale((3.0, 3.0))
    template.draw_on(drawing, 1)
    drawing.pop()

    # Draw a label (experimental)
    drawing.push()
    drawing.translate((300, 200))
    label = Label("tovid loves Linux")
    label.draw_on(drawing, 1)
    drawing.pop()

    # Draw a text box (experimental)
    drawing.push()
    drawing.translate((60, 300))
    textbox = TextBox("Some <b>bold</b> and <i>italic</i> text", (200, 200))
    textbox.draw_on(drawing, 1)
    drawing.pop()

    # Draw a safe area test (experimental)
    safe = SafeArea(93, 'yellow')
    safe.draw_on(drawing, 1)

    # Draw a thumbnail grid (if images were provided)
    if images:
        drawing.push()
        drawing.translate((350, 200))
        thumbs = ThumbGrid(images, (320, 250))
        thumbs.draw_on(drawing, 1)
        drawing.pop()

    # Draw an interpolation graph (experimental)
    drawing.comment("Interpolation graph")
    drawing.push()
    drawing.translate((60, 340))
    # Some random keyframes to graph
    keys = [Keyframe(1, 25), Keyframe(10, 5), Keyframe(30, 35),
            Keyframe(40, 35), Keyframe(45, 20), Keyframe(60, 40)]
    interp = InterpolationGraph(keys, method="cosine")
    interp.draw_on(drawing, 25)
    drawing.pop()

    print drawing.code()
    drawing.render()

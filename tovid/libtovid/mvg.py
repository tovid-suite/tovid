#! /usr/bin/env python
# mvg.py

"""A Python interface for reading/writing Magick Vector Graphics (MVG)[1].

Run this script standalone for a demonstration:

    $ python libtovid/mvg.py

To build your own MVG vector image using this module, fire up your Python
interpreter:

    $ python

And do something like this:

    >>> from libtovid.mvg import Drawing
    >>> pic = Drawing(800, 600)

This creates an image (pic) at 800x600 display resolution. pic has a wealth
of draw functions, as well as a rough-and-ready editor interface (shown later).

This thing is pretty low-level for the time being; MVG is, as one user has
described it[2], the "assembly language" of vector graphics. But basically,
you can just call function names that resemble their MVG-syntax counterparts.
Now that you have an MVG object (pic), you can draw on it:

    >>> pic.fill('blue')
    >>> pic.rectangle((0, 0), (800, 600))
    >>> pic.fill('white')
    >>> pic.rectangle((320, 240), (520, 400))

If you want to preview what you have so far, call render():

    >>> pic.render()

This calls convert with a -draw command and -composite miff:- | display to
show the image. Whatever--it lets you see what the image looks like so far.
Press 'q' or ESC to close the preview window.

You can show the current MVG text contents (line-by-line) with:

    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: fill "white"
    4: rectangle 320,240 520,400
    >

This is where the "editor" interface comes in. Each line is numbered, and the
current "cursor" position is shown by a '>' character. You can move the cursor
with goto(line_number):

    >>> pic.goto(3)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    > 3: fill "white"
    4: rectangle 320,240 520,400

The cursor indicates where new commands are inserted; for instance:

    >>> pic.stroke('black')
    >>> pic.stroke_width(2)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: stroke "black"
    4: stroke-width 2
    > 5: fill "white"
    6: rectangle 320,240 520,400

Notice that the two new commands were inserted (in order) at the cursor
position. To resume appending at the end, call goto_end():

    >>> pic.goto_end()
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: stroke "black"
    4: stroke-width 2
    5: fill "white"
    6: rectangle 320,240 520,400
    >

You can remove a given line number (or range of lines) with:

    >>> pic.remove(3, 4)
    >>> pic.code()
    1: fill "blue"
    2: rectangle 0,0 800,600
    3: fill "white"
    4: rectangle 320,240 520,400
    >

You can undo all insert, append, or remove operations with:

    >>> pic.undo(2)


You can keep drawing on the image, and call render() whenever you want to
preview.

Oh, by the way--this is almost totally untested, so please report bugs if/when
you find them.

References:
[1] http://www.imagemagick.org/script/magick-vector-graphics.php
[2] http://studio.imagemagick.org/pipermail/magick-developers/2002-February/000156.html


MVG examples:
-------------

Radial gradient example
(From http://www.linux-nantes.fr.eu.org/~fmonnier/OCaml/MVG/u.mvg.html):

    push graphic-context
      encoding "UTF-8"
      viewbox 0 0 260 180
      affine 1 0 0 1 0 0
      push defs
        push gradient 'Gradient_B' radial 130,90 130,90 125
          gradient-units 'userSpaceOnUse'
          stop-color '#4488ff' 0.2
          stop-color '#ddaa44' 0.7
          stop-color '#ee1122' 1
        pop gradient
      pop defs
      push graphic-context
        fill 'url(#Gradient_B)'
        rectangle 0,0 260,180
      pop graphic-context
    pop graphic-context

Pie chart example: http://www.imagemagick.org/source/piechart.mvg

"""
import os
import sys
import commands
import Tkinter

class Drawing:
    """A Magick Vector Graphics (MVG) image with load/save, insert/append,
    and low-level drawing functions based on the MVG syntax.

    Drawing functions are mostly identical to their MVG counterparts, e.g.
    these two are equivalent:

        rectangle 100,100 200,200       # MVG command
        rectangle((100,100), (200,200)) # Drawing function

    The only exception is MVG commands that are hyphenated. For these, use an
    underscore instead:

        font-family "Serif"      # MVG command
        font_family("Serif")     # Drawing function

    """
    def __init__(self, size=(720, 480), filename='/tmp/temp.mvg'):
        self.clear()
        self.size = size
        self.filename = filename

    def clear(self):
        """Clear the current contents and position the cursor at line 1."""
        self.data = [''] # Line 0 is null
        self.cursor = 1
        self.history = []
        self.indent = 0

    #
    # MVG drawing commands
    #

    def affine(self, scale_x, rot_x, rot_y, scale_y, translate_x, translate_y):
        """Define a 3x3 transformation matrix:
            
            [ scale_x  rot_y    translate_x ]
            [ rot_x    scale_y  translate_y ]
            [ 0        0        1           ]

        This is scaling, rotation, and translation in a single matrix,
        so it's a compact way to represent any transformation.
        See [http://www.w3.org/TR/SVG11/coords.html] for more on
        these matrices and how to use them."""
        self.insert('affine %s %s %s %s %s %s' % \
            (scale_x, rot_x, rot_y, scale_y, translate_x, translate_y))

    def arc(self, (x0, y0), (x1, y1), (start_degrees, end_degrees)):
        """Draw an arc from (x0, y0) to (x1, y1), with the given start and
        end degrees."""
        self.insert('arc %s,%s %s,%s %s,%s' % \
                    (x0, y0, x1, y1, start_degrees, end_degrees))

    def bezier(self, point_list):
        # point_list = [(x0, y0), (x1, y1), ... (xn, yn)]
        command = 'bezier'
        for x, y in point_list:
            command += ' %s,%s' % (x, y)
        self.insert(command)

    def circle(self, (center_x, center_y), (perimeter_x, perimeter_y)):
        """Draw a circle defined by center and perimeter points."""
        self.insert('circle %s,%s %s,%s' % \
                    (center_x, center_y, perimeter_x, perimeter_y))

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
        self.insert('ellipse %s,%s %s,%s %s,%s' % \
                (center_x, center_y, radius_x, radius_y, arc_start, arc_stop))
        
    def fill(self, color):
        """Set the current fill color, or 'none' for transparent fill.
        MVG/ImageMagick color usage:
        http://www.imagemagick.org/script/color.php"""
        self.insert('fill "%s"' % color)
    def fill_rgb(self, (r, g, b)):
        """Set the fill color to an RGB value."""
        self.fill('rgb(%s, %s, %s)' % (r, g, b))
    
    def fill_opacity(self, opacity):
        """Define fill opacity, from fully transparent (0.0) to fully
        opaque (1.0)."""
        self.insert('fill-opacity %s' % opacity)
    
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
        """
        self.insert('gravity %s' % direction)
    
    def image(self, compose, (x, y), (width, height), filename):
        """Draw an image at (x, y), scaled to the given width and height.
        compose may be:
            Add, Minus, Plus, Multiply, Difference, Subtract,
            Copy, CopyRed, CopyGreen, CopyBlue, CopyOpacity,
            Atop, Bumpmap, Clear, In, Out, Over, Xor
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

    def opacity(self, opacity):
        self.insert('opacity %s' % opacity)

    def path(self, path_data):
        """Draw a path. path_data is a list of instructions and coordinates,
        e.g. ['M', (100,100), 'L' (200,200), ...]
        Instructions are M (moveto), L (lineto), A (arc), Z (close path)
        For more on using paths (and a complete list of commands), see:
        http://www.cit.gu.edu.au/~anthony/graphics/imagick6/draw/#paths
        http://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
        """
        command = 'path'
        for token in path_data:
            command += ' %s,%s' % (x, y)
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
        """Rotate by the given number of degrees."""
        self.insert('rotate %s' % degrees)

    def roundrectangle(self, (x0, y0), (x1, y1), (width, height)):
        """Draw a rounded rectangle from (x0, y0) to (x1, y1), with
        the given outer width and height."""
        self.insert('roundrectangle %s,%s %s,%s %s,%s' % \
                (x0, y0, x1, y1, width, height))

    def scale(self, (x, y)):
        """Set scaling to (x, y)."""
        self.insert('scale %s,%s' % (x, y))

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
        self.insert('stroke-linecap %s' % cap_type)

    def stroke_linejoin(self, join_type):
        """Set the type of line-joining to do. join_type may be 'bevel',
        'miter', or 'round'."""
        self.insert('stroke-linejoin %s' % join_type)

    def stroke_opacity(self, opacity):
        """Set the stroke opacity. opacity may be decimal (0.0-1.0)
        or percentage (0-100)%."""
        self.insert('stroke-opacity %s' % opacity)

    def stroke_width(self, width):
        """Set the current stroke width in pixels."""
        # (Pixels or points?)
        self.insert('stroke-width %s' % width)
    
    def text(self, (x, y), text_string):
        """Draw the given text string at (x, y)."""
        # TODO: Escape special characters in text string
        self.insert('text %s,%s "%s"' % (x, y, text_string))
    
    def text_antialias(self, do_antialiasing):
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

    def code(self, editing=False):
        """Return complete MVG text for the Drawing. If editing is True, include
        line numbers and a > at the cursor position (useful for interactive
        editing). Otherwise, just return raw text with line breaks."""
        code = ''
        if editing:
            line = 1
            while line < len(self.data):
                # Put a > at the cursor position
                if line == self.cursor:
                    code += "> "
                code +=  "%s: %s\n" % (line, self.data[line])
                line += 1
            # If cursor is after the last line
            if line == self.cursor:
                code += ">"
            print code
        else:
            return '\n'.join(self.data)

    def render(self):
        """Render the .mvg with ImageMagick, and display it."""
        self.save(self.filename)
        cmd = "convert -size %sx%s " % self.size
        cmd += " xc:none "
        cmd += " -draw @%s " % self.filename
        cmd += " -composite miff:- | display"
        print "Creating preview rendering."
        print cmd
        print "Press 'q' or ESC in the image window to close the image."
        print commands.getoutput(cmd)

    def tk_render(self):
        """Like render(), using tkinter to display the image."""
        root = Tkinter.Tk()
        ppmfile = '/tmp/mvg_render.ppm'
        self.save_image(ppmfile)
        img = Tkinter.PhotoImage(file=ppmfile)
        lbl = Tkinter.Label(root, image=img)
        lbl.pack()
        Tkinter.mainloop()

    def save_image(self, img_filename):
        """Render the drawing to a .jpg, .png or other image."""
        self.save(self.filename)
        cmd = "convert -size %sx%s " % self.size
        cmd += "%s %s" % (self.filename, img_filename)
        print "Rendering drawing to: %s" % img_filename
        print commands.getoutput(cmd)

    def goto(self, line_num):
        """Move the insertion cursor to the start of the given line."""
        if line_num <= 0 or line_num > (len(self.data) + 1):
            print "Can't goto line %s" % line_num
            sys.exit(1)
        else:
            self.cursor = line_num

    def goto_end(self):
        """Move the insertion cursor to the last line in the file."""
        self.goto(len(self.data))

    def append(self, mvg_string):
        """Append the given MVG string as the last line, and position the
        cursor after the last line."""
        self.goto_end()
        self.insert(mvg_string)

    def insert(self, mvg_string):
        """Insert the given MVG string before the current line, and position
        the cursor after the inserted line."""
        self.history.append(['insert', self.cursor])
        self.data.insert(self.cursor, '  ' * self.indent + mvg_string)
        self.cursor += 1

    def remove(self, from_line, to_line=None):
        """Remove the given line, or range of lines, and position the cursor
        where the removed lines were."""
        # Remove a single line
        if not to_line:
            to_line = from_line
        cur_line = from_line
        while cur_line <= to_line:
            self.history.append(['remove', cur_line, self.data.pop(cur_line)])
            # Data was popped, so to_line decrements
            to_line -= 1
        self.cursor = from_line

    def extend(self, drawing):
        """Extend self to include all data from the given MVG object, and
        position the cursor at the end."""
        self.data.extend(drawing.data[1:])
        self.goto_end()

    def undo(self, steps=1):
        """Undo the given number of operations. Leave cursor at end."""
        step = 0
        while step < steps and len(self.history) > 0:
            action = self.history.pop()
            cmd = action[0]
            line_num = action[1]
            # Undo insertion
            if cmd == 'insert':
                print "Undoing insertion at line %s" % line_num
                self.data.pop(action[1])
            # Undo removal
            elif cmd == 'remove':
                print "Undoing removal at line %s" % line_num
                self.data.insert(line_num, action[2])
            step += 1
        if step < steps:
            print "No more to undo."
        self.goto_end()



# Demo
if __name__ == '__main__':
    pic = Drawing((720, 480), 'drawing_test.mvg')

    # Start of MVG file
    pic.push('graphic-context')
    pic.viewbox((0, 0), (720, 480))

    pic.push
    # Add a background fill
    pic.fill('darkblue')
    pic.rectangle((0, 0), (720, 480))

    # Some decorative circles
    pic.fill('blue')
    pic.circle((280, 350), (380, 450))
    # Stroke only this circle, not any later objects
    pic.push('graphic-context')
    pic.stroke('black')
    pic.stroke_width(12)
    pic.fill('orange')
    pic.circle((670, 100), (450, 100))
    pic.pop('graphic-context')

    # White text in a range of sizes
    pic.fill('white')
    for size in [12,16,20,24,28,32]:
        ypos = 100 + size * size / 5
        pic.font('Helvetica')
        pic.font_size(size)
        pic.text((100, ypos), "%s pt: The quick brown fox" % size)

    # Close out the MVG file
    pic.pop('graphic-context')

    # Display the MVG text, then show the generated image
    pic.code(editing=True)
    pic.render()

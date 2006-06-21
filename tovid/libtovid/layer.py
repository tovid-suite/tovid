#! /usr/bin/env python
# layer.py

__all__ = ['Layer', 'Background', 'Text', 'Thumb', 'ThumbGrid']

from libtovid.mvg import Drawing
from libtovid.effect import Effect

class Layer:
    """A visual element that may be composited onto a Flipbook."""
    def __init__(self):
        self.effects = []
    def draw_on(self, drawing, frame):
        """Draw the layer onto the given Drawing. Override this function in
        derived layers."""
        pass
    def draw_effects(self, drawing, frame):
        """Draw all effects onto the given Drawing for the given frame."""
        for effect in self.effects:
            effect.draw_on(drawing, frame)


class Background (Layer):
    """A background that fills the frame with a solid color, or an image."""
    def __init__(self, (width, height), color='black', filename=''):
        Layer.__init__(self)
        self.size = (width, height)
        self.color = color
        self.filename = filename
    def draw_on(self, drawing, frame):
        drawing.push('graphic-context')
        self.draw_effects(drawing, frame)
        if self.filename:
            # TODO
            pass
        elif self.color:
            drawing.fill(self.color)
            drawing.rectangle((0,0), self.size)
        drawing.pop('graphic-context')


class Text (Layer):
    """A text string, with position, size, color and font."""
    def __init__(self, text, (x, y), color='white', fontsize='20', \
                 font='Helvetica'):
        Layer.__init__(self)
        self.text = text
        self.position = (x, y)
        self.color = color
        self.fontsize = fontsize
        self.font = font
    def draw_on(self, drawing, frame):
        drawing.push('graphic-context')
        self.draw_effects(drawing, frame)
        drawing.fill(self.color)
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        drawing.text(self.position, self.text)
        drawing.pop('graphic-context')


class Thumb (Layer):
    """A thumbnail image, with size and positioning."""
    def __init__(self, filename, (x, y), (width, height)):
        Layer.__init__(self)
        self.filename = filename
        self.position = (x, y)
        self.size = (width, height)
    def draw_on(self, drawing, frame):
        drawing.push('graphic-context')
        self.draw_effects(drawing, frame)
        drawing.image('over', self.position, self.size, self.filename)
        drawing.pop('graphic-context')


class ThumbGrid (Layer):
    """A rectangular array of thumbnail images or videos."""
    def __init__(self, file_list, (width, height), (columns, rows)=(0, 0)):
        """Create a grid of images from file_list, fitting with a space no
        larger than (width, height), with the given number of columns and rows
        Use 0 to auto-layout columns or rows, or both (default)."""
        Layer.__init__(self)
        self.totalsize = (width, height)
        self.file_list = file_list
        self.columns, self.rows = \
            self._auto_dimension(len(file_list), columns, rows)
        # Now we know how many columns/rows; how big are the thumbnails?
        thumbwidth = (width - self.columns * 16) / self.columns
        thumbheight = (height - self.rows * 16) / self.rows
        self.thumbsize = (thumbwidth, thumbheight)

    def _auto_dimension(num_items, columns, rows):
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
            root = int(floor(sqrt(num_items)))
            return ((1 + num_items / root), root)
        # Rows fixed; use enough columns to fit num_items
        if columns == 0 and rows > 0:
            return ((1 + num_items / rows), rows)
        # Columns fixed; use enough rows to fit num_items
        if rows == 0 and columns > 0:
            return (columns, (1 + num_items / columns))
    def draw_on(self, drawing, frame):
        drawing.push('graphic-context')
        self.draw_effects(drawing, frame)
        for file in self.file_list:
            drawing.image('Over', self.position, self.size, file)
        drawing.pop('graphic-context')

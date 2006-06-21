#! /usr/bin/env python
# layer.py

__all__ = ['Layer', 'Background', 'Text', 'Thumb', 'ThumbGrid']

from libtovid.mvg import Drawing

class Layer:
    """A visual element that may be composited onto a Flipbook."""
    def __init__(self):
        pass
    def get_mvg(self):
        """Override this in subclasses to do the actual drawing."""
        return Drawing()


class Background (Layer):
    """An overlay that fills the available canvas space with a solid color,
    or with an image file."""
    def __init__(self, (width, height), color='black', filename=''):
        self.size = (width, height)
        self.color = color
        self.filename = filename
    def get_mvg(self):
        mvg = Drawing(self.size)
        if self.filename:
            # TODO
            pass
        elif self.color:
            mvg.fill(self.color)
            mvg.rectangle((0,0), self.size)
        return mvg


class Text (Layer):
    """A text string, with position, size, color and font."""
    def __init__(self, (x, y), text, color='white', fontsize='20', \
                 font='Helvetica'):
        self.position = (x, y)
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.font = font
    def get_mvg(self):
        mvg = Drawing()
        mvg.fill(self.color)
        mvg.font(self.font)
        mvg.font_size(self.fontsize)
        mvg.text(self.position, self.text)
        return mvg


class Thumb (Layer):
    """A thumbnail image, with size and positioning."""
    def __init__(self, (x, y), (width, height), filename):
        self.position = (x, y)
        self.size = (width, height)
        self.filename = filename
    def get_mvg(self):
        mvg = Drawing()
        mvg.image('over', self.position, self.size, self.filename)
        return mvg


class ThumbGrid (Layer):
    """A rectangular array of thumbnail images or videos."""
    def __init__(self, file_list, (width, height), (columns, rows)=(0, 0)):
        """Create a grid of images from file_list, fitting with a space no
        larger than (width, height), with the given number of columns and rows
        Use 0 to auto-layout columns or rows, or both (default)."""
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
    def get_mvg(self):
        mvg = Drawing()
        for file in self.file_list:
            mvg.image('Over', )
        return mvg
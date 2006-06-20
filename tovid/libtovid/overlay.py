#! /usr/bin/env python
# overlay.py

from libtovid.mvg import Drawing

class Overlay:
    """A visual element that may be composited onto a video canvas. May be
    semi-transparent."""
    def __init__(self):
        pass
    def get_mvg(self, frame):
        pass

class Background (Overlay):
    """An overlay that fills the available canvas space with a solid color,
    or with an image file."""
    def __init__(self, (width, height), color='black', filename=''):
        self.size = (width, height)
        self.color = color
        self.filename = filename
    def get_mvg(self, frame):
        Overlay.get_mvg(self, frame)
        mvg = Drawing(self.size)
        if self.filename:
            # TODO
            pass
        elif self.color:
            mvg.fill(self.color)
            mvg.rectangle((0,0), self.size)
        return mvg

class Text (Overlay):
    """A text string, with position, size, color and font."""
    def __init__(self, (x, y), text, color='white', fontsize='20', \
                 font='Helvetica'):
        self.position = (x, y)
        self.text = text
        self.color = color
        self.fontsize = fontsize
        self.font = font
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.fill(self.color)
        mvg.font(self.font)
        mvg.font_size(self.fontsize)
        mvg.text(self.position, self.text)
        return mvg


class Thumbnail (Overlay):
    """A thumbnail image, with size and positioning."""
    def __init__(self, (x, y), (width, height), filename):
        self.position = (x, y)
        self.size = (width, height)
        self.filename = filename
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.image('over', self.position, self.size, self.filename)
        return mvg


class ThumbGrid (Overlay):
    """A rectangular array of thumbnail images or videos."""
    def __init__(self, file_list, columns=0, rows=0):
        """Create a grid of images from file_list, with the given number of
        columns and rows (use 0 to auto-layout either columns or rows, or
        both."""
        self.columns, self.rows = \
            self._auto_dimension(len(file_list), columns, rows)
        # Now we know how many columns/rows; how big are the thumbnails?

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

#! /usr/bin/env python
# layer.py

__all__ = ['Layer', 'Background', 'Text', 'VideoClip', 'Thumb', 'ThumbGrid']

import os
import sys
import glob
from libtovid.mvg import Drawing
from libtovid.effect import Effect
from libtovid.VideoUtils import video_to_images

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
        drawing.push()
        self.draw_effects(drawing, frame)
        if self.filename is not '':
            drawing.image('over', (0, 0), self.size, self.filename)
        elif self.color:
            drawing.fill(self.color)
            drawing.rectangle((0, 0), self.size)
        drawing.pop()

class VideoClip (Layer):
    """A rectangular video clip with size and positioning."""
    def __init__(self, filename, (x, y), (width, height)):
        Layer.__init__(self)
        self.filename = filename
        self.position = (x, y)
        self.size = (width, height)
        # List of filenames of individual frames
        self.frames = []

    def rip_frames(self, start, end):
        """Rip frames from the video file, from start to end (in seconds)."""
        self.framedir = video_to_images(self.filename, start, end, self.size)
        print "Frames in: %s" % self.framedir
        # Get frame filenames
        for frame_name in glob.glob('%s/*.jpg' % self.framedir):
            self.frames.append(frame_name)
        print "Frame files:"
        print self.frames

    def draw_on(self, drawing, frame):
        drawing.push()
        self.draw_effects(drawing, frame)
        # Loop frames (modular arithmetic)
        if frame > len(self.frames):
            frame = frame % len(self.frames)
        filename = self.frames[frame]
        drawing.image('over', self.position, self.size, filename)
        drawing.pop()


class Text (Layer):
    """A simple text string, with position, size, color and font."""
    def __init__(self, text, (x, y), color='white', fontsize=20, \
                 font='Helvetica'):
        Layer.__init__(self)
        self.text = text
        self.position = (x, y)
        self.color = color
        self.fontsize = fontsize
        self.font = font
    def draw_on(self, drawing, frame):
        drawing.push()
        drawing.fill(self.color)
        drawing.font(self.font)
        drawing.font_size(self.fontsize)
        self.draw_effects(drawing, frame)
        drawing.text(self.position, self.text)
        drawing.pop()


class TextBox (Text):
    """A text box containing paragraphs, and support for simple formatting
    markup in HTML-like syntax.
    
    Formatting elements are <p>...</p>, <b>...</b>, and <i>...</i>.
    """
    def __init__(self, text, (pos_x, pos_y), (width, height), color='white',
                 fontsize=20, font='Helvetica'):
        """Formatted text at the given position, contained in a box of the
        given size."""
        Text.__init__(self, text, (pos_x, pos_y), color, fontsize, font)
        self.size = (width, height)
        # TODO: Determine max number of characters that will fit in given
        # width, and break marked-up text into lines (breaking at word
        # boundaries)

    def draw_on(self, drawing, frame):
        assert(isinstance(drawing, Drawing))
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
        draw_loc = self.position
        
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
    
                print "TextBox: tag is '%s'" % tag

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
    """A thumbnail image, with size and positioning."""
    def __init__(self, filename, (x, y), (width, height)):
        Layer.__init__(self)
        self.filename = filename
        self.position = (x, y)
        self.size = (width, height)
    def draw_on(self, drawing, frame):
        drawing.push()
        self.draw_effects(drawing, frame)
        drawing.image('over', self.position, self.size, self.filename)
        drawing.pop()


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
        drawing.push()
        self.draw_effects(drawing, frame)
        for file in self.file_list:
            drawing.image('Over', self.position, self.size, file)
        drawing.pop()


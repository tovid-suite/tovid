#! /usr/bin/env python
# animation.py

"""
Notes:

Uses a "video canvas" (a 2D canvas for each frame)
You can paint on the canvas with video objects

background
thumbnail
text
rectangle

Effects:

fade-in/out (keyframe opacity)
move (keyframe x,y coordinates)
shrink/expand (keyframe width,height)
colorfade (keyframe RGBA--generalize w/ fade-in/out?)

A canvas stores basic object-level info; MVG-level rendering does not take
place until preview() or render() is called (and then only for the necessary
frames). Think of it as "compiling" to MVG.

Effects are applied to video objects at the canvas level (since canvas is
responsible for animation, frames)

    >>> canvas = VideoCanvas(720, 480)
    >>> bgd = Background('/pub/video/test/bg.avi')
    >>> canvas.add(bgd)
    >>> title = Text((360, 100), "Quantum Leap")
    >>> canvas.add(title)
    >>> thumbs = ThumbGrid(3, 2, video_list)
    >>> 
"""

from math import floor, sqrt
from libtovid.mvg import Drawing


class Keyframe:
    """Associates a specific frame in an animation with a numeric value.
    A Keyframe is an (x, y) pair defining a "control point" on a 2D graph:
    
            100 |
                |       Keyframe(10, 50)
           data |      *
                |
              0 |__________________________
                0     10     20     30
                        frame
    
    The data can represent anything you like. For instance, opacity:
    
            100 |* Keyframe(0, 100)
                |       
     opacity(%) |
                |
              0 |____________________* Keyframe(30, 0)
                0     10     20     30
                        frame

    See the tween() function below for what you can do with these Keyframes,
    once you have them.
    """
    def __init__(self, frame, data):
        self.frame = frame
        self.data = data

def lerp(x, (x0, y0), (x1, y1)):
    """Do linear interpolation between points (x0, y0), (x1, y1), and return
    the 'y' of the given 'x'."""
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def tween(keyframes):
    """Calculate all "in-between" frames from the given keyframes, and
    return a list of values for all frames in sequence.

    For example, given three keyframes:
    
        >>> keys = [Keyframe(1, 0),
        ...         Keyframe(6, 50),
        ...         Keyframe(12, 10)]

    The value increases from 0 to 50 over frames 1-6, then back down to 10
    over frames 6-12:

        >>> tween(keys)
        [0, 10, 20, 30, 40, 50, 43, 36, 30, 23, 16, 10]

    This function can handle single-integer or (x,y) data in keyframes. An
    example using (x,y) tweening:

        >>> keys = [Keyframe(1, (20, 20)),
        ...         Keyframe(6, (80, 20)),
        ...         Keyframe(12, (100, 100))]

    Here, a point on a two-dimensional plane starts at (20, 20), moving first
    to the right, to (80, 20), then diagonally to (100, 100).

        >>> for (x, y) in tween(keys):
        ...     print (x, y)
        ...
        (20, 20)
        (32, 20)
        (44, 20)
        (56, 20)
        (68, 20)
        (80, 20)
        (83, 33)
        (86, 46)
        (90, 60)
        (93, 73)
        (96, 86)
        (100, 100)

    This function may support more complex data types in the future; for now
    it is limited to using only integers or tuples of numbers.
    """
    data = []

    # TODO: Sort keyframes in increasing order by frame number (to ensure
    # keyframes[0] is the first frame, and keyframes[-1] is the last frame)
    # Make a copy of keyframes
    import copy
    keys = copy.deepcopy(keyframes)
    first = keys[0].frame
    last = keys[-1].frame

    # Pop off keyframes as each interval is calculated
    left = keys.pop(0)
    right = keys.pop(0)
    frame = first
    while frame <= last:
        # Left endpoint
        if frame == left.frame:
            data.append(left.data)
        # Right endpoint
        elif frame == right.frame:
            data.append(right.data)
            # Get the next interval, if it exists
            if keys:
                left = right
                right = keys.pop(0)
        # Between endpoints; interpolate
        else:
            # Interpolate integers
            if isinstance(left.data, int):
                x0 = (left.frame, left.data)
                y0 = (right.frame, right.data)
                data.append(lerp(frame, x0, y0))
            # Interpolate a tuple (x,y)
            if isinstance(left.data, tuple):
                # Interpolation endpoints
                x0, y0 = left.data
                x1, y1 = right.data
                # Interpolate x and y separately
                x = lerp(frame, (left.frame, x0), \
                         (right.frame, x1))
                y = lerp(frame, (left.frame, y0), \
                         (right.frame, y1))
                # And finally...
                data.append((x, y))
        frame += 1
    return data


class Overlay:
    """A visual element that may be composited onto a video canvas. May be
    semi-transparent."""
    # TODO: Include here information about the effects channel for the overlay
    # (default: always-visible), how to render it (in general)
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
    def get_mvg(self):
        mvg = Drawing(self.size)
        if self.filename:
            # TODO
            pass
        elif self.color:
            mvg.fill(self.color)
            mvg.rectangle((0,0), self.size)
        return mvg

class Text (Overlay):
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


class Thumbnail (Overlay):
    def __init__(self, (x, y), (width, height), filename):
        self.position = (x, y)
        self.size = (width, height)
        self.filename = filename
    def get_mvg(self):
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



class Effect:
    """A "special effect" created by keyframing MVG draw commands.
    Commands that it might make sense to keyframe:
        opacity
    """
    def __init__(self, start, end):
        """Create an effect lasting from start to end (in frames)."""
        self.start = start
        self.end = end
        self.keys = {} # Keyframe lists, indexed by MVG command name

    def get_mvg(self, frame):
        """Return an MVG object for drawing the effect at the given frame."""
        mvg = Drawing()
        for command, keylist in self.keys.iteritems():
            data = tween(frame, keylist)
            if isinstance(data, tuple):
                mvg.append('%s %s,%s' % (command, data[0], data[1]))
            else:
                mvg.append('%s %s' % (command, data))
        return mvg


class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of an overlay."""
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity until fading out for fade_length frames before end."""
        Effect.__init__(self, start, end)
        self.keys['opacity'] = [\
            Keyframe(start, 0),                    # Start fading in
            Keyframe(start + fade_length, 100),    # Fade-in done
            Keyframe(end - fade_length, 100),      # Start fading out
            Keyframe(end, 0)                       # Fade-out done
            ]

class Move (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        self.keys['translate'] = [\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ]


class VideoCanvas:
    def __init__(self, width=720, height=576, frames=30):
        self.width = width
        self.height = height
        self.frames = frames
        self.overlays = []
        self.mvg = []
        for frame in range(frames):
            self.mvg.append(Drawing(self.width, self.height))

    def add(self, overlay, effect=None):
        """Add the given Overlay to the canvas, with the given Effect."""
        self.overlays.append((overlay, effect))

    def render(self, frame=0):
        """Render the given frame with ImageMagick."""
        mvg = self.mvg[frame]
        mvg.clear()
        for overlay, effect in self.overlays:
            if effect:
                mvg.extend(effect.get_mvg(frame))
            mvg.extend(overlay.get_mvg())
        mvg.code()
        mvg.render()

    def bg_image(self, filename):
        """Fill the canvas background with the given image."""
        pass

    def bg_video(self, filename):
        """Fill the canvas background with frames from the given video."""


if __name__ == '__main__':
    canvas = VideoCanvas(720,576,30)
    bgd = Background((720, 576), 'blue')
    canvas.add(bgd)
    txt = Text((360,200), "Hello world")
    move = Move(10, 20, (100,100), (200,200))
    canvas.add(txt, move)
    canvas.render()

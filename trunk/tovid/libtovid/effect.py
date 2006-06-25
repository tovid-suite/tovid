#! /usr/bin/env python
# effect.py

"""This module defines classes for creating and drawing effects on a series
of drawings (as in a Flipbook).

Effect classes are arranged in a (currently) simple hierarchy:

    Effect (base class)
    |-- Movement
    |-- Fade
    |-- Colorfade
    |-- Spectrum
    |-- Scale

"""

__all__ = ['Effect', 'Movement', 'Fade', 'Colorfade', 'Spectrum', 'Scale']

from libtovid.mvg import Drawing
from libtovid.animation import Keyframe, tween

class Effect:
    """A "special effect" created by keyframing an MVG command along
    the given frame interval."""
    def __init__(self, start, end):
        """Create an effect lasting from start frame to end frame."""
        self.start = start
        self.end = end
        # List of Keyframes
        self.keyframes = [Keyframe(0, 0)]
        # List of tweened values
        self.data = [0]

    def get_data(self, frame):
        """Get data value at the given frame."""
        if frame < self.start:
            return self.data[0]
        elif frame > self.end:
            return self.data[-1]
        else:
            return self.data[frame - self.start]

    def draw_on(self, drawing, frame):
        """Draw the effect into the given Drawing, for the given frame.
        Override this function in derived classes."""
        pass

# ============================================================================
# New effect template
# Copy and paste this code to create your own Effect
# ============================================================================
# The first line defines your effect's name. (Effect) means it inherits from
# the base Effect class.
class MyEffect (Effect):
    
    # The __init__ function is called whenever a MyEffect is created.
    # Make sure your __init__ takes start and end arguments; additional
    # arguments (such as start_val and end_val below) allow someone using
    # your effect class to customize its behavior in some way. See the
    # other effects below for examples.
    def __init__(self, start, end, start_val, end_val):
        """Create a MyEffect lasting from start to end frame.
        Modify this documentation string to describe what your effect does.
        """
        # Be sure to call this first-thing:
        Effect.__init__(self, start, end)
        # It initializes the base Effect class with start and end frames.

        # Next, define any keyframes your effect needs to use. This
        # effect just varies something from start_val to end_val:
        self.keyframes = [\
            Keyframe(start, start_val),
            Keyframe(end, end_val)
            ]

        # Call this afterwards, to calculate the values at all frames
        self.data = tween(self.keyframes)

    # Now, override the draw_on function...
    def draw_on(self, drawing, frame):
        # ...and use a MVG Drawing command, passing the data
        # for the current frame. Replace 'translate' with your
        # own drawing function (see libtovid/mvg.py for a complete list)
        drawing.translate(self.get_data(frame))

    # That's it! Your effect is ready to use.
    # See libtovid/flipbook.py for examples on how to use effects

# ============================================================================
# End of new effect template
# ============================================================================

class Movement (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        self.keyframes = [\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ]
        self.data = tween(self.keyframes)

    def draw_on(self, drawing, frame):
        """Draw the movement effect into the given Drawing."""
        drawing.translate(self.get_data(frame))

class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of a layer."""
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity, then fade out for fade_length frames before end."""
        Effect.__init__(self, start, end)
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        # The tween()ed array is indexed as an offset from the start
        # frame (self.opacities[0] gives the value at the start frame)
        self.keyframes = [\
            Keyframe(start, 0.0),                  # Start fading in
            Keyframe(start + fade_length, 1.0),    # Fade-in done
            Keyframe(end - fade_length, 1.0),      # Start fading out
            Keyframe(end, 0.0)                     # Fade-out done
            ]
        self.data = tween(self.keyframes)

    def draw_on(self, drawing, frame):
        """Draw the fade effect into the given Drawing."""
        drawing.fill_opacity(self.get_data(frame))

class Colorfade (Effect):
    """A color-slide effect between an arbitrary number of RGB colors."""
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        """Fade between the given RGB colors."""
        Effect.__init__(self, start, end)
        self.keyframes = [\
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ]
        self.data = tween(self.keyframes)

    def draw_on(self, drawing, frame):
        drawing.fill_rgb(self.get_data(frame))

class Spectrum (Effect):
    """A full-spectrum color-fade effect between start and end frames."""
    def __init__(self, start, end):
        Effect.__init__(self, start, end)
        step = (end - start) / 6
        self.keyframes = [\
            Keyframe(start, (255, 0, 0)),
            Keyframe(start + step, (255, 0, 255)),
            Keyframe(start + step*2, (0, 0, 255)),
            Keyframe(start + step*3, (0, 255, 255)),
            Keyframe(start + step*4, (0, 255, 0)),
            Keyframe(start + step*5, (255, 255, 0)),
            Keyframe(end, (255, 0, 0))
            ]
        self.data = tween(self.keyframes)

    def draw_on(self, drawing, frame):
        drawing.fill_rgb(self.data[frame - self.start])


class Scale (Effect):
    """A Scaling effect, from one size to another."""
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.keyframes =[\
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ]
        self.data = tween(self.keyframes)

    def draw_on(self, drawing, frame):
        drawing.scale(self.get_data(frame))



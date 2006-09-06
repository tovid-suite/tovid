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
    \-- KeyFunction

"""

__all__ = [\
    'Effect',
    'Movement',
    'Translate',
    'Fade',
    'Colorfade',
    'Spectrum',
    'Scale',
    'KeyFunction'
]

from libtovid.render.cairo_ import Drawing
from libtovid.animation import Keyframe, Tween

class Effect:
    """A "special effect" created by keyframing a Cairo drawing command
    along the given frame interval."""
    def __init__(self, start, end):
        """Create an effect lasting from start frame to end frame."""
        self.start = start
        self.end = end
        # List of Keyframes
        self.keyframes = [Keyframe(self.start, 0), Keyframe(self.end, 0)]
        self.tween = Tween(self.keyframes)

    def draw_on(self, drawing, frame):
        """Draw the effect into the given Drawing, for the given frame.
        Override this function in derived classes."""
        pass

# ============================================================================
# New Effect template
# Copy and paste this code to create your own Effect
# ============================================================================
# The first line defines your effect's name. (Effect) means it inherits from
# the base Effect class, and shares some properties with it.
class MyEffect (Effect):
    """Modify this documentation string to describe what your effect does.
    """
    
    # The __init__ function is called whenever a MyEffect is created.
    # Make sure your __init__ takes start and end arguments; additional
    # arguments (such as start_val and end_val below) allow someone using
    # your effect class to customize its behavior in some way. See the
    # other effects below for examples.
    def __init__(self, start, end, start_val, end_val):
        """Create a MyEffect lasting from start to end frame.
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
        self.tween = Tween(self.keyframes)

    # The draw_on function draws the effect onto a Drawing at the given frame
    def draw_on(self, drawing, frame):
        # First, it's good to make sure we really have a Drawing class
        assert isinstance(drawing, Drawing)
        # This effect varies the stroke width across a sequence of frames.
        # Replace 'stroke_width' with your own drawing function(s)
        # (see libtovid/renderers/mvg_render.py for a complete list)
        drawing.stroke_width(self.tween[frame])

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
        self.tween = Tween(self.keyframes)

    def draw_on(self, drawing, frame):
        """Draw the movement effect into the given Drawing."""
        assert isinstance(drawing, Drawing)
        drawing.translate(self.tween[frame])

class Translate (Movement):
    """Translates the layer to some relative (x,y) coordinates"""
    def __init__(self, start, end, (dx, dy)):
        Movement.__init__(self, start, end, (0,0), (dx, dy))
        

class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of a layer.
    """
    def __init__(self, start, end, fade_length=30, keyframes=None,
                 method='linear'):
        """Fade in from start, for fade_length frames; hold at full
        opacity, then fade out for fade_length frames before end.

        fade_length -- num of frames to fade-in from start, and num of
                       frames to fade-out before end. Everything in-between
                       is at full opacity.
        keyframes -- a set of Keyframe() objects, determining the fading
                     curve. Values of the Keyframe() must be floats ranging
                     from 0.0 to 1.0 (setting opacity).
        method -- linear, cosine

        """
        Effect.__init__(self, start, end)
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        if not isinstance(keyframes, list):
            self.keyframes = [\
                Keyframe(start, 0.0),                  # Start fading in
                Keyframe(start + fade_length, 1.0),    # Fade-in done
                Keyframe(end - fade_length, 1.0),      # Start fading out
                Keyframe(end, 0.0)                     # Fade-out done
                ]
        else:
            self.keyframes = keyframes

        print "Keyframes:"
        for x in self.keyframes:
            print "   frame: %d - data:" % x.frame, x.data

        self.tween = Tween(self.keyframes, method)

    def draw_on(self, drawing, frame):
        """Draw the fade effect into the given Drawing."""
        assert isinstance(drawing, Drawing)
        drawing.opacity(self.tween[frame])

class Colorfade (Effect):
    """A color-slide effect between an arbitrary number of RGB colors."""
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        """Fade between the given RGB colors."""
        Effect.__init__(self, start, end)
        self.keyframes = [\
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ]
        self.tween = Tween(self.keyframes)

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.color_all(self.tween[frame])


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
        self.tween = Tween(self.keyframes)

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        print "Drawing spectrum frame: ", self.tween[frame]
        drawing.color_all(self.tween[frame])


class Scale (Effect):
    """A Scaling effect, from one size to another."""
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.keyframes =[\
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ]
        self.tween = Tween(self.keyframes)

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        drawing.scale(self.tween[frame])


class KeyFunction (Effect):
    """A keyframed effect on an arbitrary Drawing function."""
    def __init__(self, draw_function, keyframes, method='linear'):
        """Create an effect using the given Drawing function, with values
        determined by the given list of Keyframes. For example:

            KeyFunction(Drawing.stroke_width,
                        [Keyframe(1, 1), Keyframe(30, 12)])

        This says to vary the stroke width from 1 (at frame 1) to 12 (at
        frame 30).

        The 'method' argument defines an interpolation method to use between
        keyframes, and may be either 'linear' or 'cosine'. 
        """
        # Call base constructor with start and end frames
        Effect.__init__(self, keyframes[0].frame, keyframes[-1].frame)
        # TODO: Make sure a valid function name is given
        self.draw_function = draw_function
        self.keyframes = keyframes
        # Tween keyframes using the given interpolation method
        self.tween = Tween(self.keyframes, method)

    def draw_on(self, drawing, frame):
        assert isinstance(drawing, Drawing)
        self.draw_function(drawing, self.tween[frame])

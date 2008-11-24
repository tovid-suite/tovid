#! /usr/bin/env python
# effect.py

"""This module defines classes for creating and drawing effects on a series
of drawings (as in a Flipbook).

Effect classes are arranged in a (currently) simple hierarchy:

    Effect (base class)
    |-- Movement
    |   \-- Translate
    |-- Fade
    |   \-- FadeInOut
    |-- Colorfade
    |-- Spectrum
    |-- Scale
    |-- Whirl
    |-- PhotoZoom
    \-- KeyFunction

"""

__all__ = [
    'Effect',
    'Movement',
    'Translate',
    'Fade',
    'FadeInOut'
    'Colorfade',
    'Spectrum',
    'Scale',
    'Whirl',
    'PhotoZoom',
    'KeyFunction'
    ]

from libtovid.render.drawing import Drawing
from libtovid.render.animation import Keyframe, Tween
from random import randint

### --------------------------------------------------------------------------

class Effect:
    """A "special effect" created by keyframing a Cairo drawing command
    along the given frame interval.
    """
    def __init__(self, start, end):
        """Create an effect lasting from start frame to end frame.
        """
        self.start = start
        self.end = end
        # List of Keyframes
        self.keyframes = [Keyframe(self.start, 0), Keyframe(self.end, 0)]
        self.tween = Tween(self.keyframes)

        # Parents
        self._parent_flipbook = None
        self._parent_layer = None


    def init_parent_flipbook(self, fb):
        self._parent_flipbook = fb


    def init_parent_layer(self, layer):
        self._parent_layer = layer


    def pre_draw(self, drawing, frame):
        """Set up effect elements that must be applied before drawing a Layer.

            drawing
                The Drawing to apply effects to
            frame
                The frame for which to render the effect

        Extend this function in derived classes.
        """
        drawing.save()


    def post_draw(self, drawing, frame):
        """Finalize effect elements after a Layer is drawn.

            drawing
                The Drawing to apply effects to
            frame
                The frame for which to render the effect

        Extend this function in derived classes.
        """
        drawing.restore()


### --------------------------------------------------------------------------
### New Effect template
### Copy and paste this code to create your own Effect
### --------------------------------------------------------------------------

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
        self.keyframes = [
            Keyframe(start, start_val),
            Keyframe(end, end_val)
            ]

        # Call this afterwards, to calculate the values at all frames
        self.tween = Tween(self.keyframes)

    def draw(self, drawing, frame):
        """Undocumented"""
        # Example function that can be called when drawing a layer.
        # The Layer must know that his particular effect requires the
        # calling of this function, or to add special parameters, or to
        # draw between items in the layer.
        
        # First, it's good to make sure we really have a Drawing class
        assert isinstance(drawing, Drawing)
        
        # This effect varies the stroke width across a sequence of frames.
        # Replace 'stroke_width' with your own drawing function(s)
        drawing.stroke_width(self.tween[frame])

    # Effect rendering occurs in two phases: pre_draw and post_draw.
    # These functions are already defined in the Effect base class; extend
    # them to do your effect rendering.
    def pre_draw(self, drawing, frame):
        """Do preliminary effect rendering."""
        # Always call the base class pre_draw first:
        Effect.pre_draw(self, drawing, frame)
        
        # This effect varies the stroke width across a sequence of frames.
        # Replace 'stroke_width' with your own drawing function(s)
        drawing.stroke_width(self.tween[frame])

    # Extend post_draw to do any post-rendering cleanup you need to do. Most
    # of the time, you won't need to extend this, but if you do, be sure to
    # call the base class post_draw at the end:
    def post_draw(self, drawing, frame):
        """Do post-drawing cleanup."""
        # Post-drawing cleanup here
        Effect.post_draw(self, drawing, frame)

    # That's it! Your effect is ready to use.
    # See libtovid/flipbook.py for examples on how to use effects

### --------------------------------------------------------------------------
### End of new effect template
### --------------------------------------------------------------------------


### --------------------------------------------------------------------------
### Built-in effects
### --------------------------------------------------------------------------

class Movement (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1).
        """
        Effect.__init__(self, start, end)
        self.keyframes = [
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ]
        self.tween = Tween(self.keyframes)

    def pre_draw(self, drawing, frame):
        drawing.save()
        drawing.translate(*self.tween[frame])

    def post_draw(self, drawing, frame):
        drawing.restore()

### --------------------------------------------------------------------------

class Translate (Movement):
    """Translates the layer to some relative (x,y) coordinates
    """
    def __init__(self, start, end, (dx, dy)):
        Movement.__init__(self, start, end, (0, 0), (dx, dy))
        

### --------------------------------------------------------------------------

class Fade (Effect):
    """A generic fade effect, varying the opacity of a layer.
    """
    def __init__(self, keyframes, method='linear'):
        """Fade in from start, for fade_length frames; hold at full
        opacity, then fade out for fade_length frames before end.

            fade_length
                Number of frames to fade-in from start, and number of
                frames to fade-out before end. Everything in-between
                is at full opacity.
            keyframes
                A set of Keyframe() objects, determining the fading
                curve. Values of the Keyframe() must be floats ranging
                from 0.0 to 1.0 (setting opacity).
            method
                'linear' or 'cosine' interpolation
    
        """
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        if isinstance(keyframes, list):
            if not isinstance(keyframes[0], Keyframe):
                raise ValueError, "Must be a list of Keyframe objects"
            self.keyframes = keyframes
        else:
            raise ValueError, "List of Keyframe objects required"

        self.tween = Tween(self.keyframes, method)
        

    def pre_draw(self, drawing, frame):
        """Called before drawing on a layer.
        """
        drawing.push_group()


    def post_draw(self, drawing, frame):
        """Called after drawing on a layer.
        """
        assert isinstance(drawing, Drawing)
        drawing.pop_group_to_source()
        drawing.paint_with_alpha(self.tween[frame])

### --------------------------------------------------------------------------

class FadeInOut (Fade):
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity, then fade out for fade_length frames before end.

            fade_length
                Number of frames to fade-in from start, and number of
                frames to fade-out before end. Everything in-between
                is at full opacity.
        """
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        self.keyframes = [
                Keyframe(start, 0.0),                  # Start fading in
                Keyframe(start + fade_length, 1.0),    # Fade-in done
                Keyframe(end - fade_length, 1.0),      # Start fading out
                Keyframe(end, 0.0)                     # Fade-out done
                ]

        self.tween = Tween(self.keyframes)

### --------------------------------------------------------------------------
    
class Colorfade (Effect):
    """A color-slide effect between an arbitrary number of RGB colors.
    """
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        """Fade between the given RGB colors."""
        Effect.__init__(self, start, end)
        self.keyframes = [
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ]
        self.tween = Tween(self.keyframes)


    def pre_draw(self, drawing, frame):
        """Set source color"""
        drawing.set_source(self.tween[frame])


    def post_draw(self, drawing, frame):
        pass


### --------------------------------------------------------------------------

class Spectrum (Effect):
    """A full-spectrum color-fade effect between start and end frames.
    """
    def __init__(self, start, end):
        Effect.__init__(self, start, end)
        step = (end - start) / 6
        self.keyframes = [
            Keyframe(start, (1.0, 0, 0)),
            Keyframe(start + step, (1.0, 0, 1.0)),
            Keyframe(start + step*2, (0, 0, 1.0)),
            Keyframe(start + step*3, (0, 1.0, 1.0)),
            Keyframe(start + step*4, (0, 1.0, 0)),
            Keyframe(start + step*5, (1.0, 1.0, 0)),
            Keyframe(end, (1.0, 0, 0))
            ]
        self.tween = Tween(self.keyframes)


    def pre_draw(self, drawing, frame):
        drawing.set_source(self.tween[frame])


    def post_draw(self, drawing, frame):
        pass

### --------------------------------------------------------------------------

class Scale (Effect):
    """A Scaling effect, from one size to another.
    """
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.keyframes = [
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ]
        self.tween = Tween(self.keyframes)


    def pre_draw(self, drawing, frame):
        drawing.save()
        drawing.scale(self.tween[frame])


    def post_draw(self, drawing, frame):
        drawing.restore()

### --------------------------------------------------------------------------

class Whirl (Effect):
    """Rotates an object a number of times.
    """
    def __init__(self, keyframes, center=(0, 0), method='linear', units='deg'):
        """Create a Whirl effect
        
            method
                'linear' or 'cosine', for passing from one angle to another
            units
                'deg' or 'rad', the unit used in the Keyframes
        """
        if units != 'deg' and units != 'rad':
            raise ValueError, "units must be 'rad' (radians) or 'deg' (degrees)"
        self.units = units
        
        if not isinstance(center, tuple):
            raise ValueError, "center must be a two-value tuple"
        self.center = center

        self.keyframes = keyframes
        self.tween = Tween(self.keyframes, method)


    def pre_draw(self, drawing, frame):
        drawing.save()
        # how to center the thing ? so you give a rotation point ?
        drawing.translate(*self.center)
        if self.units is 'deg':
            drawing.rotate_deg(self.tween[frame])
        elif self.units is 'rad':
            drawing.rotate_rad(self.tween[frame])


    def post_draw(self, drawing, frame):
        drawing.translate(- self.center[0], - self.center[1])
        drawing.restore()

### --------------------------------------------------------------------------

class PhotoZoom (Effect):
    """Zoom in and create dynamism by moving a picture.

    Normally applies to an Image layer, but can be used with others.
    """
    def __init__(self, keyframes, subject=(0, 0), direction=None,
                 movement=50, method='linear'):
        """Create a PhotoZoom effect

            keyframes
                0.0 for beginning of effect, and 1.0 to reach the end,
                intermediate values show the intermediate state of the effect.
            subject
                Position of the subject of interest. That is the point where
                the zoom in/out will focus it's attention.
                If (0, 0), the focus will be chosen randomly in the 2/3 of
                the center of the screen.
            direction
                'in', 'out', None (random)
            movement
                0 to 100, percentage of movement to create.
            method
                'linear' or 'cosine'
        """
        if direction not in ['in', 'out', None]:
            raise ValueError, "'direction' must be 'in', 'out' or None"
        if (direction == None):
            self.direction = randint(0, 1) and 'in' or 'out'
        else:
            self.direction = direction

        print "Zoom in direction: %s" % self.direction
        
        self.subject = subject

        self.movement = movement

        self.keyframes = keyframes
        self.tween = Tween(self.keyframes, method)


    def pre_draw(self, drawing, frame):
        drawing.save()

        fb = self._parent_flipbook
        # Use subject, or randomize in the center 1/3 of the image.
        if (self.subject == (0, 0)):
            self.subject = (randint(int(0.33 * fb.w),
                                    int(0.66 * fb.w)),
                            randint(int(0.33 * fb.h),
                                    int(0.66 * fb.h)))

        # Max moving = 25% * pixels estimation * movement factor
        zoomfactor = 0.25 * (self.movement / 100.)

        inter = self.tween[frame]
        
        if (self.direction == 'in'):
            gozoom = 1.0 + (1.0 - inter) * zoomfactor
        else:
            gozoom = 1.0 + inter * zoomfactor

        drawing.scale_centered(self.subject[0], self.subject[1],
                               gozoom, gozoom)


    def post_draw(self, drawing, frame):
        drawing.restore()

### --------------------------------------------------------------------------

class KeyFunction (Effect):
    """A keyframed effect on an arbitrary Drawing function.
    """
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

    def pre_draw(self, drawing, frame):
        drawing.save()
        self.draw_function(drawing, self.tween[frame])

    def post_draw(self, drawing, frame):
        drawing.restore()

### --------------------------------------------------------------------------

#! /usr/bin/env python
# effect.py

__all__ = ['Effect', 'Fade', 'Movement', 'Scale', 'Colorfade']

from libtovid.mvg import Drawing
from libtovid.animation import Keyframe, tween

class Effect:
    """A "special effect" created by keyframing MVG draw commands.
    """
    def __init__(self, start, end):
        """Create an effect lasting from start frame to end frame."""
        self.start = start
        self.end = end

    def draw_on(self, drawing, frame):
        """Draw the effect into the given Drawing, for the given frame.
        Override this function in derived classes."""
        pass


class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of a layer."""
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity until fading out for fade_length frames before end."""
        Effect.__init__(self, start, end)
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        # The tween()ed array is indexed as an offset from the start
        # frame (self.opacities[0] gives the value at the start frame)
        self.opacities = tween([\
            Keyframe(start, 0.0),                  # Start fading in
            Keyframe(start + fade_length, 1.0),    # Fade-in done
            Keyframe(end - fade_length, 1.0),      # Start fading out
            Keyframe(end, 0.0)                     # Fade-out done
            ])
    def draw_on(self, drawing, frame):
        """Draw the fade effect into the given Drawing."""
        drawing.fill_opacity(self.opacities[frame - self.start])


class Movement (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        self.translations = tween([\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ])
    def draw_on(self, drawing, frame):
        """Draw the movement effect into the given Drawing."""
        drawing.translate(self.translations[frame - self.start])


class Scale (Effect):
    """A Scaling effect, from one size to another."""
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.scalings = tween([\
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ])
    def draw_on(self, drawing, frame):
        drawing.scale(self.scalings[frame - self.start])


class Colorfade (Effect):
    """A color-slide effect between an arbitrary number of RGB colors."""
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        """Fade between the given RGB colors."""
        Effect.__init__(self, start, end)
        self.colors = tween([\
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ])
    def draw_on(self, drawing, frame):
        drawing.fill_rgb(self.colors[frame - self.start])

class Spectrum (Effect):
    """A full-spectrum color-fade effect between start and end frames."""
    def __init__(self, start, end):
        Effect.__init__(self, start, end)
        step = (end - start) / 6
        keys = [\
            Keyframe(start, (255, 0, 0)),
            Keyframe(start + step, (255, 0, 255)),
            Keyframe(start + step*2, (0, 0, 255)),
            Keyframe(start + step*3, (0, 255, 255)),
            Keyframe(start + step*4, (0, 255, 0)),
            Keyframe(start + step*5, (255, 255, 0)),
            Keyframe(end, (255, 0, 0))
            ]
        self.colors = tween(keys)
    def draw_on(self, drawing, frame):
        drawing.fill_rgb(self.colors[frame - self.start])


# Scaling effects
class Appear (Scale):
    """An "appear from nowhere" effect, quickly scaling up from a point."""
    def __init__(self, frame):
        """Appear starting at the given frame, with a 10-frame scale-in."""
        Scale.__init__(self, start, start + 10, (0.0, 0.0), (1.0, 1.0))

class Disappear (Scale):
    """A disappearance effect, scaling down to a point. Opposite of Appear."""
    def __init__(self, start, end):
        """Disappear finishing at the given frame, with a 10-frame scale-out."""
        Scale.__init__(self, end - 10, end, (1.0, 1.0), (0.0, 0.0))


# Demo
if __name__ == '__main__':
    fade = Colorfade(1, 10, (255, 128, 0), (128, 64, 255))
    print "Fading color from rgb(255, 128, 0) to rgb(128, 64, 255)"
    print "10-frame colorfade test:"
    for frame in range(1, 11):
        print "Frame %s" % frame
        mvg = fade.draw_on(frame)
        mvg.code()


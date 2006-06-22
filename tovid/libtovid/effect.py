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
        self.opacities = [None] + tween([\
            Keyframe(start, 0.0),                  # Start fading in
            Keyframe(start + fade_length, 1.0),    # Fade-in done
            Keyframe(end - fade_length, 1.0),      # Start fading out
            Keyframe(end, 0.0)                     # Fade-out done
            ])
    def draw_on(self, drawing, frame):
        """Draw the fade effect into the given Drawing."""
        drawing.fill_opacity(self.opacities[frame])


class Movement (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        self.translations = [None] + tween([\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ])
    def draw_on(self, drawing, frame):
        """Draw the movement effect into the given Drawing."""
        drawing.translate(self.translations[frame])


class Scale (Effect):
    """A Scaling effect, from one size to another."""
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.scalings = [None] + tween([\
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ])
    def draw_on(self, drawing, frame):
        drawing.scale(self.scalings[frame])


class Colorfade (Effect):
    """A color-slide effect, from one RGB color to another."""
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        Effect.__init__(self, start, end)
        self.colors = [None] + tween([\
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ])
    def draw_on(self, drawing, frame):
        drawing.fill_rgb(self.colors[frame])

if __name__ == '__main__':
    fade = Colorfade(1, 10, (255, 128, 0), (128, 64, 255))
    print "Fading color from rgb(255, 128, 0) to rgb(128, 64, 255)"
    print "10-frame colorfade test:"
    for frame in range(1, 11):
        print "Frame %s" % frame
        mvg = fade.draw_on(frame)
        mvg.code()


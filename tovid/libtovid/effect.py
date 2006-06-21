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
    def get_mvg(self, frame):
        """Return a Drawing that renders the effect at the given frame.
        Override this function in derived classes."""
        return Drawing()


class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of an overlay."""
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity until fading out for fade_length frames before end."""
        Effect.__init__(self, start, end)
        # A fill-opacity curve, something like:
        #         ______        100%
        #        /      \
        # start./        \.end  0%
        #
        self.opacity = [None] + tween([\
            Keyframe(start, 0.0),                  # Start fading in
            Keyframe(start + fade_length, 1.0),    # Fade-in done
            Keyframe(end - fade_length, 1.0),      # Start fading out
            Keyframe(end, 0.0)                     # Fade-out done
            ])
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.fill_opacity(self.opacity[frame])
        return mvg


class Movement (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        self.translate = [None] + tween([\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ])
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.translate(self.translate[frame])
        return mvg


class Scale (Effect):
    """A Scaling effect, from one size to another."""
    def __init__(self, start, end, (w0, h0), (w1, h1)):
        Effect.__init__(self, start, end)
        self.scale = [None] + tween([\
            Keyframe(start, (w0, h0)),
            Keyframe(end, (w1, h1))
            ])
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.scale(self.scale[frame])
        return mvg


class Colorfade (Effect):
    """A color-slide effect, from one RGB color to another."""
    def __init__(self, start, end, (r0, g0, b0), (r1, g1, b1)):
        Effect.__init__(self, start, end)
        self.color = [None] + tween([\
            Keyframe(start, (r0, g0, b0)),
            Keyframe(end, (r1, g1, b1))
            ])
    def get_mvg(self, frame):
        mvg = Drawing()
        mvg.fill_rgb(self.color[frame])
        return mvg

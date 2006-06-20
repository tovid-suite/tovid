#! /usr/bin/env python
# effect.py

from libtovid.mvg import Drawing

class Effect:
    """A "special effect" created by keyframing MVG draw commands.
    Commands that it might make sense to keyframe:
        fill-opacity NUM%
        fill rgb(r, g, b) or rgba(r, g, b, a)
        scale (x, y)
        translate (x, y)

    """
    def __init__(self, start, end):
        """Create an effect lasting from start to end (in frames)."""
        self.start = start
        self.end = end
        self.mvg_values = {} # Value lists, indexed by MVG command name

    def keyframe(self, command, keyframes):
        """Keyframe the given MVG command with the given list of Keyframes.
        This function creates a list that may be indexed by frame number
        to retrieve the corresponding (dependent) variable's value."""
        self.mvg_values[command] = [None] + tween(keyframes)

    def get_mvg(self, frame):
        """Return a Drawing that renders the effect at the given frame."""
        mvg = Drawing()
        for command, values in self.mvg_values.iteritems():
            value = values[frame]
            if isinstance(value, tuple):
                mvg.append('%s %f,%f' % (command, value[0], value[1]))
            else:
                mvg.append('%s %f' % (command, value))
        return mvg


class Fade (Effect):
    """A fade-in/fade-out effect, varying the opacity of an overlay."""
    def __init__(self, start, end, fade_length=30):
        """Fade in from start, for fade_length frames; hold at full
        opacity until fading out for fade_length frames before end."""
        Effect.__init__(self, start, end)
        fade_curve = [\
            Keyframe(start, 0.0),                  # Start fading in
            Keyframe(start + fade_length, 1.0),    # Fade-in done
            Keyframe(end - fade_length, 1.0),      # Start fading out
            Keyframe(end, 0.0)                     # Fade-out done
            ]
        self.keyframe('fill-opacity', fade_curve)


class Move (Effect):
    """A movement effect, from one point to another."""
    def __init__(self, start, end, (x0, y0), (x1, y1)):
        """Move from start (x0, y0) to end (x1, y1)."""
        Effect.__init__(self, start, end)
        trans_curve = [\
            Keyframe(start, (x0, y0)),
            Keyframe(end, (x1, y1))
            ]
        self.keyframe('translate', trans_curve)


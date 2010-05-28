"""This module provides classes and functions for working with animation.
Two classes are provided:

    :class:`Keyframe`
        A frame with a specific data value
    :class:`Tween`
        A data sequence interpolated from Keyframes

The data being interpolated may represent color, opacity, location, or anything
else that can be described numerically. Keyframe data may be scalar (single
integers or decimal values) or vector (tuples such as (x, y) coordinates or
(r, g, b) color values).

For example, let's define three keyframes::

    >>> keys = [Keyframe(1, 0),
    ...         Keyframe(6, 50),
    ...         Keyframe(12, 10)]

The value increases from 0 to 50 over frames 1-6, then back down to 10
over frames 6-12. The values at intermediate frames (2-5 and 7-11) can be
interpolated or "tweened" automatically, using the Tween class::

    >>> tween = Tween(keys)
    >>> tween.data
    [0, 10, 20, 30, 40, 50, 43, 36, 30, 23, 16, 10]

Another example using tweening of (x, y) coordinates::

    >>> keys = [Keyframe(1, (20, 20)),
    ...         Keyframe(6, (80, 20)),
    ...         Keyframe(12, (100, 100))]

Here, a point on a two-dimensional plane starts at (20, 20), moving first
to the right, to (80, 20), then diagonally to (100, 100)::

    >>> tween = Tween(keys)
    >>> for (x, y) in tween.data:
    ...     print((x, y))
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

"""

__all__ = [
    'Keyframe',
    'Tween',
    'lerp',
    'cos_interp',
    'interpolate',
]

import copy
import doctest
import math

class Keyframe:
    """Associates a specific frame in an animation with a numeric value.
    A Keyframe is a (frame, data) pair defining a "control point" on a graph::

            100 |
                |       Keyframe(10, 50)
           data |      *
                |
              0 |__________________________
                1     10     20     30
                        frame

    The data can represent anything you like. For instance, opacity::

            100 |* Keyframe(1, 100)
                |
     opacity(%) |
                |
              0 |____________________* Keyframe(30, 0)
                1     10     20     30
                        frame

    See the Tween class below for what you can do with these Keyframes,
    once you have them.
    """
    def __init__(self, frame, data):
        """Create a keyframe, associating a given frame with some data.
        The data may be an integer, floating-point value, or a tuple like
        (x, y) or (r, g, b).
        """
        self.frame = frame
        self.data = data


### --------------------------------------------------------------------------
### Interpolation algorithms
### --------------------------------------------------------------------------

def lerp(x, (x0, y0), (x1, y1)):
    """Do linear interpolation between points ``(x0, y0)``, ``(x1, y1)``, and
    return the ``y`` for the given ``x``.

    This form of interpolation simply connects two points with a straight
    line. Blunt, but effective.
    """
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def cos_interp(x, (x0, y0), (x1, y1)):
    """Do cosine-based interpolation between ``(x0, y0)``, ``(x1, y1)`` and
    return the ``y`` for the given ``x``.

    Essentially, a crude alternative to polynomial spline interpolation; this
    method transitions between two values by matching a segment of the cosine
    curve [0, pi] (for decreasing value) or [pi, 2*pi] (for increasing value)
    to the interval between the given points.

    It gives smoother results at inflection points than linear interpolation,
    but will result in "ripple" effects if keyframes are too dense or many.
    """
    # Map the interpolation area (domain of x) to [0, pi]
    x_norm = math.pi * (x - x0) / (x1 - x0)
    # For y0 < y1, use upward-sloping part of the cosine curve [pi, 2*pi]
    if y0 < y1:
        x_norm += math.pi
    # Calculate and return resulting y-value
    y_min = min(y1, y0)
    y_diff = abs(y1 - y0)
    return y_min + y_diff * (math.cos(x_norm) + 1) / 2.0


def interpolate(frame, left, right, method):
    """Interpolate data between left and right Keyframes at the given frame,
    using the given interpolation method ('linear' or 'cosine'). Return the
    value at the given frame.

    The left and right Keyframes mark the endpoints of the curve to be
    interpolated. For example, if a value changes from 50 to 80 over the
    course of frames 1 to 30::

        >>> left = Keyframe(1, 50)
        >>> right = Keyframe(30, 80)

    Then, the value at frame 10 can be interpolated as follows::

        >>> interpolate(10, left, right, 'linear')
        59
        >>> interpolate(10, left, right, 'cosine')
        56.582194019564263

    For frames outside the keyframe interval, the corresponding endpoint value
    is returned::

        >>> interpolate(0, left, right, 'linear')
        50
        >>> interpolate(40, left, right, 'linear')
        80

    """
    assert isinstance(left, Keyframe) and isinstance(right, Keyframe)
    # At or beyond endpoints, return endpoint value
    if frame <= left.frame:
        return left.data
    elif frame >= right.frame:
        return right.data

    # Use the appropriate interpolation function
    if method == 'cosine':
        interp_func = cos_interp
    else: # method == 'linear'
        interp_func = lerp

    # Interpolate integers or floats
    if isinstance(left.data, int) or isinstance(left.data, float):
        p0 = (left.frame, left.data)
        p1 = (right.frame, right.data)
        return interp_func(frame, p0, p1)
    # Interpolate a tuple (x, y, ...)
    elif isinstance(left.data, tuple):
        # Interpolate each dimension separately
        dim = 0
        result = []
        while dim < len(left.data):
            interp_val = interp_func(frame,
                                     (left.frame, left.data[dim]),
                                     (right.frame, right.data[dim]))
            result.append(interp_val)
            dim += 1
        return tuple(result)


class Tween:
    """An "in-between" sequence, calculated by interpolating the data in a
    list of keyframes according to a given interpolation method.

    First, define some keyframes::

        >>> keyframes = [Keyframe(1, 1), Keyframe(10, 25)]

    At frame 1, the value is 1; at frame 10, the value is 25. To get an
    interpolation of the data between these two keyframes, use::

        >>> tween = Tween(keyframes)

    Now, retrieve the interpolated data all at once::

        >>> tween.data
        [1, 3, 6, 9, 11, 14, 17, 19, 22, 25]

    Or by using array notation, indexed by frame number::

        >>> tween[3]
        6
        >>> tween[8]
        19
    """
    def __init__(self, keyframes, method='linear'):
        """Create an in-between sequence from a list of keyframes. The
        interpolation method can be 'linear' or 'cosine'.

        See effect.py for implementation examples.
        """
        for keyframe in keyframes:
            assert isinstance(keyframe, Keyframe)
        self.keyframes = keyframes
        self.start = self.keyframes[0].frame
        self.end = self.keyframes[-1].frame
        self.data = []
        self.method = method
        # Do the tweening
        self._tween()


    def _tween(self):
        """Perform in-betweening calculation on the current keyframes and
        fill self.data with tweened values, indexed by frame number.
        """
        self.data = []
        # TODO: Sort keyframes in increasing order by frame number (to ensure
        # keyframes[0] is the first frame, and keyframes[-1] is the last frame)
        # Make a copy of keyframes
        keys = copy.copy(self.keyframes)
        first = self.start
        last = self.end

        # If keyframe interval is empty, use constant data from first keyframe
        if first == last:
            self.data = keys[0].data
            return

        # Pop off keyframes as each interval is calculated
        left = keys.pop(0)
        right = keys.pop(0)
        frame = first
        # Interpolate until the last frame is reached
        while frame <= last:
            value = interpolate(frame, left, right, self.method)
            self.data.append(value)
            # Get the next interval, if it exists
            if frame == right.frame and len(keys) > 0:
                left = right
                right = keys.pop(0)
            frame += 1


    def __getitem__(self, frame):
        """Return the interpolated data at the given frame. This allows
        accessing a tweened value with subscripting by frame number::

            >>> keys = [Keyframe(1, 1), Keyframe(30, 50)]
            >>> tween = Tween(keys)
            >>> tween[1]
            1
            >>> tween[30]
            50
            >>> tween[21]
            34

        Frame numbers outside the keyframed region have the same values as
        those at the corresponding endpoints::

            >>> tween[0]
            1
            >>> tween[100]
            50
        """
        # If data is a single value, frame is irrelevant
        if not isinstance(self.data, list):
            return self.data
        # Otherwise, return the value for the given frame, extending endpoints
        elif frame < self.start:
            return self.data[0]
        elif frame > self.end:
            return self.data[-1]
        else:
            return self.data[frame - self.start]


if __name__ == '__main__':
    doctest.testmod(verbose=True)

    p0 = (1, 1)
    p1 = (20, 20)

    print("Interpolation methods")
    print("x      lerp     cos_interp")
    for x in range(1, 21):
        print("%s      %s       %s" % \
              (x, lerp(x, p0, p1), cos_interp(x, p0, p1)))

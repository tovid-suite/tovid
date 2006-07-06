#! /usr/bin/env python
# animation.py

"""This module provides classes and functions for working with animation.
Two classes are provided:

    Keyframe: A frame with a specific data value
    Tween:    A data sequence interpolated from Keyframes

The data being interpolated may represent color, opacity, location, or anything
else that can be described numerically. Keyframe data may be scalar (single
integers or decimal values) or vector (tuples such as (x, y) coordinates or
(r, g, b) color values).

For example, let's define three keyframes:

    >>> keys = [Keyframe(1, 0),
    ...         Keyframe(6, 50),
    ...         Keyframe(12, 10)]

The value increases from 0 to 50 over frames 1-6, then back down to 10
over frames 6-12. The values at intermediate frames (2-5 and 7-11) can be
interpolated or "tweened" automatically, using the Tween class:

    >>> tween = Tween(keys)
    >>> tween.data
    [0, 10, 20, 30, 40, 50, 43, 36, 30, 23, 16, 10]

Another example using tweening of (x, y) coordinates:

    >>> keys = [Keyframe(1, (20, 20)),
    ...         Keyframe(6, (80, 20)),
    ...         Keyframe(12, (100, 100))]

Here, a point on a two-dimensional plane starts at (20, 20), moving first
to the right, to (80, 20), then diagonally to (100, 100).

    >>> tween = Tween(keys)
    >>> for (x, y) in tween.data:
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

"""

__all__ = ['Keyframe', 'lerp', 'cos_interp', 'interpolate', 'tween']

import copy
import doctest
import math

class Keyframe:
    """Associates a specific frame in an animation with a numeric value.
    A Keyframe is a (frame, data) pair defining a "control point" on a graph:
    
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

    See the Tween class below for what you can do with these Keyframes,
    once you have them.
    """
    def __init__(self, frame, data):
        self.frame = frame
        self.data = data


# Interpolation algorithms

def lerp(x, (x0, y0), (x1, y1)):
    """Do linear interpolation between points (x0, y0), (x1, y1), and return
    the 'y' of the given 'x'.

    This form of interpolation simply connects two points with a straight
    line. Blunt, but effective."""
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def cos_interp(x, (x0, y0), (x1, y1)):
    """Do cosine-based interpolation between (x0, y0), (x1, y1) and return
    the 'y' of the given 'x'.

    Essentially, a crude alternative to polynomial spline interpolation; this
    method transitions between two values by matching a segment of the cosine
    curve [0, pi] (for decreasing value) or [pi, 2*pi] (for increasing value)
    to the interval between the given points.

    It gives smoother results at inflection points than linear interpolation, 
    but will result in "ripple" effects if keyframes are too dense or many.   
    """
    # Map interpolation area (domain of x) to [0, pi]
    x_norm = math.pi * (x - x0) / (x1 - x0)
    # For y0 < y1, use upward-sloping part of the cosine curve [pi, 2*pi]
    if y0 < y1:
        x_norm += math.pi
    # Calculate and return resulting y-value
    y_min = min(y1, y0)
    y_diff = abs(y1 - y0)
    return y_min + y_diff * (math.cos(x_norm) + 1) / 2.0


# Single-interval interpolation function

def interpolate(frame, left, right, method):
    """Interpolate data between left and right Keyframes at the given frame,
    using the given interpolation method ('linear' or 'cosine'). Return the
    value at the given frame."""
    assert isinstance(left, Keyframe) and isinstance(right, Keyframe)
    # Use the appropriate interpolation function
    if method == 'cosine':
        interp_func = cos_interp
    else: # method == 'linear'
        interp_func = lerp
    # Interpolate integers or floats
    if isinstance(left.data, int) or isinstance(left.data, float):
        x0 = (left.frame, left.data)
        y0 = (right.frame, right.data)
        return interp_func(frame, x0, y0)
    # Interpolate a tuple (x, y, ...)
    elif isinstance(left.data, tuple):
        # Interpolate each dimension separately
        dim = 0
        result = []
        while dim < len(left.data):
            result.append(interp_func(frame, (left.frame, left.data[dim]), \
                 (right.frame, right.data[dim])))
            dim += 1
        return tuple(result)


class Tween:
    """Stores a list of keyframes and their corresponding interpolation over
    the course of a given frame interval.
    """
    def __init__(self, keyframes, method='linear'):
        """Create an in-between sequence from the given list of keyframes,
        using the given interpolation method (which may be 'linear' or 
        'cosine')."""
        assert isinstance(keyframes[0], Keyframe)
        self.keyframes = keyframes
        self.data = []
        self._tween(method)

    def _tween(self, method):
        """Perform in-betweening calculation on the current keyframes and
        fill self.data with tweened values, indexed by frame number.
        """
        self.data = []
        # TODO: Sort keyframes in increasing order by frame number (to ensure
        # keyframes[0] is the first frame, and keyframes[-1] is the last frame)
        # Make a copy of keyframes
        keys = copy.deepcopy(self.keyframes)
        self.start = keys[0].frame
        self.end = keys[-1].frame
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
        while frame <= last:
            # Left endpoint
            if frame == left.frame:
                self.data.append(left.data)
            # Right endpoint
            elif frame == right.frame:
                self.data.append(right.data)
                # Get the next interval, if it exists
                if keys:
                    left = right
                    right = keys.pop(0)
            # Between endpoints; interpolate
            else:
                self.data.append(interpolate(frame, left, right, method))
            frame += 1

    def __getitem__(self, frame):
        """Return the interpolated data at the given frame. Frame numbers
        outside the keyframed region have the same values as those at the
        corresponding endpoints.
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
    
    print "Interpolation methods"
    print "x      lerp     cos_interp"
    for x in range(1, 21):
        print "%s      %s       %s" % \
              (x, lerp(x, p0, p1), cos_interp(x, p0, p1))

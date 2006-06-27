#! /usr/bin/env python
# animation.py

"""This module provides classes and functions for working with animation.
"""
__all__ = ['Keyframe', 'lerp', 'interpolate', 'tween']

import copy
import doctest
import math

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

def cos_interp(x, (x0, y0), (x1, y1)):
    """Do cosine-based interpolation between (x0, y0), (x1, y1) and return
    the 'y' of the given 'x'."""
    # Map interpolation area (domain of x) to [0, pi]
    x_norm = math.pi * x / (x1 - x0)
    # For y0 < y1, use upward-sloping part of the cosine curve
    if y0 < y1:
        x_norm += math.pi
    # Calculate and return resulting y-value
    y_min = min(y1, y0)
    y_diff = abs(y1 - y0)
    return y_min + y_diff * (math.cos(x_norm) + 1) / 2.0


def interpolate(frame, left, right):
    """Interpolate data between left and right Keyframes at the given frame."""
    # Interpolate integers or floats
    if isinstance(left.data, int) or isinstance(left.data, float):
        x0 = (left.frame, left.data)
        y0 = (right.frame, right.data)
        return lerp(frame, x0, y0)
    # Interpolate a tuple (x, y, ...)
    elif isinstance(left.data, tuple):
        # Interpolate each dimension separately
        dim = 0
        result = []
        while dim < len(left.data):
            result.append(lerp(frame, (left.frame, left.data[dim]), \
                 (right.frame, right.data[dim])))
            dim += 1
        return tuple(result)


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
    keys = copy.deepcopy(keyframes)
    first = keys[0].frame
    last = keys[-1].frame
    if first == last:
        return keys[0].data

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
            data.append(interpolate(frame, left, right))
        frame += 1
    return data



if __name__ == '__main__':
    #doctest.testmod()

    p0 = (1, 1)
    p1 = (20, 20)
    
    print "Interpolation methods"
    print "x      lerp     cos_interp"
    for x in range(1, 21):
        print "%s      %s       %s" % \
              (x, lerp(x, p0, p1), cos_interp(x, p0, p1))

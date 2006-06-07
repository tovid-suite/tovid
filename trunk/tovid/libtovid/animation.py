#! /usr/bin/env python
# animation.py

from libtovid.mvg import MVG

class Keyframe:
    def __init__(self, frame, data):
        self.frame = frame
        self.data = data

def tween(frame, startkey, endkey):
    """Return the value at the given frame, interpolated between start and
    end Keyframes.
    """
    # At endpoints and beyond, return the endpoint value
    if frame <= startkey.frame:
        return startkey.data
    elif frame >= endkey.frame:
        return endkey.data

    # Do simple linear interpolation
    # TODO: Support other interpolation methods (constant, B-spline, etc.)
    # Current frame's distance along the [start-end] interval
    # (as a percentage [0.0-1.0]).
    dist = float(frame - startkey.frame) / (endkey.frame - startkey.frame)

    # Total change in the value of data
    total_change = endkey.data - startkey.data
    # TODO: Support tuple data (to interpolate (x,y) values simultaneously)
    result = startkey.data + (total_change * dist)

    # Return int, if original was int
    if isinstance(startkey.data, int):
        return int(result)

    return float(result)



class VideoCanvas:
    def __init__(self, width=720, height=576, frames=30):
        self.width = width
        self.height = height
        self.frames = frames
        # Create empty frames
        self.mvg = []
        for frame in range(frames):
            self.mvg.append(MVG(width, height))

    def render(self, frame=0):
        """Render the given frame with ImageMagick."""
        mvg[frame].render()

    def bg_image(self, filename):
        """Fill the canvas background with the given image."""
        pass

    def bg_video(self, filename):
        """Fill the canvas background with frames from the given video."""


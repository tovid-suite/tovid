#! /usr/bin/env python
# flipbook.py

from libtovid.mvg import Drawing

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    It has several frames (or "pages", if you like), 
    """
    def __init__(self, frames=30, (width, height)=(720, 576)):
        self.frames = frames
        self.size = width, height
        self.layers = []
        self.drawings = []
        for frame in range(frames):
            self.drawings.append(Drawing(self.size, 'temp.mvg'))

    def add(self, name, layer):
        """Add a named Layer to the flipbook."""
        self.layers[name] = layer

    def get_mvg(self, frame=1):
        """Get an MVG Drawing for the given frame."""
        mvg = self.drawings[frame]
        mvg.clear()
        for overlay in self.overlays:
            # Save context and draw the overlay
            mvg.push('graphic-context')
            mvg.extend(overlay.get_mvg(frame))
            mvg.pop('graphic-context')
        mvg.code()
        mvg.render()

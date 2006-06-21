#! /usr/bin/env python
# flipbook.py

from libtovid.mvg import Drawing
from libtovid.layer import Background, Text
from libtovid.effect import Fade, Movement

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    It has several frames (or "pages")
    """
    def __init__(self, frames=30, (width, height)=(720, 576)):
        self.frames = frames
        self.size = width, height
        self.layers = []
        self.drawings = []
        for frame in range(frames):
            self.drawings.append(Drawing(self.size, 'temp.mvg'))

    def add(self, layer):
        """Add a Layer to the flipbook."""
        self.layers.append(layer)

    def render(self, frame=1):
        """Render a Drawing for the given frame."""
        print "Rendering Flipbook frame %s" % frame
        drawing = self.drawings[frame]
        drawing.clear()
        for layer in self.layers:
            layer.draw_on(drawing, frame)
        print drawing.code()
        drawing.render()

# Demo
if __name__ == '__main__':
    print "Flipbook demo"
    flip = Flipbook()
    bgd = Background(flip.size, 'red')
    text = Text("The quick brown fox", (0, 0))
    text.effects.append(Fade(1, 30, 10))
    text.effects.append(Movement(1, 30, (100, 100), (500, 300)))
    flip.add(bgd)
    flip.add(text)
    flip.render(1)
    flip.render(5)
    flip.render(15)
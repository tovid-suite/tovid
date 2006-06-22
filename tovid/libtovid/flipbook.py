#! /usr/bin/env python
# flipbook.py

from libtovid.mvg import Drawing
from libtovid.layer import Thumb, Background, Text
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

    def add(self, layer):
        """Add a Layer to the flipbook."""
        self.layers.append(layer)

    def render(self, frame=1):
        """Render a Drawing for the given frame."""
        print "Rendering Flipbook frame %s" % frame
        drawing = Drawing(self.size, '/tmp/flipbook.mvg')
        # Write MVG header stuff
        drawing.push('graphic-context')
        drawing.viewbox((0, 0), self.size)
        # Draw each layer
        for layer in self.layers:
            layer.draw_on(drawing, frame)
        print drawing.code()
        drawing.pop('graphic-context')
        # Render the drawing
        drawing.render()

# Demo
if __name__ == '__main__':
    print "Flipbook demo"
    flip = Flipbook()

    # Background image
    bgd = Background(flip.size, filename='/pub/video/test/clouds.jpg')
    flip.add(bgd)

    # Text layer with fading and movement effects
    text = Text("The quick brown fox", (0, 0), fontsize='40')
    text.effects.append(Fade(1, 30, 10))
    text.effects.append(Movement(1, 30, (100, 100), (500, 300)))
    flip.add(text)

    flip.render(1)
    flip.render(5)
    flip.render(15)

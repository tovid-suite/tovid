#! /usr/bin/env python
# flipbook.py

import os
import sys
from libtovid.animation import Keyframe
from libtovid.mvg import Drawing
from libtovid import layer
from libtovid import effect
from libtovid.VideoUtils import images_to_video

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    """
    def __init__(self, frames=30, size=(720, 576)):
        """Create a flipbook of the given length in frames, at the given
        resolution."""
        self.frames = frames
        self.size = size
        self.layers = []
        self.drawings = []

    def add(self, layer, position=(0, 0)):
        """Add a Layer to the flipbook."""
        self.layers.append((layer, position))

    def render(self, frame=1):
        """Render a Drawing for the given frame."""
        print "Rendering Flipbook frame %s" % frame
        # Render the drawing
        drawing = self.drawing(frame)
        drawing.render()

    def drawing(self, frame):
        """Get a Drawing of the given frame"""
        drawing = Drawing(self.size)
        # Write MVG header stuff
        drawing.push()
        drawing.viewbox((0, 0), self.size)
        # Draw each layer
        for layer, position in self.layers:
            drawing.push()
            drawing.translate(position)
            layer.draw_on(drawing, frame)
            drawing.pop()
        drawing.pop()
        return drawing

    def render_video(self, m2v_file):
        """Render the flipbook to an .m2v video stream file."""
        # TODO: Get rid of temp-dir hard-coding
        tmp = '/tmp/flipbook'
        try:
            os.mkdir(tmp)
        except:
            print "Temp dir %s already exists, overwriting."
        # Write each Flipbook frame as an .mvg file, then convert to .jpg
        frame = 1
        while frame < self.frames:
            drawing = self.drawing(frame)
            print "Drawing for frame: %s" % frame
            print drawing.code(editing=False)
            drawing.save('%s/flip_%04d.mvg' % (tmp, frame))
            # jpeg2yuv likes frames to start at 0
            drawing.save_image('%s/%08d.jpg' % (tmp, frame - 1))
            frame += 1
        images_to_video(tmp, m2v_file, 'dvd', 'pal')


# Demo
if __name__ == '__main__':
    print "Flipbook demo"

    flip = Flipbook(90)

    # Background image
    bgd = layer.Background('grey')
    flip.add(bgd)

    # Text layer with fade, movement, and spectrum effects
    text1 = layer.Text("Spectrum effect demo")
    text1.add_effect(effect.Spectrum(1, 90))
    flip.add(text1, (20, 30))

    text2 = layer.Text("Fade effect demo")
    text2.add_effect(effect.Fade(30, 90, 20))
    flip.add(text2, (20, 60))

    text3 = layer.Text("Movement effect demo")
    text3.add_effect(effect.Movement(20, 70, (0, 0), (20, 5)))
    flip.add(text3, (20, 90))

    text4 = layer.Text("Keyframed fill opacity demo", color='lightgreen')
    pulse = [Keyframe(1, 0.2),
              Keyframe(20, 1.0),
              Keyframe(40, 0.2),
              Keyframe(60, 1.0),
              Keyframe(80, 0.5),
              Keyframe(90, 1.0)]
    text4.add_effect(effect.KeyFunction(Drawing.fill_opacity, pulse))
    flip.add(text4, (20, 120))

    pulse_graph = layer.InterpolationGraph(pulse)
    flip.add(pulse_graph, (20, 150))

    # Video clip
    #clip = layer.VideoClip(video, (320, 240))
    #clip.rip_frames(0, 90)
    #clip.effects.append(effect.Fade(1, 90, 20))
    #flip.add(clip, (260, 200))
    
    # Render the final video
    flip.render_video('/tmp/flipbook.m2v')
    print "Output in /tmp/flipbook.m2v (we hope!)"


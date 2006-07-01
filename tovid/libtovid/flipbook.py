#! /usr/bin/env python
# flipbook.py

__all__ = ['Flipbook']

import os
import sys
from libtovid.animation import Keyframe
from libtovid.mvg import Drawing
from libtovid import layer
from libtovid import effect
from libtovid.media import MediaFile

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

    def render_video(self, out_prefix):
        """Render the flipbook to an .m2v video stream file."""
        # TODO: Get rid of temp-dir hard-coding
        tmp = "%s_frames" % out_prefix
        m2v_file = "%s.m2v" % out_prefix
        if os.path.exists(tmp):
            print "Temp dir %s already exists, overwriting." % tmp
            os.system('rm -rf %s' % tmp)
        os.mkdir(tmp)

        # Write each Flipbook frame as an .mvg file, then convert to .jpg
        frame = 1
        while frame <= self.frames:
            print "Drawing frame %s of %s" % (frame, self.frames)
            drawing = self.drawing(frame)
            print drawing.code(editing=False)
            drawing.save('%s/flip_%04d.mvg' % (tmp, frame))
            # jpeg2yuv likes frames to start at 0
            drawing.save_image('%s/%08d.jpg' % (tmp, frame - 1))
            frame += 1
        video = MediaFile(m2v_file)
        video.encode(tmp, m2v_file, 'dvd', 'pal')
        print "Output file is: %s" % m2v_file


def draw_text_demo(flipbook):
    """Draw a demonstration of Text layers with various effects."""
    # Background image
    bgd = layer.Background('black')
    flipbook.add(bgd)

    text1 = layer.Text("Spectrum effect demo")
    text1.add_effect(effect.Spectrum(1, 90))
    flipbook.add(text1, (20, 30))
    flipbook.add(text1, (25, 35))
    flipbook.add(text1, (30, 40))

    text2 = layer.Text("Fade effect demo")
    text2.add_effect(effect.Fade(30, 90, 20))
    flipbook.add(text2, (20, 60))

    text3 = layer.Text("Movement effect demo")
    text3.add_effect(effect.Movement(20, 70, (0, 0), (20, 5)))
    flipbook.add(text3, (20, 90))

    # Keyframed opacity demos, using both linear and cosine interpolation
    pulse = [Keyframe(1, 0.2),
              Keyframe(20, 1.0),
              Keyframe(40, 0.2),
              Keyframe(60, 1.0),
              Keyframe(80, 0.5),
              Keyframe(90, 1.0)]
    # Text Layers
    text_linear = layer.Text("Keyframed opacity (linear)", color='lightgreen')
    text_cosine = layer.Text("Keyframed opacity (cosine)", color='lightgreen')
    # Effects
    fade_linear = effect.KeyFunction(Drawing.fill_opacity, pulse, 'linear')
    fade_cosine = effect.KeyFunction(Drawing.fill_opacity, pulse, 'cosine')
    # Graph of the keyframe effects
    graph_linear = layer.InterpolationGraph(pulse, method='linear')
    graph_cosine = layer.InterpolationGraph(pulse, method='cosine')
    # Add effects to the text layers
    text_linear.add_effect(fade_linear)
    text_cosine.add_effect(fade_cosine)
    # Add layers to the flipbook
    flipbook.add(text_linear, (20, 120))
    flipbook.add(graph_linear, (20, 150))
    flipbook.add(text_cosine, (320, 120))
    flipbook.add(graph_cosine, (320, 150))

# Demo
if __name__ == '__main__':
    
    flip = Flipbook(10)

    draw_text_demo(flip)

    # Video clip
    #clip = layer.VideoClip(video, (320, 240))
    #clip.rip_frames(0, 90)
    #clip.effects.append(effect.Fade(1, 90, 20))
    #flip.add(clip, (260, 200))
    
    # Render the final video
    flip.render_video('/tmp/flipbook')


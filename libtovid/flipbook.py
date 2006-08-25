#! /usr/bin/env python
# flipbook.py

"""This module provides the Flipbook class.

Run this module standalone for a demonstration:

    $ python libtovid/flipbook.py

Much like a paper flipbook made of many individual drawings, the Flipbook class
has a collection of Drawing objects (from libtovid/renderers/mvg_render.py) that,
when displayed in sequence, make up an animation or video.

To use this module interactively, run 'python' from the command-line, and do:

    >>> from libtovid.flipbook import Flipbook

To create a Flipbook with 90 frames, at 720x480 resolution, do:

    >>> flipbook = Flipbook(90, (720, 480))

All drawing upon a Flipbook is achieved through the use of layers
(libtovid/layer.py). To use them, import the layer module:

    >>> from libtovid import layer

You can add layers to a Flipbook on-the-fly:

    >>> flipbook.add(layer.Background('black'))
    >>> flipbook.add(layer.Text("Hello, world"))

Or, create layers separately before adding them to the Flipbook:

    >>> text = Text("Elephant talk")
    >>> flipbook.add(text)

This latter approach is useful if you plan to apply animation effects to the
Layer. For this, effects classes (libtovid/effect.py) may be applied. First,
import:

    >>> from libtovid import effect

Now, say we want the text "Elephant talk" to move across the screen, say from
(100, 100) to (500, 100) over the course of the first 90 frames. The
effect.Movement class does the trick:

    >>> text.add_effect(effect.Movement(1, 90, (100, 100), (500, 100)))

You can preview a specific frame of the Flipbook by calling render():

    >>> flipbook.render(50)

Or, you can generate all frames and create an .m2v video stream file by calling
render_video():

    >>> flipbook.render_video('/tmp/flipbook')

See the demo below for more on what's possible with Flipbooks.
"""

__all__ = ['Flipbook']

import os
import sys
from libtovid.animation import Keyframe
from libtovid.render.mvg import Drawing
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

    def render_video(self, out_prefix, format, tvsys):
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
        video.encode_frames(tmp, m2v_file, format, tvsys)
        print "Output file is: %s" % m2v_file


def draw_text_demo(flipbook, last_frame):
    """Draw a demonstration of Text layers with various effects."""
    assert isinstance(flipbook, Flipbook)
    # Background image
    bgd = layer.Background('black')
    flipbook.add(bgd)

    text1 = layer.Text("Spectrum effect demo")
    text1.add_effect(effect.Spectrum(1, last_frame))
    flipbook.add(text1, (20, 30))

    text2 = layer.Text("Fade effect demo")
    text2.add_effect(effect.Fade(1, last_frame, last_frame / 4))
    flipbook.add(text2, (20, 60))

    text3 = layer.Text("Movement effect demo")
    text3.add_effect(effect.Movement(1, last_frame, (0, 0), (300, 50)))
    flipbook.add(text3, (20, 90))

    # Keyframed opacity demos, using both linear and cosine interpolation
    pulse = [Keyframe(1, 0.2),
              Keyframe(last_frame * 2/10, 1.0),
              Keyframe(last_frame * 4/10, 0.2),
              Keyframe(last_frame * 6/10, 1.0),
              Keyframe(last_frame * 8/10, 0.5),
              Keyframe(last_frame, 1.0)]
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
    flipbook.add(text_linear, (20, 150))
    flipbook.add(graph_linear, (20, 180))
    flipbook.add(text_cosine, (340, 150))
    flipbook.add(graph_cosine, (340, 180))

# Demo
if __name__ == '__main__':
    if len(sys.argv) > 1:
        frames = int(sys.argv[1])
    else:
        frames = 90
    flip = Flipbook(frames, (720, 480))

    draw_text_demo(flip, frames)

    # Video clip
    #clip = layer.VideoClip(video, (320, 240))
    #clip.rip_frames(0, 90)
    #clip.effects.append(effect.Fade(1, 90, 20))
    #flip.add(clip, (260, 200))
    
    # Render the final video
    flip.render_video('/tmp/flipbook', 'dvd', 'ntsc')


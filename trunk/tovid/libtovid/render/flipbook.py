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
from libtovid.render.animation import Keyframe
from libtovid.render.drawing import Drawing
from libtovid.render import layer, effect, standards
from libtovid.media import MediaFile
from libtovid.transcode import encode

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    """
    def __init__(self, frames, format, tvsys):
        """Create a flipbook of the given length in frames, at the given
        resolution.

        frames -- number of frames at the standard's framerate.
        format -- one of 'dvd', 'dvd-vcd', etc.. look in the standards
                  module.
        tvsys -- one of 'ntsc', 'pal', etc.. look in the standards module.
        """
        self.frames = frames
        # TODO: We'll need aspect ratio here.. 4:3 or 16:9 anamorphic ?
        self.format = format
        self.tvsys = tvsys
        self.layers = []
        self.drawings = []

        w, h = standards.get_resolution(format, tvsys)
        dx, dy = standards.get_scaling(format, tvsys)
        self.width = int(w / dx)
        self.height = int(h / dy)
        self.size = (self.width, self.height)

    def add(self, layer, position=(0, 0)):
        """Add a Layer to the flipbook."""
        self.layers.append((layer, position))

    def render(self, frame=1):
        """Render a Drawing for the given frame.

        Mostly for debugging."""
        print "Rendering Flipbook frame %s" % frame
        # Render the drawing
        drawing = self.get_drawing(frame)
        drawing.render()

    def get_drawing(self, frame):
        """Get a Drawing of the given frame"""
        drawing = Drawing(standards.get_resolution(self.format, self.tvsys))
        # Set scaling to cope with aspect ratios:
        drawing.base_scaling(standards.get_scaling(self.format, self.tvsys))
        
        # Draw each layer
        for layer, position in self.layers:
            drawing.save()
            drawing.translate(position)
            # Apply effects and draw
            layer.draw_with_effects(drawing, frame)
            drawing.restore()

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
            drawing = self.get_drawing(frame)
            # jpeg2yuv likes frames to start at 0
            drawing.save_png('%s/%08d.png' % (tmp, frame - 1))
            frame += 1
        video = MediaFile(m2v_file)
        
        encode.encode_frames(tmp, m2v_file, self.format, self.tvsys)
        print "Output file is: %s" % m2v_file
        encode.encode_audio(video, None, [])


def draw_text_demo(flipbook, last_frame):
    """Draw a demonstration of Text layers with various effects."""
    assert isinstance(flipbook, Flipbook)
    # Background image
    bgd = layer.Background('black')
    flipbook.add(bgd)

    text1 = layer.Text(u"Spectrum effect demo", color=None)
    text1.add_effect(effect.Spectrum(1, last_frame))
    flipbook.add(text1, (20, 30))

    #text2 = layer.Text(u"FadeInOut effect demo")
    #text2.add_effect(effect.FadeInOut(1, last_frame, last_frame / 4))
    #flipbook.add(text2, (20, 60))

    text3 = layer.Text(u"Movement effect demo")
    text3.add_effect(effect.Movement(1, last_frame, (0, 0), (300, 50)))
    flipbook.add(text3, (20, 90))

    text4 = layer.Text(u"Whirl effect demo", color=None, align='center')
    k = [Keyframe(0, 0),
         Keyframe(30, 0),
         Keyframe(40, 15),
         Keyframe(45, -10),
         Keyframe(50, 10),
         Keyframe(55, -2),
         Keyframe(60, 0)]
    text4.add_effect(effect.Whirl(k, center=(25, 10), units='deg'))
    text4.add_effect(effect.Colorfade(1, last_frame, (1.0,0,0), (0, 1.0, 0)))
    flipbook.add(text4, (340, 350))

    text5 = layer.Text(u'Whirl effect demo2 ', color='white', align="center")
    k2 = [Keyframe(0,0),
          Keyframe(last_frame, 720)]
    text5.add_effect(effect.Whirl(k2, center=(25, 10), units='deg'))
    flipbook.add(text5, (450, 400))

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
    eff_linear = effect.Fade(pulse, 'linear')
    eff_cosine = effect.Fade(pulse, 'cosine')
    # Graph of the keyframe effects
    graph_linear = layer.InterpolationGraph(pulse, method='linear')
    graph_cosine = layer.InterpolationGraph(pulse, method='cosine')
    # Add effects to the text layers
    text_linear.add_effect(eff_linear)
    text_cosine.add_effect(eff_cosine)
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
    flip = Flipbook(frames, 'dvd', 'ntsc')

    draw_text_demo(flip, frames)

    # Video clip
    #clip = layer.VideoClip(video, (320, 240))
    #clip.rip_frames(0, 90)
    #clip.effects.append(effect.Fade(1, 90, 20))
    #flip.add(clip, (260, 200))
    
    # Render the final video
    flip.render_video('/tmp/flipbook')

    print "To create demo video (for distribution), run:"
    print """cat /tmp/flipbook.m2v /tmp/flipbook.m2v /tmp/flipbook.m2v /tmp/flipbook.m2v /tmp/flipbook.m2v | ffmpeg2theora --aspect 4:3 --title "libtovid Flipbook demo (flipbook.py)" -o /dev/stdout - > FlipbookDemo.ogm """


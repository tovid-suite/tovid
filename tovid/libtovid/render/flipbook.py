#! /usr/bin/env python
# flipbook.py

"""This module provides the Flipbook class, a collection of drawings that, when
displayed in sequence, make up an animation or video.

Run this module standalone for a demonstration:

    $ python flipbook.py

To use this module interactively, run 'python' from the command-line, and do:

    >>> from libtovid.render.flipbook import Flipbook

To create a Flipbook 10 seconds long with 'dvd' and 'ntsc' standards, do:

    >>> flipbook = Flipbook(10, 'dvd', 'ntsc', '4:3')

You can retrieve the canvas width and height with:

    >>> flipbook.canvas
    (640, 480)
    >>> flipbook.w
    640
    >>> flipbook.h
    480

All drawing upon a Flipbook is achieved through the use of layers (layer.py).
To use them, import the layer module:

    >>> from libtovid.render import layer

You can add layers to a Flipbook on-the-fly:

    >>> flipbook.add(layer.Background('black'))
    >>> flipbook.add(layer.Text("Hello, world"))

Or, create layers separately before adding them to the Flipbook:

    >>> text = Text("Elephant talk")
    >>> flipbook.add(text)

This latter approach is useful if you plan to apply animation effects to the
Layer. For this, effects classes (effect.py) may be applied. First, import:

    >>> from libtovid.render import effect

Now, say we want the text "Elephant talk" to move across the screen, say from
(100, 100) to (500, 100) over the course of the first 90 frames. The
effect.Movement class does the trick:

    >>> text.add_effect(effect.Movement(1, 90, (100, 100), (500, 100)))

You can preview a specific frame of the Flipbook by calling render():

    >>> flipbook.render(50)

Or, you can generate all frames and create an .m2v video stream file by calling
render_video():

    >>> filename = flipbook.render_video()

See the demo below for more on what's possible with Flipbooks.
"""

__all__ = ['Flipbook']

import os
import sys
import time
import math
import cairo
import shutil
import random
from libtovid.render.animation import Keyframe
from libtovid.render.drawing import Drawing, write_ppm, write_png, interlace_drawings
from libtovid.render import layer, effect
from libtovid import standard
from libtovid.media import MediaFile, standard_media
from libtovid.backend import mplex, mplayer
from libtovid import encode
from libtovid import utils

class Flipbook:
    """A collection of Drawings that together comprise an animation.
    """
    def __init__(self, seconds, format, tvsys, aspect='4:3', interlaced=False):
        """Create a flipbook of the given length in seconds, at the given
        resolution.

            seconds: Length of flipbook playback in seconds
            format:  'dvd', 'vcd', 'svcd', 'dvd-vcd', or 'half-dvd'
            tvsys:   'ntsc' or 'pal'
            aspect:  '4:3' or '16:9' (the latter only for format='dvd')
                     (default: '4:3')
            interlaced: True/False. When enabled, the framerate will be
                     doubled, but only half the frames (twice the fields)
                     will be rendered.

        Once you've created the Flipbook, you can grab the dimensions
        in with the property:

            flipbook.canvas as (width, height)

        and with the two properties:

            flipbook.w (width)
            flipbook.h (height)
        """
        self.tmpdir = '/tmp'
        if 'TMPDIR' in os.environ:
            self.tmpdir = os.environ['TMPDIR']
        self.seconds = float(seconds)
        self.fps = standard.fps(tvsys)
        self.fpsratio = standard.fpsratio(tvsys)
        if (interlaced):
            self.fps *= 2
        self.interlaced = interlaced
        self.frames = int(seconds * self.fps)
        self.output_size = standard.resolution(format, tvsys)
        # TODO: We'll need aspect ratio here.. 4:3 or 16:9 anamorphic ?
        self.format = format
        self.tvsys = tvsys
        if (aspect not in ['4:3', '16:9']):
            raise ValueError, "aspect must be: '4:3' or '16:9'"
        self.aspect = aspect
        self.widescreen = False
        if (aspect == '16:9'):
            self.widescreen = True
            
        self.canvas = self._get_canvas_size()
        self.w = self.canvas[0]
        self.h = self.canvas[1]

        # Empty layers, and currently no drawings.
        self.layers = []
        self.drawings = []

        self._called_init_childs = False


    ### Child-parent handling
    def _init_childs(self):
        """Give access to all descendant layers and effects to their parents.

        In layers, you can access your parent layer (if sublayed) with:
            layer._parent_layer
        and to the top Flipbook object with:
            layer._parent_flipbook

        This function gets called just before rendering a video with
            render_video()

        It's also called in emergency if you call directly get_drawing().
        """
        for x in range(0, len(self.layers)):
            self.layers[x][0]._init_parent_flipbook(self)
            self.layers[x][0]._init_childs()

        self._called_init_childs = True
        
        
    # Utility functions

    def stof(self, seconds):
        """Return the number of frames to the specified time (in seconds)"""
        return int(self.fps * float(seconds))

    def _get_canvas_size(self):
        ow = self.output_size[0]
        oh = self.output_size[1]
        a = self.aspect.split(':')

        # Calculate the square pixels canvas size based on aspect ratio
        # and intended output size.
        x = float(a[0]) * float(oh) / float(a[1])
        # Make sure they are factor of '2'
        nw = int(math.ceil(x / 2.0) * 2)

        # We'll always change only the width, like it seems the standard,
        # since on TVs, the number of *lines* can't change (when interlacing
        # is into business)
        return (nw, oh)
        

    def add(self, layer, position=(0, 0)):
        """Add a Layer to the flipbook."""
        self.layers.append((layer, position))

    def render(self, frame=1):
        """Render the given frame."""

        print "DEPRECATED FUNCTION."
        exit()
        
        filename = "/tmp/flipbook_%s.png" % frame
        print "Rendering Flipbook frame %s to %s" % (frame, filename)
        drawing = self.get_drawing(frame)

        drawing.save_png(filename, self.output_size[0], self.output_size[1])

    def get_drawing(self, frame):
        """Get a Drawing of the given frame

        TODO: 0-based or 1-based ?
        """

        # Make sure all layers and effects has been initialized with parents.
        if (not self._called_init_childs):
            self._init_childs()
            
        drawing = Drawing(self.canvas[0], self.canvas[1])
        # Draw each layer
        for layer, position in self.layers:
            drawing.save()
            drawing.translate(position[0], position[1])
            # Apply effects and draw
            layer.draw_with_effects(drawing, frame)
            drawing.restore()
        return drawing


    def render_video(self, out_filename=None):
        """Render the flipbook to an .m2v video stream file.

            out_filename:    Filename for output.
                             If not specified, a temporary filename
                             will be given, and returned from the function.
        
        Return the filename of the output, in both cases.
        """
        ## Make sure layers and effects have been initialized with parents.
        self._init_childs()

        #
        # if self.tmpdir = /tmp, we get:
        # /tmp
        # /tmp/flipbook-120391232-work/
        # /tmp/flipbook-120391232-work/bunch-of-files..m2v, .ac3, etc.
        # /tmp/flipbook-120391232.mpg -> final output..
        #
        
        tmp_prefix = '';tmp_workdir = '';
        while 1:
            rnd = random.randint(1000000, 9999999)
            tmp_prefix = "%s/flipbook-%s" % (self.tmpdir, rnd)
            tmp_workdir = "%s-work" % (tmp_prefix)

            if not os.path.exists(tmp_workdir):
                break

        # In case no filename has been specified.
        if not out_filename:
            out_filename = "%s.mpg" % tmp_workdir

        os.mkdir(tmp_workdir)

        # Encode the frames to an .m2v file
        m2v_file = "%s/video.m2v" % tmp_workdir
        ac3_file = "%s/audio.ac3" % tmp_workdir


        try:
            cairo.ImageSurface.get_data

            pngorpnm = 'ppmtoy4m -F %s -A %s -Ip -B -S 420mpeg2' % \
                     (self.fpsratio, self.aspect)
            _write_img = write_ppm  # set write function just below
        except:
            pngorpnm = 'ppmtoy4m -F %s -A %s -Ip -S 420mpeg2' % \
                     (self.fpsratio, self.aspect)
            _write_img = write_png
            
        # Cinelerra params: -b 0 -q 5 -a 2 -F 4 -I 0 -M 2 -f 8 -R 0
        # TODO: move this to encode.py
        # -M (multi-threading, num CPUs)
        #
        # -b 0 -q 5
        #    or
        # -b 7500
        pipe = os.popen("%s | mpeg2enc -q 5 -g 45 -G 45 -f 8 -a 2 -I 0 -o '%s'" % (pngorpnm,  m2v_file), 'w')
        
        frame = 1
        while frame <= self.frames:
            print "Drawing frame %s of %s" % (frame, self.frames)
            # Il faudra ici sauver DEUX drawing si on est en mode entrelacé, puis
            # les combiner en UN drawing avant de rendre en .PNG.
            # Entre les deux, on alterne les MASKS, ligne à ligne, etc..
            if (self.interlaced):
                draw1 = self.get_drawing(frame)
                frame += 1
                draw2 = self.get_drawing(frame)

                drawing = interlace_drawings(draw1, draw2)
            else:
                drawing = self.get_drawing(frame)

            # jpeg2yuv likes frames to start at 0
                _write_img(drawing, pipe,
                           self.output_size[0], self.output_size[1],
                           tmp_workdir)
                
            frame += 1

        print "Closing encoder. Output to %s" % out_filename
        pipe.close()

        print "Waiting for encoder to finish..."
        time.sleep(0.5)

        os.system("ls -al %s" % m2v_file)
        os.system("cp %s /tmp/go.m2v" % m2v_file)
        vidonly = mplayer.identify(m2v_file)

        # Fix length
        vidonly.length = float(self.seconds)

        outvid = MediaFile(out_filename, self.format, self.tvsys)
        outvid.aspect = self.aspect
        # Important to render 16:9 video correctly.
        outvid.widescreen = self.widescreen

        print "Running audio encoder..."
        encode.encode_audio(vidonly, ac3_file, outvid)

        print "Mplex..."
        mplex.mux(m2v_file, ac3_file, outvid)

        # Clean up
        print "Cleaning up %s ..." % tmp_workdir
        shutil.rmtree(tmp_workdir)

        print "Output: %s" % out_filename
        return out_filename


        

def draw_text_demo(flipbook):
    """Draw a demonstration of Text layers with various effects."""
    assert isinstance(flipbook, Flipbook)

    last_frame = flipbook.frames
    
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
    text4.add_effect(effect.Colorfade(1, last_frame, (1.0, 0, 0), (0, 1.0, 0)))
    flipbook.add(text4, (340, 350))

    text5 = layer.Text(u'Whirl effect demo2 ', color='white', align="center")
    k2 = [Keyframe(0, 0),
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
    start_time = time.time() # Benchmark

    if len(sys.argv) > 1:
        seconds = int(sys.argv[1])
    else:
        seconds = 3
    flip = Flipbook(seconds, 'dvd', 'ntsc')

    draw_text_demo(flip)

    # Video clip
    #clip = layer.VideoClip(video, (320, 240))
    #clip.rip_frames(0, 90)
    #clip.effects.append(effect.Fade(1, 90, 20))
    #flip.add(clip, (260, 200))
    
    # Render the final video
    filename = flip.render_video('/tmp/flipbook.mpg')

    print "Took %f seconds to render: %s" % (time.time() - start_time, filename)
    

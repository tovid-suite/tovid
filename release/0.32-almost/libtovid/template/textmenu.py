__all__ = ['TextMenu']

from libtovid import cli
from libtovid import deps
from libtovid import log
from libtovid.backend import spumux

class TextMenu:
    """Simple menu with selectable text titles. For now, basically a clone
    of the classic 'makemenu' output.
    """
    def __init__(self, target, titles, style):
        deps.require('convert composite ppmtoy4m sox ffmpeg mpeg2enc')
        self.target = target
        self.titles = titles
        self.style = style
        self.basename = self.target.filename
        self.bg_canvas = self.basename + '.bg_canvas.png'
        self.fg_canvas = self.basename + '.fg_canvas.png'
        self.fg_highlight = self.basename + '.fg_highlight.png'
        self.fg_selection = self.basename + '.fg_selection.png'


    def generate(self):
        """Generate the menu.
        """
        # TODO: Store intermediate images in a temp folder
        log.info("Creating a menu with %s titles" % len(self.titles))
        self.build_reusables()
        log.info("Drawing a background canvas...")
        self.draw_background_canvas()
        log.info("Drawing the background layer...")
        self.draw_background_layer()
        log.info("Drawing the highlight layer...")
        self.draw_highlight_layer()
        log.info("Drawing the selection layer...")
        self.draw_selection_layer()
        log.info("Generating the video stream...")
        self.gen_video()
        log.info("Generating the audio stream...")
        self.gen_audio()
        log.info("Multiplexing audio and video streams...")
        self.gen_mpeg()
        log.info("Multiplexing subtitles into .mpg...")
        self.mux_subtitles()


    def build_reusables(self):
        """Assemble some re-usable ImageMagick command snippets.
        For now, just create an ImageMagick draw command for all title text
        for placing labels and highlights.
        """
        spacing = 30    # Pixel spacing between lines
        y = 0           # Current y-coordinate
        y2 = spacing    # Next y-coordinate
        titlenum = 1        # Title number (for labeling)
        labels = ''
        buttons = ''
        for title in self.titles:
            log.info("Adding '%s'" % title)
            # TODO: Escape special characters in title

            # For VCD, number the titles
            if self.target.format == 'vcd':
                labels += " text 0,%s '%s. %s' " % (y, titlenum, title)
            # Others use title string alone
            else:
                labels += " text 15,%s '%s'" % (y, title)
                buttons += " text 0,%s '>'" % y

            # Increment y-coordinates and title number
            y = y2
            y2 += spacing
            titlenum += 1
        self.im_labels = labels
        self.im_buttons = buttons


    def draw_background_canvas(self):
        """Draw background canvas.
        """
        # Generate default blue-black gradient background
        # TODO: Implement -background
        convert = cli.Command('convert',
            '-size', '%sx%s' % self.target.expand,
            'gradient:blue-black',
            '-gravity', 'center',
            '-matte', self.bg_canvas)
        convert.run()


    def draw_background_layer(self):
        """Draw the background layer for the menu, including static title text.
        """
        # Draw text titles on a transparent background.
        convert = cli.Command('convert',
            '-size', '%sx%s' % self.target.scale,
            'xc:none', '+antialias',
            '-font', self.style.font,
            '-pointsize', self.style.fontsize,
            '-fill', self.style.textcolor,
            '-stroke', 'black',
            '-strokewidth', 3,
            '-draw', 'gravity %s %s' % (self.style.align, self.im_labels),
            '-stroke', 'none',
            '-draw', 'gravity %s %s' % (self.style.align, self.im_labels),
            self.fg_canvas)
        convert.run()
        # Composite text over background
        composite = cli.Command('composite',
            '-compose', 'Over',
            '-gravity', 'center',
            self.fg_canvas, self.bg_canvas,
            '-depth', 8, '%s.ppm' % self.basename)
        composite.run()


    def draw_highlight_layer(self):
        """Draw menu highlight layer, suitable for multiplexing.
        """
        # Create text layer (at safe-area size)
        convert = cli.Command('convert',
            '-size', '%sx%s' % self.target.scale,
            'xc:none', '+antialias',
            '-font', self.style.font,
            '-weight', 'bold',
            '-pointsize', self.style.fontsize,
            '-fill', self.style.highlightcolor,
            '-draw', 'gravity %s %s' % (self.style.align, self.im_buttons),
            '-type', 'Palette', '-colors', 3,
            self.fg_highlight)
        convert.run()
        # Pseudo-composite, to expand layer to target size
        composite = cli.Command('composite',
            '-compose', 'Src',
            '-gravity', 'center',
            self.fg_highlight, self.bg_canvas,
            '%s.hi.png' % self.basename)
        composite.run()


    def draw_selection_layer(self):
        """Draw menu selections on a transparent background."""
        # Create text layer (at safe-area size)
        convert = cli.Command('convert',
            '-size', '%sx%s' % self.target.scale,
            'xc:none', '+antialias',
            '-font', self.style.font,
            '-weight', 'bold',
            '-pointsize', self.style.fontsize,
            '-fill', self.style.selectcolor,
            '-draw', 'gravity %s %s' % (self.style.align, self.im_buttons),
            '-type', 'Palette', '-colors', 3,
            self.fg_selection)
        convert.run()
        # Pseudo-composite, to expand layer to target size
        composite = cli.Command('composite',
            '-compose', 'Src',
            '-gravity', 'center',
            self.fg_selection, self.bg_canvas,
            '%s.sel.png' % self.basename)
        composite.run()


    def gen_video(self):
        """Generate a video stream (mpeg1/2) from the menu background image.
        """
        # ppmtoy4m part
        ppmtoy4m = cli.Command('ppmtoy4m', '-S', '420mpeg2')
        if self.target.tvsys == 'ntsc':
            ppmtoy4m.add('-A', '10:11', '-F', '30000:1001')
        else:
            ppmtoy4m.add('-A', '59:54', '-F', '25:1')
        # TODO: Remove hardcoded frame count
        ppmtoy4m.add('-n', 90)
        ppmtoy4m.add('-r', '%s.ppm' % self.basename)

        # mpeg2enc part
        mpeg2enc = cli.Command('mpeg2enc', '-a', 2)
        # PAL/NTSC
        if self.target.tvsys == 'ntsc':
            mpeg2enc.add('-F', 4, '-n', 'n')
        else:
            mpeg2enc.add('-F', 3, '-n', 'p')
        # Use correct format flags and filename extension
        if self.target.format == 'vcd':
            self.vstream = '%s.m1v' % self.basename
            mpeg2enc.add('-f', 1)
        else:
            self.vstream = '%s.m2v' % self.basename
            if self.target.format == 'dvd':
                mpeg2enc.add('-f', 8)
            elif self.target.format == 'svcd':
                mpeg2enc.add('-f', 4)
        mpeg2enc.add('-o', self.vstream)
        pipe = cli.Pipe(ppmtoy4m, mpeg2enc)
        pipe.run()


    def gen_audio(self):
        """Generate an audio stream (mp2/ac3) from the given audio file
        (or generate silence instead).
        """
        if self.target.format in ['vcd', 'svcd']:
            self.astream = "%s.mp2" % self.basename
        else:
            self.astream = "%s.ac3" % self.basename
        ffmpeg = cli.Command('ffmpeg')
        # TODO: Support including an audio stream.
        # For now, generate 4-second silence
        ffmpeg.add('-f', 's16le',
                   '-i', '/dev/zero',
                   '-t', 4)
        ffmpeg.add('-ac', 2, '-ab', 224,
                   '-ar', self.target.samprate,
                   '-acodec', self.target.acodec,
                   '-y',
                   self.astream)
        ffmpeg.run()


    def gen_mpeg(self):
        """Multiplex audio and video streams to create an mpeg.
        """
        mplex = cli.Command('mplex', '-o', '%s.mpg' % self.basename)
        # Format flags
        if self.target.format == 'vcd':
            mplex.add('-f', 1)
        else:
            # Variable bitrate
            mplex.add('-V')
            if self.target.format == 'dvd':
                mplex.add('-f', 8)
            elif self.target.format == 'svcd':
                mplex.add('-f', 4)
        mplex.add(self.astream, self.vstream)
        mplex.run()


    def mux_subtitles(self):
        """Multiplex the output video with highlight and selection
        subtitles, so the resulting menu can be navigated.
        """
        # TODO: Fix all this silly hardcoding of filenames (duplicated above)
        menu_mpg = self.basename + '.mpg'
        image = None
        select = self.basename + '.sel.png'
        highlight = self.basename + '.hi.png'
        spumux.add_subpictures(menu_mpg, image, select, highlight)


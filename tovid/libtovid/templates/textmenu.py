#! /usr/bin/env python
# textmenu.py

__all__ = ['generate']

from libtovid.cli import Command, Pipe
from libtovid import deps
from libtovid import log

def generate(options):
    """Generate a menu with selectable text titles."""
    deps.require('convert composite ppmtoy4m sox ffmpeg mpeg2enc')
    TextMenu(options)


class TextMenu:
    """Simple menu with selectable text titles. For now, basically a clone
    of the classic 'makemenu' output.
    """
    def __init__(self, target, titles, style):
        self.options = options
        basename = target.filename
        # TODO: Store intermediate images in a temp folder
        self.bg_canvas = basename + '.bg_canvas.png'
        self.fg_canvas = basename + '.fg_canvas.png'
        self.fg_highlight = basename + '.fg_highlight.png'
        self.fg_selection = basename + '.fg_selection.png'
        print "Creating a menu with %s titles" % len(titles)
        self.build_reusables(target, titles)
        self.draw_background_canvas(target)
        self.draw_background_layer(target, style)
        self.draw_highlight_layer(target, style)
        self.draw_selection_layer(target, style)
        self.gen_video(target)
        self.gen_audio(target)
        self.gen_mpeg(target)
        self.script.run()

    def build_reusables(self, target, titles):
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
        for title in titles:
            print "Adding '%s'" % title
            # TODO: Escape special characters in title
            
            # For VCD, number the titles
            if target.format == 'vcd':
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
    
    def draw_background_canvas(self, target):
        """Draw background canvas."""
        # Generate default blue-black gradient background
        # TODO: Implement -background
        convert = Command('convert',
            '-size', '%sx%s' % target.expand,
            'gradient:blue-black',
            '-gravity', 'center',
            '-matte', self.bg_canvas)
        convert.run()
    
    def draw_background_layer(self, target, style):
        """Draw the background layer for the menu, including static title text.
        """
        # Draw text titles on a transparent background.
        convert = Command('convert',
            ' -size', '%sx%s' % target.scale,
            'xc:none', '-antialias',
            '-font', style.font,
            '-pointsize', style.fontsize,
            ' -fill', style.textcolor,
            '-stroke', 'black',
            '-strokewidth', 3,
            '-draw', 'gravity %s %s' % (style.align, self.im_labels),
            '-stroke', 'none',
            '-draw', 'gravity %s %s' % (style.align, self.im_labels),
            self.fg_canvas)
        convert.run()
        # Composite text over background
        composite = Command('composite',
            '-compose', 'Over',
            '-gravity', 'center',
            self.fg_canvas, self.bg_canvas,
            '-depth', 8, '%s.ppm' % target.filename)
        composite.run()
    
    def draw_highlight_layer(self, target, style):
        """Draw menu highlight layer, suitable for multiplexing."""
        # Create text layer (at safe-area size)
        convert = Command('convert',
            '-size', '%sx%s' % target.scale,
            'xc:none', '-antialias',
            '-font', style.font,
            '-weight', 'bold',
            '-pointsize', style.fontsize,
            '-fill', style.highlightcolor,
            '-draw', 'gravity %s %s' % (style.align, self.im_buttons),
            '-type', 'Palette', '-colors', 3,
            self.fg_highlight)
        convert.run()
        # Pseudo-composite, to expand layer to target size
        composite = Command('composite',
            '-compose', 'Src',
            '-gravity', 'center',
            self.fg_highlight, self.bg_canvas,
            '%s.hi.png' % target.filename)
        composite.run()
    
    def draw_selection_layer(self, target, style):
        """Draw menu selections on a transparent background."""
        # Create text layer (at safe-area size)
        convert = Command('convert',
            '-size', '%sx%s' % target.scale,
            'xc:none', '-antialias',
            '-font', style.font,
            '-weight', 'bold',
            '-pointsize', style.fontsize,
            '-fill', style.selectcolor,
            '-draw', 'gravity %s %s' % (style.align, self.im_buttons),
            '-type', 'Palette', '-colors', 3,
            self.fg_selection)
        convert.run()
        # Pseudo-composite, to expand layer to target size
        composite = Command('composite',
            '-compose', 'Src',
            '-gravity', 'center',
            self.fg_selection, self.bg_canvas,
            '%s.sel.png' % target.filename)
        composite.run()
    
    def gen_video(self, target):
        """Generate a video stream (mpeg1/2) from the menu background image.
        Corresp. to lines 495-502 of makemenu."""
        # ppmtoy4m part
        ppmtoy4m = Command('ppmtoy4m', '-S', '420mpeg2')
        if target.tvsys == 'ntsc':
            ppmtoy4m.add('-A', '10:11', '-F', '30000:1001')
        else:
            ppmtoy4m.add('-A', '59:54', '-F', '25:1')
        # TODO: Remove hardcoded frame count
        ppmtoy4m.add('-n', 90)
        ppmtoy4m.add('-r', '%s.ppm' % target.filename)
    
        # mpeg2enc part
        mpeg2enc = Command('mpeg2enc', '-a', 2)
        # PAL/NTSC
        if target.tvsys == 'ntsc':
            mpeg2enc.add('-F', 4, '-n', 'n')
        else:
            mpeg2enc.add('-F', 3, '-n', 'p')
        # Use correct format flags and filename extension
        if target.format == 'vcd':
            self.vstream = '%s.m1v' % target.filename
            mpeg2enc.add('-f', 1)
        else:
            self.vstream = '%s.m2v' % target.filename
            if target.format == 'dvd':
                mpeg2enc.add('-f', 8)
            elif target.format == 'svcd':
                mpeg2enc.add('-f', 4)
        mpeg2enc.add('-o', self.vstream)
        pipe = Pipe(ppmtoy4m, mpeg2enc)
        pipe.run()
    
    def gen_audio(self, target):
        """Generate an audio stream (mp2/ac3) from the given audio file
        (or generate silence instead).
        """
        if target.format in ['vcd', 'svcd']:
            self.astream = "%s.mp2" % target.filename
        else:
            self.astream = "%s.ac3" % target.filename
        ffmpeg = Command('ffmpeg')
        # TODO: Fix this
        # If audio file was provided, encode it
        #if self.options['audio']:
        #    cmd += ' -i "%s"' % self.options['audio']
        # Otherwise, generate 4-second silence
        #else:
        #    cmd += ' -f s16le -i /dev/zero -t 4'
        ffmpeg.add('-ac', 2, '-ab', 224,
                   '-ar', target.samprate,
                   '-acodec', target.acodec,
                   '-y',
                   self.astream)
        ffmpeg.run()
    
    def gen_mpeg(self, target):
        """Multiplex audio and video streams to create an mpeg.
        """
        mplex = Command('mplex', '-o', '%s.temp.mpg' % target.filename)
        # Format flags
        if target.format == 'vcd':
            mplex.add('-f', 1)
        else:
            # Variable bitrate
            mplex.add('-V')
            if target.format == 'dvd':
                mplex.add('-f', 8)
            elif target.format == 'svcd':
                mplex.add('-f', 4)
        mplex.add(self.astream, self.vstream)
        mplex.run()
    
    def mux_subtitles(self, target):
        """Multiplex the output video with highlight and selection
        subtitles, so the resulting menu can be navigated.
        """
        xml =  '<subpictures>\n'
        xml += '  <stream>\n'
        xml += '  <spu force="yes" start="00:00:00.00"\n'
        xml += '       highlight="%s.hi.png"\n' % target.filename
        xml += '       select="%s.sel.png"\n' % target.filename
        xml += '       autooutline="infer">\n'
        xml += '  </spu>\n'
        xml += '  </stream>\n'
        xml += '</subpictures>\n'
        try:
            xmlfile = open('%s.xml' % target.filename, 'w')
        except:
            log.error('Could not open file "%s.xml"' % target.filename)
        else:
            xmlfile.write(xml)
            xmlfile.close()
    
        # TODO: Make Command class (or an auxiliary class) support redirection
        # (or, even better, do it in subtitles.py so this function can be
        # shorter)
        spumux = 'spumux "%s.xml" < "%s.temp.mpg" > "%s.mpg"' % \
                (target.filename, target.filename, target.filename)
        # TODO: Run spumux command

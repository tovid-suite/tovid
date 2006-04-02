#! /usr/bin/env python
# textmenu.py

__all__ = ['generate']

from libtovid.cli import Command

#for app in ['convert', 'composite', 'ppmtoy4m', 'sox', 'ffmpeg', 'mpeg2enc']:
#    verify_app(app)

def generate(options):
    """Generate a menu with selectable text titles."""
    TextMenu(options)

class TextMenu:
    """Simple menu with selectable text titles. For now, basically a clone
    of the classic 'makemenu' output."""
    def __init__(self, options):
        self.options = options
        # TODO: Store intermediate images in a temp folder
        self.bg_canvas = 'pymakemenu.bg_canvas.png'
        self.fg_canvas = 'pymakemenu.fg_canvas.png'
        self.fg_highlight = 'pymakemenu.fg_highlight.png'
        self.fg_selection = 'pymakemenu.fg_selection.png'
        print "Creating a menu with %s titles" % len(options['titles'])
        self.build_reusables()
        self.draw_background_canvas()
        self.draw_background_layer()
        self.draw_highlight_layer()
        self.draw_selection_layer()
        self.gen_video()
        self.gen_audio()
        self.gen_mpeg()

    def build_reusables(self):
        """Assemble some re-usable ImageMagick command snippets.
        For now, just create an ImageMagick draw command for all title text
        for placing labels and highlights.
        Corresponds to lines 343-377 of makemenu"""
        spacing = 30    # Pixel spacing between lines
        y = 0           # Current y-coordinate
        y2 = spacing    # Next y-coordinate
        titlenum = 1        # Title number (for labeling)
        labels = ''
        buttons = ''
        for title in self.options['titles']:
            print "Adding '%s'" % title
            # TODO: Escape special characters in title
            
            # For VCD, number the titles
            if self.options['format'] == 'vcd':
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
        Corresp. to lines 400-411 of makemenu."""
        # Generate default blue-black gradient background
        # TODO: Implement -background
        cmd = 'convert '
        cmd += ' -size %sx%s ' % self.options['expand']
        cmd += ' gradient:blue-black '
        cmd += ' -gravity center -matte '
        cmd += ' %s' % self.bg_canvas
        run(cmd)
    
    def draw_background_layer(self):
        """Draw the background layer for the menu, including static title text.
        Corresp. to lines 438-447, 471-477 of makemenu."""
        # Draw text titles on a transparent background.
        cmd = 'convert '
        cmd += ' -size %sx%s ' % self.options['scale']
        cmd += ' xc:none -antialias -font "%s" ' % self.options['font']
        cmd += ' -pointsize %s ' % self.options['fontsize']
        cmd += ' -fill "%s" ' % self.options['textcolor']
        cmd += ' -stroke black -strokewidth 3 '
        cmd += ' -draw "gravity %s %s" ' % (self.options['align'], self.im_labels)
        cmd += ' -stroke none -draw "gravity %s %s" ' % \
                (self.options['align'], self.im_labels)
        cmd += ' %s' % self.fg_canvas
        run(cmd)
        # Composite text over background
        cmd = 'composite -compose Over -gravity center '
        cmd += ' %s %s ' % (self.fg_canvas, self.bg_canvas)
        cmd += ' -depth 8 "%s.ppm"' % self.options['out']
        run(cmd)
    
    def draw_highlight_layer(self):
        """Draw menu highlight layer, suitable for multiplexing.
        Corresp. to lines 449-458, 479-485 of makemenu."""
        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % self.options['scale']
        cmd += ' xc:none -antialias -font "%s" ' % self.options['font']
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % self.options['fontsize']
        cmd += ' -fill "%s" ' % self.options['highlightcolor']
        cmd += ' -draw "gravity %s %s" ' % (self.options['align'], self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_highlight
        run(cmd)
        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_highlight, self.bg_canvas)
        cmd += ' png8:"%s.hi.png"' % self.options['out']
        run(cmd)
    
    def draw_selection_layer(self):
        """Draw menu selections on a transparent background.
        Corresp. to lines 460-469, 487-493 of makemenu."""
        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % self.options['scale']
        cmd += ' xc:none -antialias -font "%s" ' % self.options['font']
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % self.options['fontsize']
        cmd += ' -fill "%s" ' % self.options['selectcolor']
        cmd += ' -draw "gravity %s %s" ' % (self.options['align'], self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_selection
        run(cmd)
        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_selection, self.bg_canvas)
        cmd += ' png8:"%s.sel.png"' % self.options['out']
        run(cmd)
    
    def gen_video(self):
        """Generate a video stream (mpeg1/2) from the menu background image.
        Corresp. to lines 495-502 of makemenu."""
        
        # ppmtoy4m part
        cmd = 'ppmtoy4m -S 420mpeg2 '
        if self.options['tvsys'] == 'ntsc':
            cmd += ' -A 10:11 -F 30000:1001 '
        else:
            cmd += ' -A 59:54 -F 25:1 '
        # TODO: Remove hardcoded frame count
        cmd += ' -n 90 '
        cmd += ' -r "%s.ppm" ' % self.options['out']
        # mpeg2enc part
        cmd += ' | mpeg2enc -a 2 '
        # PAL/NTSC
        if self.options['tvsys'] == 'ntsc':
            cmd += ' -F 4 -n n '
        else:
            cmd += ' -F 3 -n p '
        # Use correct format flags and filename extension
        if self.options['format'] == 'vcd':
            self.vstream = '%s.m1v' % self.options['out']
            cmd += ' -f 1 '
        else:
            self.vstream = '%s.m2v' % self.options['out']
            if self.options['format'] == 'dvd':
                cmd += ' -f 8 '
            elif self.options['format'] == 'svcd':
                cmd += ' -f 4 '
        cmd += ' -o "%s" ' % self.vstream
        run(cmd)
    
    def gen_audio(self):
        """Generate an audio stream (mp2/ac3) from the given audio file
        (or generate silence instead).
        Corresp. to lines 413-430, 504-518 of makemenu."""
        # If audio file was provided, create .wav of it
        if self.options['audio']:
            cmd = 'sox "%s" ' % self.options['audio']
            cmd += ' -r %s ' % self.options['samprate']
            cmd += ' -w "%s.wav" ' % self.options['out']
        # Otherwise, generate 4-second silence
        else:
            cmd = 'cat /dev/zero | sox -t raw -c 2 '
            cmd += ' -r %s -w -s - ' % self.options['samprate']
            cmd += ' -t wav "%s.wav" trim 0 4 ' % self.options['out']
        run(cmd)
        
        # mp2 for (S)VCD
        if self.options['format'] in ['vcd', 'svcd']:
            self.astream = '%s.mp2' % self.options['out']
            cmd = 'cat "%s.wav" | mp2enc ' % self.options['out']
            cmd += ' -r %s -s ' % self.options['samprate']
        # ac3 for all others
        else:
            self.astream = '%s.ac3' % self.options['out']
            cmd = 'ffmpeg -i "%s.wav" ' % self.options['out']
            cmd += ' -ab 224 -ar %s ' % self.options['samprate']
            cmd += ' -ac 2 -acodec ac3 -y '
        cmd += ' "%s" ' % self.astream
        run(cmd)
    
    def gen_mpeg(self):
        """Multiplex audio and video streams to create an mpeg.
        Corresp. to lines 520-526 of makemenu."""
        
        cmd = 'mplex -o "%s.temp.mpg" ' % self.options['out']
        # Format flags
        if self.options['format'] == 'vcd':
            cmd += ' -f 1 '
        else:
            # Variable bitrate
            cmd += ' -V '
            if self.options['format'] == 'dvd':
                cmd += ' -f 8 '
            elif self.options['format'] == 'svcd':
                cmd += ' -f 4 '
        cmd += ' "%s" "%s" ' % (self.astream, self.vstream)
        run(cmd)
    
    def mux_subtitles(self):
        """Multiplex the output video with highlight and selection
        subtitles, so the resulting menu can be navigated.
        Corresp. to lines 528-548 of makemenu."""
    
        xml =  '<subpictures>\n'
        xml += '  <stream>\n'
        xml += '  <spu force="yes" start="00:00:00.00"\n'
        xml += '       highlight="%s.hi.png"\n' % self.options['out']
        xml += '       select="%s.sel.png"\n' % self.options['out']
        xml += '       autooutline="infer">\n'
        xml += '  </spu>\n'
        xml += '  </stream>\n'
        xml += '</subpictures>\n'
        try:
            xmlfile = open('%s.xml' % self.options['out'], 'w')
        except:
            log.error('Could not open file "%s.xml"' % self.options['out'])
        else:
            xmlfile.write(xml)
            xmlfile.close()
    
        cmd = 'spumux "%s.xml" < "%s.temp.mpg" > "%s.mpg"' % \
                (self.options['out'], self.options['out'], self.options['out'])
        run(cmd)

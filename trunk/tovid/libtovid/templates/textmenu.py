#! /usr/bin/env python
# textmenu.py

__all__ = ['generate']

# TODO: Rewrite to use Command class

from libtovid.cli import Command, Script, verify_app
from libtovid import log

def generate(options):
    """Generate a menu with selectable text titles."""
    for app in ['convert', 'composite', 'ppmtoy4m',
                'sox', 'ffmpeg', 'mpeg2enc']:
        verify_app(app)
    TextMenu(options)


class TextMenu:
    """Simple menu with selectable text titles. For now, basically a clone
    of the classic 'makemenu' output."""
    def __init__(self, target, titles, style):
        self.options = options
        self.script = Script('TextMenu')
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
        Corresponds to lines 343-377 of makemenu"""
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
        """Draw background canvas.
        Corresp. to lines 400-411 of makemenu."""
        # Generate default blue-black gradient background
        # TODO: Implement -background
        cmd = 'convert'
        cmd += ' -size %sx%s' % target.expand
        cmd += ' gradient:blue-black'
        cmd += ' -gravity center -matte %s' % self.bg_canvas
        self.script.append(cmd)
    
    def draw_background_layer(self, target, style):
        """Draw the background layer for the menu, including static title text.
        Corresp. to lines 438-447, 471-477 of makemenu."""
        # Draw text titles on a transparent background.
        cmd = 'convert'
        cmd += ' -size %sx%s' % target.scale
        cmd += ' xc:none -antialias -font "%s"' % style.font
        cmd += ' -pointsize %s' % style.fontsize
        cmd += ' -fill "%s"' % style.textcolor
        cmd += ' -stroke black -strokewidth 3 '
        cmd += ' -draw "gravity %s %s"' % \
                   (style.align, self.im_labels)
        cmd += ' -stroke none -draw "gravity %s %s" ' % \
                   (style.align, self.im_labels)
        cmd += self.fg_canvas
        self.script.append(cmd)
        # Composite text over background
        cmd = 'composite'
        cmd += ' -compose Over -gravity center'
        cmd += ' %s %s' % (self.fg_canvas, self.bg_canvas)
        cmd += ' -depth 8 "%s.ppm"' % target.filename
        self.script.append(cmd)
    
    def draw_highlight_layer(self, target, style):
        """Draw menu highlight layer, suitable for multiplexing.
        Corresp. to lines 449-458, 479-485 of makemenu."""
        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % target.scale
        cmd += ' xc:none -antialias -font "%s" ' % style.font
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % style.fontsize
        cmd += ' -fill "%s" ' % style.highlightcolor
        cmd += ' -draw "gravity %s %s" ' % (style.align, self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_highlight
        self.script.append(cmd)
        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_highlight, self.bg_canvas)
        cmd += ' png8:"%s.hi.png"' % target.filename
        self.script.append(cmd)
    
    def draw_selection_layer(self, target, style):
        """Draw menu selections on a transparent background.
        Corresp. to lines 460-469, 487-493 of makemenu."""
        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % target.scale
        cmd += ' xc:none -antialias -font "%s" ' % style.font
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % style.fontsize
        cmd += ' -fill "%s" ' % style.selectcolor
        cmd += ' -draw "gravity %s %s" ' % (style.align, self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_selection
        self.script.append(cmd)
        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_selection, self.bg_canvas)
        cmd += ' png8:"%s.sel.png"' % target.filename
        self.script.append(cmd)
    
    def gen_video(self, target):
        """Generate a video stream (mpeg1/2) from the menu background image.
        Corresp. to lines 495-502 of makemenu."""
        
        # ppmtoy4m part
        cmd = 'ppmtoy4m -S 420mpeg2 '
        if target.tvsys == 'ntsc':
            cmd += ' -A 10:11 -F 30000:1001 '
        else:
            cmd += ' -A 59:54 -F 25:1 '
        # TODO: Remove hardcoded frame count
        cmd += ' -n 90 '
        cmd += ' -r "%s.ppm" ' % target.filename
        # mpeg2enc part
        cmd += ' | mpeg2enc -a 2 '
        # PAL/NTSC
        if target.tvsys == 'ntsc':
            cmd += ' -F 4 -n n '
        else:
            cmd += ' -F 3 -n p '
        # Use correct format flags and filename extension
        if target.format == 'vcd':
            self.vstream = '%s.m1v' % target.filename
            cmd += ' -f 1 '
        else:
            self.vstream = '%s.m2v' % target.filename
            if target.format == 'dvd':
                cmd += ' -f 8 '
            elif target.format == 'svcd':
                cmd += ' -f 4 '
        cmd += ' -o "%s" ' % self.vstream
        self.script.append(cmd)
    
    def gen_audio(self, target):
        """Generate an audio stream (mp2/ac3) from the given audio file
        (or generate silence instead).
        Corresp. to lines 413-430, 504-518 of makemenu."""
        if target.format in ['vcd', 'svcd']:
            self.astream = "%s.mp2" % target.filename
        else:
            self.astream = "%s.ac3" % target.filename
        cmd = 'ffmpeg '
        # TODO: Fix this
        # If audio file was provided, encode it
        #if self.options['audio']:
        #    cmd += ' -i "%s"' % self.options['audio']
        # Otherwise, generate 4-second silence
        #else:
        #    cmd += ' -f s16le -i /dev/zero -t 4'
        cmd += ' -ac 2 -ab 224'
        cmd += ' -ar %s' % target.samprate
        cmd += ' -acodec %s' % target.acodec
        cmd += ' -y "%s"' % self.astream
        self.script.append(cmd)
    
    def gen_mpeg(self, target):
        """Multiplex audio and video streams to create an mpeg.
        Corresp. to lines 520-526 of makemenu."""
        cmd = 'mplex -o "%s.temp.mpg" ' % target.filename
        # Format flags
        if target.format == 'vcd':
            cmd += ' -f 1 '
        else:
            # Variable bitrate
            cmd += ' -V '
            if target.format == 'dvd':
                cmd += ' -f 8 '
            elif target.format == 'svcd':
                cmd += ' -f 4 '
        cmd += ' "%s" "%s" ' % (self.astream, self.vstream)
        self.script.append(cmd)
    
    def mux_subtitles(self, target):
        """Multiplex the output video with highlight and selection
        subtitles, so the resulting menu can be navigated.
        Corresp. to lines 528-548 of makemenu."""
    
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
    
        cmd = 'spumux "%s.xml" < "%s.temp.mpg" > "%s.mpg"' % \
                (target.filename, target.filename, target.filename)
        self.script.append(cmd)

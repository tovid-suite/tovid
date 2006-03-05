#! /usr/bin/env python2.4
# MenuPlugins.py

__doc__ = \
"""This module implements several backends for generating MPEG menus
from a list of video titles."""

__all__ = ['MenuPlugin', 'TextMenu', 'ThumbMenu']

import os

import libtovid
from libtovid.utils import degunk
from libtovid.log import Log

log = Log('MenuPlugins.py')


# TODO: Eliminate this:
FRAMES=90


class MenuPlugin:
    """Base plugin class; all menu-generators inherit from this."""
    def __init__(self, menu):
        self.menu = menu
        # List of commands to be executed
        self.commands = []
        
        self.preproc()

    def preproc(self):
        if self.menu['format'] == 'dvd':
            width = 720
            samprate = 48000
            if self.menu['tvsys'] == 'ntsc':
                height = 480
            else:
                height = 576
        else:
            width = 352
            samprate = 44100
            if self.menu['tvsys'] == 'ntsc':
                height = 240
            else:
                height = 288
        
        self.samprate = samprate
        # TODO: Proper safe area. Hardcoded for now.
        self.expand = (width, height)
        self.scale = (int(width * 0.9), int(height * 0.9))
        
    def run(self):
        for cmd in self.commands:
            log.info("MenuPlugin: Running the following command:")
            log.info(cmd)
            for line in os.popen(cmd, 'r').readlines():
                log.debug(line)


class TextMenu (MenuPlugin):
    """Simple menu with selectable text titles. For now, basically a clone
    of the classic 'makemenu' output."""
    def __init__(self, menu):
        MenuPlugin.__init__(self, menu)
        # TODO: Store intermediate images in a temp folder
        self.bg_canvas = 'pymakemenu.bg_canvas.png'
        self.fg_canvas = 'pymakemenu.fg_canvas.png'
        self.fg_highlight = 'pymakemenu.fg_highlight.png'
        self.fg_selection = 'pymakemenu.fg_selection.png'
        
        print "Creating a menu with %s titles" % len(self.menu['titles'])
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
        for title in self.menu['titles']:
            print "Adding '%s'" % title
            # TODO: Escape special characters in title
            
            # For VCD, number the titles
            if self.menu['format'] == 'vcd':
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
        cmd = 'convert -size %sx%s ' % self.expand
        cmd += ' gradient:blue-black '
        cmd += ' -gravity center -matte '
        cmd += ' %s' % self.bg_canvas
        self.commands.append(cmd)


    def draw_background_layer(self):
        """Draw the background layer for the menu, including static title text.
        Corresp. to lines 438-447, 471-477 of makemenu."""

        # Draw text titles on a transparent background.
        cmd = 'convert -size %sx%s ' % self.scale
        cmd += ' xc:none -antialias -font "%s" ' % self.menu['font']
        cmd += ' -pointsize %s ' % self.menu['fontsize']
        cmd += ' -fill "%s" ' % self.menu['textcolor']
        cmd += ' -stroke black -strokewidth 3 '
        cmd += ' -draw "gravity %s %s" ' % (self.menu['align'], self.im_labels)
        cmd += ' -stroke none -draw "gravity %s %s" ' % \
                (self.menu['align'], self.im_labels)
        cmd += ' %s' % self.fg_canvas
        self.commands.append(cmd)

        # Composite text over background
        cmd = 'composite -compose Over -gravity center '
        cmd += ' %s %s ' % (self.fg_canvas, self.bg_canvas)
        cmd += ' -depth 8 "%s.ppm"' % self.menu['out']
        self.commands.append(cmd)


    def draw_highlight_layer(self):
        """Draw menu highlight layer, suitable for multiplexing.
        Corresp. to lines 449-458, 479-485 of makemenu."""

        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % self.scale
        cmd += ' xc:none -antialias -font "%s" ' % self.menu['font']
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % self.menu['fontsize']
        cmd += ' -fill "%s" ' % self.menu['highlightcolor']
        cmd += ' -draw "gravity %s %s" ' % (self.menu['align'], self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_highlight
        self.commands.append(cmd)
        
        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_highlight, self.bg_canvas)
        cmd += ' png8:"%s.hi.png"' % self.menu['out']
        self.commands.append(cmd)


    def draw_selection_layer(self):
        """Draw menu selections on a transparent background.
        Corresp. to lines 460-469, 487-493 of makemenu."""

        # Create text layer (at safe-area size)
        cmd = 'convert -size %sx%s ' % self.scale
        cmd += ' xc:none -antialias -font "%s" ' % self.menu['font']
        cmd += ' -weight bold '
        cmd += ' -pointsize %s ' % self.menu['fontsize']
        cmd += ' -fill "%s" ' % self.menu['selectcolor']
        cmd += ' -draw "gravity %s %s" ' % (self.menu['align'], self.im_buttons)
        cmd += ' -type Palette -colors 3 '
        cmd += ' png8:%s' % self.fg_selection
        self.commands.append(cmd)

        # Pseudo-composite, to expand layer to target size
        cmd = 'composite -compose Src -gravity center '
        cmd += ' %s %s ' % (self.fg_selection, self.bg_canvas)
        cmd += ' png8:"%s.sel.png"' % self.menu['out']
        self.commands.append(cmd)


    def gen_video(self):
        """Generate a video stream (mpeg1/2) from the menu background image.
        Corresp. to lines 495-502 of makemenu."""
        
        # ppmtoy4m part
        cmd = 'ppmtoy4m -S 420mpeg2 '
        if self.menu['tvsys'] == 'ntsc':
            cmd += ' -A 10:11 -F 30000:1001 '
        else:
            cmd += ' -A 59:54 -F 25:1 '
        cmd += ' -n %s ' % FRAMES
        cmd += ' -r "%s.ppm" ' % self.menu['out']
        # mpeg2enc part
        cmd += ' | mpeg2enc -a 2 '
        # PAL/NTSC
        if self.menu['tvsys'] == 'ntsc':
            cmd += ' -F 4 -n n '
        else:
            cmd += ' -F 3 -n p '
        # Use correct format flags and filename extension
        if self.menu['format'] == 'vcd':
            self.vstream = '%s.m1v' % self.menu['out']
            cmd += ' -f 1 '
        else:
            self.vstream = '%s.m2v' % self.menu['out']
            if self.menu['format'] == 'dvd':
                cmd += ' -f 8 '
            elif self.menu['format'] == 'svcd':
                cmd += ' -f 4 '
        cmd += ' -o "%s" ' % self.vstream
        self.commands.append(cmd)


    def gen_audio(self):
        """Generate an audio stream (mp2/ac3) from the given audio file
        (or generate silence instead).
        Corresp. to lines 413-430, 504-518 of makemenu."""
        # If audio file was provided, create .wav of it
        if self.menu['audio']:
            cmd = 'sox "%s" ' % self.menu['audio']
            cmd += ' -r %s ' % self.samprate
            cmd += ' -w "%s.wav" ' % self.menu['out']
        # Otherwise, generate 4-second silence
        else:
            cmd = 'cat /dev/zero | sox -t raw -c 2 '
            cmd += ' -r %s -w -s - ' % self.samprate
            cmd += ' -t wav "%s.wav" trim 0 4 ' % self.menu['out']
        self.commands.append(cmd)
        
        # mp2 for (S)VCD
        if self.menu['format'] in ['vcd', 'svcd']:
            self.astream = '%s.mp2' % self.menu['out']
            cmd = 'cat "%s.wav" | mp2enc ' % self.menu['out']
            cmd += ' -r %s -s ' % self.samprate
        # ac3 for all others
        else:
            self.astream = '%s.ac3' % self.menu['out']
            cmd = 'ffmpeg -i "%s.wav" ' % self.menu['out']
            cmd += ' -ab 224 -ar %s ' % self.samprate
            cmd += ' -ac 2 -acodec ac3 -y '
        cmd += ' "%s" ' % self.astream
        self.commands.append(cmd)


    def gen_mpeg(self):
        """Multiplex audio and video streams to create an mpeg.
        Corresp. to lines 520-526 of makemenu."""
        
        cmd = 'mplex -o "%s.temp.mpg" ' % self.menu['out']
        # Format flags
        if self.menu['format'] == 'vcd':
            cmd += ' -f 1 '
        else:
            # Variable bitrate
            cmd += ' -V '
            if self.menu['format'] == 'dvd':
                cmd += ' -f 8 '
            elif self.menu['format'] == 'svcd':
                cmd += ' -f 4 '
        cmd += ' "%s" "%s" ' % (self.astream, self.vstream)
        self.commands.append(cmd)

    def mux_subtitles(self):
        """Multiplex the output video with highlight and selection
        subtitles, so the resulting menu can be navigated.
        Corresp. to lines 528-548 of makemenu."""

        xml =  '<subpictures>\n'
        xml += '  <stream>\n'
        xml += '  <spu force="yes" start="00:00:00.00"\n'
        xml += '       highlight="%s.hi.png"\n' % self.menu['out']
        xml += '       select="%s.sel.png"\n' % self.menu['out']
        xml += '       autooutline="infer">\n'
        xml += '  </spu>\n'
        xml += '  </stream>\n'
        xml += '</subpictures>\n'
        try:
            xmlfile = open('%s.xml' % self.menu['out'], 'w')
        except:
            log.error('Could not open file "%s.xml"' % self.menu['out'])
        else:
            xmlfile.write(xml)
            xmlfile.close()

        cmd = 'spumux "%s.xml" < "%s.temp.mpg" > "%s.mpg"' % \
                (self.menu['out'], self.menu['out'], self.menu['out'])
        self.commands.append(cmd)


# ===========================================================
# Supporting variables and classes for thumbnail menu


# List of top-left coordinates and size for default menu
# thumbnails (for now, a 4x3 grid)
thumb_slots = [
    (72, 48),   (224, 48),   (376, 48),   (528, 48),
    (72, 192),  (224, 192),  (376, 192),  (528, 192),
    (72, 342),  (224, 342),  (376, 342),  (528, 342)
]
    

class ImageSequence:
    """A collection of images comprising a video sequence."""

    def __init__(self, outdir, size):
        """Create an image sequence in the given directory, at the given
        size (x,y)."""
        self.outdir = outdir
        self.size = size

        
    def generate(self, video):
        """Create an image sequence from the given Video."""
        # Create work directory if it doesn't exist
        if not os.path.exists(self.outdir):
            print "Creating thumbnail directory: %s" % self.outdir
            os.mkdir(self.outdir)

        cmd = 'mplayer "%s" ' % video['in']

        x, y = self.size

        cmd += ' -zoom -x %s -y %s ' % self.size
        cmd += ' -vo jpeg:outdir="%s" -ao null ' % self.outdir
        cmd += ' -ss 05:00 -frames %s ' % FRAMES

        print "Creating image sequence from %s" % video['in']
        print cmd
        for line in os.popen(cmd, 'r').readlines():
            #print line
            pass



    def label(self, text):
        for image in glob.glob('%s/*.jpg' % self.outdir):
            cmd = 'convert "%s"' % image
            cmd += ' -gravity south'
            cmd += ' -stroke "#0004" -strokewidth 1'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' -stroke none -fill white'
            cmd += ' -annotate 0 "%s"' % text
            cmd += ' "%s"' % image

            print 'Labeling "%s" with command:' % image
            print cmd
            for line in os.popen(cmd, 'r').readlines():
                print line


class Thumbnail:
    """Video thumbnail, a small preview of a video, with effects"""
    def __init__(self, video, size = (120,90), loc = (0,0)):
        """Create a thumbnail from the given Video."""
        self.video = video
        self.size = size
        self.loc = loc
        self.outdir = os.path.abspath('thumb_%s' % degunk(self.video.name))
        self.imageseq = ImageSequence(self.outdir, self.size)

    def generate(self):
        print "Generating ImageSeqence for thumbnail '%s'" % self.video.name
        self.imageseq.generate(self.video)

    def label(self):
        print "Labeling thumbnail '%s'" % self.video.name
        self.imageseq.label(self.video.name)

        
class ThumbMenu (MenuPlugin):
    """Menu of video thumbnails"""
    def __init__(self, menu):
        """Create a thumbnail menu from the given Menu."""
        self.menu = menu
        self.thumbs = []
        self.outdir = os.path.abspath('menu_%s' % degunk(self.menu.name))
        print "\n\nself.outdir: %s\n\n" % self.outdir
        # Find out how many thumbnails are needed
        self.numthumbs = len(menu.children)
        # Arrange thumbs in a grid
        # TODO: Support more than 12 (generalize)
        if self.numthumbs > 12:
            print "Sorry, can't do more than 12 thumbnails on a menu (yet)."
            sys.exit()
        thumbsize = (120, 90)
        index = 0
        for video in self.menu.children:
            thumb = Thumbnail(video, thumbsize, thumb_slots[index])
            print "Appending video '%s' to thumbnails" % video.name
            self.thumbs.append(thumb)
            index += 1
        self.generate()
            
    def generate(self):
        for thumb in self.thumbs:
            thumb.generate()
            # Apply effects
            if 'label' in self.menu['effects']:
                thumb.label()

        if not os.path.exists(self.outdir):
            print "\n\nCreating scratch dir: %s\n\n" % self.outdir
            os.mkdir(self.outdir)

        # Composite thumbs over background
        for frame in range(FRAMES):
            cmd = 'convert -size 720x480 %s' % self.menu['background']
            for thumb in self.thumbs:
                cmd += ' -page +%s+%s' % thumb.loc
                cmd += ' -label "%s"' % thumb.video.name
                cmd += ' %s/%s.jpg' % (thumb.outdir, string.zfill(frame, 8))
            cmd += ' -mosaic %s/%s.jpg' % (self.outdir, string.zfill(frame, 8))
            print cmd
            os.popen(cmd, 'r')
            
        # Generate video stream of composite images
        self.outfile = os.path.abspath("%s.m2v" % degunk(self.menu.name))
        cmd = 'jpeg2yuv -v 0 -f 29.970 -I p -n %s' % FRAMES
        cmd += ' -L 1 -b1 -j "%s/%%08d.jpg"' % self.outdir
        cmd += ' | mpeg2enc -v 0 -q 3 -f 8 -o "%s"' % self.outfile
        print "Generating video stream with command:"
        print cmd
        for line in os.popen(cmd, 'r'):
            print line


def generate_highlight_png(coords):
    """Generate a transparent highlight .png for the menu, with
    cursor positions near the given coordinates.
    """
    outfile = 'high.png'
    cmd = 'convert -size 720x480 xc:none +antialias'
    cmd += ' -fill "#20FF40"'
    for rect in coords:
        x0, y0, x1, y1 = rect
        cmd += ' -draw "rectangle %s,%s %s,%s"' % \
            (x0, y1+4, x1, y1+10)
    cmd += ' -type Palette -colors 3 png8:%s' % outfile
    print cmd
    for line in os.popen(cmd, 'r').readlines():
        print line
    return outfile

  
    



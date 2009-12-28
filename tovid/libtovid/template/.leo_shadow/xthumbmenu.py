#@+leo-ver=4-thin
#@+node:eric.20090722212922.3454:@shadow thumbmenu.py
__all__ = ['ThumbMenu']

from libtovid.render import layer, flipbook

#@+others
#@+node:eric.20090722212922.3456:class ThumbMenu
class ThumbMenu:
    """A menu of thumbnail videos."""
    #@    @+others
    #@+node:eric.20090722212922.3457:__init__
    def __init__(self, target, files, titles, style):
        self.target = target
        self.files = files
        self.titles = titles
        self.style = style
        self.basename = self.target.filename

    #@-node:eric.20090722212922.3457:__init__
    #@+node:eric.20090722212922.3458:generate
    def generate(self):
        print("Generating a menu with %s thumbnails" % len(self.titles))
        menu = flipbook.Flipbook(5, self.target.format, self.target.tvsys)
        width, height = self.target.scale
        thumbs = layer.ThumbGrid(self.files, self.titles,
                                 (width * 0.8, height * 0.8))
        menu.add(thumbs, (width/10, height/10))
        menu.render_video(self.basename)

    #@-node:eric.20090722212922.3458:generate
    #@-others
#@-node:eric.20090722212922.3456:class ThumbMenu
#@-others
#@-node:eric.20090722212922.3454:@shadow thumbmenu.py
#@-leo

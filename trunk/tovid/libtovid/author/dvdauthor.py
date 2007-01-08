#! /usr/bin/env python
# dvdauthor.py

"""This module provides functions for authoring a DVD using dvdauthor.
"""

__all__ = ['get_xml']

from libtovid import xml
from libtovid import layout

def get_xml(disc):
    """Return a string containing dvdauthor XML for the given Disc.
    """
    assert isinstance(disc, layout.Disc)
    root = xml.Element('dvdauthor', dest=disc.name.replace(' ', '_'))
    vmgm = root.add('vmgm')
    if disc.topmenu:
        menus = vmgm.add('menus')
        menus.add('video')
        pgc = menus.add('pgc', entry='title')
        vob = pgc.add('vob', file=disc.topmenu.filename)
        for index, titleset in enumerate(disc.titlesets):
            vob.add('button', 'jump titleset %d;' % (index + 1))

    for titleset in disc.titlesets:
        ts = root.add('titleset')
        if titleset.menu:
            menus = ts.add('menus')
            menus.add('video')
            menus.add('pgc', entry='root')
            vob = menus.add('vob', file=menu.filename)
            for index, video in enumerate(menu.videos):
                vob.add('button', 'jump title %d;' % (index + 1))
            vob.add('button', 'jump vmgm menu;')
        for video in titleset.videos:
            pgc = ts.add('pgc')
            pgc.add('vob', file=video.filename,
                    chapters=','.join(video.chapters))
            pgc.add('post', 'call menu;')

    return str(root)


if __name__ == '__main__':
    videos = [
        layout.Video('video1.mpg'),
        layout.Video('video2.mpg'),
        layout.Video('video3.mpg')]
    menu = layout.Menu('menu.mpg', videos, 'dvd', 'ntsc')
    titleset = layout.Titleset(videos, menu)
    disc = layout.Disc('dvd_test', 'dvd', 'ntsc', [titleset])

    print "XML example"
    print get_xml(disc)

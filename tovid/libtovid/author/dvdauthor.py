#! /usr/bin/env python
# dvdauthor.py

"""This module provides functions for authoring a DVD using dvdauthor.
"""

__all__ = ['get_xml']

from libtovid import xml
from libtovid.layout import Video, Menu, Titleset, Disc

def get_xml(disc):
    """Return a string containing dvdauthor XML for the given Disc.
    """
    assert isinstance(disc, Disc)
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
        menu = titleset.menu
        ts = root.add('titleset')
        if menu:
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
    videos1 = [
        Video('video1.mpg'),
        Video('video2.mpg'),
        Video('video3.mpg')]
    menu1 = Menu('menu1.mpg', videos1)
    videos2 = [
        Video('video4.mpg'),
        Video('video5.mpg'),
        Video('video6.mpg')]
    menu2 = Menu('menu2.mpg', videos2)
    titlesets = [
        Titleset(videos1, menu1),
        Titleset(videos2, menu2)]
    disc = Disc('vcd_test', 'vcd', 'ntsc', titlesets)

    print "XML example"
    print get_xml(disc)

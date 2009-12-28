#@+leo-ver=4-thin
#@+node:eric.20090722212534.2374:@shadow author.py
"""This module is for authoring a DVD or (S)VCD using dvdauthor or vcdimager.
"""

__all__ = [
    'Disc',
    'Menu',
    'Video',
    'Group',
    'Titleset',
    'vcdimager_xml',
    'dvdauthor_xml',
]

from libtovid import xml


#@+others
#@+node:eric.20090722212534.2376:class Video
###
### Supporting classes
###

class Video:
    """A video title for inclusion on a video disc.
    """
    #@    @+others
    #@+node:eric.20090722212534.2377:__init__
    def __init__(self, filename, title=''):
        self.filename = filename
        self.title = title
        self.chapters = []


    #@-node:eric.20090722212534.2377:__init__
    #@-others
#@-node:eric.20090722212534.2376:class Video
#@+node:eric.20090722212534.2378:class Group
class Group:
    """A group title for inclusion on a video disc.
    """
    #@    @+others
    #@+node:eric.20090722212534.2379:__init__
    def __init__(self, filenames, title):
        self.filenames = filenames
        self.title = title


    #@-node:eric.20090722212534.2379:__init__
    #@-others
#@-node:eric.20090722212534.2378:class Group
#@+node:eric.20090722212534.2380:class Menu
class Menu:
    """A menu for navigating the titles on a video disc.
    """
    #@    @+others
    #@+node:eric.20090722212534.2381:__init__
    def __init__(self, filename='', videos=None):
        """Create a menu linking to the given Videos."""
        self.filename = filename
        self.videos = videos or []

    #@-node:eric.20090722212534.2381:__init__
    #@+node:eric.20090722212534.2382:add
    def add(self, video):
        """Add a Video to the Menu."""
        self.videos.append(video)


    #@-node:eric.20090722212534.2382:add
    #@-others
#@-node:eric.20090722212534.2380:class Menu
#@+node:eric.20090722212534.2383:class Titleset
class Titleset:
    """A group of videos, with an optional Menu.
    """
    #@    @+others
    #@+node:eric.20090722212534.2384:__init__
    def __init__(self, menu=None, videos=None):
        """Create a Titleset containing the given Videos.
        """
        self.menu = menu
        self.videos = videos or []

    #@-node:eric.20090722212534.2384:__init__
    #@+node:eric.20090722212534.2385:add
    def add(self, video):
        """Add a Video to the Titleset."""
        self.videos.append(video)


    #@-node:eric.20090722212534.2385:add
    #@-others
#@-node:eric.20090722212534.2383:class Titleset
#@+node:eric.20090722212534.2386:class Disc
class Disc:
    """A video disc containing one or more Titlesets, and an optional
    top Menu for navigating to each Titleset.

    """
    #@    @+others
    #@+node:eric.20090722212534.2387:__init__
    def __init__(self, name='Untitled', format='dvd', tvsys='ntsc',
                 titlesets=None):
        """Create a Disc with the given properties.

            format
                'vcd', 'svcd', or 'dvd'
            tvsys
                'pal' or 'ntsc'
            title
                String containing the title of the disc
            titlesets
                List of Titlesets
        """
        self.name = name
        self.format = format
        self.tvsys = tvsys
        self.topmenu = None
        self.titlesets = titlesets or []



    #@-node:eric.20090722212534.2387:__init__
    #@-others
#@-node:eric.20090722212534.2386:class Disc
#@+node:eric.20090722212534.2388:_add_titleset
###
### Internal functions
###

def _add_titleset(titleset, ts_id, segment_items, sequence_items, pbc):
    """Add titleset content to a vcdimager XML structure. This function is
    used internally, mainly to keep vcdimager_xml() from being too long.
    """
    menu = titleset.menu
    videos = titleset.videos
    # Add menu
    if menu:
        segment_items.add('segment-item', src=menu.filename,
                          id='seg-menu-%d' % ts_id)
        # Add menu to pbc
        selection = pbc.add('selection', id='select-menu-%d' % ts_id)
        selection.add('bsn', '1')
        # Link back to topmenu (not sure what'll happen if there isn't one...)
        selection.add('return', ref='select-topmenu')
        selection.add('loop', '0', jump_timing='immediate')
        selection.add('play-item', ref='seg-menu-%d' % ts_id)
        # Navigational links to titleset videos
        for video_id in range(len(videos)):
            selection.add('select',
                          ref='play-title-%d-%d' % (ts_id, video_id))
    # Add videos
    for video_id, video in enumerate(videos):
        # Add sequence items
        sequence_item = sequence_items.add('sequence-item')
        sequence_item.set(id='seq-title-%d-%d' % (ts_id, video_id),
                          src=video.filename)
        # Add chapter entries
        for chapterid, chapter in enumerate(video.chapters):
            sequence_item.add('entry', chapter, id='chapter-%d' % chapterid)
        # Add playlists to pbc
        playlist = pbc.add('playlist')
        playlist.set(id='play-title-%d-%d' % (ts_id, video_id))
        # Add prev/next links if appropriate
        if 0 <= video_id < len(videos):
            if 0 < video_id:
                playlist.add('prev',
                             ref='play-title-%d-%d' % (ts_id, video_id-1))
            if video_id < len(videos) - 1:
                playlist.add('next',
                             ref='play-title-%d-%d' % (ts_id, video_id+1))
        # Add a return link to the menu, if there is one
        if menu:
            playlist.add('return', ref='select-menu-%d' % ts_id)
        playlist.add('wait', '0')
        playlist.add('play-item', ref='seq-title-%d-%d' % (ts_id, video_id))


#@-node:eric.20090722212534.2388:_add_titleset
#@+node:eric.20090722212534.2389:vcdimager_xml
###
### Exported functions
###

def vcdimager_xml(disc):
    """Return the vcdimager XML string for the given Disc.
    """
    assert isinstance(disc, Disc)
    # XML header (will be added later)
    header = '<?xml version="1.0"?>\n'
    header += '<!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"\n'
    header += '  "http://www.gnu.org/software/vcdimager/videocd.dtd">\n'
    # Root videocd element
    attributes = {
        'xmlns': 'http://www.gnu.org/software/vcdimager/1.0/',
        'class': disc.format}
    if disc.format == 'vcd':
        attributes['version'] = '2.0'
    else: # SVCD
        attributes['version'] = '1.0'
    root = xml.Element('videocd')
    root.set(**attributes)
    # Add info block
    info = root.add('info')
    info.add('album-id', 'VIDEO_DISC')
    info.add('volume-count', '1')
    info.add('volume-number', '1')
    info.add('restriction', '0')
    # Add pvd block
    pvd = root.add('pvd')
    pvd.add('volume-id', 'VIDEO_DISC')
    pvd.add('system-id', 'CD-RTOS CD-BRIDGE')

    # Add segment, sequence, and pbc
    segment_items = root.add('segment-items')
    sequence_items = root.add('sequence-items')
    pbc = root.add('pbc')
    # Add topmenu
    if disc.topmenu:
        segment_items.add('segment-item', src=disc.topmenu.filename,
                          id='seg-topmenu')
        selection = pbc.add('selection', id='select-topmenu')
        selection.add('bsn', '1')
        selection.add('loop', '0', jump_timing='immediate')
        selection.add('play-item', ref='seg-topmenu')
    # Add titlesets
    for ts_id, titleset in enumerate(disc.titlesets):
        _add_titleset(titleset, ts_id, segment_items, sequence_items, pbc)
        # If we're doing a topmenu, add a link to the titleset menu
        if disc.topmenu:
            selection.add('select', ref='select-menu-%d' % ts_id)

    # Return XML with header prepended
    return header + str(root) + '\n'


#@-node:eric.20090722212534.2389:vcdimager_xml
#@+node:eric.20090722212534.2390:dvdauthor_xml
def dvdauthor_xml(disc):
    """Return the dvdauthor XML string for the given Disc.
    """
    assert isinstance(disc, Disc)
    # Root dvdauthor element
    root = xml.Element('dvdauthor', dest=disc.name.replace(' ', '_'))
    vmgm = root.add('vmgm')
    # Add topmenu if present
    if disc.topmenu:
        menus = vmgm.add('menus')
        menus.add('video')
        pgc = menus.add('pgc', entry='title')
        vob = pgc.add('vob', file=disc.topmenu.filename)
        for index, titleset in enumerate(disc.titlesets):
            if titleset.menu:
                pgc.add('button', 'jump titleset %d menu;' % (index + 1))
            else:
                pgc.add('button', 'jump titleset %d;' % (index + 1))
    # Add each titleset
    for titleset in disc.titlesets:
        menu = titleset.menu
        ts = root.add('titleset')
        # Add menu if present
        if menu:
            menus = ts.add('menus')
            menus.add('video')
            pgc = menus.add('pgc', entry='root')
            vob = pgc.add('vob', file=menu.filename)
            for index, video in enumerate(titleset.videos):
                pgc.add('button', 'jump title %d;' % (index + 1))
            if disc.topmenu:
                pgc.add('button', 'jump vmgm menu;')
        titles = ts.add('titles')
        # Add a pgc for each video
        for video in titleset.videos:
            pgc = titles.add('pgc')
            vob = pgc.add('vob', file=video.filename)
            if video.chapters:
                vob.set(chapters=','.join(video.chapters))
            pgc.add('post', 'call menu;')
    # Return XML string
    return str(root) + '\n'


#@-node:eric.20090722212534.2390:dvdauthor_xml
#@-others
#@<<main>>
#@+node:eric.20090722212922.3486:<<main>>
if __name__ == '__main__':
    menu1 = Menu('menu1.mpg')
    videos1 = [
        Video('video1.mpg'),
        Video('video2.mpg'),
        Video('video3.mpg')]
    menu2 = Menu('menu2.mpg')
    videos2 = [
        Video('video4.mpg'),
        Video('video5.mpg'),
        Video('video6.mpg')]
    titlesets = [
        Titleset(menu1, videos1),
        Titleset(menu2, videos2)]
    disc = Disc('dvd_test', 'dvd', 'ntsc', titlesets)

    print("dvdauthor XML example:")
    print(dvdauthor_xml(disc))

    print("vcdimager XML example:")
    print(vcdimager_xml(disc))
#@-node:eric.20090722212922.3486:<<main>>
#@nl
#@nonl
#@-node:eric.20090722212534.2374:@shadow author.py
#@-leo

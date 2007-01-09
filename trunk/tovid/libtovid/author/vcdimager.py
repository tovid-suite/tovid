#! /usr/bin/env python
# vcdimager.py

"""This module provides functions for authoring a video CD using vcdimager.
"""

__all__ = ['get_xml']

from libtovid import xml
from libtovid.layout import Video, Menu, Titleset, Disc
    
def get_xml(disc):
    """Return the vcdimager XML string for authoring a disc.
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
    root.set(attributes)
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
    # Add segment, sequence, and pbc...
    segment_items = root.add('segment-items')
    sequence_items = root.add('sequence-items')
    pbc = root.add('pbc')
    # ...and add titleset content to them
    for ts_id, titleset in enumerate(disc.titlesets):
        _add_titleset(titleset, ts_id, segment_items, sequence_items, pbc)
    # Return XML with header prepended
    return header + str(root)


def _add_titleset(titleset, ts_id, segment_items, sequence_items, pbc):
    """Internal function to add titleset content to the XML structure.
    """
    menu = titleset.menu
    videos = titleset.videos
    # Add menu
    if menu:
        segment_items.add('segment-item', src=menu.filename,
                          id='seg-menu-%d' % ts_id)
        # Add menu to pbc
        selection = pbc.add('selection', id='select-menu-%d' % ts_id)
        selection.add('play-item', ref='seg-menu-%d' % ts_id)
        selection.add('bsn', '1')
        selection.add('loop', '0', jump_timing='immediate')
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
        playlist.add('play-item', ref='seq-title-%d-%d' % (ts_id, video_id))
        playlist.add('wait', '0')
        playlist.add('return', ref='select-menu')
        # Add prev/next links if appropriate
        if 0 <= video_id < len(videos):
            if 0 < video_id:
                playlist.add('prev',
                             ref='seq-title-%d-%d' % (ts_id, video_id-1))
            if video_id < len(videos) - 1:
                playlist.add('next',
                             ref='seq-title-%d-%d' % (ts_id, video_id+1))

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

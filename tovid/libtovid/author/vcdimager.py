#! /usr/bin/env python
# vcdimager.py

"""This module provides functions for authoring a video CD using vcdimager.
"""

__all__ = ['get_xml']

from libtovid import xml
from libtovid import layout

def get_xml(disc):
    """Return the vcdimager XML string for authoring a disc.
    
        disc:  A Disc with one Titleset
    """
    assert isinstance(disc, layout.Disc)
    # TODO: Support more than one titleset
    videos = disc.titlesets[0].videos
    menu = disc.titlesets[0].menu
    
    # Root videocd element
    attributes = {
        'xmlns': 'http://www.gnu.org/software/vcdimager/1.0/',
        'class': disc.format}
    if disc.format == 'vcd':
        attributes['version'] = '2.0'
    else: # SVCD
        attributes['version'] = '1.0'
    videocd = xml.Element('videocd')
    videocd.set(attributes)
    
    # info block
    info = videocd.add('info')
    info.add('album-id', 'VIDEO_DISC')
    info.add('volume-count', '1')
    info.add('volume-number', '1')
    info.add('restriction', '0')
    
    # pvd block
    pvd = videocd.add('pvd')
    pvd.add('volume-id', 'VIDEO_DISC')
    pvd.add('system-id', 'CD-RTOS CD-BRIDGE')
    
    # segment-items
    if menu:
        segment_items = videocd.add('segment-items')
        segment_items.add('segment-item', src=menu, id='seg-menuit does')
    
    # sequence-items
    sequence_items = videocd.add('sequence-items')
    for index, video in enumerate(videos):
        sequence_item = sequence_items.add('sequence-item')
        sequence_item.set(id='seq-title-%d' % index, src=video.filename)
        # Add chapter entries
        for chapterid, chapter in enumerate(video.chapters):
            sequence_item.add('entry', chapter, id='chapter-%d' % chapterid)
    
    # pbc block
    pbc = videocd.add('pbc')
    # Menu, if any
    if menu:
        selection = pbc.add('selection', id='select-menu')
        selection.add('play-item', ref='seg-menu')
        selection.add('bsn', '1')
        selection.add('loop', '0', jump_timing='immediate')
        for index in range(len(videos)):
            selection.add('select', ref='play-title-%d' % index)
        # TODO: Next/prev to have multi-page main menus?
    # Video playlist items
    for index in range(len(videos)):
        playlist = pbc.add('playlist', id='play-title-%d' % index)
        playlist.add('play-item', ref='seq-title-%d' % index)
        playlist.add('wait', '0')
        playlist.add('return', ref='select-menu')
        if 0 <= index < len(videos):
            if 0 < index:
                playlist.add('prev', ref='seq-title-%s' % (index - 1))
            if index < len(videos) - 1:
                playlist.add('next', ref='seq-title-%s' % (index + 1))

    # TODO: Proper way to include headers in libtovid.xml?
    header = '<?xml version="1.0"?>\n'
    header += '<!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"\n'
    header += '  "http://www.gnu.org/software/vcdimager/videocd.dtd">\n'
    return header + str(videocd)


if __name__ == '__main__':
    videos = [
        layout.Video('video1.mpg'),
        layout.Video('video2.mpg'),
        layout.Video('video3.mpg')]
    menu = layout.Menu('menu.mpg', videos, 'vcd', 'ntsc')
    titleset = layout.Titleset(videos, menu)
    disc = layout.Disc('vcd_test', 'vcd', 'ntsc', [titleset])

    print "XML example"
    print get_xml(disc)

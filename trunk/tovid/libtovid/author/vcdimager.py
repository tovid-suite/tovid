#! /usr/bin/env python
# vcdimager.py

"""This module provides functions for authoring a video CD using vcdimager.

"""

# __all__ = []

from libtovid import xml

def get_xml(disc):
    """Return vcdxbuild XML suitable for authoring the given Disc.
    """
    xml = """<?xml version="1.0"?>
    <!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
      "http://www.gnu.org/software/vcdimager/videocd.dtd">
    <videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
    """
    # format == vcd|svcd, version=1.0 (svcd) | 2.0 (vcd)
    assert disc.format in ['vcd', 'svcd']
    if disc.format == 'vcd':
        xml += 'class="vcd" version="2.0">\n'
    elif disc.format == 'svcd':
        xml += 'class="svcd" version="1.0">\n'

    if disc.format == 'svcd':
        xml += '<option name="update scan offsets" value="true" />'

    xml += """<info>
      <album-id>VIDEO_DISC</album-id>
      <volume-count>1</volume-count>
      <volume-number>1</volume-number>
      <restriction>0</restriction>
    </info>
    <pvd>
      <volume-id>VIDEO_DISC</volume-id>
      <system-id>CD-RTOS CD-BRIDGE</system-id>
    </pvd>
    """
    
    # TODO:
    # segment-items
    # sequence-items
    # pbc + selections
    xml += '</videocd>'


# vcdimager XML element definitions
"""
videocd ['xmlns', 'class', 'version']
option ['name', 'value']
info
    album-id
    volume-count
    volume-number
    next-volume-use-sequence2
    next-volume-use-lid2
    restriction
    time-offset
pvd
    volume-id
    system-id
    application-id
    preparer-id
    publisher-id
filesystem
    folder
        name
    file ['src', 'format']
        name
segment-items
    segment-item ['src', 'id']
sequence-items
    sequence-item ['src', 'id']
        entry ['id']
        auto-pause
pbc
    playlist ['id']
        prev ['ref']
        next ['ref']
        return ['ref']
        playtime
        wait
        autowait
        play-item ['ref']
    selection ['id']
        bsn
        prev ['ref']
        next ['ref']
        return ['ref']
        default ['ref']
        timeout ['ref']
        wait
        loop ['jump-timing']
        play-item ['ref']
        select ['ref']
    endlist
"""
if __name__ == '__main__':
    attributes = {
        'xmlns': 'http://www.gnu.org/software/vcdimager/1.0/',
        'class': 'vcd',
        'version': '2.0'}
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
    menu = 'menu.mpg'
    segment_items = videocd.add('segment-items')
    segment_items.add('segment-item', src=menu, id='seg-menu-1')
    
    # sequence-items
    videos = {
        1: 'video1.mpg',
        2: 'video2.mpg',
        3: 'video3.mpg'}
    sequence_items = videocd.add('sequence-items')
    for index, video in videos.items():
        sequence_items.add('sequence-item', src=video,
                           id='seq-title-%d' % index)
    
    # pbc block
    pbc = videocd.add('pbc')
    selection = pbc.add('selection', id='select-menu-1')
    selection.add('bsn', '1')
    selection.add('loop', '0', jump_timing='immediate')
    selection.add('play-item', ref='seg-menu-1')
    for index in videos.keys():
        selection.add('select', ref='play-title-%d' % index)
        playlist = pbc.add('playlist', id='play-title-%d' % index)
        playlist.add('return', ref='select-menu-1')
        playlist.add('wait', '0')
        playlist.add('play-item', ref='seq-title-%d' % index)
    
    print "XML example"
    print videocd
    
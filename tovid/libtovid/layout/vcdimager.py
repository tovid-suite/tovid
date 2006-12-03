#! /usr/bin/env python
# vcdimager.py

"""This module provides functions for authoring a video CD using vcdimager.

"""

__all__ = []

def get_xml(disc):
    """Return vcdxbuild XML suitable for authoring the given disc.
    """
    xml = """<?xml version="1.0"?>
    <!DOCTYPE videocd PUBLIC "-//GNU/DTD VideoCD//EN"
      "http://www.gnu.org/software/vcdimager/videocd.dtd">
    <videocd xmlns="http://www.gnu.org/software/vcdimager/1.0/"
    """
    # format == vcd|svcd, version=1.0 (svcd) | 2.0 (vcd)
    assert disc.format in ['vcd', 'svcd']
    if disc.format == 'vcd':
        version = "2.0"
    elif disc.format == 'svcd':
        version = "1.0"
    
    xml += 'class="%s" version="%s">\n' % (disc.format, version)

    if format == 'svcd':
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

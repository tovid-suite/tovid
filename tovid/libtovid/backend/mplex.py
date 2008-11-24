#! /usr/bin/env python
# mplex.py

"""Multiplexing using ``mplex``.
"""

__all__ = [
    'mux',
]

from libtovid import cli

def mux(vstream, astream, target):
    """Multiplex audio and video stream files to the given target.
    
        vstream
            Filename of MPEG video stream
        astream
            Filename of MP2/AC3 audio stream
        target
            Profile of output file
        
    """
    cmd = cli.Command('mplex')
    format = target.format
    if format == 'vcd':
        cmd.add('-f', '1')
    elif format == 'dvd-vcd':
        cmd.add('-V', '-f', '8')
    elif format == 'svcd':
        cmd.add('-V', '-f', '4', '-b', '230')
    elif format == 'half-dvd':
        cmd.add('-V', '-f', '8', '-b', '300')
    elif format == 'dvd':
        cmd.add('-V', '-f', '8', '-b', '400')
    # elif format == 'kvcd':
    #   cmd += ' -V -f 5 -b 350 -r 10800 '
    cmd.add(vstream, astream, '-o', target.filename)
    # Run the command to multiplex the streams
    cmd.run()
    

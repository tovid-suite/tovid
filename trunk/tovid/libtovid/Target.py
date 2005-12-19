#! /usr/bin/env python

# ===========================================================
# Target
# ===========================================================

std_widths = {
    352: ['vcd', 'dvd-vcd', 'half-dvd'],
    480: ['pal', 'svcd'],
    720: ['dvd']
}
std_heights = {
    240: ['ntsc', 'vcd', 'dvd-vcd'],
    288: ['pal', 'vcd', 'dvd-vcd'],
    480: ['ntsc', 'half-dvd', 'svcd', 'dvd'],
    576: ['pal', 'half-dvd', 'svcd', 'dvd']
}
std_codecs = {
    'mpeg1': ['vcd'],
    'mpeg2': ['svcd', 'dvd-vcd', 'half-dvd', 'dvd']
}
std_fpss = {
    25.00: ['pal'],
    29.97: ['ntsc']
}

def match_std(defs, keywords):
    for value in defs:
        # Make sure all keywords match
        match = True
        for key in keywords:
            if key not in defs[value]:
                match = False
                break
        if match:
            return value

    print "Couldn't match %s in %s" % (keywords, defs)
    return None
            

class Target:
    def __init__(self, format, tvsys):
        self.format = format
        self.tvsys = tvsys

        self.codec = match_std(std_codecs, [format])
        self.width = match_std(std_widths, [format])
        self.height = match_std(std_heights, [format, tvsys])
        self.fps = match_std(std_fpss, [tvsys])

    def get_resolution():
        """Return the pixel width and height as an (x,y) tuple."""
        return (self.width, self.height)

if __name__ == "__main__":
    t1 = Target('vcd', 'ntsc')
    t2 = Target('dvd', 'pal')

    print "t1:"
    print t1.codec
    print t1.width
    print t1.height
    print t1.fps

    print "t2:"
    print t2.codec
    print t2.width
    print t2.height
    print t2.fps

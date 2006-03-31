#! /usr/bin/env python2.4
# standards.py

"""This module defines functions for retrieving information about multimedia
standards. Any data about widely-published standards should be defined here,
for use by all libtovid modules."""

# TODO: This module needs major cleanup, ruthless code-culling and
# overall simplification.

__all__ = ['VideoStandard', 'AudioStandard']

def get_resolution(format, tvsys):
    """Get the pixel resolution (x,y) for the given format and TV system."""
    width = match_std(std_widths, [format])
    height = match_std(std_heights, [format, tvsys])
    return (width, height)

def get_codec(format, tvsys):
    return match_std(std_codecs, [format])

def get_fps(format, tvsys):
    return match_std(std_fpss, [tvsys])


# Standard format/tvsystem definitions, indexed by value.  Each value
# corresponds to a list of matching standards (vcd/svcd/dvd) or TV systems
# (pal/ntsc) by keyword.
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
    """Find values in defs by matching associated keywords."""
    for value in defs:
        # Make sure all keywords match
        match = True
        for key in keywords:
            # Unmatched keyword?
            if key not in defs[value]:
                match = False
                break
        # All keywords matched?
        if match:
            return value

    print "Couldn't match %s in %s" % (keywords, defs)
    return None


def validate_specs(video, audio):
    """Return a list of audio and video standards matched by the given specs."""
    width = video.width
    height = video.height
    if width == 352:
        if height == 240: res = 'ntsc vcd'
        elif height == 288: res = 'pal vcd'
        elif height == 480: res = 'ntsc half'
        elif height == 576: res = 'pal half'
    elif width == 480:
        if height == 480: res = 'ntsc svcd'
        elif height == 576: res = 'pal svcd'
    elif width == 528:
        if height == 480: res = 'ntsc kvcdx3'
        elif height == 576: res = 'pal kvcdx3'
    elif width == 544:
        if height == 480: res = 'ntsc kvcdx3a'
        elif height == 576: res = 'pal kvcdx3a'
    elif width in [704, 720]:
        if height == 480: res = 'ntsc dvd'
        elif height == 576: res = 'pal dvd'


def video_is_valid(vstream, vstandard):
    """Return True if the video stream is valid under the given standard."""
    if (vstream.width == vstandard.width and
         vstream.height == vstandard.height and
         vstream.fps == vstandard.fps and
         vstream.codec == vstandard.codec and
         vstream.bitrate >= vstandard.minBitrate and
         vstream.bitrate <= vstandard.maxBitrate):
        return True
    else:
        return False

def audio_is_valid(astream, astandard):
    """Return True if the audio stream is valid under the given standard."""
    if (astream.bitrate >= astandard.minBitrate and
         astream.bitrate <= astandard.maxBitrate and
         astream.codec == astandard.codec and
         astream.samprate == astandard.samprate):
        return True
    else:
        return False

# ===========================================================
# TODO: Merge stuff above with stuff below somehow...
# ===========================================================

class VideoStandard:
    def __init__(self, keywords = [], codec = "",
                  resolution = (0, 0), fps = 0, bitrateRange = (0, 0)):
        self.keywords = keywords 
        self.codec = codec
        self.width, self.height = resolution
        self.fps = fps
        self.minBitrate, self.maxBitrate = bitrateRange

    def display(self):
        print "=========== Video standard ============="
        print "Keywords: %s" % self.keywords
        print "Codec: %s" % self.codec
        print "Width: %s" % self.width
        print "Height: %s" % self.height
        print "FPS: %s" % self.fps
        print "Minimum bitrate: %s" % self.minBitrate
        print "Maximum bitrate: %s" % self.maxBitrate


class AudioStandard:
    def __init__(self, keywords = [], codec = "",
                  samprate = 0, channels = 0, bitrateRange = (0, 0)):
        self.keywords = keywords 
        self.codec = codec
        self.samprate = samprate
        self.channels = channels
        self.minBitrate, self.maxBitrate = bitrateRange

    def display(self):
        print "=========== Audio standard ============="
        print "Keywords: %s" % self.keywords
        print "Codec: %s" % self.codec
        print "Sampling rate: %s" % self.samprate
        print "Minimum bitrate: %s" % self.minBitrate
        print "Maximum bitrate: %s" % self.maxBitrate


VideoStandardList = [
    # VideoStandard([keywords], codec, (width, height), fps, (minBitrate, maxBitrate))

    # VCD standard formats
    VideoStandard(["vcd", "pal"], "mpeg1", (352, 288), 25.00, (1152, 1152)),
    VideoStandard(["vcd", "ntsc"], "mpeg1", (352, 240), 29.97, (1152, 1152)),
    VideoStandard(["vcd", "ntsc", "ntscfilm"], "mpeg1", (352, 240), 23.976, (1152, 1152)),

    # SVCD standard formats
    VideoStandard(["svcd" , "pal"], "mpeg2", (480, 576), 25.00, (0, 2600)),
    VideoStandard(["svcd" , "ntsc"], "mpeg2", (480, 480), 29.97, (0, 2600)),
    VideoStandard(["svcd" , "ntsc", "ntscfilm"], "mpeg2", (480, 480), 23.976, (0, 2600)),

    # DVD standard formats
    VideoStandard(["dvd", "pal"], "mpeg2", (720, 576), 25.00, (0, 9800)),
    VideoStandard(["dvd", "ntsc"], "mpeg2", (720, 480), 29.97, (0, 9800)),
    VideoStandard(["dvd", "ntsc", "ntscfilm"], "mpeg2", (720, 480), 23.976, (0, 9800)),

    VideoStandard(["half-dvd", "pal"], "mpeg2", (352, 576), 25.00, (0, 9800)),
    VideoStandard(["half-dvd", "ntsc"], "mpeg2", (352, 480), 29.97, (0, 9800)),
    VideoStandard(["half-dvd", "ntsc", "ntscfilm"], "mpeg2", (352, 480), 23.976, (0, 9800)),
    VideoStandard(["dvd-vcd", "pal"], "mpeg2", (352, 288), 25.00, (0, 9800)),
    VideoStandard(["dvd-vcd", "ntsc"], "mpeg2", (352, 240), 29.97, (0, 9800)),
    VideoStandard(["dvd-vcd", "ntsc", "ntscfilm"], "mpeg2", (352, 240), 23.976, (0, 9800)),

    # KVCDX3 standard formats
    VideoStandard(["kvcdx3", "pal"], "mpeg2", (528, 576), 25.00, (0, 9800)),
    VideoStandard(["kvcdx3", "ntsc"], "mpeg2", (528, 480), 29.97, (0, 9800)),
    VideoStandard(["kvcdx3", "ntsc", "ntscfilm"], "mpeg2", (528, 480), 23.976, (0, 9800))
] # End of VideoList

# ===========================================================
# List of defined audio standards
# ===========================================================
AudioStandardList = [
    # AudioStandard([keywords], codec, samprate, channels, (minBitrate, maxBitrate))

    # VCD standard formats
    AudioStandard(["vcd", "pal"], "mp2", 44100, 2, (224, 224)),
    AudioStandard(["vcd", "ntsc"], "mp2", 44100, 2, (224, 224)),

    # SVCD standard formats
    AudioStandard(["svcd", "pal"], "mp2", 44100, 2, (32, 1536)),
    AudioStandard(["svcd", "ntsc"], "mp2", 44100, 2, (32, 384)),

    # DVD standard formats
    AudioStandard(["dvd", "ac3"], "ac3", 48000, 2, (32, 1536)),
    AudioStandard(["dvd", "mp2"], "mp2", 48000, 2, (32, 1536)),
    AudioStandard(["dvd", "pcm"], "pcm", 48000, 2, (32, 1536))
    # 5.1-channel audio
    #AudioStandard(["dvd"], "ac3", 48000, 5.1, (32, 1536))
    #AudioStandard(["dvd"], "mp2", 48000, 5.1, (32, 1536)),
] # End of AudioList




# Find the first standard in VideoStandardList
# matching all keywords in a list
def matchVideoStandard(keywords):
    for vstd in VideoStandardList:
        match = True
        # Check if all keywords are contained in vstd.keywords
        for word in keywords:
            if word not in vstd.keywords:
                match = False

        # If a match was found, return this vstd
        if match:
            return vstd

    # If no match, None is returned
    return None



# Find the first standard in AudioStandardList
# matching all keywords in a list
def matchAudioStandard(keywords):
    for astd in AudioStandardList:
        match = True
        # Check if all keywords are contained in astd.keywords
        for word in keywords:
            if word not in astd.keywords:
                match = False

        # If a match was found, return this astd
        if match:
            return astd

    # If no match, None is returned
    return None
        


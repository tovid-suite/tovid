#! /usr/bin/env python
# deps.py

"""This module is for verifying libtovid's run-time dependencies.
For example:

    deps.require(deps.core)

will look for all of tovid's core dependencies. If any cannot be found, the
missing ones are printed and an exception is raised. Run deps.py from a prompt
for further examples.

In practice:

    try:
        deps.require(deps.core)
    except deps.MissingError:
        print "Exiting..."
        sys.exit(1)

deps.core is an internal dictionary of tovid's core dependencies, where the
keys are the names, and the values are brief descriptions with URLs.

Provided dependency dictionaries:
    core      -- grep/sed/md5sum, mplayer, mencoder, mpjpegtools, ffmpeg
    magick    -- composite, convert
    dvd       -- spumux, dvdauthor, growisofs
    vcd       -- vcdxbuild, cdrdao
    transcode -- tcprobe, tcrequant
    plugin    -- sox, normalize
    all       -- ALL dependencies above
    
If you don't want to use a provided dictionary, you can specify individual
program names to look for:

    deps.require("more less cat")

require also provides ways to print custom URLs and help when it cannot find
dependencies. See help(deps.require) or keep reading.
"""

__all__ = [\
    'require']

import subprocess
import textwrap

###
### Exceptions
###

class DepError(Exception): pass
class InputError(DepError): pass
class MissingError(DepError): pass

###
### Module data
###

# Dictionary format: {  "name": "dep_url"  }
all = {}

core = { 
    "grep":         "a GNU utility (www.gnu.org/software/grep)",
    "sed":          "a GNU utility (directory.fsf.org/GNU/software/sed.html)",
    "md5sum":       "a GNU utility (www.gnu.org/software/coreutils)",
    "mplayer":      "part of mplayer (www.mplayerhq.hu)",
    "mencoder":     "part of mplayer (www.mplayerhq.hu)",
    "mplex":        "part of mjpegtools (mjpeg.sf.net)",
    "mpeg2enc":     "part of mjpegtools (mjpeg.sf.net)",
    "yuvfps":       "part of mjpegtools (mjpeg.sf.net)",
    "yuvdenoise":   "part of mjpegtools (mjpeg.sf.net)",
    "ppmtoy4m":     "part of mjpegtools (mjpeg.sf.net)",
    "mp2enc":       "part of mjpegtools (mjpeg.sf.net)",
    "jpeg2yuv":     "part of mjpegtools (mjpeg.sf.net)",
    "ffmpeg":       "a video encoding utility (ffmpeg.mplayerhq.hu)"      }
all.update(core)

magick = {
    "composite":    "part of ImageMagick (www.imagemagick.org)",
    "convert":      "part of ImageMagick (www.imagemagick.org)"     }
all.update(magick)

dvd = {
    "spumux":       "part of dvdauthor (dvdauthor.sf.net)",
    "dvdauthor":    "part of dvdauthor (dvdauthor.sf.net)",
    "growisofs":    "part of dvd+rw-tools (fy.chalmers.se/~appro/linux/DVD+RW)"}
all.update(dvd)

vcd = {
    "vcdxbuild":    "part of vcdimager (www.vcdimager.org)",
    "cdrdao":       "a cd burning application (cdrdao.sf.net)"   }
all.update(vcd)

transcode = {
    "tcprobe":      "part of transcode (www.transcoding.org)",
    "tcrequant":    "part of transcode (www.transcoding.org)"   }
all.update(transcode)

plugin = {
    "sox":          "swiss army knife for sound (sox.sf.net)",
    "normalize":    "wave gain and normalization (normalize.nongnu.org)" }
all.update(plugin)

__missing_dependency_message = \
"""Please install the above MISSING dependencies and try again. See
http://tovid.wikia.com/wiki/Tovid_dependencies or http://tovid.org
for more help.
"""

###
### Internal functions
###

def __whych(executable):
    """Returns the stdout from "which 'executable'"."""
    return subprocess.Popen(['which', executable], 
                            stdout=subprocess.PIPE).stdout.read()


def __have_dep(dependency):
    """Returns 'True' if 'dependency' exists, 'False' if not."""
    which_try = subprocess.Popen(['which', dependency],
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if which_try.wait() == 0:
        return True
    else:
        return False

###
### Exported functions
###

def require(dep, 
           help="You need these to finish what you were doing.",
           url="oops"):

    """Assert that one or more dependencies exist on the system, raise
    a 'MissingError' exception if not.
    
        dep:    The dependencies to assert. OK types: dict, list, str. 
                For dicts, the keys are used as names; for lists, the 
                members; and for a string, words separated by spaces.
        help:   A description about why the dependencies are needed,
        url:    A short description of the dep, and its homepage

    NB: url may be stored in one of the internal dependency dictionaries.
    In this case, the url is automatically taken from the dictionary value,
    overriding any input specified. Also, url is used for EVERY dep that
    doesn't have an existing entry in a dictionary, so be careful when
    checking for more than one dependency while giving a url.

    Examples:
        require(all)
            Look for ALL dependencies that are defined internally.

        require(core, "You are missing CORE dependencies!")
            Use the core dictionary to determine which dependencies to 
            look for. Print the help message if any dependency is missing.

        require("xine", "You can't preview!", "a video player (xinehq.de)")
            Check for xine and print the custom help and URL messages
            if missing.

        require("mplayer mencoder", url="a video player (mplayerhq.hu)")
            Look for mplayer and mencoder. Use the default help message,
            but print a custom URL.

    """
    # Get the deps to check for: dictionary.keys(), or a list
    if type(dep) == dict:
        dep = dep.keys()
    elif type(dep) == str:
        dep = dep.split(' ')
    elif type(dep) != list:
        raise InputError, "%s is not dictionary, list, or string!" % str(dep)

    # Find the missing dependencies
    have_group = True
    for d in dep:
        if not __have_dep(d):
            # Set the url message
            if all.has_key(d): 
                d_url = all[d]
            else:
                d_url = url
            # Tell the user which dependencies they're missing
            print "  MISSING: %s, %s." % (d, d_url)
            have_group = False

    # Having reported the missing dependencies, print the help message and quit
    if not have_group:
        print "\n", textwrap.fill(help + ' ' + __missing_dependency_message, 79)
        raise MissingError, "Cannot find required dependencies!"


###
### Main
###

if __name__ == "__main__":
    trials = [  
        (core,        "You are missing CORE dependencies!", "custom url 1"),
        (core,        "You are missing CORE dependencies!", "custom url 2"),
        ("grp md5sm", "You're missing some vowels!",        "custom url 4"),
        ("foo",       "heh, you don't have foo?!",          "see foo.org")   ]

    for dep, help, url in trials:
        try:
            print "================================================"
            print "Starting test..."
            require(dep, help, url)
        except MissingError:
            print "<< Would exit here. >>\n"
        else:
            print "Test passed!\n"


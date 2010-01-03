#@+leo-ver=4-thin
#@+node:eric.20090722212922.2656:@shadow manpage.py
"""This module is for parsing manual pages and extracting necessary information
for creating a metaGUI.

Needed capabilities:

* Retrieve text of a given manpage
* Read manpage for a given program and create a list of command-line options,
  with expected parameters and accompanying paragraph(s) of documentation.


"""

__all__ = [
    'get',
    'parse',
]

import re
import os
import textwrap
from libtovid.metagui.control import *

#@+others
#@+node:eric.20090722212922.2658:class Matcher
class Matcher:
    #@    @+others
    #@+node:eric.20090722212922.2659:search
    def search(self, pattern, text):
        self.value = re.search(pattern, text)
        return self.value
    #@-node:eric.20090722212922.2659:search
    #@+node:eric.20090722212922.2660:__getitem__
    def __getitem__(self, index):
        return self.value.group(index)

    #@-node:eric.20090722212922.2660:__getitem__
    #@-others
#@-node:eric.20090722212922.2658:class Matcher
#@+node:eric.20090722212922.2661:get
def get(program):
    """Return the text of the 'man' page for the given command-line program.
    """
    text = os.popen('man %s | col -b' % program).readlines()
    return ''.join(text)

#@-node:eric.20090722212922.2661:get
#@+node:eric.20090722212922.2662:class Option
class Option:
    #@    @+others
    #@+node:eric.20090722212922.2663:__init__
    def __init__(self, header='', doc=''):
        self.header = header
        self.doc = ''
        self.append(doc)
        # Get option name from header
        self.option = header.split()[0].lstrip('-')

    #@-node:eric.20090722212922.2663:__init__
    #@+node:eric.20090722212922.2664:getopt
    def getopt(self):
        """Get option name(s) and argument type from option header."""
        text = self.header
        option = ''
        arg = ''
        match = Matcher()
        # Typical option header styles
        # -f, --foobar
        if match.search('(-\w), --[-\w]+', text):
            option = match[1]
        # -f ARG, --foobar=ARG
        elif match.search('(-\w) (\w+), --[-\w]+=\w+', text):
            option = match[1]
            arg = match[2]
        # -foo
        elif match.search('(-[-\w]+)', text):
            option = match[1]
        # -foo ARG
        elif match.search('(-[-\w]+) \[?(\w+)]?', text):
            option = match[1]
            arg = match[2]

        return (option, arg)

    #@-node:eric.20090722212922.2664:getopt
    #@+node:eric.20090722212922.2665:append
    def append(self, text):
        """Append text to the documentation, with extra whitespace removed.
        """
        text = text.replace('\t', ' ')
        text = text.replace('  ', ' ')
        text = text.strip()
        # Join hyphenated words at end of lines
        if self.doc.endswith('-'):
            self.doc = self.doc.rstrip('-') + text
        else:
            self.doc += ' ' + text

    #@-node:eric.20090722212922.2665:append
    #@+node:eric.20090722212922.2666:__str__
    def __str__(self):
        text = self.header + '\n'
        text += textwrap.fill(self.doc.strip())
        return text

    #@-node:eric.20090722212922.2666:__str__
    #@-others
#@-node:eric.20090722212922.2662:class Option
#@+node:eric.20090722212922.2667:parse
def parse(text):
    """Generate meta-GUI from manpage documentation"""
    options = []
    # Match lines defining options
    option = re.compile("^ *-(\w+) ?(.*)")
    for line in text.splitlines():
        if re.match(option, line):
            options.append(Option(line.strip()))
        elif len(options) > 0:
            options[-1].append(line)
    return options

#@-node:eric.20090722212922.2667:parse
#@-others
#@-node:eric.20090722212922.2656:@shadow manpage.py
#@-leo

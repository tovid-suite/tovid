#! /usr/bin/env python
# builder.py

"""This module is a GUI builder with a GUI. It generates metagui code for
a specific program, with user interaction for fine-tuning the metagui widgets.

Ideas:

Parse manpage to get usage/option information, ex.:

    -audio-demuxer <[+]name> (-audiofile only)
    -audiofile <filename>
    -audiofile-cache <kBytes>
    -bandwidth <value> (network only)

User-customizable regex will ignore (..), create Controls for <..> etc.

Or: Keep a collection of "samples" of every time an option
is mentioned (anywhere in the manpage), and base widget config
decisions on the samples.

Need a GUI for making the process interactive. i.e. "I found these options
in the manpage, but you can make adjustments if necessary":

    [ ] -option1 [Number[^]] [Label] [default]
        [Tooltip text________________________]
        [min] [max] [scale[^]]

    [x] -option2 [Choice[^]] [Label] [default]
        [Tooltip text________________________]
        [a|b|c]
        
[Number[^]] is a combobox for choosing control type; [min] [max] [scale[^]]
and [a|b|c] are control-configuration widgets that appear depending on the
chosen control type. Checking an option includes it in the metaGUI.
"""

pass

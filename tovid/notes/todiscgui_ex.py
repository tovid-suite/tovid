#! /usr/bin/env python
# todiscgui_ex.py

"""Experimental todisc GUI using only meta.py widgets.

//Note: This isn't fully implemented yet--I'm writing the docs first.//

This module demonstrates a simplified approach to creating GUIs for
command-line programs. It's designed so _anyone_ can easily write their
own GUI, without having any programming experience.

It assumes your GUI is a direct frontend to a command-line program, with
each command-line option having an associated GUI control widget. Say, if
your program takes input and output filenames:

    $ tovid -in movie.avi -out movie_encoded

then you can create GUI widgets for those options like this:

    ('in', Filename, "Input filename")
    ('out', Filename, "Output prefix")

Command-line options are associated with GUI widgets by enclosing a tuple of
things in parentheses. These have the general format:

    ('option', Metawidget, "Label", ...)

where 'option' is a command-line option (without the leading '-'), Metawidget
is a class like Filename, Choice, or Number, describing what type of value the
option sets, and "Label" is the text that should appear next to the GUI widget
that controls the option's value. Other parameters describe the option,
its default value, and hints about how to draw the GUI control widget; they
are specific to the flavor of Metawidget being used.

Related options are grouped in a Panel by providing a panel name, and a
comma-separated list of option tuples:

    general = Panel("General",
        ('bgaudio', Filename, "Background audio file"),
        ('submenus', Flag, "Create submenus"),
        ('menu-length', Number, "Length of menu (seconds)", 0, 120)
        )

This will create three GUI widgets in a panel labeled "General": one for typing
or browsing to a filename, one for enabling or disabling submenus, and another 
for setting menu length to a number between 0 and 120.

To create the GUI with only this one panel, you can do this:

    app = Application("todisc GUI", 'todisc', general)
    app.run()

This creates the GUI, draws all the widgets, and will run your command-line
program at the push of a button.

If your program has a lot of options, one panel may not be enough to hold them
all without looking cluttered, so you may break them down into multiple Panels,
which will be shown in the GUI as tabs that you can switch between. Create a
list of Panels like this:

    panels = [
        Panel("Thumbnails",
            ('thumb-mist-color', Color, ...),
            ('wave', Text, ...)
        ),
        Panel("Text and Font",
            ('menu-font', Font, ...),
            ('menu-fontsize', Number, ...)
        )
    ]

Once you have a panel or list of panels, you can create the GUI and run it
like this:

    app = Application("todisc GUI", 'todisc', panels)
    app.run()


"""

# Get all the Metawidgets we'll need
from libtovid.gui.meta import *

# Panels, grouping together related options
general =  Panel("General",
    ('showcase', Filename,
        'Showcase', 'load', 'Select an image or video file.'),
    ('background', Filename,
        'Background', 'load', 'Select an image or video file'),
    ('bgaudio', Filename,
        'Audio', 'load', 'Select an audio file'),
    ('submenus', Flag,
        'Create submenus'),
    ('static', Flag,
        'Static menus (takes less time)'),
    ('menu-title', Text,
        'Menu title'),
    ('menu-length', Number,
        'Menu length', 0, 120, 'scale'),
    ('keep-files', Flag,
        'Keep useful intermediate files on exit', False),
    ('no-ask', Flag,
        'No prompts for questions', False),
    ('no-warn', Flag,
        'Do not pause at warnings', False),
    ('use-makemenu', Flag,
        'Use makemenu script instead of todisc, and exit', False),
    ('tovidopts', Optional, Text,
        'Custom tovid options')
)

menu = Panel("Menu",
    ('ani-submenus', Flag,
        'Animated submenus (takes more time)'),
    ('menu-fade', Flag,
        'Fade in menu', False),
    ('seek', Optional, List,
        'Seek time', 'Single value or list'),
    ('bgvideo-seek', Optional, Number,
        'Background video seek time', 0, 3600, 'scale', 2),
    ('bgaudio-seek', Optional, Number,
        'Background audio seek time', 0, 3600, 'scale', 2),
    ('showcase-seek', Optional, Number,
        'Showcase video seek time', 0, 3600, 'scale', 2),
    ('align', Optional, Choice,
        'Montage alignment', 'north|south|east|west'),
    ('intro', Filename,
        'Intro video', 'load', 'Select a video file'),
    ('showcase-titles-align', Optional, Choice,
        'Video(s) title alignment', 'west|east|center'),
    ('showcase-framestyle', Optional, Choice,
        'Showcase frame style', 'none|glass'),
    ('showcase-geo', Optional, Text,
        'Showcase image position (XxY')
)

thumbnails = Panel("Thumbnails",
    ('3dthumbs', Flag,
        'Create 3D thumbs'),
    ('thumb-shape', Optional, Choice,
        'Thumb shape', 'normal|oval|plectrum|egg'),
    ('opacity', Optional, Number,
        'Thumbnail opacity', 1, 100, 'spin', 100),
    ('blur', Optional, Number,
        'Blur', 1, 5, 'spin', 4),
    ('rotate-thumbs', Optional, List,
        'Rotate Thumbs (list)'),
    ('wave', Optional, Text,
        'Wave effect for showcase thumb', 'default'),
    ('rotate', Optional, Number,
        'Rotate Showcase thumb', -30, 30, 'spin', 5),
    ('thumb-mist-color', Optional, Color,
        'Thumb mist color [white]'),
    ('tile3x1', Flag,
        'Arrange thumb montage in 1 row of 3 thumbs')
)

audio = Panel("Audio",
    ('menu-audio-length', Optional, Number,
        'Menu audio length', 0, 120, 'scale'),
    ('menu-audio-fade', Optional, Number,
        'Menu audio fade', 0, 10, 'scale', 1),
    ('submenu-audio', Optional, Filename,
        'Submenu audio file', 'load',
        'Select an audio file, or video file with audio'),
    ('submenu-audio-length', Optional, Number,
        'Submenu audio length', 0, 120, 'scale'),
    ('submenu-audio-fade', Optional, Number,
        'Submenu audio fade', 0, 10, 'scale', 1)
)

text = Panel("Text and Font",
    ('menu-font', Optional, Font,
        'Menu title font'),
    ('thumb-font', Optional, Font,
        'Video title(s) font'),
    ('menu-fontsize', Optional, Number,
        'Menu title font size', 0, 80, 'scale'),
    ('thumb-fontsize', Optional, Number,
        'Video title(s) font size', 0, 80, 'scale'),
    ('title-color', Optional, Color,
        'Title color'),
    ('submenu-title-color', Optional, Color,
        'Submenu title color'),
    ('thumb-text-color', Optional, Color,
        'Video title(s) color'),
    ('text-mist', Flag,
        'Text mist', False),
    ('text-mist-color', Optional, Color,
        'Text mist color'),
    ('text-mist-opacity', Optional, Number,
        'Text mist opacity', 1, 100, 'spin', 60),
    ('menu-title-geo', Optional, Choice,
        'Menu title position', 'north|south|west|east|center'),
    ('menu-title-offset', Optional, Text,
        'Offset for menu title position', '+0+0'),
    ('stroke-color', Optional, Color,
        'Stroke color'),
    ('submenu-stroke-color', Optional, Color,
        'Submenu stroke color'),
    ('title-gap', Optional, Number,
        'Space between Textmenu titles (pixels)', 0, 400, 'spin', 2),
    ('text-start', Optional, Number,
        'Start Textmenu titles at: (pixels)', 0, 460, 'spin', 2)
)

authoring = Panel("Authoring",
    ('chapters', Optional, List,
        'Number of Chapters', 'Single value or list'),
    ('chain-videos', Optional, List,
        'Chain videos together', ' See "man todisc" for details'),
    ('widescreen', Optional, Choice,
        'Widescreen', 'nopanscan|noletterbox'),
    ('aspect', Optional, Choice,
        'Aspect ratio', '4:3|16:9'),
    ('highlight-color', Optional, Color,
        'Highlight color'),
    ('select-color', Optional, Color,
        'Selection color'),
    ('button-style', Optional, Choice,
        'Button style', 'rect|text|text-rect'),
    ('audio-lang', Optional, List,
        'Default audio language', "Single value or list"),
    ('subtitles', Optional, List,
        'Default subtitle language', "Single value or list"),
    ('outlinewidth', Optional, Number,
        'Outlinewidth for spumux buttons', 0, 20, 'scale'),
    ('loop', Optional, Number,
        'Loop', 0, 30, 'scale'),
    ('playall', Flag,
        '"Play all" button', False)
)

# A list of all panels, shown in tabs in this order
panels = [
    general,
    menu,
    thumbnails,
    audio,
    text,
    authoring
]

# Create and run the application
todiscgui = Application('todisc GUI', 'todisc', panels)
todiscgui.run()

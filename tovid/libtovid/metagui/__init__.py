#! /usr/bin/env python
# __init__.py (metagui)


"""A simplified GUI-writing module.


INTRODUCTION

This module demonstrates a simplified approach to creating GUIs for
command-line programs. It's designed so _anyone_ can easily write their
own GUI, without having any programming experience.

It assumes your GUI is a direct frontend to one or more command-line programs,
with each command-line option having an associated GUI control widget. Several
kinds of widget are provided, for setting Filename, Color, Number or Font, or
for picking a Choice or Flag.

You probably know of a handful of command-line applications that would be
much better with a GUI, even a cheesy-looking Tkinter one. This module makes
it easy to create one.


DEFINE CONTROLS

Say, if you have a program that takes input and output filenames:

    $ tovid -in movie.avi -out movie_encoded

then you can create GUI widgets for those options like this:

    Filename('-in', "Input filename")
    Filename('-out', "Output prefix")

These have the general format:

    Control('-option', "Label", ...)

where:

    Control   is a Control subclass, such as Filename, Choice, or Number,
              describing what type of value is being controlled;
    'option'  is a command-line option (without the leading '-'),
              whose value is set by the Control; and
    "Label"   is the text that should appear next to the GUI Control.

Other parameters include default value, help/tooltip text to show, allowable
values, and hints about how to draw the GUI control widget; they are specific
to the flavor of Control being used. Here's a sampling:

    Choice    Multiple-choice values
    Color     Color selection button
    Filename  Type or [Browse] a filename
    FileList  Add/remove/rearrange filename list
    Flag      Check box, yes or no
    Font      Font selection button
    List      Space-separated list
    Number    Number between A and B
    Text      Plain old text

For a full list of available Control subclasses and how to use them,
see libtovid/metagui/control.py.


CREATING THE GUI

First, give your Controls a place to live, in a Panel:

    general = Panel("General",
        Filename('-bgaudio', "Background audio file"),
        Flag('-submenus', "Create submenus"),
        Number('-menu-length', "Length of menu (seconds)", 0, 120)
        )

This will create three GUI widgets in a Panel labeled "General": one for typing
or browsing to a filename, one for enabling or disabling submenus, and another 
for setting menu length to a number between 0 and 120. You can nest panels
inside one another for grouping; sub-Panels have their own label and list of
Controls or sub-Panels.

Once you have a Panel, you can create an Application:

    app = Application('todisc', [general])

This says your application will run the 'todisc' command-line program,
passing options set by the "General" panel. Now, create the GUI:

    gui = GUI('MyGUI', [app])
    gui.run()

This creates the GUI, draws all the widgets, and will run your command-line
program at the push of a button.


CREATE A MULTI-PANEL GUI

If your program has a lot of options, one panel may not be enough to hold them
all without looking cluttered, so you may break them down into multiple Panels,
which will be shown in the GUI as tabs that you can switch between. Create
Panels like this:

    thumbs = Panel("Thumbnails",
        Color('-thumb-mist-color', ...),
        Text('-wave', ...)
    )
    text = Panel("Text",
        Font('-menu-font', ...),
        Number('-menu-fontsize', ...)
    )

then, create the Application and GUI:

    todisc = Application('todisc', [thumbs, text])
    gui = GUI('MyGUI', [todisc])
    gui.run()

If multiple panels are given to Application, a tabbed interface is created,
with one tab for each panel.


CREATE A MULTI-APPLICATION GUI

If your GUI needs to be able to run several different command-line programs,
you can create a multi-application GUI. Create panels for each application,
then create the applications:

    todisc = Application('todisc', [todisc_panel1, todisc_panel2])
    tovid = Application('tovid', [tovid_panel1, tovid_panel2])

and then the GUI:

    gui = GUI('MultiGUI', [todisc, tovid])
    gui.run()

See the apps/ directory for example GUIs.
"""

# Export everything from support, control, and gui modules
# (Open to suggestion about more elegant ways to do this...)
from support import *
from control import *
from gui import *
from support import __all__ as all_support
from control import __all__ as all_control
from gui import __all__ as all_gui
__all__ = [\
    'support',
    'control',
    'gui',
    'manpage',
    'builder',
    'tooltip',
    'odict'] + all_support + all_control + all_gui


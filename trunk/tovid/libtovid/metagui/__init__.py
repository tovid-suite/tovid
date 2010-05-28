"""This module provides a simpler way to create GUIs for command-line programs.

It assumes your GUI is a direct frontend to one or more command-line programs,
with each command-line option having an associated GUI control widget. Several
kinds of widget are provided, for setting Filename, Color, Number or Font, or
for picking a Choice or Flag.

You probably know a handful of command-line applications that could benefit
from a GUI, even a cheesy-looking Tkinter one. This module makes it easy to
create one.


Define controls
---------------

Say, if you have a program that takes input and output filenames::

    $ tovid -in movie.avi -out movie_encoded

then you can create GUI widgets for those options like this::

    Filename('Input filename', '-in')
    Filename('Output prefix', '-out')

These have the general format::

    Control('Label', '-option', ...)

where:

    ``Control``
        is a ``Control`` subclass appropriate to whatever is being controlled
    ``'Label'``
        is the text that should appear next to the GUI Control
    ``'-option'``
        is a command-line option whose value is set by the Control

Other parameters include default value, help/tooltip text to show, allowable
values, and hints about how to draw the GUI control widget; they are specific
to the flavor of Control being used.

For a full list of available Control subclasses and how to use them,
see the :mod:`libtovid.metagui.control` module.


Creating the GUI
----------------

Controls can be grouped together either vertically or horizontally (using a
VPanel or HPanel, respectively)::

    general = VPanel('General',
        Filename('Background audio file', '-bgaudio'),
        Flag('Create submenus', '-submenus'),
        Number('Length of menu (seconds)', '-menu-length', 0, 120)
        )

This will create three GUI widgets in a panel labeled 'General': one for typing
or browsing to a filename, one for enabling or disabling submenus, and another
for setting menu length to a number between 0 and 120. You can nest panels
inside one another for grouping; sub-panels have their own label and list of
Controls or sub-Panels.

Once you have a panel, you can create an Application::

    app = Application('todisc', [general])

This says your application will run the 'todisc' command-line program,
passing options set by the 'General' panel. Now, create the GUI::

    gui = GUI('MyGUI', [app])
    gui.run()

This creates the GUI, draws all the widgets, and will run your command-line
program at the push of a button.


Create a multi-panel GUI
------------------------

If your program has a lot of options, one panel may not be enough to hold them
all without looking cluttered, so you may break them down into multiple Panels,
which will be shown in the GUI as tabs that you can switch between. Create
Panels like this::

    thumbs = Panel('Thumbnails',
        Color('Mist color', '-thumb-mist-color', ...),
        Text('Wave', '-wave', ...)
    )
    text = Panel('Text',
        Font('Menu font face', '-menu-font', ...),
        Number('Menu font size', '-menu-fontsize', ...)
    )

then, create the Application and GUI::

    todisc = Application('todisc', [thumbs, text])
    gui = GUI('MyGUI', [todisc])
    gui.run()

If multiple panels are given to Application, a tabbed interface is created,
with one tab for each panel.
"""

# Export everything from support, control, panel, and gui modules
# (I'm open to suggestion about more elegant ways to do this...)
from libtovid.metagui.support import *
from libtovid.metagui.control import *
from libtovid.metagui.panel import *
from libtovid.metagui.gui import *

from libtovid.metagui.support import __all__ as all_support
from libtovid.metagui.control import __all__ as all_control
from libtovid.metagui.panel import __all__ as all_panel
from libtovid.metagui.gui import __all__ as all_gui
__all__ = [
    'variable',
    'support',
    'control',
    'gui',
    'log',
    'manpage',
    'builder',
    'tooltip',
    'widget'] + all_support + all_control + all_panel + all_gui


#@+leo-ver=4-thin
#@+node:eric.20090722212922.2545:@shadow builder.py
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

__all__ = [
    'ControlEditor',
    'ControlChooser',
]

from inspect import getargspec

# Python < 3.x
try:
    import Tkinter as tk
# Python 3.x
except ImportError:
    import tkinter as tk

# Absolute imports
from libtovid.odict import Odict
from libtovid.metagui import Text, Number, Flag
from libtovid.metagui.control import CONTROLS
from libtovid.metagui.support import ComboBox

#@+others
#@+node:eric.20090722212922.2547:class ControlEditor
class ControlEditor (tk.Frame):
    """A GUI control panel for setting Control arguments."""
    #@    @+others
    #@+node:eric.20090722212922.2548:__init__
    def __init__(self, control):
        """Create a GUI panel for the given Control subclass.
        """
        self.control = control
        # Find out what arguments/defaults the Control constructor has
        args, varargs, varkw, defaults = getargspec(self.control.__init__)
        self.kwargs = Odict(args[1:], defaults)

    #@-node:eric.20090722212922.2548:__init__
    #@+node:eric.20090722212922.2549:draw
    def draw(self, master):
        """Draw widgets for adjusting all Control.__init__ arguments."""
        tk.Frame.__init__(self, master)
        for arg, default in self.kwargs.items():
            if type(default) == str:
                widget = Text('', arg, default)
            elif type(default) == int:
                widget = Number('', arg, default)
            elif type(default) == bool:
                widget = Flag('', arg, default)
            else:
                widget = Text('', arg, default)

            widget.draw(self)
            widget.pack()


    #@-node:eric.20090722212922.2549:draw
    #@-others
#@-node:eric.20090722212922.2547:class ControlEditor
#@+node:eric.20090722212922.2550:class ControlChooser
class ControlChooser (tk.Frame):
    """A GUI panel for choosing a Control type and setting its arguments."""
    #@    @+others
    #@+node:eric.20090722212922.2551:__init__
    def __init__(self):
        self.control = tk.StringVar()

    #@-node:eric.20090722212922.2551:__init__
    #@+node:eric.20090722212922.2552:draw
    def draw(self, master):
        tk.Frame.__init__(self, master)
        self.choices = ComboBox(self, CONTROLS.keys(),
                                variable=self.control,
                                command=self.refresh)
        self.choices.pack()
        self.editor = ControlEditor(Number)
        self.control.set('Number')
        self.editor.draw(self)
        self.editor.pack()

    #@-node:eric.20090722212922.2552:draw
    #@+node:eric.20090722212922.2553:refresh
    def refresh(self, event=None):
        """Show the editor for the currently selected control.
        """
        self.editor.pack_forget()
        newcontrol = CONTROLS[self.control.get()]
        self.editor = ControlEditor(newcontrol)
        self.editor.draw(self)
        self.editor.pack()

    #@-node:eric.20090722212922.2553:refresh
    #@-others
#@-node:eric.20090722212922.2550:class ControlChooser
#@-others

#@<<demo>>
#@+node:eric.20090723212423.3633:<<demo>>
# Demo
if __name__ == '__main__':
    root = tk.Tk()
    chooser = ControlChooser()
    chooser.draw(root)
    chooser.pack()
    root.mainloop()

#@-node:eric.20090723212423.3633:<<demo>>
#@nl
#@-node:eric.20090722212922.2545:@shadow builder.py
#@-leo

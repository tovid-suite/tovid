#! /usr/bin/env python
# meta.py

"""This module defines several Tkinter "meta widgets".
"""

__all__ = [
    'Metawidget',
    'Choice',
    'ColorPicker',
    'FileEntry',
    'Flag',
    'FontPicker',
    'LabelEntry',
    'Number',
    'Optional',
    'OptionFrame']

from Tkinter import *
from tkFileDialog import *
from tkColorChooser import askcolor
from libtovid import log

### --------------------------------------------------------------------
### Custom widgets
### --------------------------------------------------------------------

class Metawidget (Frame):
    """A base class for extended special-purpose widgets.

    A Metawidget may contain any number of other widgets, and store a
    single variable value. Presumably, a subclass will link self.variable
    to one or more control widgets, via their textvariable attribute.
    
    See the Metawidget subclasses below for examples of how self.variable,
    get() and set() are used.
    """
    def __init__(self, master=None, vartype=str, *args, **kwargs):
        """Create a Metawidget with the given master and variable type.

            master:   Tkinter widget that will contain this Metawidget
            vartype:  Type of stored variable (str, bool, int, or float)
        """
        Frame.__init__(self, master, *args, **kwargs)
        vartypes = {
            str: StringVar,
            bool: BooleanVar,
            int: IntVar,
            float: DoubleVar}
        # Create an appropriate Tkinter variable type
        if vartype in vartypes:
            self.variable = vartypes[vartype]()
        # Or use a generic Variable
        else:
            self.variable = Variable()

    def get(self):
        """Return the value of the Metawidget's variable."""
        return self.variable.get()

    def set(self, value):
        """Set the Metawidget's variable to the given value."""
        self.variable.set(value)

    def enable(self, enable=True):
        """Enable or disable all sub-widgets."""
        if enable:
            newstate = NORMAL
        else:
            newstate = DISABLED
        for widget in self.children.values():
            widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)


### --------------------------------------------------------------------

class Flag (Metawidget):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 master=None,
                 label="Debug",
                 default=False,
                 *args, **kwargs):
        """Create a Flag widget with the given label and default value.

            master:   Tkinter widget that will contain this Flag
            label:    Text label for the flag
            default:  Default value (True or False)
        """
        Metawidget.__init__(self, master, bool, *args, **kwargs)
        log.debug("Creating Flag(%s)" % label)
        self.variable.set(default)
        # Create and pack widgets
        self.check = Checkbutton(self, text=label, variable=self.variable)
        self.check.pack()

### --------------------------------------------------------------------

class Choice (Metawidget):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 master=None,
                 label="Choices",
                 choices='A|B',
                 default=None,
                 *args, **kwargs):
        """Initialize Choice widget with the given label and list of choices.

            master:   Tkinter widget that will contain this Choice
            label:    Text label for the choices
            choices:  Available choices, in list form: ['one', 'two']
                      or string form: 'one|two'
            default:  Default choice, or None to use first choice in list
        """
        # TODO: Allow alternative choice styles (listbox, combobox?)
        Metawidget.__init__(self, master, *args, **kwargs)
        log.debug("Choice(%s, %s)" % (label, choices))
        # If choices is a string, split on '|'
        if type(choices) == str:
            choices = choices.split('|')
        # Use first choice if default wasn't provided
        if default is None:
            default = choices[0]
        self.variable.set(default)
        # Create and pack widgets
        self.label = Label(self, text=label)
        self.label.pack(side=LEFT)
        self.rb = {}
        for choice in choices:
            self.rb[choice] = Radiobutton(self, text=choice, value=choice,
                                          variable=self.variable)
            self.rb[choice].pack(side=LEFT)


### --------------------------------------------------------------------

class Number (Metawidget):
    """A widget for choosing or entering a number"""
    def __init__(self,
                 master=None,
                 label="Number",
                 min=1,
                 max=10,
                 #resolution=1,
                 style='spin',
                 default=None,
                 *args, **kwargs):
        """Create a number-setting widget.
        
            master:   Tkinter widget that will contain this Number
            label:    Text label describing the meaning of the number
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' or 'scale'
            default:  Default value, or None to use minimum
        """
        # TODO: Multiple styles (entry, spinbox, scale)
        Metawidget.__init__(self, master, int, *args, **kwargs)
        log.debug("Creating Number(%s, %s, %s)" % (label, min, max))
        # Use min if default wasn't provided
        if default is None:
            default = min
        self.variable.set(default)
        # Create and pack widgets
        self.label = Label(self, name='label', text=label)
        if style == 'spin':
            self.number = Spinbox(self, from_=min, to=max,
                                  textvariable=self.variable)
        else: # 'scale'
            self.number = Scale(self, from_=min, to=max,
                                variable=self.variable, orient=HORIZONTAL)
        self.label.pack(side=LEFT)
        self.number.pack(side=LEFT)

### --------------------------------------------------------------------

class LabelEntry (Metawidget):
    """A labeled text entry box"""
    def __init__(self,
                 master=None,
                 label="Text",
                 default='',
                 *args, **kwargs):
        Metawidget.__init__(self, master, str, *args, **kwargs)
        log.debug("Creating LabelEntry(%s)" % label)
        self.variable.set(default)
        # Create and pack widgets
        self.label = Label(self, text=label)
        self.entry = Entry(self, width=30, textvariable=self.variable)
        self.label.pack(side=LEFT)
        self.entry.pack(side=LEFT)

### --------------------------------------------------------------------

class FileEntry (Metawidget):
    """A filename selector with a label, text entry, and browse button.
    """
    def __init__(self,
                 master=None,
                 label='Filename',
                 type='load',
                 desc='Select a file to load',
                 default='',
                 *args, **kwargs):
        """Create a FileEntry with label, text entry, and browse button.
        
            master:  Tkinter widget that will contain the FileEntry
            label:   Text of label next to file entry box
            type:    Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
            default: Default filename
        """
        Metawidget.__init__(self, master, *args, **kwargs)
        log.debug("Creating FileEntry(%s)" % label)
        self.variable.set(default)
        self.type = type
        self.desc = desc
        # Create and grid widgets
        self.label = Label(self, text=label, justify=LEFT)
        self.entry = Entry(self, width=40, textvariable=self.variable)
        self.button = Button(self, text="Browse...", command=self.browse)
        self.label.grid(row=0, column=0, sticky=E)
        self.entry.grid(row=0, column=1, sticky=EW)
        self.button.grid(row=0, column=2, sticky=E)
        # Link button's variable to ours
        self.button.variable = self.variable

    def browse(self, event=None):
        """Event handler when browse button is pressed"""
        if self.type == 'save':
            filename = asksaveasfilename(parent=self, title=self.desc)
        else: # 'load'
            filename = askopenfilename(parent=self, title=self.desc)
        # Got a filename? Save it
        if filename:
            self.set(filename)

### --------------------------------------------------------------------

class ColorPicker (Metawidget):
    def __init__(self,
                 master=None,
                 label="Color",
                 default='',
                 *args, **kwargs):
        """Create a widget that opens a color-chooser dialog.
        
            master:  Tkinter widget that will contain the ColorPicker
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
        """
        Metawidget.__init__(self, master, str, *args, **kwargs)
        log.debug("Creating ColorPicker(%s)" % label)
        self.variable.set(default)
        # Create and pack widgets
        self.label = Label(self, text=label)
        self.button = Button(self, text="None", command=self.change)
        self.label.pack(side=LEFT)
        self.button.pack(side=LEFT)
        
    def change(self):
        """Choose a color, and set the button's label and color to match."""
        rgb, color = askcolor(self.get())
        if color:
            self.set(color)
            self.button.config(text=color, foreground=color)

### --------------------------------------------------------------------

class FontPicker (Metawidget):
    # TODO
    pass

### --------------------------------------------------------------------

class Optional (Frame):
    """Container that shows/hides an optional Metawidget."""
    def __init__(self,
                 master=None,
                 widget=None,
                 label='Option',
                 *args, **kwargs):
        """Create an Optional widget.

            master:  Tkinter widget that will contain the Optional
            widget:  A Metawidget to show or hide
            label:   Label for the optional widget
        """
        Frame.__init__(self, master)
        log.debug("Creating Optional(%s)" % label)
        self.active = BooleanVar()
        # Create and pack widgets
        self.check = Checkbutton(self, text=label, variable=self.active,
                                 command=self.showHide, justify=LEFT)
        self.check.pack(side=LEFT)
        self.widget = widget(self, '', *args)
        self.widget.pack(side=LEFT)
        self.widget.disable()
        self.active.set(False)
    
    def showHide(self):
        """Show or hide the sub-widget."""
        if self.active.get():
            self.widget.enable()
        else:
            self.widget.disable()

    def get(self):
        """Return the sub-widget's value if active, or None if inactive."""
        if self.active.get():
            return self.widget.get()
        else:
            return None
    
    def set(self, value):
        """Set sub-widget's value."""
        self.widget.set(value)

### --------------------------------------------------------------------

class OptionFrame (Frame):
    """A Frame containing Metawidgets that control command-line options.
    """
    def __init__(self, master=None, *args, **kwargs):
        """Create an OptionFrame with the given master and control widgets.

            master:  Tkinter widget that will contain this OptionFrame
            args:    Positional arguments to pass to Frame constructor
            kwargs:  Keyword arguments to pass to Frame constructor
        """
        Frame.__init__(self, master, *args, **kwargs)
        self.controls = {}

    def add(self, option, widget):
        """Add a widget controlling the given option.
        """
        assert isinstance(widget, Widget)
        self.controls[option] = widget
        
    def get(self, option):
        """Get the value of the given option from its associated widget.
        """
        return self.controls[option].get()

    def set(self, option, value):
        """Set the value of the widget associated with the given option.
        """
        self.controls[option].set(value)

    def arglist(self):
        """Return a list of command-line arguments for all options.
        """
        args = []
        for option, widget in self.controls.items():
            value = widget.get()
            # Boolean values control a flag
            if value == True:
                args.append("-%s" % option)
            # All others use '-option value'
            elif value:
                args.append("-%s" % option)
                args.append(value)
        return args

### --------------------------------------------------------------------

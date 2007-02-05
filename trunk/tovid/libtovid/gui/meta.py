#! /usr/bin/env python
# meta.py

"""This module defines several Tkinter "meta widgets".
"""

__all__ = [
    'Metawidget',
    'BrowseButton',
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
    def __init__(self, master=None, vartype=str):
        """Create a Metawidget with the given master and variable type.

            master:   Tkinter widget that will contain this Metawidget
            vartype:  Type of stored variable (str, bool, int, or float)
        """
        Frame.__init__(self, master)
        types = {
            str: StringVar,
            bool: BooleanVar,
            int: IntVar,
            float: DoubleVar}
        # Use an appropriate Tkinter variable type
        if vartype in types:
            self.variable = types[vartype]()
        # Or use a generic Variable
        else:
            self.variable = Variable()
        self.names = []
        self.widgets = []

    def __getitem__(self, name):
        """Return the widget indexed by the given name.
        """
        if name in self.names:
            return self.widgets[self.names.index(name)]
        else:
            raise KeyError("Widget named '%s' does not exist." % key)

    def __setitem__(self, name, widget):
        """Store a widget with the given name.
        """
        assert isinstance(widget, Widget)
        if name in self.names:
            self.widgets[self.names.index(name)] = widget
        else:
            self.names.append(name)
            self.widgets.append(widget)

    def pack_all(self, *args, **kwargs):
        """Pack all widgets in the order they were defined. This function
        takes the same arguments as the regular Tkinter pack() function.
        """
        for widget in self.widgets:
            widget.pack(*args, **kwargs)

    def grid_all(self, *args, **kwargs):
        """Grid all widgets in the order they were defined. This function
        takes the same arguments as the regular Tkinter grid() function.
        """
        for widget in self.widgets:
            widget.grid(*args, **kwargs)

    def get(self):
        """Return the value of the Metawidget's variable."""
        return self.variable.get()

    def set(self, value):
        """Set the Metawidget's variable to the given value."""
        self.variable.set(value)

    def enable(self, enable=True):
        """Enable or disable sub-widgets."""
        if enable:
            newstate = ACTIVE
        else:
            newstate = DISABLED
        for widget in self.widgets:
            widget.config(state=newstate)

    def disable(self):
        """Disable sub-widgets."""
        self.enable(False)

### --------------------------------------------------------------------

class Flag (Metawidget):
    """A widget for controlling a yes/no value."""
    def __init__(self, master=None, label="Debug", default=False):
        """Create a Flag widget with the given label and default value.

            master:   Tkinter widget that will contain this Flag
            label:    Text label for the flag
            default:  Default value (True or False)
        """
        Metawidget.__init__(self, master, bool)
        print "Creating Flag", label
        self.variable.set(default)
        # Create and pack widgets
        self['check'] = Checkbutton(self, text=label, variable=self.variable)
        self.pack_all()

### --------------------------------------------------------------------

class Choice (Metawidget):
    """A widget for choosing one of several options.
    """
    def __init__(self, master=None, label="Choices", choices=['A', 'B'],
                 default=None):
        """Initialize Choice widget with the given label and list of choices.

            master:   Tkinter widget that will contain this Choice
            label:    Text label for the choices
            choices:  Available choices, in list form: ['one', 'two']
                      or string form: 'one|two'
            default:  Default choice, or None to use first choice in list
        """
        # TODO: Allow alternative choice styles (listbox, combobox?)
        Metawidget.__init__(self, master)
        print "Creating Choice", label, choices
        # If choices is a string, split on '|'
        if type(choices) == str:
            choices = choices.split('|')
        # Use first choice if default wasn't provided
        if default is None:
            default = choices[0]
        self.variable.set(default)
        # Create and pack widgets
        self['label'] = Label(self, text=label)
        for choice in choices:
            self['rb_%s' % choice] =\
                Radiobutton(self, text=choice, value=choice,
                            variable=self.variable, command=self.change)
        self.pack_all(side=LEFT)

    def change(self):
        """Event handler called when the radiobutton is changed.
        Print the new value chosen."""
        print "%s chosen" % self.get()

### --------------------------------------------------------------------

class Number (Metawidget):
    """A widget for choosing or entering a number"""
    def __init__(self, master=None, label="Number", min=1, max=10,
                 style='spin', default=None):
        """Create a number-setting widget.
        
            master:   Tkinter widget that will contain this Number
            label:    Text label describing the meaning of the number
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' or 'scale'
            default:  Default value, or None to use minimum
        """
        # TODO: Multiple styles (entry, spinbox, scale)
        Metawidget.__init__(self, master, int)
        print "Creating Number", label, min, max
        # Use min if default wasn't provided
        if default is None:
            default = min
        self.variable.set(default)
        # Create and pack widgets
        self['label'] = Label(self, text=label)
        if style == 'spin':
            self['number'] = Spinbox(self, from_=min, to=max,
                                     textvariable=self.variable)
        else: # 'scale'
            self['number'] = Scale(self, from_=min, to=max, orient=HORIZONTAL,
                                   variable=self.variable)
        self.pack_all(side=LEFT)
        

### --------------------------------------------------------------------

class LabelEntry (Metawidget):
    """A labeled text entry box"""
    def __init__(self, master=None, label="Text", default=''):
        Metawidget.__init__(self, master, str)
        print "Creating LabelEntry", label
        self.variable.set(default)
        # Create and pack widgets
        self['label'] = Label(self, text=label)
        self['entry'] = Entry(self, width=30, textvariable=self.variable)
        self.pack_all(side=LEFT)

### --------------------------------------------------------------------

class BrowseButton (Metawidget):
    """A "Browse" button that opens a file browser for loading/saving a file.
    """
    # TODO: simpler widget name
    def __init__(self, master=None, type='load', title="Select a file"):
        """Create a file-browser button.
        
            master:   Tkinter widget that will contain this BrowseButton
            type:     What kind of file dialog to use ('load' or 'save')
            title:    Text to display in the titlebar of the file dialog
        """
        Metawidget.__init__(self, master, str)
        print "Creating BrowseButton", type
        self.type = type
        self.title = title
        # Create and pack widgets
        self['button'] = Button(self, text="Browse...", command=self.onClick)
        self.pack_all()

    def onClick(self, event=None):
        """Event handler when button is pressed"""
        if self.type == 'save':
            filename = asksaveasfilename(parent=self, title=self.title)
        else: # 'load'
            filename = askopenfilename(parent=self, title=self.title)
        # Got a filename? Save it
        if filename and self.variable:
            self.set(filename)

### --------------------------------------------------------------------

class FileEntry (Metawidget):
    """A filename selector frame, consisting of label, entry, and browse button.
    """
    def __init__(self, master=None, label='Filename', type='load',
                 desc='Select a file to load', default=''):
        """Create a FileEntry with label, text entry, and browse button.
        
            master:  Tkinter widget that will contain the FileEntry
            label:   Text of label next to file entry box
            type:    Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
            default: Default value
        """
        Metawidget.__init__(self, master)
        print "Creating FileEntry", label
        self.variable.set(default)
        # Create and grid widgets
        self['label'] = Label(self, text=label)
        self['entry'] = Entry(self, width=40, textvariable=self.variable)
        self['button'] = BrowseButton(self, type, desc)
        self['label'].grid(row=0, column=0, sticky=E)
        self['entry'].grid(row=0, column=1, sticky=EW)
        self['button'].grid(row=0, column=2, sticky=E)
        # Link button's variable to ours
        self['button'].variable = self.variable

### --------------------------------------------------------------------

class ColorPicker (Metawidget):
    def __init__(self, master=None, label="Color", default=''):
        """Create a widget that opens a color-chooser dialog.
        
            master:  Tkinter widget that will contain the ColorPicker
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
        """
        Metawidget.__init__(self, master, str)
        print "Creating ColorPicker", label
        self.variable.set(default)
        # Create and pack widgets
        self['label'] = Label(self, text=label)
        self['button'] = Button(self, text="None", command=self.change)
        self.pack_all(side=LEFT)

    def change(self):
        rgb, color = askcolor(self.get())
        if color:
            self.set(color)
            self['button'].config(text=color, foreground=color)

### --------------------------------------------------------------------

class FontPicker (Metawidget):
    # TODO
    pass

### --------------------------------------------------------------------

class Optional (Metawidget):
    """Container that shows/hides an optional Metawidget."""
    def __init__(self, master=None, widget=None, label='Option', *args):
        """Create an Optional widget.

            master:  Tkinter widget that will contain the Optional
            widget:  A Metawidget to show or hide
            label:   Label for the optional widget
            *args:   Additional arguments to pass to the sub-widget
        """
        Metawidget.__init__(self, master, bool)
        print "Creating Optional", label
        self.active = False
        # Create and pack widgets
        self['check'] = Checkbutton(self, text=label, command=self.showHide)
        self['widget'] = widget(self, '', *args)
        self.pack_all(side=LEFT)
        self['widget'].disable()
    
    def showHide(self):
        """Show or hide the sub-widget."""
        if self.active:
            self['widget'].disable()
            self.active = False
        else:
            self['widget'].enable()
            self.active = True

    def get(self):
        """Return the sub-widget's value if active, or None if inactive."""
        if self.active:
            return self['widget'].get()
        else:
            return None
    
    def set(self, value):
        """Set sub-widget's value."""
        self['widget'].set(value)

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

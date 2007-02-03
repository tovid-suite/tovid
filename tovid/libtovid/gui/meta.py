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
    'Optional']

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

    def get(self):
        """Return the value of the Metawidget's variable."""
        return self.variable.get()

    def set(self, value):
        """Set the Metawidget's variable to the given value."""
        self.variable.set(value)

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
        self.variable.set(default)
        self.check = Checkbutton(self, text=label, variable=self.variable)
        self.check.pack()

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
        # If choices is a string, split on '|'
        if type(choices) == str:
            choices = choices.split('|')
        # Use first choice if default wasn't provided
        if default is None:
            default = choices[0]
        self.variable.set(default)

        self.label = Label(self, text=label+':')
        self.label.pack(side=LEFT)
        # Radiobutton widgets, indexed by choice value
        self.rb = {}
        for choice in choices:
            self.rb[choice] =\
                Radiobutton(self, text=choice, value=choice,
                            variable=self.variable, command=self.change)
            self.rb[choice].pack(side=LEFT)
        # First choice by default
        self.set(choices[0])

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
        # Use min if default wasn't provided
        if default is None:
            default = min
        self.variable.set(default)
        self.label = Label(self, text=label+':')
        self.label.pack(side=LEFT)
        if style == 'spin':
            self.number = Spinbox(self, from_=min, to=max,
                                  textvariable=self.variable)
        else:
            self.number = Scale(self, from_=min, to=max, orient=HORIZONTAL,
                                variable=self.variable)
        self.number.pack(side=LEFT)

### --------------------------------------------------------------------

class LabelEntry (Metawidget):
    """A labeled entry box"""
    # TODO: simpler widget name
    def __init__(self, master=None, label="Text", default=''):
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        self.label = Label(self, text=label+':')
        self.entry = Entry(self, width=30, textvariable=self.variable)
        self.label.pack(side=LEFT)
        self.entry.pack(side=LEFT)

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
        self.button = Button(self, text="Browse...", command=self.onClick)
        self.button.pack()
        self.type = type
        self.title = title

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
        self.variable.set(default)
        self.label = Label(self, text=label+':')
        self.entry = Entry(self, width=40, textvariable=self.variable)
        self.button = BrowseButton(self, type, desc)
        # Link our variable with button's
        self.button.variable = self.variable
        # Draw
        self.label.grid(row=0, column=0, sticky=E)
        self.entry.grid(row=0, column=1, sticky=EW)
        self.button.grid(row=0, column=2, sticky=E)

### --------------------------------------------------------------------

class ColorPicker (Metawidget):
    def __init__(self, master=None, label="Color", default=''):
        """Create a widget that opens a color-chooser dialog.
        
            master:  Tkinter widget that will contain the ColorPicker
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
        """
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        self.label = Label(self, text=label+':')
        self.button = Button(self, text="None", command=self.change)
        self.label.pack(side=LEFT)
        self.button.pack(side=LEFT)

    def change(self):
        rgb, color = askcolor(self.get())
        if color:
            self.set(color)
            self.button.config(text=color, foreground=color)

### --------------------------------------------------------------------

class FontPicker (Metawidget):
    # TODO
    pass

### --------------------------------------------------------------------

class Optional (Metawidget):
    def __init__(self, master=None, widget=None, label='Show', *args):
        Metawidget.__init__(self, master, bool)

        self.check = Checkbutton(self, text=label,
                                 command=self.showHide)
        self.widget = widget(self, '', *args)
        self.check.pack(side=LEFT)
        #self.widget.pack(side=LEFT)
        self.shown = False
    
    def showHide(self):
        """Show or hide the sub-widget."""
        if self.shown:
            self.widget.pack_forget()
            self.shown = False
        else:
            self.widget.pack(side=LEFT)
            self.shown = True

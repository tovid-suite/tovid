#! /usr/bin/env python
# control.py

"""Control widget classes.

This module defines a Control class and several derivatives. A Control is a
special-purpose GUI widget for setting a value such as a number or filename.

"""

__all__ = [
    'Control',
    # Control subclasses
    'Choice',
    'Color',
    'Filename',
    'Flag',
    'FlagGroup',
    'Font',
    'Text',
    'List',
    'Number',
    'FileList',
    'TextList']

import Tkinter as tk
from widget import Widget
from support import ListVar
import support
import os

### --------------------------------------------------------------------
class MissingOption (Exception):
    def __init__(self, option):
        self.option = option

### --------------------------------------------------------------------
# Map python types to Tkinter variable types
_vartypes = {
    str: tk.StringVar,
    bool: tk.BooleanVar,
    int: tk.IntVar,
    float: tk.DoubleVar,
    list: ListVar}

### --------------------------------------------------------------------
from tooltip import ToolTip

class Control (Widget):
    """A widget that controls the value of a command-line option.

    A Control is a specialized GUI widget that controls a command-line option
    via a local variable, accessed via get() and set() methods.
    
    Control subclasses may have any number of sub-widgets such as labels,
    buttons or entry boxes; one of the sub-widgets should be linked to the
    controlled variable via an option like:
    
        entry = Entry(self, textvariable=self.variable)
    
    See the Control subclasses below for examples of how self.variable,
    get() and set() are used.
    """
    def __init__(self,
                 vartype=str,
                 label='',
                 option='',
                 default='',
                 help='',
                 **kwargs):
        """Create a Control for an option.

            vartype:  Python type of stored variable
                      (str, bool, int, float, list)
            label:    Label shown in the GUI for the Control
            option:   Command-line option associated with this Control,
                      or '' to create a positional argument
            default:  Default value for the Control
            help:     Help text to show in a tooltip
            **kwargs: Keyword arguments of the form key1=arg1, key2=arg2
        
        Keyword arguments allowed:
        
            pull=Control(...):  Mirror value from another Control
            required=True:      Required option, must be set or run will fail
            filter=function:    Text-filtering function for pulled values
            toggles=True:       May be toggled on and off
        """
        Widget.__init__(self)
        self.vartype = vartype
        self.variable = None
        self.label = label
        self.option = option
        self.default = default or vartype()
        self.help = help
        self.kwargs = kwargs

        # TODO: Find a way to condense/separate keyword handling
        # Controls a mandatory option?
        self.required = False
        if 'required' in kwargs:
            self.required = bool(kwargs['required'])
        # Has an enable/disable toggle button?
        self.toggles = False
        if 'toggles' in self.kwargs:
            self.toggles = bool(self.kwargs['toggles'])
        # allow passing in a first argument to the controls command
        if 'preargs' in self.kwargs:
            self.preargs = self.kwargs['preargs']
        else:
            self.preargs = ""
            
        # List of Controls to copy updated values to
        self.copies = []
        if 'pull' in self.kwargs:
            if not isinstance(self.kwargs['pull'], Control):
                raise TypeError("Can only pull values from a Control.")
            pull_from = self.kwargs['pull']
            pull_from.copy_to(self)
        # Filter expression when pulling from another Control
        self.filter = None
        if 'filter' in self.kwargs:
            if not callable(self.kwargs['filter']):
                raise TypeError("Pull filter must be a function.")
            self.filter = self.kwargs['filter']

    def copy_to(self, control):
        """Update another control whenever this control's value changes.
        """
        if not isinstance(control, Control):
            raise TypeError("Can only copy values to a Control.")
        self.copies.append(control)

    def draw(self, master):
        """Draw the control widgets in the given master.
        
        Override this method in derived classes, and call the base
        class draw() method:
        
            Control.draw(self, master)
        
        """
        Widget.draw(self, master)
        # Create tk.Variable to store Control's value
        if self.vartype in _vartypes:
            self.variable = _vartypes[self.vartype]()
        else:
            self.variable = tk.Variable()
        # Set default value
        if self.default:
            self.variable.set(self.default)
        # Draw tooltip
        if self.help != '':
            self.tooltip = ToolTip(self, text=self.help, delay=1000)
        # Draw enabler checkbox
        if self.toggles:
            self.enabled = tk.BooleanVar()
            self.check = tk.Checkbutton(self, text='',
                                        variable=self.enabled,
                                        command=self.enabler)
            self.check.pack(side='left')

    def post(self):
        """Post-draw initialization.
        """
        if self.toggles:
            self.enabler()

    def enabler(self):
        """Enable or disable the Control when the checkbox is toggled.
        """
        if self.enabled.get():
            self.enable()
        else:
            self.disable()
            self.check.config(state='normal')

    def get(self):
        """Return the value of the Control's variable."""
        # self.variable isn't set until draw() is called
        if not self.variable:
            raise Exception("Must call draw() before get()")
        return self.variable.get()

    def set(self, value):
        """Set the Control's variable to the given value."""
        # self.variable isn't set until draw() is called
        if not self.variable:
            raise Exception("Must call draw() before set()")
        self.variable.set(value)
        # Update controls that are copying this control's value
        for control in self.copies:
            control.variable.set(value)

    def get_args(self):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.
        """
        # TODO: Raise exception if draw() hasn't been called
        args = []
        value = self.get()

        # Return empty if the control is toggled off
        if self.toggles:
            if not self.enabled.get():
                return []
        # Skip if unmodified or empty
        elif value == self.default or value == []:
            # ...unless it's required
            if self.required:
                raise MissingOption(self.option)
            else:
                return []

        # '-option'
        if self.option != '':
            args.append(self.option)
        if self.preargs:
            args.append(self.preargs)
        # List of arguments
        if type(value) == list:
            args.extend(value)
        # Single argument
        else:
            args.append(value)
        return args

    def __repr__(self):
        """Return a Python code representation of this Control."""
        # Get derived class name
        control = str(self.__class__).split('.')[-1]
        return "%s('%s', '%s', '%s', %s, '%s')" % \
               (control, self.option, self.label, self.default, self.help)

    
### --------------------------------------------------------------------
### Control subclasses
### --------------------------------------------------------------------

class Flag (Control):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 label="Flag",
                 option='',
                 default=False,
                 help='',
                 **kwargs):
        """Create a Flag widget with the given label and default value.

            label:    Text label for the flag
            option:   Command-line flag passed
            default:  Default value (True or False)
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, bool, label, option, default, help, **kwargs)
        # Enable an associated control when this Flag is True
        self.enables = None
        if 'enables' in kwargs:
            self.enables = kwargs['enables']
            if not isinstance(self.enables, Widget):
                raise Exception("A Flag can only enable a Widget (Control or Panel)")

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        self.check = tk.Checkbutton(self, text=self.label,
                                    variable=self.variable,
                                    command=self.enabler)
        self.check.pack(side='left')
        # Draw any controls enabled by this one
        if self.enables:
            self.enables.draw(self)
            self.enables.pack(side='left', fill='x', expand=True)
            # Disable if False
            if not self.default:
                self.enables.disable()
        Control.post(self)

    def enabler(self):
        """Enable/disable a Control based on the value of the Flag."""
        if not self.enables:
            return
        if self.get():
            self.enables.enable()
        else:
            self.enables.disable()

    def get_args(self):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.
        """
        args = []
        if self.get() == True:
            if self.option:
                args.append(self.option)
            if self.enables:
                args.extend(self.enables.get_args())
        return args

### --------------------------------------------------------------------

class FlagGroup (Control):
    """A wrapper widget for grouping Flag controls, and allowing
    mutually-exclusive flags.
    """
    def __init__(self,
                 label='',
                 state='normal',
                 *flags,
                 **kwargs):
        """Create a FlagGroup with the given label and state.
        
            label:    Label for the group
            state:    'normal' for independent Flags, 'exclusive' for
                      mutually-exclusive Flags (more like a Choice)
            *flags:   One or more Flag controls to include in the group
        """
        Control.__init__(self, str, '', label, '', '')
        self.flags = flags
        self.state = state
        self.label = label
        self.side = 'top'
        if 'side' in kwargs:
            self.side = kwargs['side']
    
    def draw(self, master):
        """Draw Flag controls in the given master."""
        Control.draw(self, master)
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(fill='x', expand=True)
        for flag in self.flags:
            flag.draw(frame)
            flag.check.bind('<Button-1>', self.select)
            flag.pack(anchor='nw', side=self.side, fill='x', expand=True)
        Control.post(self)

    def select(self, event):
        """Event handler called when a Flag is selected."""
        # For normal flags, nothing to do
        if self.state != 'exclusive':
            return
        # For exclusive flags, clear all but the clicked Flag
        for flag in self.flags:
            if flag.check != event.widget:
                flag.set(False)
            flag.enabler()

    def get_args(self):
        """Return a list of arguments for setting the relevant flag(s)."""
        args = []
        for flag in self.flags:
            if flag.option != 'none':
                args.extend(flag.get_args())
        return args

### --------------------------------------------------------------------
from libtovid.odict import Odict, convert_list
from support import ComboBox

class Choice (Control):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 label="Choices",
                 option='',
                 default='',
                 help='',
                 choices='A|B',
                 style='radio',
                 packside='left',
                 **kwargs):
        """Initialize Choice widget with the given label and list of choices.

            label:    Text label for the choices
            option:   Command-line option to set
            default:  Default choice, or '' to use first choice in list
            help:     Help text to show in a tooltip
            choices:  Available choices, in string form: 'one|two|three'
                      or list form: ['one', 'two', 'three'], or as a
                      list-of-lists: [['a', "Use A"], ['b', "Use B"], ..].
                      A dictionary is also allowed, as long as you don't
                      care about preserving choice order.
            style:    'radio' for radiobuttons, 'dropdown' for a drop-down list
        """
        self.choices = convert_list(choices)
        Control.__init__(self, str, label, option,
                         default or self.choices.values()[0],
                         help, **kwargs)
        if style not in ['radio', 'dropdown']:
            raise ValueError("Choice style must be 'radio' or 'dropdown'")
        self.style = style
        self.packside = packside

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        if self.style == 'radio':
            frame = tk.LabelFrame(self, text=self.label)
            frame.pack(anchor='nw', fill='x')
            self.rb = {}
            for choice, label in self.choices.items():
                self.rb[choice] = tk.Radiobutton(frame,
                    text=label, value=choice, variable=self.variable)
                self.rb[choice].pack(anchor='nw', side=self.packside)
        else: # dropdown/combobox
            tk.Label(self, text=self.label).pack(side='left')
            self.combo = ComboBox(self, self.choices.keys(),
                                  variable=self.variable)
            self.combo.pack(side='left')
        Control.post(self)

### --------------------------------------------------------------------

class Number (Control):
    """A widget for choosing or entering a number"""
    def __init__(self,
                 label="Number",
                 option='',
                 default=0,
                 help='',
                 min=1,
                 max=10,
                 style='spin',
                 units='',
                 **kwargs):
        """Create a number-setting widget.
        
            label:    Text label describing the meaning of the number
            option:   Command-line option to set
            default:  Default value, or 0 to use minimum.
            help:     Help text to show in a tooltip
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' for a spinbox, or 'scale' for a slider
            units:    Units of measurement (ex. "kbits/sec"), used as a label
    
        The default/min/max may be integers or floats.
        """
        Control.__init__(self, type(default), label, option, default or min,
                         help, **kwargs)
        self.min = min
        self.max = max
        self.style = style
        self.units = units

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, name='label', text=self.label).pack(side='left')
        if self.style == 'spin':
            self.number = tk.Spinbox(self, from_=self.min, to=self.max,
                                     width=4, textvariable=self.variable)
            self.number.pack(side='left')
            tk.Label(self, name='units', text=self.units).pack(side='left')

        else: # 'scale'
            # Use integer or float resolution
            if type(self.default) == int:
                res = 1
            else:
                res = 0.001
            tk.Label(self, name='units', text=self.units).pack(side='left')
            self.number = tk.Scale(self, from_=self.min, to=self.max,
                                   resolution=res,
                                   tickinterval=(self.max - self.min),
                                   variable=self.variable, orient='horizontal')
            self.number.pack(side='left', fill='x', expand=True)
        Control.post(self)

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets."""
        # Overridden to make Scale widget look disabled
        Control.enable(self, enabled)
        if self.style == 'scale':
            if enabled:
                self.number['fg'] = 'black'
                self.number['troughcolor'] = 'white'
            else:
                self.number['fg'] = '#A3A3A3'
                self.number['troughcolor'] = '#D9D9D9'
                

### --------------------------------------------------------------------

class Text (Control):
    """A widget for entering a line of text"""
    def __init__(self,
                 label="Text",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        """
            label:    Label for the text
            option:   Command-line option to set
            default:  Default value of text widget
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label, justify='left').pack(side='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side='left', fill='x', expand=True)
        Control.post(self)

### --------------------------------------------------------------------
import shlex

class List (Text):
    """A widget for entering a space-separated list of text items"""
    def __init__(self,
                 label="List",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        Text.__init__(self, label, option, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Text.draw(self, master)
        Text.post(self)

    def get(self):
        """Split text into a list at whitespace boundaries."""
        text = Text.get(self)
        return shlex.split(text)

    def set(self, listvalue):
        """Set a value to a list, joined with spaces."""
        text = ' '.join(listvalue)
        Text.set(self, text)
    

### --------------------------------------------------------------------
from tkFileDialog import asksaveasfilename, askopenfilename

class Filename (Control):
    """A widget for entering or browsing for a filename"""
    def __init__(self,
                 label='Filename',
                 option='',
                 default='',
                 help='',
                 action='load',
                 desc='Select a file to load',
                 **kwargs):
        """Create a Filename with label, text entry, and browse button.
        
            label:   Text of label next to file entry box
            option:  Command-line option to set
            default: Default filename
            help:    Help text to show in a tooltip
            action:  Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)
        self.action = action
        self.desc = desc

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        # Create and pack widgets
        tk.Label(self, text=self.label, justify='left').pack(side='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.button = tk.Button(self, text="Browse...", command=self.browse)
        self.entry.pack(side='left', fill='x', expand=True)
        self.button.pack(side='left')
        Control.post(self)

    def browse(self, event=None):
        """Event handler when browse button is pressed"""
        if self.action == 'save':
            filename = asksaveasfilename(parent=self, title=self.desc)
        else: # 'load'
            filename = askopenfilename(parent=self, title=self.desc)
        # Got a filename? Display it
        if filename:
            self.set(filename)

### --------------------------------------------------------------------
import tkColorChooser

class Color (Control):
    """A widget for choosing a color"""
    def __init__(self,
                 label="Color",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        """Create a widget that opens a color-chooser dialog.
        
            label:   Text label describing the color to be selected
            option:  Command-line option to set
            default: Default color (named color or hexadecimal RGB)
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, text="None", command=self.change)
        self.button.pack(side='left')
        Control.post(self)

    def change(self):
        """Choose a color, and set the button's label and color to match."""
        rgb, color = tkColorChooser.askcolor(self.get())
        if color:
            self.set(color)
            self.button.config(text=color, foreground=color)
    
### --------------------------------------------------------------------

class Font (Control):
    """A font selector widget"""
    def __init__(self,
                 label='Font',
                 option='',
                 default='Helvetica',
                 help='',
                 **kwargs):
        """Create a widget that opens a font chooser dialog.
        
            label:   Text label for the font
            option:  Command-line option to set
            default: Default font
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.choose)
        self.button.pack(side='left', padx=8)
        Control.post(self)

    def choose(self):
        """Open a font chooser to select a font."""
        chooser = support.FontChooser(self)
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------
from support import DragList

class TextList (Control):
    """A widget for listing and editing several text strings"""
    def __init__(self,
                 label="Text list",
                 option='',
                 default=None,
                 help='',
                 **kwargs):
        Control.__init__(self, list, label, option, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(fill='x', expand=True)
        self.selected = tk.StringVar()
        self.listbox = DragList(frame, choices=self.variable,
                                chosen=self.selected)
        self.listbox.pack(fill='x', expand=True)
        # TODO: Event handling to allow editing items
        self.editbox = tk.Entry(frame, width=30, textvariable=self.selected)
        self.editbox.bind('<Return>', self.setTitle)
        self.editbox.pack(fill='x', expand=True)
        Control.post(self)

    def setTitle(self, event):
        """Event handler when Enter is pressed after editing a title."""
        index = self.listbox.curindex
        self.variable[index] = self.selected.get()
        # TODO: Select next item in list and focus the editbox

### --------------------------------------------------------------------
from tkFileDialog import askopenfilenames

class FileList (Control):
    """A widget for listing several filenames"""
    def __init__(self,
                 label="File list",
                 option='',
                 default=None,
                 help='',
                 **kwargs):
        """Create a widget with a list of files, and add/remove buttons.
        """
        Control.__init__(self, list, label, option, default, help, **kwargs)
        self.filetypes=[('All Files', '*.*')]
        if 'filetypes' in kwargs:
            self.filetypes = kwargs['filetypes']

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(fill='x', expand=True)
        # List of files
        self.listbox = DragList(frame, choices=self.variable,
                                command=self.select)
        self.listbox.pack(fill='x', expand=True)
        # Add/remove buttons
        group = tk.Frame(frame)
        self.add = tk.Button(group, text="Add...", command=self.addFiles)
        self.remove = tk.Button(group, text="Remove", command=self.removeFiles)
        self.add.pack(side='left', fill='x', expand=True)
        self.remove.pack(side='left', fill='x', expand=True)
        group.pack(fill='x')
        Control.post(self)

    def select(self, event=None):
        """Event handler when a filename in the list is selected.
        """
        pass

    def addFiles(self):
        """Event handler to add files to the list"""
        files = askopenfilenames(parent=self, title='Add files', filetypes=self.filetypes)
        self.listbox.add(*files)
        for dest in self.copies:
            self.listbox.linked = dest.listbox
            dest.listbox.linked = self.listbox
            if dest.filter:
                titles = [dest.filter(file) for file in files]
                dest.listbox.add(*titles)
            else:
                dest.listbox.add(*files)

    def removeFiles(self):
        """Event handler to remove selected files from the list"""
        # TODO: Support multiple selection
        selected = self.listbox.curindex
        self.listbox.delete(selected)
        for control in self.copies:
            control.listbox.delete(selected)

### --------------------------------------------------------------------

# Exported control classes, indexed by name
CONTROLS = {
    'Choice': Choice,
    'Color': Color,
    'Filename': Filename,
    'Flag': Flag,
    'FlagGroup': FlagGroup,
    'Font': Font,
    'Text': Text,
    'List': List,
    'Number': Number,
    'FileList': FileList,
    'TextList': TextList,
}

### --------------------------------------------------------------------

# Demo
if __name__ == '__main__':
    root = tk.Tk()
    for name, control in CONTROLS.items():
        frame = tk.LabelFrame(root, text=name, padx=10, pady=10,
                          font=('Helvetica', 10, 'bold'))
        frame.pack(fill='both', expand=True)
        widget = control()
        widget.draw(frame)
        widget.pack(fill='both')
    root.mainloop()
    

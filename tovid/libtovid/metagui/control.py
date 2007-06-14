#! /usr/bin/env python
# control.py

"""Control widget classes.

This module defines a Control class and several derivatives. A Control is a
special-purpose GUI widget for setting a value such as a number or filename.

"""

"""
Pull behavior

When a widget pulls from another, it's expected that:

- The pulling widget synchronizes its valus with another control; when that
  control changes, so does pulling control
- The exact value is pulled, or a modified copy is pulled (to do regexp
  search/replace at minimum)

Lists are a special case, because they have more interactivity than other
widgets. When items in one list are rearranged or removed, the pulling
list should rearrange/remove corresponding items.

Q. Should correspondence in ordering be assumed?

Q. Would pulling ever be useful for non-lists?

Q. Would any other controls benefit by event-binding behaviors?

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
from support import ListVar
import support

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

class Control (tk.Frame):
    """A widget that controls the value of an option.

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
                 option='',
                 label='',
                 default='',
                 help='',
                 **kwargs):
        """Create a Control for an option.

            vartype:  Type of stored variable (str, bool, int, float, list)
            option:   Command-line option associated with this Control, or
                      '' to create a positional argument
            label:    Label shown in the GUI for the Control
            default:  Default value for the Control
            help:     Help text to show in a tooltip
            **kwargs: Keyword arguments of the form key1=arg1, key2=arg2
        """
        self.vartype = vartype
        self.variable = None
        self.option = option
        self.label = label
        self.default = default or vartype()
        self.help = help
        self.kwargs = kwargs
        self.active = False
        # Controls a mandatory option?
        self.required = False
        if 'required' in kwargs:
            self.required = kwargs['required']
        # List of Controls to copy updated values to
        self.copies = []
        if 'pull' in self.kwargs:
            pull_from = self.kwargs['pull']
            if not isinstance(pull_from, Control):
                raise TypeError("Can only pull values from a Control.")
            pull_from.copy_to(self)

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
        tk.Frame.__init__(self, master)
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
        self.active = True

    def get(self):
        """Return the value of the Control's variable."""
        # self.variable isn't set until draw() is called
        if not self.variable:
            raise "Must call draw() before get()"
        return self.variable.get()

    def set(self, value):
        """Set the Control's variable to the given value."""
        # self.variable isn't set until draw() is called
        if not self.variable:
            raise "Must call draw() before set()"
        self.variable.set(value)
        # Update controls that are copying this control's value
        for control in self.copies:
            control.variable.set(value)

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets."""
        if enabled:
            newstate = 'normal'
        else:
            newstate = 'disabled'
        for widget in self.children.values():
            # Some widgets don't support state changes
            if 'state' in widget.config():
                widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)

    def get_args(self):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.
        """
        # TODO: Raise exception if draw() hasn't been called
        args = []
        value = self.get()

        # Skip if unmodified or empty
        if value == self.default or value == []:
            if self.required:
                raise MissingOption(self.option)
            else:
                return []

        # -option <argument>
        args.append(self.option)
        # List of arguments
        if self.vartype == list:
            args.extend(value)
        # Single argument
        else:
            args.append(value)
        return args

    def destroy(self):
        tk.Frame.destroy(self)
        self.active = False

    def __repr__(self):
        """Return a Python code representation of this Control."""
        # Get derived class name
        control = str(self.__class__).split('.')[-1]
        return "%s('%s', '%s')" % (control, self.option, self.label)

### --------------------------------------------------------------------
### Control subclasses
### --------------------------------------------------------------------

class Flag (Control):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 option='',
                 label="Flag",
                 default=False,
                 help='',
                 **kwargs):
        """Create a Flag widget with the given label and default value.

            label:    Text label for the flag
            default:  Default value (True or False)
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, bool, option, label, default, help, **kwargs)
        # Enable an associated control when this Flag is True
        self.enables = None
        if 'enables' in kwargs:
            self.enables = kwargs['enables']
            if not isinstance(self.enables, Control):
                raise "A Flag can only enable another Control"

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        self.check = tk.Checkbutton(self, text=self.label,
                                    variable=self.variable,
                                    command=self.enabler)
        self.check.pack(side='left')
        # Draw any controls enabled by this one
        if self.enables:
            print "Drawing enabled Control: %s" % self.enables.__class__
            self.enables.draw(self)
            self.enables.pack(side='left')
            # Disable if False
            if not self.default:
                self.enables.disable()

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
            state:    'normal' for regular Flags, 'exclusive' for
                      mutually-exclusive Flags
            *flags:   All additional arguments are Flag controls
        """
        Control.__init__(self, str, '', label, '', '')
        self.flags = flags
        self.state = state
    
    def draw(self, master):
        """Draw Flag controls in the given master."""
        Control.draw(self, master)
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(fill='x', expand=True)
        for flag in self.flags:
            flag.draw(frame)
            flag.check.bind('<Button-1>', self.select)
            flag.pack(anchor='nw', side='top')

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
import odict
from support import ComboBox

class Choice (Control):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 option='',
                 label="Choices",
                 default=None,
                 help='',
                 choices='A|B',
                 style='radio',
                 packside='left',
                 **kwargs):
        """Initialize Choice widget with the given label and list of choices.

            label:    Text label for the choices
            default:  Default choice, or None to use first choice in list
            help:     Help text to show in a tooltip
            choices:  Available choices, in string form: 'one|two|three'
                      or list form: ['one', 'two', 'three'], or as a
                      list-of-lists: [['a', "Use A"], ['b', "Use B"], ..].
                      A dictionary is also allowed, as long as you don't
                      care about preserving choice order.
            style:    'radio' for radiobuttons, 'dropdown' for a drop-down list
        """
        self.choices = odict.from_list(choices)
        Control.__init__(self, str, option, label,
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


### --------------------------------------------------------------------

class Number (Control):
    """A widget for choosing or entering a number"""
    def __init__(self,
                 option='',
                 label="Number",
                 default=None,
                 help='',
                 min=1,
                 max=10,
                 style='spin',
                 units='',
                 **kwargs):
        """Create a number-setting widget.
        
            label:    Text label describing the meaning of the number
            default:  Default value, or None to use minimum
            help:     Help text to show in a tooltip
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' for a spinbox, or 'scale' for a slider
            units:    Units of measurement (ex. "kbits/sec"), used as a label
        """
        Control.__init__(self, int, option, label, default or min,
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
            tk.Label(self, name='units', text=self.units).pack(side='left')
            self.number = tk.Scale(self, from_=self.min, to=self.max,
                                   tickinterval=(self.max - self.min),
                                   variable=self.variable, orient='horizontal')
            self.number.pack(side='left', fill='x', expand=True)


    def enable(self, enabled=True):
        """Enable or disable all sub-widgets. Overridden to make Scale widget
        look disabled."""
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
                 option='',
                 label="Text",
                 default='',
                 help='',
                 **kwargs):
        """
            label:    Label for the text
            default:  Default value of text widget
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label, justify='left').pack(side='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side='left', fill='x', expand=True)

### --------------------------------------------------------------------
import shlex

class List (Text):
    """A widget for entering a space-separated list of text items"""
    def __init__(self,
                 option='',
                 label="List",
                 default='',
                 help='',
                 **kwargs):
        Text.__init__(self, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Text.draw(self, master)

    def get(self):
        """Split text into a list at whitespace boundaries."""
        text = Text.get(self)
        return shlex.split(text)

    def set(self, listvalue):
        """Set a value to a list, joined with spaces."""
        text = ' '.join(listvalue)
        Text.set(self, text)
    
    def get_args(self):
        """Return a list of arguments."""
        return self.get()

### --------------------------------------------------------------------
from tkFileDialog import asksaveasfilename, askopenfilename

class Filename (Control):
    """A widget for entering or browsing for a filename"""
    def __init__(self,
                 option='',
                 label='Filename',
                 default='',
                 help='',
                 action='load',
                 desc='Select a file to load',
                 **kwargs):
        """Create a Filename with label, text entry, and browse button.
        
            label:   Text of label next to file entry box
            default: Default filename
            help:    Help text to show in a tooltip
            action:  Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
        """
        Control.__init__(self, str, option, label, default, help, **kwargs)
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
                 option='',
                 label="Color",
                 default='',
                 help='',
                 **kwargs):
        """Create a widget that opens a color-chooser dialog.
        
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, text="None", command=self.change)
        self.button.pack(side='left')
        
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
                 option='',
                 label='Font',
                 default='Helvetica',
                 help='',
                 **kwargs):
        """Create a widget that opens a font chooser dialog.
        
            label:   Text label for the font
            default: Default font
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.choose)
        self.button.pack(side='left', padx=8)

    def choose(self):
        """Open a font chooser to select a font."""
        chooser = support.FontChooser()
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------
from support import DragList

class TextList (Control):
    """A widget for listing and editing several text strings"""
    def __init__(self,
                 option='',
                 label="Text list",
                 default=None,
                 help='',
                 **kwargs):
        Control.__init__(self, list, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        self.selected = tk.StringVar()
        self.listbox = DragList(self, choices=self.variable,
                                chosen=self.selected)
        self.listbox.pack(fill='x', expand=True)
        # TODO: Event handling to allow editing items
        self.editbox = tk.Entry(self, width=30, textvariable=self.selected)
        self.editbox.bind('<Return>', self.setTitle)
        self.editbox.pack(fill='x', expand=True)

    def setTitle(self, event):
        """Event handler when Enter is pressed after editing a title."""
        index = self.listbox.curindex
        self.variable[index] = self.selected.get()
        # TODO: Select next item in list and focus the editbox

### --------------------------------------------------------------------

class FileList (Control):
    """A widget for listing several filenames"""
    def __init__(self,
                 option='',
                 label="File list",
                 default=None,
                 help='',
                 **kwargs):
        Control.__init__(self, list, option, label, default, help, **kwargs)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        # List of files
        self.listbox = DragList(self, choices=self.variable,
                                command=self.select)
        self.listbox.pack(fill='x', expand=True)
        # Add/remove buttons
        group = tk.Frame(self)
        self.add = tk.Button(group, text="Add...", command=self.addFiles)
        self.remove = tk.Button(group, text="Remove", command=self.removeFiles)
        self.add.pack(side='left', fill='x', expand=True)
        self.remove.pack(side='left', fill='x', expand=True)
        group.pack(fill='x')
        # Dirty hack to get linked files/titles to work

    def select(self, event=None):
        """Event handler when a filename in the list is selected.
        """
        pass

    def addFiles(self):
        """Event handler to add files to the list"""
        files = tkFileDialog.askopenfilenames(parent=self, title='Add files')
        self.listbox.add(*files)
        for control in self.copies:
            control.listbox.add(*files)

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
    'TextList': TextList}

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
    

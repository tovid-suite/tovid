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
    'FlagChoice',
    'Font',
    'Text',
    'List',
    'Number',
    'FileList',
    'TextList',
    # Deprecated
    'PlainLabel']

import shlex
import Tkinter as tk
import tkColorChooser
import tkFileDialog
from libtovid.gui.tooltip import ToolTip
from libtovid import log


# Map python types to Tkinter variable types
vartypes = {
    str: tk.StringVar,
    bool: tk.BooleanVar,
    int: tk.IntVar,
    float: tk.DoubleVar,
    list: tk.Variable}

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
                 help=''):
        """Create a Control for an option.

            vartype:  Type of stored variable (str, bool, int, float, list)
            option:   Command-line option associated with this Control
            label:    Label for the Control
            default:  Default value for the Control
            help:     Help text to show in a tooltip
        """
        self.vartype = vartype
        self.variable = None
        self.option = option
        self.label = label
        self.help = help
        # Store value in normal Python variable until draw() is called
        self.value = self.vartype(default)

    def draw(self, master):
        """Draw the control widgets in the given master.
        
        Override this method in derived classes, and call the base
        class draw() method:
        
            Control.draw(self, master)
        
        """
        tk.Frame.__init__(self, master)
        # Draw tooltip
        if self.help != '':
            self.tooltip = ToolTip(self, text=self.help, delay=1000)
        # Create a suitable tk.Variable
        if self.vartype in vartypes:
            self.variable = vartypes[self.vartype]()
        else:
            self.variable = tk.Variable()
        # Put the stored value in the Variable
        self.set(self.value)

    def get(self):
        """Return the value of the Control's variable."""
        # self.variable isn't set until draw() is called
        if self.variable:
            return self.variable.get()
        else:
            return self.value

    def set(self, value):
        """Set the Control's variable to the given value."""
        # self.variable isn't set until draw() is called
        if self.variable:
            self.variable.set(value)
        else:
            self.value = value

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

    def get_options(self):
        """Return a list of arguments for passing this command-line option.
        draw must be called before this function.
        """
        # TODO: Raise exception if draw() hasn't been called
        args = []
        value = self.get()
        # Boolean values control a flag
        if self.vartype == bool and value:
            args.append("-%s" % self.option)
        # Others use '-option value'
        elif value:
            args.append("-%s" % self.option)
            # List of arguments
            if self.vartype == list:
                args.extend(value)
            # Single argument
            else:
                args.append(value)
        return args



### --------------------------------------------------------------------
### Control subclasses
### --------------------------------------------------------------------

class Flag (Control):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 option='',
                 label="Flag",
                 default=False,
                 help=''):
        """Create a Flag widget with the given label and default value.

            label:    Text label for the flag
            default:  Default value (True or False)
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, bool, option, label, default, help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        self.check = tk.Checkbutton(self, text=self.label, variable=self.variable)
        self.check.pack(side='left')

### --------------------------------------------------------------------

class FlagGroup (Control):
    """A wrapper widget for grouping Flag controls, and allowing
    mutually-exclusive flags.
    """
    def __init__(self,
                 label='',
                 default='',
                 state='normal',
                 *flags):
        """Create a FlagGroup with the given label and state.
        
            label:    Label for the group
            default:  Default selection
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
        # For exclusive flags, clear all but the selected Flag
        for flag in self.flags:
            # Turn on the Flag that was clicked
            if flag == event.widget:
                flag.set(True)
            else:
                flag.set(False)

    def get_options(self):
        """Return a list of arguments for setting the relevant flag(s)."""
        args = []
        for flag in self.flags:
            if flag.option != 'none':
                args.extend(flag.get_options())
        return args

### --------------------------------------------------------------------

class Choice (Control):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 option='',
                 label="Choices",
                 default=None,
                 help='',
                 choices='A|B',
                 packside='left'):
        """Initialize Choice widget with the given label and list of choices.

            label:    Text label for the choices
            default:  Default choice, or None to use first choice in list
            help:     Help text to show in a tooltip
            choices:  Available choices, in string form: 'one|two|three'
                      or list form: ['one', 'two', 'three'], or as a
                      list-of-lists: [['a', "Use A"], ['b', "Use B"], ..].
                      A dictionary is also allowed, as long as you don't
                      care about preserving choice order.
        """
        Control.__init__(self, str, option, label, default, help)
        if type(choices) not in [str, list, dict]:
            raise TypeError("choices must be a string, list, or dictionary.")
        # Convert choices to a list if necessary
        if type(choices) == str:
            choices = choices.split('|')
        if type(choices) == list:
            first = choices[0]
            # list of strings
            if type(first) == str:
                choices = [[c, c] for c in choices]
            # list of 2-element string lists? If not, exception
            elif type(first) != list or len(first) != 2:
                raise TypeError("choices lists must either be"\
                    "['a', 'b', 'c'] or [['a', 'A'], ['b', 'B']] style.")
        self.choices = []
        self.labels = []
        # Now, save it all as two separate lists
        for choice, label in choices:
            self.choices.append(choice)
            self.labels.append(label)
        self.packside = packside
        if not default:
            self.set(self.choices[0])

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(anchor='nw', fill='x')
        self.rb = {}
        for choice, label in zip(self.choices, self.labels):
            self.rb[choice] = tk.Radiobutton(frame, text=label, value=choice,
                                             variable=self.variable)
            self.rb[choice].pack(anchor='nw', side=self.packside)

### --------------------------------------------------------------------

class FlagChoice (Choice):
    """A widget for choosing among several mutually-exclusive flag options."""
    def __init__(self,
                 option='',
                 label="Flag choices",
                 default='a',
                 help='',
                 choices=[['a', "Option A"], ['b', "Option B"]],
                 packside='left'):
        """Create a FlagChoice that sets one of several flag options.
        
            option:    Ignored
            label:     Overall choice label
            default:   Default (initial) choice
            help:      Help text to show in a tooltip
            choices:   List of flag options (in the same formats accepted
                       by Choice). Include a choice called 'none' to allow
                       passing no flags.
        """
        Choice.__init__(self, '', label, default, help, choices, packside)
    
    def get_options(self):
        """Return argument for setting the selected flag."""
        arg = self.variable.get()
        if arg == 'none':
            return []
        else:
            return ["-%s" % arg]
    

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
                 style='spin'):
        """Create a number-setting widget.
        
            label:    Text label describing the meaning of the number
            default:  Default value, or None to use minimum
            help:     Help text to show in a tooltip
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' for a spinbox, or 'scale' for a slider
        """
        # Use min if default wasn't provided
        if default is None:
            default = min
        Control.__init__(self, int, option, label, default, help)
        self.min = min
        self.max = max
        self.style = style

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, name='label', text=self.label).pack(side='left')
        if self.style == 'spin':
            self.number = tk.Spinbox(self, from_=self.min, to=self.max,
                                     width=4, textvariable=self.variable)
            self.number.pack(side='left')
        else: # 'scale'
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
                 help=''):
        """
            label:    Label for the text
            default:  Default value of text widget
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label, justify='left').pack(side='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side='left', fill='x', expand=True)

### --------------------------------------------------------------------

class List (Text):
    """A widget for entering a space-separated list of text items"""
    def __init__(self,
                 option='',
                 label="List",
                 default='',
                 help=''):
        Text.__init__(self, option, label, default, help)

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

### --------------------------------------------------------------------

class Filename (Control):
    """A widget for entering or browsing for a filename
    """
    def __init__(self,
                 option='',
                 label='Filename',
                 default='',
                 help='',
                 type='load',
                 desc='Select a file to load'):
        """Create a Filename with label, text entry, and browse button.
        
            label:   Text of label next to file entry box
            default: Default filename
            help:    Help text to show in a tooltip
            type:    Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
        """
        Control.__init__(self, str, option, label, default, help)
        self.type = type
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
        if self.type == 'save':
            filename = tkFileDialog.asksaveasfilename(parent=self,
                                                      title=self.desc)
        else: # 'load'
            filename = tkFileDialog.askopenfilename(parent=self,
                                                    title=self.desc)
        # Got a filename? Save it
        if filename:
            self.set(filename)

### --------------------------------------------------------------------

class Color (Control):
    """A widget for choosing a color"""
    def __init__(self,
                 option='',
                 label="Color",
                 default='',
                 help=''):
        """Create a widget that opens a color-chooser dialog.
        
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help)

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
                 help=''):
        """Create a widget that opens a font chooser dialog.
        
            label:   Text label for the font
            default: Default font
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, str, option, label, default, help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.choose)
        self.button.pack(side='left', padx=8)

    def choose(self):
        """Open a font chooser to select a font."""
        chooser = FontChooser()
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------

# Deprecated
class PlainLabel (Control):
    """A plain label or spacer widget"""
    def __init__(self,
                 option='',
                 label="Text",
                 default=''):
        Control.__init__(self, str, option, label)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')

### --------------------------------------------------------------------

class ScrollList (Control):
    """A widget for choosing from a list of values
    """
    def __init__(self,
                 option='',
                 label="List",
                 default=None,
                 help=''):
        """Create a ScrollList widget.
        
            label:    Text label for the list
            default:  List of initial values, or None for empty
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, list, option, label, default or [], help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        self.selected = tk.StringVar() # Currently selected list item
        # Listbox label
        tk.Label(self, text=self.label).pack(anchor='w')
        # Group listbox and scrollbar together
        group = tk.Frame(self)
        self.scrollbar = tk.Scrollbar(group, orient='vertical',
                                      command=self.scroll)
        self.listbox = tk.Listbox(group, width=30, listvariable=self.variable,
                                  yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='left', fill='y')
        group.pack(fill='both')
        self.listbox.bind('<Button-1>', self.select)

    def add(self, *values):
        """Add the given values to the list."""
        for value in values:
            self.listbox.insert('end', value)

    def scroll(self, *args):
        """Event handler when the list is scrolled
        """
        apply(self.listbox.yview, args)

    def select(self, event):
        """Event handler when an item in the list is selected
        """
        self.curindex = self.listbox.nearest(event.y)
        self.selected.set(self.listbox.get(self.curindex))

    def get(self):
        """Return a list of all entries in the list."""
        # Overridden because Listbox stores variable as a tuple
        entries = self.variable.get()
        return list(entries)
    
    def set(self, values):
        """Set the list values to those given."""
        self.variable.set(tuple(values))

### --------------------------------------------------------------------

class DragList (ScrollList):
    """A scrollable listbox with drag-and-drop support"""
    def __init__(self,
                 option='',
                 label="List",
                 default=None,
                 help=''):
        ScrollList.__init__(self, option, label, default, help)
        self.curindex = 0

    def draw(self, master):
        """Draw control widgets in the given master."""
        ScrollList.draw(self, master)
        self.listbox.bind('<Button-1>', self.select)
        self.listbox.bind('<B1-Motion>', self.drag)
        self.listbox.bind('<ButtonRelease-1>', self.drop)

    def select(self, event):
        """Event handler when an item in the list is selected.
        """
        # Set currently selected item and change the cursor to a double-arrow
        ScrollList.select(self, event)
        self.config(cursor="double_arrow")
    
    def drag(self, event):
        """Event handler when an item in the list is dragged
        """
        # If item is dragged to a new location, delete/insert
        loc = self.listbox.nearest(event.y)
        if loc != self.curindex:
            item = self.listbox.get(self.curindex)
            self.listbox.delete(self.curindex)
            self.listbox.insert(loc, item)
            self.curindex = loc

    def drop(self, event):
        """Event handler when an item in the list is "dropped"
        """
        # Change the mouse cursor back to the default arrow.
        self.config(cursor="")

### --------------------------------------------------------------------

class FileList (DragList):
    """A widget for listing several filenames"""
    def __init__(self,
                 option='',
                 label="File list",
                 default=None,
                 help=''):
        DragList.__init__(self, option, label, default, help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        DragList.draw(self, master)
        group = tk.Frame(self)
        self.add = tk.Button(group, text="Add...", command=self.addFiles)
        self.remove = tk.Button(group, text="Remove", command=self.removeFiles)
        self.add.pack(side='left', fill='x', expand=True)
        self.remove.pack(side='left', fill='x', expand=True)
        group.pack(fill='x')

    def addFiles(self):
        """Event handler to add files to the list"""
        files = tkFileDialog.askopenfilenames(parent=self, title='Add files')
        for file in files:
            log.debug("Adding '%s' to the file list" % file)
            self.listbox.insert('end', file)

    def removeFiles(self):
        """Event handler to remove files from the list"""
        selection = self.listbox.curselection()
        # Using reverse order prevents reflow from messing up indexing
        for line in reversed(selection):
            log.debug("Removing '%s' from the file list" %\
                      self.listbox.get(line))
            self.listbox.delete(line)

### --------------------------------------------------------------------

class TextList (DragList):
    """A widget for listing and editing several text strings"""
    def __init__(self,
                 option='',
                 label="Text list",
                 default=None,
                 help=''):
        DragList.__init__(self, option, label, default, help)

    def draw(self, master):
        """Draw control widgets in the given master."""
        DragList.draw(self, master)
        # TODO: Event handling to allow editing items
        self.editbox = tk.Entry(self, width=30, textvariable=self.selected)
        self.editbox.bind('<Return>', self.setTitle)
        self.editbox.pack(fill='x', expand=True)

    def setTitle(self, event):
        """Event handler when Enter is pressed after editing a title."""
        newtitle = self.selected.get()
        log.debug("Setting title to '%s'" % newtitle)
        self.listbox.delete(self.curindex)
        self.listbox.insert(self.curindex, newtitle)

### --------------------------------------------------------------------

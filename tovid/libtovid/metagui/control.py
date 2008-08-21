#! /usr/bin/env python
# control.py

"""Control widget classes.

This module defines a Control class and several derivatives. A Control is a
special-purpose GUI widget for setting a value such as a number or filename.

Control subclasses:
    
    Choice
        Multiple-choice selection, with radiobutton or dropdown style
    Color
        RGB color selection, with color picker
    Filename
        Filename selection, with filesystem browse button
    Flag
        Checkbox for enabling/disabling an option
    Font
        Font name chooser
    Number
        Numeric entry, with min/max and optional slide bar
    Text
        Plain text string
    SpacedText
        Plain text, interpreted as a space-separated list of strings
    List
        List of values, editable in another Control

"""

__all__ = [
    'Control',
    # Subclasses
    'Choice',
    'Color',
    'Filename',
    'Flag',
    'Font',
    'List',
    'Number',
    'SpacedText',
    'Text',
]

import os
import Tkinter as tk
from widget import Widget
from variable import ListVar, DictVar
from support import DragList, ScrollList, FontChooser
from support import ensure_type

### --------------------------------------------------------------------
class MissingOption (Exception):
    def __init__(self, option):
        self.option = option

class NotDrawn (Exception):
    pass

### --------------------------------------------------------------------
# Map python types to Tkinter variable types
_tk_vartypes = {
    str: tk.StringVar,
    bool: tk.BooleanVar,
    int: tk.IntVar,
    float: tk.DoubleVar,
    list: ListVar,
    dict: DictVar,
}

### --------------------------------------------------------------------
from tooltip import ToolTip

class Control (Widget):
    """A specialized GUI widget that controls a command-line option.

    Control subclasses may have any number of sub-widgets such as labels,
    buttons or entry boxes; one of the sub-widgets should be linked to
    self.variable like so:
    
        textbox = tk.Entry(self, textvariable=self.variable)
    
    See the Control subclasses below for examples of how self.variable,
    get() and set() are used.
    """

    # Dict of all instantiated Controls, indexed by option string
    all = {}

    def by_option(option):
        """Return the Control instance for a given option string,
        or None if no Control has that option string.
        """
        if option != '' and option in Control.all:
            return Control.all[option]
        else:
            return None
    by_option = staticmethod(by_option)


    def __init__(self,
                 vartype=str,
                 label='',
                 option='',
                 default='',
                 help='',
                 required=False,
                 toggles=False,
                 **kwargs):
        """Create a Control for an option.

            vartype:  Python type of stored variable
                      (str, bool, int, float, list, dict)
            label:    Label shown in the GUI for the Control
            option:   Command-line option associated with this Control,
                      or '' to create a positional argument
            default:  Default value for the Control
            help:     Help text to show in a tooltip
            required: Indicates a required (non-optional) option
            toggles:  Control widget may be toggled on/off
            **kwargs: Keyword arguments of the form key1=arg1, key2=arg2
        
        """
        Widget.__init__(self, label)
        self.vartype = vartype
        self.variable = None
        self.label = label
        self.option = option
        self.default = default or vartype()
        self.help = help
        self.required = required
        self.toggles = toggles
        self.kwargs = kwargs

        # Add self to all
        if self.option != '':
            Control.all[self.option] = self


    def draw(self, master):
        """Draw the control widgets in the given master.
        
        Override this method in derived classes, and call the base
        class draw() method:
        
            Control.draw(self, master)
        
        """
        Widget.draw(self, master)
        # Create tk.Variable to store Control's value
        if self.vartype in _tk_vartypes:
            self.variable = _tk_vartypes[self.vartype](self)
        else:
            self.variable = tk.Variable(self)
        # Set default value
        if self.default:
            self.variable.set(self.default)
        # Draw tooltip
        if self.help != '':
            self.tooltip = ToolTip(self, text=self.help, delay=1000)
        # Draw enabler checkbox
        if self.toggles:
            self.enabled = tk.BooleanVar(self)
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
        """Event handler: Enable/disable the Control when self.check is toggled.
        """
        if self.enabled.get():
            self.enable()
        else:
            self.disable()
            self.check.config(state='normal')


    def get(self):
        """Return the value of the Control's variable.
        """
        # self.variable isn't defined until draw() is called
        if not self.variable:
            raise NotDrawn("Must call draw() before get()")
        return self.variable.get()


    def set(self, value):
        """Set the Control's variable to the given value.
        """
        # self.variable isn't defined until draw() is called
        if not self.variable:
            raise NotDrawn("Must call draw() before set()")
        self.variable.set(value)


    def set_variable(self, variable):
        """Set the Control to reference the given Tkinter variable.
        """
        need_type = _tk_vartypes[self.vartype]
        if not isinstance(variable, need_type):
            raise TypeError("Variable must be of type '%s'" % need_type)
        self.variable = variable


    def reset(self):
        """Reset the Control's value to the default.
        """
        self.set(self.default)


    def focus(self):
        """Set the focus to this Control.
        Override in subclasses if needed.
        """
        pass


    def get_args(self):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.
        """
        # self.variable isn't defined until draw() is called
        if not self.variable:
            raise NotDrawn("Must call draw() before get_args()")

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
            if type(value) == list:
                if any(value):
                    args.append(self.option)
            else:
                args.append(self.option)
            
        # List of arguments
        if type(value) == list:
            args.extend(value)
        # Single argument
        else:
            args.append(value)
        return args


    def __repr__(self):
        """Return a Python code representation of this Control.
        """
        return "%s('%s', '%s')" % \
               (self.__class__.__name__, self.label, self.option)


### --------------------------------------------------------------------
### Control subclasses
### --------------------------------------------------------------------

from libtovid.odict import convert_list
from support import ComboBox

class Choice (Control):
    """Multiple-choice selector, with radiobutton or dropdown style.
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
        """Draw control widgets in the given master.
        """
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
import tkColorChooser

def hex_to_rgb(color):
    """Convert a hexadecimal color '#aabbcc' to an rgb tuple.
    """
    color = color.lstrip('#')
    red, green, blue = (color[0:2], color[2:4], color[4:6])
    return (int(red, 16), int(green, 16), int(blue, 16))


class Color (Control):
    """RGB hexadecimal color chooser.
    """
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
        """Draw control widgets in the given master.
        """
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.change)
        self.button.pack(side='left')
        Control.post(self)


    def change(self):
        """Event handler for the color button; choose and set a new color.
        """
        rgb, color = tkColorChooser.askcolor(self.get())
        if color:
            self.set(color)


    def set(self, color):
        """Set the current color to a hex value,
        and set the button's label and color to match.
        """
        self.variable.set(color)
        # Choose a foreground color that will show up
        r, g, b = hex_to_rgb(str(color))
        if (r + g + b) > 384:
            fg_color = '#000000' # black
        else:
            fg_color = '#ffffff' # white
        # Set button background color to chosen color
        self.button.config(text=color, foreground=fg_color, background=color)


### --------------------------------------------------------------------
from tkFileDialog import asksaveasfilename, askopenfilename

class Filename (Control):
    """Filename entry box with browse button.
    """
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
        # Type of files to load, with extensions
        self.filetypes=[('All Files', '*.*')]
        if 'filetypes' in kwargs:
            self.filetypes = kwargs['filetypes']


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

class Flag (Control):
    """Yes/no checkbox, for flag-type options.
    """
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
        if 'enables' in kwargs:
            self.enables = kwargs['enables']
            ensure_type("Flag can only enable a Widget", Widget, self.enables)
        else:
            self.enables = None



    def draw(self, master):
        """Draw the Flag in the given master widget.
        """
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
        """Enable/disable a Control based on the value of the Flag.
        """
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

class Font (Control):
    """Font name chooser."""
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
        """Draw the Font selector in the given master widget.
        """
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.choose)
        self.button.pack(side='left', padx=8)
        Control.post(self)


    def choose(self):
        """Open a font chooser to select a font.
        """
        chooser = FontChooser(self)
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------

class Number (Control):
    """Numeric entry box or slider.
    """
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
        """Draw the Number entry in the given master widget.
        """
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
        """Enable or disable all sub-widgets.
        """
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
import shlex

class Text (Control):
    """Text string entry box.
    """
    def __init__(self,
                 label="Text",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        """Create a text-entry control.
        
            label:    Label for the text
            option:   Command-line option to set
            default:  Default value of text widget
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)


    def draw(self, master):
        """Draw the Text control in the given master widget.
        """
        Control.draw(self, master)
        tk.Label(self, text=self.label, justify='left').pack(side='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side='left', fill='x', expand=True)
        Control.post(self)

    def focus(self):
        """Highlight the text entry box for editing.
        """
        self.entry.select_range(0, 'end')
        self.entry.focus_set()


class SpacedText (Text):
    """Text string interpreted as a space-separated list of strings
    """
    def __init__(self,
                 label="List",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        Text.__init__(self, label, option, default, help, **kwargs)


    def draw(self, master):
        """Draw SpacedText control in the given master widget.
        """
        Text.draw(self, master)


    def get(self):
        """Get current text, split into a list of strings.
        """
        text = Text.get(self)
        return shlex.split(text)


    def set(self, listvalue):
        """Set the text equal to the given list, joined with spaces and
        double-quoted. Double-quotes in list values are backslash-escaped.
        """
        def quote(val):
            return '"%s"' % val.replace('"', '\\"')
        text = ' '.join([quote(val) for val in listvalue])
        Text.set(self, text)

### --------------------------------------------------------------------
from tkFileDialog import askopenfilenames

class List (Control):
    """A list of values, editable with a given Control.

    Examples:

        List('Filenames', '-files', control=Filename())
        List('Colors', '-colors', control=Color())
        List('Texts', '-texts', control=Text())
        List('Choices', '-choices', control=Choice())

    """
    def __init__(self,
                 label="Text List",
                 option='',
                 default=None,
                 help='',
                 control=Text(),
                 **kwargs):
        """Create a control for a list-type option.
        """
        ensure_type("List requires a Control instance", Control, control)
        Control.__init__(self, list, label, option, default, help, **kwargs)
        self.control = control


    def draw(self, master, edit_only=False):
        """Draw the List and associated Control in the given master.
        If edit_only=True, omit add/move/remove features.
        """
        Control.draw(self, master)

        # Frame to draw list and child Control in
        frame = tk.LabelFrame(self, text=self.label)
        frame.pack(fill='x', expand=True)

        # Add/remove buttons
        if not edit_only:
            button_frame = tk.Frame(frame)
            add_button = \
                tk.Button(button_frame, text="Add", command=self.add)
            remove_button = \
                tk.Button(button_frame, text="Remove", command=self.remove)
            add_button.pack(fill='x', expand=True, side='left')
            remove_button.pack(fill='x', expand=True, side='left')
            button_frame.pack(fill='x', expand=True)

        # Scrolled or draggable listbox
        if edit_only:
            self.listbox = ScrollList(frame, self.variable)
        else:
            self.listbox = DragList(frame, self.variable)
        self.listbox.callback('select', self.select)
        self.listbox.pack(fill='both', expand=True)

        # Draw child Control
        self.control.draw(frame)
        self.control.pack(anchor='nw', fill='x', expand=True)
        # Child is disabled until values are added
        if not edit_only:
            self.control.disable()

        # Add event handler to child, to update selected list item
        # when child control's variable is modified
        def _modify(name, index, mode):
            self.modify()
        self.control.variable.trace_variable('w', _modify)


    def modify(self):
        """Event handler when the Control's variable is modified.
        """
        index = self.listbox.curindex
        new_value = self.control.get()
        self.variable[index] = new_value


    def select(self, index, value):
        """Select an item in the list and enable editing.
        """
        print("List.select(%d, %s)" % (index, value))
        self.control.set(value)
        self.control.focus()


    def add(self):
        """Event handler for the "Add" button.
        """
        # Index of first item to be added
        index = self.listbox.items.count()

        print("List.add, adding at index %d" % index)

        # For filenames, show a file chooser to add one or more files
        if isinstance(self.control, Filename):
            files = askopenfilenames(parent=self, title='Add files',
                                     filetypes=self.control.filetypes)
            self.listbox.add(*files)
        # For all others, add an item to the list
        else:
            value = self.control.default
            self.listbox.add(value)

        # Select the last item in the list, and enable the control
        self.listbox.select_index(-1)
        self.control.enable()


    def remove(self):
        """Event handler for the "Remove" button.
        """
        if self.listbox.items.count() > 0:
            index = self.listbox.curindex
            self.listbox.delete(index)

        # If last item was removed, disable the Control
        if self.listbox.items.count() == 0:
            self.control.disable()


    def set_variable(self, variable):
        """Set the List to use the given ListVar as its variable.
        """
        Control.set_variable(self, variable)
        self.listbox.set_variable(variable)


### --------------------------------------------------------------------

# Exported control classes, indexed by name
CONTROLS = {
    'Choice': Choice,
    'Color': Color,
    'Filename': Filename,
    'Flag': Flag,
    'Font': Font,
    'Number': Number,
    'SpacedText': SpacedText,
    'Text': Text,
    'List': List,
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
    

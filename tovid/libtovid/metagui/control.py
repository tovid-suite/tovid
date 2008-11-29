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


Option revamp ideas

Need a way to handle positional arguments, where the position in the
command-line does not necessarily correspond to the draw-order in the GUI.

Currently, an empty '' option is used for positional arguments, which
prevents them from having a global name. If instead, a convention were
adopted for option strings, where:

    List('Input files', '<in_files>', ...)

would create a positional argument, where the order of positioning is
defined somewhere else, like:

    Application('grep', panel1, panel2, ...
        expected = '[options] <in_files>')

or ffmpeg:

    _infile = Filename('Input file', '<infile>')
    _outfile = Filename('Output file', '<outfile>')
    _options = VPanel('Options', ...)

    expected = '[options] <infile> [options] <outfile>'

Would that work?

Or tovid-batch, where -infiles is an option, but must come last:

    expected = '[options] -infiles'

Q. How does '[options]' include everything _but_ -infiles?

Focus on getting most of the tovid scripts metagui-ized, then go from there.

Some options are like begin/end tokens:

    makexml -group <file_list> -endgroup

Some have complex expected followup options:

    makexml -topmenu VIDEO \
        -menu MENU1.mpg <file_list1> \
        -menu MENU2.mpg <file_list2>

How deep should metagui get into parsing all this?

Shorthand for a FlagGroup of Flags might be handy:

    format = FlagChoice('Format', '-vcd|-dvd|-svcd')

"""

__all__ = [
    'Control',
    # Subclasses
    'Choice',
    'Color',
    'Filename',
    'Flag',
    'FlagOpt',
    'Font',
    'List',
    'Number',
    'SpacedText',
    'Text',
]

import Tkinter as tk
from widget import Widget
from variable import VAR_TYPES
from support import DragList, ScrollList, FontChooser
from support import ensure_type

### --------------------------------------------------------------------
class NotDrawn (Exception):
    """Exception raised when a Control has not been drawn yet.
    """
    pass

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

    @staticmethod
    def by_option(option):
        """Return the Control instance for a given option string,
        or None if no Control has that option string.
        """
        if option != '' and option in Control.all:
            return Control.all[option]
        else:
            raise ValueError("No Control exists fot option: '%s'" % option)


    def __init__(self,
                 vartype=str,
                 label='',
                 option='',
                 default='',
                 help='',
                 toggles=False,
                 labelside='left',
                 **kwargs):
        """Create a Control for an option.

            vartype
                Python type of stored variable
                (str, bool, int, float, list, dict)
            label
                Label shown in the GUI for the Control
            option
                Command-line option associated with this Control,
                or '' to create a positional argument
            default
                Default value for the Control
            help
                Help text to show in a tooltip
            toggles
                Control widget may be toggled on/off
            labelside
                Position of label ('left' or 'top'). It's up to the
                derived Control class to use this appropriately.
            **kwargs: Keyword arguments of the form key1=arg1, key2=arg2
        
        """
        Widget.__init__(self, label)
        self.vartype = vartype
        self.variable = None
        self.label = label
        self.option = option
        self.default = default or vartype()
        self.help = help
        self.toggles = toggles
        self.labelside = labelside
        self.kwargs = kwargs

        # Defined in draw()
        self.checked = None
        self.tooltip = None
        self.check = None

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
        if self.vartype in VAR_TYPES:
            self.variable = VAR_TYPES[self.vartype](self)
        else:
            self.variable = tk.Variable(self)
        # Set default value
        if self.default:
            self.variable.set(self.default)
        # Draw tooltip
        if self.help != '':
            self.tooltip = ToolTip(self, text=self.help, delay=1000)
        # Draw the toggle checkbox if desired
        if self.toggles:
            self.checked = tk.BooleanVar()
            self.check = tk.Checkbutton(self, text='', command=self.toggle,
                                        var=self.checked)
            self.check.pack(side='left')


    def toggle(self):
        """Enable or disable the Control when self.check is toggled.
        """
        # If checkbox is checked, enable Control
        if self.checked.get():
            self.enable()
        # Otherwise, disable (then re-enable checkbox)
        else:
            self.disable()
            self.check.config(state='normal')


    def post(self):
        """Post-draw initialization.
        """
        if not self.enabled:
            self.disable()
        if self.toggles:
            self.toggle()


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
        need_type = VAR_TYPES[self.vartype]
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


    def get_args(self, variable=None):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.

            variable
                Tkinter Variable to use as the current value,
                or None to use self.variable.
        """
        args = []

        # Use the provided variable, or self.variable
        if variable != None:
            value = variable.get()
        else:
            value = self.get()

        # Return empty if the control is toggled off
        if not self.enabled:
            return []

        # Skip if unmodified or empty
        elif value == self.default or value == []:
            return []

        # Add option string
        if self.option != '':
            # For <option>, don't pass the option string
            if self.option.startswith('<') and self.option.endswith('>'):
                pass
            # For lists, only pass the option if the list has content
            elif type(value) == list:
                if any(value):
                    args.append(self.option)
            # All others--just append the option string
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
                 side='left',
                 **kwargs):
        """Initialize Choice widget with the given label and list of choices.

            label
                Text label for the choices
            option
                Command-line option to set
            default
                Default choice, or '' to use first choice in list
            help
                Help text to show in a tooltip
            choices
                Available choices, in string form: 'one|two|three'
                or list form: ['one', 'two', 'three'], or as a
                list-of-lists: [['a', "Use A"], ['b', "Use B"], ..].
                A dictionary is also allowed, as long as you don't
                care about preserving choice order.
            style
                'radio' for radiobuttons, 'dropdown' for a drop-down list
            side
                'left' for horizontal, 'top' for vertical arrangement

        """
        self.choices = convert_list(choices)
        Control.__init__(self, str, label, option,
                         default or self.choices.values()[0],
                         help, **kwargs)
        if style not in ['radio', 'dropdown']:
            raise ValueError("Choice style must be 'radio' or 'dropdown'")
        self.style = style
        self.side = side


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
                self.rb[choice].pack(anchor='nw', side=self.side)
        else: # dropdown/combobox
            label = tk.Label(self, text=self.label)
            label.pack(anchor='w', side=self.labelside)
            self.combo = ComboBox(self, self.choices.keys(),
                                  variable=self.variable)
            self.combo.pack(side='left')
        Control.post(self)

### --------------------------------------------------------------------
import tkColorChooser
import re

# Support functions for Color control
def _is_hex_rgb(color):
    """Return True if color appears to be a hex '#RRGGBB value.
    """
    if type(color) != str:
        return False
    if re.match('#[0-9a-fA-F]{3}', color):
        return True
    else:
        return False

def _hex_to_rgb(color):
    """Convert a hexadecimal color string '#RRGGBB' to an RGB tuple.
    """
    color = color.lstrip('#')
    red, green, blue = (color[0:2], color[2:4], color[4:6])
    return (int(red, 16), int(green, 16), int(blue, 16))

def _rgb_to_hex(rgb_tuple):
    """Convert an RGB tuple into a hexadecimal color string '#RRGGBB'.
    """
    red, green, blue = rgb_tuple
    return '#%02x%02x%02x' % (red, green, blue)


class Color (Control):
    """A color chooser that may have hex '#RRGGBB' or 'ColorName' values.
    """
    def __init__(self,
                 label="Color",
                 option='',
                 default='',
                 help='',
                 **kwargs):
        """Create a widget that opens a color-chooser dialog.
        
            label
                Text label describing the color to be selected
            option
                Command-line option to set
            default
                Default color (named color or hexadecimal RGB)
            help
                Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)


    def draw(self, master):
        """Draw control widgets in the given master.
        """
        Control.draw(self, master)
        label = tk.Label(self, text=self.label)
        label.pack(side=self.labelside)
        # Button for opening a color picker popup
        self.button = tk.Button(self, text='Color', command=self.pick_color)
        self.button.pack(side='left')
        # Textbox for typing in an RGB hex value or color name
        self.editbox = tk.Entry(self, textvariable=self.variable, width=8)
        self.editbox.bind('<Return>', self.enter_color)
        self.editbox.pack(side='left')
        # Indicate the current (default) color
        if _is_hex_rgb(self.default):
            self.indicate_color(self.default)
        Control.post(self)


    def enter_color(self, event):
        """Event handler when Enter is pressed in the color entry box.
        """
        color = self.variable.get().strip()
        self.set(color)


    def pick_color(self):
        """Event handler for the color picker button; choose and set a color.
        """
        rgb, color = tkColorChooser.askcolor(self.get())
        if color:
            self.set(str(color))


    def set(self, color):
        """Set the current color to an RGB hex value or color name.
        """
        # Update variable with whatever color name or RGB value was given
        # (even if it's not necessarily a valid color)
        self.variable.set(color)

        if _is_hex_rgb(color):
            self.indicate_color(color)
        else:
            # Try to get color by name, converting from 16-bit to 8-bit RGB
            try:
                hexcolor = _rgb_to_hex([x / 256 for x in self.winfo_rgb(color)])
            # For unknown color names, 
            except (tk.TclError):
                if _is_hex_rgb(self.default):
                    hexcolor = self.default
                else:
                    hexcolor = '#FFFFFF'
            self.indicate_color(hexcolor)


    def indicate_color(self, bg_color):
        """Change the button background color to the given RGB hex value.
        """
        if not _is_hex_rgb(bg_color):
            raise ValueError("indicate_color needs an 8-bit #RRGGBB hex string")
        # Choose a foreground color that will be visible
        r, g, b = _hex_to_rgb(bg_color)
        if (r + g + b) > 384: # hack
            fg_color = '#000000' # black
        else:
            fg_color = '#ffffff' # white
        # Set editbox background color to chosen color
        #self.editbox.config(foreground=fg_color, background=bg_color,
        #                    insertbackground=fg_color)
        #self.editbox.icursor('end')
        self.button.config(foreground=fg_color, background=bg_color)


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
                 filetypes='all',
                 **kwargs):
        """Create a Filename with label, text entry, and browse button.
        
            label
                Text of label next to file entry box
            option
                Command-line option to set
            default
                Default filename
            help
                Help text to show in a tooltip
            action
                Do you intend to 'load' or 'save' this file?
            desc
                Brief description (shown in title bar of file browser dialog)
            filetypes
                Types of files to show in the file browser dialog. May be 'all'
                for all file types, or a list of ('label', '*.ext') tuples.
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)
        self.action = action
        self.desc = desc
        if filetypes == 'all':
            self.filetypes = [('All Files', '*.*')]
        else:
            self.filetypes = filetypes


    def draw(self, master):
        """Draw control widgets in the given master."""
        Control.draw(self, master)
        # Create and pack widgets
        label = tk.Label(self, text=self.label, justify='left')
        label.pack(side=self.labelside)
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
            filename = askopenfilename(parent=self, title=self.desc,
                                       filetypes=self.filetypes)
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
                 enables=None,
                 **kwargs):
        """Create a Flag widget with the given label and default value.

            label
                Text label for the flag
            option
                Command-line flag passed
            default
                Default value (True or False)
            help
                Help text to show in a tooltip
            enables
                Option or list of options to enable when the Flag is checked
        """
        Control.__init__(self, bool, label, option, default, help, **kwargs)

        # Ensure the "enables" arg is the right type
        if not enables:
            self.enables = []
        elif type(enables) == list:
            self.enables = enables
        elif type(enables) == str:
            self.enables = [enables]
        else:
            raise TypeError("Flag 'enables' argument must be"
                            " an option string or list of option strings"
                            " (got %s instead)" % enables)
        # Will be a list of enabled Controls, filled in by draw()
        self.controls = []


    def draw(self, master):
        """Draw the Flag in the given master widget.
        """
        Control.draw(self, master)
        self.check = tk.Checkbutton(self, text=self.label,
                                    variable=self.variable,
                                    command=self.enabler)
        self.check.pack(side=self.labelside)

        # Enable/disable related controls
        if self.enables:
            #print("%s will enable:" % self.option)
            #print(self.enables)
            pass
        
        self.controls = [Control.by_option(opt) for opt in self.enables]
        Flag.enabler(self)
        Control.post(self)


    def enabler(self):
        """Enable/disable related Controls based on Flag state.
        """
        if not self.controls:
            return
        for control in self.controls:
            if self.get():
                if control.is_drawn:
                    control.enable()
                else:
                    control.enabled = True
            else:
                if control.is_drawn:
                    control.disable()
                else:
                    control.enabled = False

    
    def get_args(self):
        """Return a list of arguments for passing this command-line option.
        draw() must be called before this function.
        """
        args = []
        # If flag is true, and option is nonempty, append to args
        if self.get() and self.option:
            args.append(self.option)
        return args

### --------------------------------------------------------------------

class FlagOpt (Flag):
    """Like a normal Flag, but has an optional argument following it.
    """
    def __init__(self,
                 label="Flag",
                 option='',
                 default=False,
                 help='',
                 control=None,
                 **kwargs):
        """Create a FlagOpt widget; like a Flag, but has an optional argument
        which may be set using an associated Control.
        
            label
                Text label for the flag
            option
                Command-line flag passed
            default
                Default value (True or False)
            help
                Help text to show in a tooltip
            control
                Another Control, for setting the argument value (required)
        
        """
        Flag.__init__(self, label, option, default, help, **kwargs)
        if control != None:
            ensure_type("FlagOpt needs a Control instance", Control, control)
        self.control = control


    def draw(self, master):
        Flag.draw(self, master)
        # Pack the arg control next to the flag checkbox
        self.control.draw(self)
        self.control.pack(anchor='nw', side='left', fill='x', expand=True)
        # Disable if flag defaults to false
        if not self.default:
            self.control.disable()


    def enabler(self):
        """Enable or disable the arg Control when the flag changes.
        """
        Flag.enabler(self)
        if self.get():
            self.control.enable()
        else:
            self.control.disable()


    def get_args(self):
        args = Flag.get_args(self)
        if len(args) > 0:
            args.extend(self.control.get_args())
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
        
            label
                Text label for the font
            option
                Command-line option to set
            default
                Default font
            help
                Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)


    def draw(self, master):
        """Draw the Font selector in the given master widget.
        """
        Control.draw(self, master)
        tk.Label(self, text=self.label).pack(side=self.labelside)
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
                 units='',
                 style='spin',
                 **kwargs):
        """Create a number-setting widget.
        
            label
                Text label describing the meaning of the number
            option
                Command-line option to set
            default
                Default value
            help
                Help text to show in a tooltip
            min, max
                Range of allowable numbers (inclusive)
            style
                'spin' for a spinbox, or 'scale' for a slider
            units
                Units of measurement (ex. "kbits/sec"), used as a label
    
        The default/min/max may be integers or floats.
        """
        Control.__init__(self, type(default), label, option, default,
                         help, **kwargs)
        self.min = min
        self.max = max
        self.units = units
        self.style = style


    def draw(self, master):
        """Draw the Number entry in the given master widget.
        """
        Control.draw(self, master)
        tk.Label(self, name='label', text=self.label).pack(side=self.labelside)
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
        
            label
                Label for the text
            option
                Command-line option to set
            default
                Default value of text widget
            help
                Help text to show in a tooltip
        """
        Control.__init__(self, str, label, option, default, help, **kwargs)


    def draw(self, master):
        """Draw the Text control in the given master widget.
        """
        Control.draw(self, master)
        label = tk.Label(self, text=self.label, justify='left')
        label.pack(side=self.labelside)
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.entry.pack(side='left', fill='x', expand=True)
        Control.post(self)


    def focus(self):
        """Highlight the text entry box for editing.
        """
        self.entry.select_range(0, 'end')
        self.entry.focus_set()

### --------------------------------------------------------------------

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
        frame.pack(fill='both', expand=True)

        # Scrolled or draggable listbox
        if edit_only:
            self.listbox = ScrollList(frame, self.variable)
        else:
            self.listbox = DragList(frame, self.variable)
        self.listbox.callback('select', self.select)
        self.listbox.pack(fill='both', expand=True)

        # Frame to hold add/remove buttons and child Control
        tool_frame = tk.Frame(frame)
        tool_frame.pack(fill='x')

        # Add/remove buttons (not shown for edit_only)
        if not edit_only:
            add_button = \
                tk.Button(tool_frame, text="Add", command=self.add)
            remove_button = \
                tk.Button(tool_frame, text="Del", command=self.remove)
            add_button.pack(fill='x', side='left')
            remove_button.pack(fill='x', side='left')

        # Draw associated Control
        self.control.draw(tool_frame)
        self.control.pack(fill='x', side='left', expand=True)
        # Disabled until values are added
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
        # Only update the list if the new value is different
        if self.variable[index] != new_value:
            self.variable[index] = new_value


    def select(self, index, value):
        """Select an item in the list and enable editing.
        """
        # Only set control if value is different
        if self.control.get() != value:
            self.control.set(value)
        self.control.focus()


    def add(self):
        """Event handler for the "Add" button.
        """
        # Index of first item to be added
        index = self.listbox.items.count()

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

class ControlChoice (Control):
    """A choice of values from any of several other Controls.
    """
    def __init__(self,
                 label="Text List",
                 option='',
                 default=None,
                 help='',
                 *controls,
                 **kwargs):
        Control.__init__(self, str, label, option, default, help, **kwargs)
        ensure_type("ControlChoice needs Control instances", Control, *controls)
        self.controls = list(controls)


    def draw(self, master):
        pass


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
    

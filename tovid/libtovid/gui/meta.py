#! /usr/bin/env python
# meta.py

"""Let's say I'd like to write a GUI with as little code as possible.

I want to create a GUI application for a command-line program, and I shouldn't
have to say more than this:

    1. the name of my command-line program
    2. the command-line options it expects
    3. the kind of argument each option expects

For #3, I want to be able to specify some kind of GUI Control that will set
the value of some option. My program has a bunch of different kinds of
arguments, so I'll need a lot of Controls:

    Choice    Multiple-choice values
    Color     Color selection button
    Filename  Type or [Browse] a filename
    FileList  Add/remove/rearrange filename list
    Flag      Check box, yes or no
    Font      Font selection button
    List      Space-separated list
    Number    Number between A and B
    Text      Plain old text

(Don't bother me with all the GUI code backend stuff for this, either.)
I should be able to group the controls into, like, a Panel, and link each
of them to the command-line option they should set. So I can fulfill both
#2 and #3 in my list just by writing:

    panel = Panel("Main",
        ('image', Filename, 'Image to display'),
        ('width', Number, 'Width in pixels'),
        ('height', Number, 'Height in pixels')
    )

Then, to fulfill item #1, let's keep it simple:

    app = Application('showimage', [panel])

There's the name of my program, and the panel that has all the controls. I've
said my three things, and that should be enough to create a GUI. Like:

    gui = GUI('Da showimage GUI', [app])
    gui.run()

How hard can it be?
"""

__all__ = [
    'Control',
    # Control subclasses
    'Choice',
    'Color',
    'Filename',
    'Flag',
    'Font',
    'Text',
    'List',
    'Number',
    'FileList',
    'TextList',
    # Other helper frames
    'Tabs',
    'Optional',
    'PlainLabel',
    # GUI creation interface
    'OptionControl',
    'Panel',
    'Application',
    'GUI']

import os
import shlex
from libtovid import log
from libtovid.cli import Command
# Tkinter
import Tkinter as tk
import Tix
import tkFileDialog
import tkColorChooser
import tkSimpleDialog
from libtovid.gui.tooltip import ToolTip

log.level = 'debug'

### --------------------------------------------------------------------
### Custom widgets
### --------------------------------------------------------------------

class Control (tk.Frame):
    """A widget that controls a value.

    A Control is a specialized GUI widget that stores a variable value.
    The value is accessed via get() and set() methods.
    
    Control subclasses may have any number of sub-widgets such as labels,
    buttons or entry boxes; one of the sub-widgets should be linked to the
    controlled variable via an option like:
    
        entry = Entry(self, textvariable=self.variable)
    
    See the Control subclasses below for examples of how self.variable,
    get() and set() are used.
    """
    def __init__(self, master=None, vartype=str, help=''):
        """Create a Control with the given master and variable type.

            master:   Tkinter widget that will contain this Control
            vartype:  Type of stored variable (str, bool, int, float, list)
            help:     Help text to show in a tooltip
        """
        tk.Frame.__init__(self, master)
        vartypes = {
            str: tk.StringVar,
            bool: tk.BooleanVar,
            int: tk.IntVar,
            float: tk.DoubleVar,
            list: tk.Variable}
        # Create an appropriate Tkinter variable type
        if vartype in vartypes:
            self.variable = vartypes[vartype]()
        # Or use a generic Variable
        else:
            self.variable = tk.Variable()
        # Create tooltip if necessary
        if help != '':
            self.tooltip = ToolTip(self, text=help, delay=1000)

    def get(self):
        """Return the value of the Control's variable."""
        return self.variable.get()

    def set(self, value):
        """Set the Control's variable to the given value."""
        self.variable.set(value)

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets."""
        if enabled:
            newstate = 'normal'
        else:
            newstate = 'disabled'
        for widget in self.children.values():
            widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)


### --------------------------------------------------------------------
### Control subclasses
### --------------------------------------------------------------------

class Flag (Control):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 master=None,
                 label="Flag",
                 default=False,
                 help=''):
        """Create a Flag widget with the given label and default value.

            master:   Tkinter widget that will contain this Flag
            label:    Text label for the flag
            default:  Default value (True or False)
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, master, bool, help)
        self.set(default)
        # Create and pack widgets
        self.check = tk.Checkbutton(self, text=label, variable=self.variable)
        self.check.pack(side='left')

### --------------------------------------------------------------------

class Choice (Control):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 master=None,
                 label="Choices",
                 default=None,
                 help='',
                 choices='A|B',
                 packside='left'):
        """Initialize Choice widget with the given label and list of choices.

            master:   Tkinter widget that will contain this Choice
            label:    Text label for the choices
            default:  Default choice, or None to use first choice in list
            help:     Help text to show in a tooltip
            choices:  Available choices, in string form: 'one|two|three'
                      or list form: ['one', 'two', 'three']
        """
        Control.__init__(self, master, str, help)
        # If choices is a string, split on '|'
        if type(choices) == str:
            choices = choices.split('|')
        # Use first choice if no default was provided
        self.set(default or choices[0])
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.label.pack(side=packside)
        self.rb = {}
        for choice in choices:
            self.rb[choice] = tk.Radiobutton(self, text=choice, value=choice,
                                             variable=self.variable)
            self.rb[choice].pack(side=packside)


### --------------------------------------------------------------------

class Number (Control):
    """A widget for choosing or entering a number"""
    def __init__(self,
                 master=None,
                 label="Number",
                 default=None,
                 help='',
                 min=1,
                 max=10,
                 style='spin'):
        """Create a number-setting widget.
        
            master:   Tkinter widget that will contain this Number
            label:    Text label describing the meaning of the number
            default:  Default value, or None to use minimum
            help:     Help text to show in a tooltip
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' for a spinbox, or 'scale' for a slider
        """
        # TODO: Multiple styles (entry, spinbox, scale)
        Control.__init__(self, master, int, help)
        # Use min if default wasn't provided
        if default is None:
            default = min
        self.set(default)
        self.style = style
        # Create and pack widgets
        self.label = tk.Label(self, name='label', text=label)
        self.label.pack(side='left')
        if self.style == 'spin':
            self.number = tk.Spinbox(self, from_=min, to=max, width=4,
                                     textvariable=self.variable)
            self.number.pack(side='left')
        else: # 'scale'
            self.number = tk.Scale(self, from_=min, to=max,
                                   tickinterval=max-min,
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
                 master=None,
                 label="Text",
                 default='',
                 help=''):
        """
            master:   Tkinter widget that will contain this Text
            label:    Label for the text
            default:  Default value of text widget
            help:     Help text to show in a tooltip
        """
        Control.__init__(self, master, str, help)
        self.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label, justify='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.label.pack(side='left')
        self.entry.pack(side='left', fill='x', expand=True)

### --------------------------------------------------------------------

class List (Text):
    """A widget for entering a space-separated list of text items"""
    def __init__(self,
                 master=None,
                 label="List",
                 default='',
                 help=''):
        Text.__init__(self, master, label, default, help)

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
                 master=None,
                 label='Filename',
                 default='',
                 help='',
                 type='load',
                 desc='Select a file to load'):
        """Create a Filename with label, text entry, and browse button.
        
            master:  Tkinter widget that will contain the FileEntry
            label:   Text of label next to file entry box
            default: Default filename
            help:    Help text to show in a tooltip
            type:    Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
        """
        Control.__init__(self, master, str, help)
        self.set(default)
        self.type = type
        self.desc = desc
        # Create and pack widgets
        self.label = tk.Label(self, text=label, justify='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.button = tk.Button(self, text="Browse...", command=self.browse)
        self.label.pack(side='left')
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
                 master=None,
                 label="Color",
                 default='',
                 help=''):
        """Create a widget that opens a color-chooser dialog.
        
            master:  Tkinter widget that will contain the ColorPicker
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, master, str, help)
        self.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.button = tk.Button(self, text="None", command=self.change)
        self.label.pack(side='left')
        self.button.pack(side='left')
        
    def change(self):
        """Choose a color, and set the button's label and color to match."""
        rgb, color = tkColorChooser.askcolor(self.get())
        if color:
            self.set(color)
            self.button.config(text=color, foreground=color)
    
### --------------------------------------------------------------------

class FontChooser (tkSimpleDialog.Dialog):
    """A widget for choosing a font"""
    def __init__(self, master=None):
        tkSimpleDialog.Dialog.__init__(self, master, "Font chooser")

    def get_fonts(self):
        """Return a list of font names available in ImageMagick."""
        find = "convert -list type | sed '/Path/,/---/d' | awk '{print $1}'"
        return [line.rstrip('\n') for line in os.popen(find).readlines()]

    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        self.fontlist = ScrollList(master, "Available fonts",
                                   self.get_fonts())
        self.fontlist.pack(fill='both', expand=True)
        return self.fontlist
    
    def apply(self):
        """Set the selected font.
        """
        self.result = self.fontlist.selected.get()


class Font (Control):
    """A font selector widget"""
    def __init__(self,
                 master=None,
                 label='Font',
                 default='Helvetica',
                 help=''):
        """Create a widget that opens a font chooser dialog.
        
            master:  Tkinter widget that will contain this Font
            label:   Text label for the font
            default: Default font
            help:    Help text to show in a tooltip
        """
        Control.__init__(self, master, str, help)
        self.set(default)
        self.label = tk.Label(self, text=label)
        self.label.pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                                command=self.choose)
        self.button.pack(side='left', padx=8)

    def choose(self):
        """Open a font chooser to select a font."""
        chooser = FontChooser()
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------

class Optional (tk.Frame):
    """Container that shows/hides an optional Control"""
    def __init__(self,
                 master=None,
                 widget=None,
                 label='Option',
                 *args):
        """Create an Optional widget.

            master:  Tkinter widget that will contain the Optional
            widget:  A Control to show or hide
            label:   Label for the optional widget
        """
        tk.Frame.__init__(self, master)
        self.active = tk.BooleanVar()
        # Create and pack widgets
        self.check = tk.Checkbutton(self, text=label, variable=self.active,
                                    command=self.showHide, justify='left')
        self.check.pack(side='left')
        self.widget = widget(self, '', *args)
        self.widget.pack(side='left', expand=True, fill='x')
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

class PlainLabel (Control):
    """A plain label or spacer widget"""
    def __init__(self,
                 master=None,
                 label="Text",
                 default=''):
        Control.__init__(self, master, str)
        self.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.label.pack(side='left')

### --------------------------------------------------------------------

class Tabs (tk.Frame):
    """A tabbed frame, with tab buttons that switch between several frames.
    """
    def __init__(self, master, side='top'):
        """Create a tabbed frame widget.
        
            master: Tkinter widget that will contain the tabs widget
            side:   Side to show the tab controls on
                    ('top', 'bottom', 'left', or 'right')
        
        Tabs are added to the tab bar via the add() method. The added frames
        should have the Tabs frame as their master. For example:
        
            tabs = Tabs(self)
            spam = tk.Frame(tabs, ...)
            tabs.add("Spam", spam)
            eggs = tk.Frame(tabs, ...)
            tabs.add("Eggs", eggs)
            tabs.draw()
            tabs.pack(...)
        
        Tabs are drawn in the order they are added, with the first being
        initially active.
        """
        tk.Frame.__init__(self, master)
        self.side = side
        self.labels = []
        self.frames = []
        self.selected = tk.IntVar()
        self.index = 0
        #self.draw()    
    
    def add(self, label, frame):
        """Add a new tab for the given frame.

            label: Label shown in the tab
            frame: tk.Frame shown when the tab is activated
        """
        self.labels.append(label)
        self.frames.append(frame)

    def draw(self):
        """Draw the tab bar and the first enclosed frame.
        """
        # Tkinter configuration common to all tab buttons
        config = {
            'variable': self.selected,
            'command': self.change,
            'selectcolor': 'white',
            'indicatoron': 0,
            'padx': 4, 'pady': 4
            }
        # Frame to hold tab buttons
        self.buttons = tk.Frame(self)
        # For tabs on left or right, pack tab buttons vertically
        if self.side in ['left', 'right']:
            button_side = 'top'
            bar_anchor = 'n'
        else:
            button_side = 'left'
            bar_anchor = 'w'
        # Tab buttons, numbered from 0
        for index, label in enumerate(self.labels):
            button = tk.Radiobutton(self.buttons, text=label, value=index,
                                    **config)
            button.pack(anchor='nw', side=button_side, fill='x')
        self.buttons.pack(anchor=bar_anchor, side=self.side)
        # Activate the first tab
        self.selected.set(0)
        self.change()

    def change(self):
        """Switch to the selected tab's frame.
        """
        # Unpack the existing frame
        self.frames[self.index].pack_forget()
        # Pack the newly-selected frame
        selected = self.selected.get()
        self.frames[selected].pack(side=self.side, fill='both')
        # Remember this tab's index
        self.index = selected

### --------------------------------------------------------------------
### GUI interface-definition API
### --------------------------------------------------------------------

class OptionControl:
    """A Control that controls a command-line option."""
    def __init__(self, option, metawidget, *args):
        """Create an OptionControl.
        
            option:     Command-line option name (without the leading '-')
            metawidget: Control type (Filename, Choice, Flag etc.)
            *args:      Arguments to the given Control.

        The 'required' keyword may be passed as the first item in args;
        if present, the widget is drawn always-enabled (representing a
        mandatory command-line argument). Otherwise, the widget is drawn
        initially disabled, with a checkbox to enable it.
        """
        self.option = option
        self.metawidget = metawidget
        self.args = args
        self.widget = None
    
    def get_widget(self, master):
        """Create and return a Control instance.
        
            master: Tkinter widget to use as master
        """
        # Required widget, always shown
        if self.args[0] == 'required':
            self.widget = self.metawidget(master, *self.args[1:])
        # Flag widget, always shown
        elif self.metawidget == Flag:
            self.widget = self.metawidget(master, *self.args)
        # Optional widget, may be enabled/disabled
        else:
            # Hack: extract Control label
            label = self.args[0]
            args = self.args[1:]
            self.widget = Optional(master, self.metawidget, label, *args)
        return self.widget

    def get_options(self):
        """Return a list of arguments for passing this command-line option.
        get_widget must be called before this function.
        """
        if not self.widget:
            raise "Must call get_widget() before calling get_options()"
        args = []
        value = self.widget.get()
        # Boolean values control a flag
        if value == True:
            args.append("-%s" % self.option)
        # Others use '-option value'
        elif value:
            args.append("-%s" % self.option)
            # List of arguments
            if type(value) == list:
                args.append(*value)
            # Single argument
            else:
                args.append(value)
        return args

### --------------------------------------------------------------------

class Panel:
    def __init__(self, title='', *optdefs):
        """Create a Panel to hold option-metawidget associations.
        
            title:   Title of panel (name shown in tab bar)
            optdefs: Parenthesized tuples with option name, metawidget name,
                     and metawidget arguments.

        For example:

            Panel("General",
                ('bgaudio', Filename, "Background audio file"),
                ('submenus', Flag, "Create submenus"),
                ('menu-length', Number, "Length of menu (seconds)")
                )
        
        This creates a panel with three GUI widgets that control command-line
        options '-bgaudio', '-submenus', and '-menu-length'.
        """
        self.title = title
        self.controls = [] # OptionControl instances
        self.frame = None
        for optdef in optdefs:
            if type(optdef) == tuple:
                self.controls.append(OptionControl(*optdef))
            # TODO: Support keywords like 'spacer'
            else:
                raise "Panel option definitions must be in tuple form."

    def get_widget(self, master):
        """Return the panel widget (tk.Frame with Controls packed inside it).
        
            master: Tkinter widget to use as master
        """
        self.frame = tk.Frame(master)
        for control in self.controls:
            widget = control.get_widget(self.frame)
            widget.pack(anchor='nw', fill='x', expand=True)
        return self.frame

    def get_options(self):
        """Return a list of all command-line options from contained widgets.
        """
        if not self.frame:
            raise "Must call get_widget() before calling get_options()"
        args = []
        for control in self.controls:
            args += control.get_options()
        return args

### --------------------------------------------------------------------
    
class Application (tk.Frame):
    """GUI frontend for a command-line program.
    """
    def __init__(self, program, panels=None,
                 width=400, height=600):
        """Define a GUI application frontend for a command-line program.
        
            program: Command-line program that the GUI is a frontend for
            panels:  List of Panels (groups of widgets), containing controls
                     for the given program's options. Use [panel] to pass
                     a single panel. If there are multiple panels, a tabbed
                     application is created.
            width:   Pixel width of application window
            height:  Pixel height of application window

        After defining the Application, call run() to show/execute it.
        """
        self.program = program
        self.panels = panels or []
        self.width = width
        self.height = height
        self.showing = False
        self.frame = None

    def get_frame(self, master):
        """Return a tk.Frame containing the application, using the given master.
        """
        # If self.window has already been created, return it
        if self.frame:
            return self.frame
        # Main window with fixed width/height
        self.frame = \
            tk.LabelFrame(master, text=self.program, padx=8, pady=8,
                          width=self.width, height=self.height,
                          font=('Helvetica', 14, 'bold'))
        self.frame.pack()
        # Prevent resizing
        self.frame.pack_propagate(False)
        # Single-panel application
        if len(self.panels) == 1:
            panel = self.panels[0].get_widget(self.frame)
            panel.pack(fill='x')
        # Multi-panel (tabbed) application
        else:
            tabs = Tabs(self.frame)
            for panel in self.panels:
                tabs.add(panel.title, panel.get_widget(tabs))
            tabs.draw()
            tabs.pack()
        # "Run" button
        button = tk.Button(self.frame, text="Run %s now" % self.program,
                           command=self.execute)
        button.pack(anchor='s', fill='x', expand=True)
        return self.frame

    def get_options(self):
        """Get a list of all command-line arguments from all panels.
        """
        if isinstance(self.panels, Panel):
            return self.panels.get_options()
        elif isinstance(self.panels, list):
            args = []
            for panel in self.panels:
                args += panel.get_options()
            return args

    def execute(self):
        """Run the program with all the supplied options.
        """
        args = self.get_options()
        command = Command(self.program, *args)
        print "Running command:", str(command)
        print "(not really)"


class GUI (tk.Tk):
    def __init__(self, title, applications):
        """Create a GUI for the given applications.
        
            title:        Text shown in the title bar
            applications: List of Applications to include in the GUI
        """
        tk.Tk.__init__(self)
        self.title(title)
        # Index applications by program name
        programs = [app.program for app in applications]
        self.appdict = dict(zip(programs, applications))
        self.apps = applications
        # On/off (checkbutton) variables for each program
        self.showing = {}
        self.frames = {}
        for app in self.apps:
            self.showing[app] = tk.BooleanVar()
            self.showing[app].set(False)

    def draw(self):
        for app in self.apps:
            self.frames[app] = app.get_frame(self)
            self.frames[app].pack_forget()
        # self.frames[self.apps[0]].pack()

    def draw_menu(self, window):
        """Draw a menu bar in the given window.
        """
        # Create and add the menu bar
        menubar = tk.Menu(window)
        window.config(menu=menubar)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        # Application menu
        # (only included for multi-application GUIs)
        if len(self.apps) > 1:
            appmenu = tk.Menu(menubar, tearoff=True)
            appmenu.add_separator()
            for app in self.apps:
                appmenu.add_checkbutton(label=app.program,
                                        variable=self.showing[app],
                                        command=self.show_app)
            menubar.add_cascade(label="Application", menu=appmenu)

    def execute(self):
        """Run the current application's program."""
        app = self.appdict[self.current_app.get()]
        app.execute()

    def show_app(self):
        """Show all applications that are checked, and hide those that aren't.
        """
        for app, ischecked in self.showing.items():
            if ischecked.get():
                self.frames[app].pack(side='left', padx=8, pady=8)
                self.program = app.program
            else:
                self.frames[app].pack_forget()

    def run(self):
        """Run the GUI"""
        self.draw()
        self.draw_menu(self)
        # Enter the main event handler
        self.mainloop()
        # TODO: Interrupt handling









### --------------------------------------------------------------------
### Not exported yet
### --------------------------------------------------------------------

class ScrollList (Control):
    """A widget for choosing from a list of values
    """
    def __init__(self, master=None, label="List", values=None):
        """Create a ScrollList widget.
        
            master:    Tkinter widget that will contain this ScrollList
            label:     Text label for the list
            values:    List of initial values
        """
        Control.__init__(self, master, list)
        self.selected = tk.StringVar() # Currently selected list item
        # Listbox label
        self.label = tk.Label(self, text=label)
        self.label.pack(anchor=tk.W)
        # Group listbox and scrollbar together
        group = tk.Frame(self)
        self.scrollbar = tk.Scrollbar(group, orient='vertical',
                                      command=self.scroll)
        self.listbox = tk.Listbox(group, width=30, listvariable=self.variable,
                                  yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='left', fill='y', expand=True)
        group.pack()
        self.listbox.bind('<Button-1>', self.select)
        if values:
            self.add(*values)

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

### --------------------------------------------------------------------

class DragList (ScrollList):
    """A scrollable listbox with drag-and-drop support"""
    def __init__(self, master=None, label="List", values=None):
        ScrollList.__init__(self, master, label, values)
        self.listbox.bind('<Button-1>', self.select)
        self.listbox.bind('<B1-Motion>', self.drag)
        self.listbox.bind('<ButtonRelease-1>', self.drop)
        self.curindex = 0

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
    def __init__(self, master=None, label="File list", files=None):
        DragList.__init__(self, master, label, files)
        # Group Add/Remove buttons
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
    def __init__(self, master=None, label="Text list", values=None):
        DragList.__init__(self, master, label, values)
        self.editbox = tk.Entry(self, width=30, textvariable=self.selected)
        self.editbox.bind('<Return>', self.setTitle)
        self.editbox.pack(fill='x', expand=True)

    def setTitle(self, event):
        """Event handler when Enter is pressed after editing a title."""
        newtitle = self.get()
        log.debug("Setting title to '%s'" % newtitle)
        self.listbox.delete(self.curindex)
        self.listbox.insert(self.curindex, newtitle)


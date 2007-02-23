#! /usr/bin/env python
# __init__.py (metagui)

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

# TODO: Multi-flag Choice (for -dvd|-vcd|-svcd, -pal|-ntsc etc.)
# TODO: Files/titles multi-list
# Group options in a Panel with a label

# Export everything from support and control modules
# (Anyone know of a more concise way to do this?)
from support import *
from control import *
from support import __all__ as all_support
from control import __all__ as all_control
__all__ = [
    # GUI creation interface
    'OptionControl',
    'Panel',
    'Application',
    'GUI'] + all_support + all_control


from libtovid import log
from libtovid.cli import Command
# Tkinter
import Tkinter as tk
# meta

log.level = 'debug'

### --------------------------------------------------------------------
### GUI interface-definition API
### --------------------------------------------------------------------

class OptionControl:
    """A Control that controls a command-line option."""
    def __init__(self, option, control, *args):
        """Create an OptionControl.
        
            option:  Command-line option name (without the leading '-')
            control: Control type (Filename, Choice, Flag etc.)
            *args:   Arguments to the given Control

        The 'required' keyword may be passed as the first item in args;
        if present, the widget is drawn always-enabled (representing a
        mandatory command-line argument). Otherwise, the widget is drawn
        initially disabled, with a checkbox to enable it.
        """
        self.option = option
        self.control = control
        self.args = args
        self.widget = None
    
    def get_widget(self, master):
        """Create and return a Control instance.
        
            master: Tkinter widget to use as master
        """
        # Required widget, always shown
        if self.args[0] == 'required':
            self.widget = self.control(master, *self.args[1:])
        # Flag widget, always shown
        elif self.control == Flag:
            self.widget = self.control(master, *self.args)
        # Optional widget, may be enabled/disabled
        else:
            # Hack: extract Control label
            label = self.args[0]
            args = self.args[1:]
            self.widget = Optional(master, self.control, label, *args)
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
        """Create a Panel to hold option-control associations.
        
            title:   Title of panel (name shown in tab bar)
            optdefs: Parenthesized tuples with option name, control name,
                     and control arguments.

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

### --------------------------------------------------------------------

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

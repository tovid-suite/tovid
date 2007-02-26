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

"""Notes:

Support alignment keywords in Panel argument list, i.e.:

    panel = Panel("General",
        ('foo', Number, ...),
        'beside',
        ('bar', Filename, ...)
    )

places the 'foo' and 'bar' widgets side-by-side (instead of the default,
'below'). Other possible keywords:

    'spacer'
    'group' ... 'endgroup' groups controls in a sub-frame
    'Any other text' becomes a label inserted at that position

"""

# Export everything from support and control modules
# (Anyone know of a more concise way to do this?)
from support import *
from control import *
from support import __all__ as all_support
from control import __all__ as all_control
__all__ = [
    # GUI creation interface
    'Panel',
    'Application',
    'GUI',
    # Submodules
    'manpage',
    'builder'] + all_support + all_control

from libtovid import log
from libtovid.cli import Command
import Tkinter as tk

log.level = 'debug'

### --------------------------------------------------------------------
### GUI interface-definition API
### --------------------------------------------------------------------

class Panel (tk.LabelFrame):
    """A group of option controls in a rectangular frame.

    For example:

        Panel("General",
            Filename('bgaudio', "Background audio file"),
            Flag('submenus', "Create submenus"),
            Number('menu-length', "Length of menu (seconds)")
            )

    This creates a panel with three GUI widgets that control command-line
    options '-bgaudio', '-submenus', and '-menu-length'.
    """
    def __init__(self, title='', *contents):
        """Create a Panel to hold option-control associations.
        
            title:    Title of panel (name shown in tab bar)
            contents: Controls or sub-Panels
        """
        self.title = title
        self.contents = []
        for item in contents:
            if isinstance(item, Control) or isinstance(item, Panel):
                self.contents.append(item)
            else:
                raise "Panel may only contain Controls or other Panels"

    def draw(self, master):
        """Draw Controls in a Frame with the given master, and return the Frame.
        """
        tk.LabelFrame.__init__(self, master, text=self.title, padx=8, pady=4)
        for item in self.contents:
            item.draw(self)
            item.pack(anchor='nw', fill='x', expand=True)

    def get_options(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for child in self.children:
            args += child.get_options()
        return args

### --------------------------------------------------------------------

class Application (tk.Frame):
    """Graphical frontend for a command-line program
    """
    def __init__(self, program, panels=None):
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
        self.showing = False
        self.frame = None

    def draw(self, master):
        """Draw the Application in the given master.
        """
        tk.Frame.__init__(self, master)
        # Single-panel application
        if len(self.panels) == 1:
            panel = self.panels[0]
            panel.draw(self)
            panel.pack(anchor='n', fill='x', expand=True)
        # Multi-panel (tabbed) application
        else:
            tabs = Tabs(self)
            for panel in self.panels:
                panel.draw(tabs)
                tabs.add(panel.title, panel)
            tabs.draw()
            tabs.pack(anchor='n', fill='x', expand=True)
        # "Run" button
        button = tk.Button(self, text="Run %s now" % self.program,
                           command=self.execute)
        button.pack(anchor='s', fill='x', expand=True)

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
    """GUI with one or more Applications
    """
    def __init__(self, title, applications, width=500, height=800):
        """Create a GUI for the given applications.
        
            title:        Text shown in the title bar
            applications: List of Applications to included in the GUI
        """
        tk.Tk.__init__(self)
        self.title(title)
        self.apps = applications
        self.width = width
        self.height = height

    def run(self):
        """Run the GUI"""
        self.draw()
        self.draw_menu(self)
        # Enter the main event handler
        self.mainloop()
        # TODO: Interrupt handling

    def draw(self):
        """Draw widgets."""
        self.frame = tk.Frame(self, width=self.width, height=self.height)
        self.frame.pack(fill='both', expand=True)
        self.frame.pack_propagate(False)
        self.resizable(width=True, height=True)
        # Single-application GUI
        if len(self.apps) == 1:
            app = self.apps[0].draw(self.frame)
            app.pack(anchor='n', fill='x', expand=True)
        # Multi-application (tabbed) GUI
        else:
            tabs = Tabs(self.frame, 'top', ('Helvetica', 14, 'bold'))
            for app in self.apps:
                app.draw(tabs)
                tabs.add(app.program, app)
            tabs.draw()
            tabs.pack(anchor='n', fill='x', expand=True)

    def draw_menu(self, window):
        """Draw a menu bar in the given top-level window.
        """
        # Create and add the menu bar
        menubar = tk.Menu(window)
        window.config(menu=menubar)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

### --------------------------------------------------------------------

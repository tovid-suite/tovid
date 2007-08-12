#! /usr/bin/env python
# gui.py

"""Classes for creating and laying out GUI applications.
"""

__all__ = [
    'Panel',
    'HPanel',
    'VPanel',
    'Dropdowns',
    'Drawer',
    'Tabs',
    'Application',
    'GUI']

import sys
import Tkinter as tk

from widget import Widget
from control import Control, MissingOption
from libtovid.cli import Command

### --------------------------------------------------------------------
### GUI interface-definition API
### --------------------------------------------------------------------

class Panel (Widget):
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
        """Create a Panel to hold control widgets or sub-panels.
        
            title:    Title of panel (name shown in tab bar)
            contents: One or more Widgets (Controls, Panels, Drawers etc.)
        """
        Widget.__init__(self)
        if type(title) != str:
            raise TypeError("First argument to Panel must be a text label.")
        self.title = title
        self.contents = []
        for item in contents:
            if isinstance(item, Widget):
                self.contents.append(item)
            else:
                import traceback
                # Print helpful info from stack trace
                last_error = traceback.extract_stack()[0]
                filename, lineno, foo, code = last_error
                print "Error on line %(lineno)s of %(filename)s:" % vars()
                print "    " + code
                print "Panel '%s' may only contain Widget subclasses" \
                      " (Controls, Panels, Drawers etc.)" \
                      " got %s instead" % type(item)
                sys.exit(1)

    def draw(self, master, side='top'):
        """Draw Panel and its contents in the given master.
        """
        Widget.draw(self, master)
        # Get a labeled or unlabeled frame
        if self.title:
            frame = tk.LabelFrame(self, text=self.title)
            frame.pack(fill='both', expand=True)
        else:
            frame = self
        # Draw all contents in the frame
        for item in self.contents:
            item.draw(frame)
            item.pack(side=side, anchor='nw', fill='x', expand=True,
                  padx=4, pady=4)

    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        Print error messages if any required options are missing.
        """
        args = []
        for item in self.contents:
            try:
                args += item.get_args()
            except MissingOption, missing:
                print "Missing a required option: " + missing.option
        return args

### --------------------------------------------------------------------

class HPanel (Panel):
    """A panel with widgets packed left-to-right"""
    def __init__(self, title='', *contents):
        Panel.__init__(self, title, *contents)

    def draw(self, master):
        Panel.draw(self, master, 'left')

### --------------------------------------------------------------------

class VPanel (Panel):
    """A panel with widgets packed top-to-bottom"""
    def __init__(self, title='', *contents):
        Panel.__init__(self, title, *contents)

    def draw(self, master):
        Panel.draw(self, master, 'top')

### --------------------------------------------------------------------
from support import ComboBox, ListVar
from control import Control
from libtovid.odict import Odict

class Dropdowns (Panel):
    """A Panel that uses dropdowns for selecting and setting options.
    
    Given a list of controls, the Dropdowns panel displays, initially,
    a single dropdown list. Each control is a choice in the list, and
    is shown as two columns, option and label (with help shown in a tooltip).
    
    Selecting a control causes that control to be displayed, so that it
    may be set to the desired value (along with a "remove" button to discard
    the control). The dropdown list is shifted downward, so another control
    and option may be set.
    """
    def __init__(self, title='', *contents):
        Panel.__init__(self, title, *contents)
        # Controls, indexed by option
        self.controls = Odict()
        for control in self.contents:
            if not isinstance(control, Control):
                raise TypeError("Can only add Controls to a Dropdown")
            self.controls[control.option] = control

    def draw(self, master):
        if self.title:
            tk.LabelFrame.__init__(self, master, text=self.title,
                                   padx=8, pady=8)
        else:
            tk.LabelFrame.__init__(self, master, bd=0, text='',
                                   padx=8, pady=8)
        self.choices = ListVar(items=self.controls.keys())
        self.chosen = tk.StringVar()
        self.chooser = ComboBox(self, self.choices, variable=self.chosen,
                                command=self.choose_new)
        self.chooser.pack(fill='both', expand=True)

    def choose_new(self, event=None):
        """Create and display the chosen control."""
        chosen = self.chosen.get()
        if chosen == '':
            return
        self.chooser.pack_forget()
        # Put control and remove button in a frame
        frame = tk.Frame(self)
        button = tk.Button(frame, text="X",
                           command=lambda:self.remove(chosen))
        button.pack(side='left')
        control = self.controls[chosen]
        control.draw(frame)
        control.pack(side='left', fill='x', expand=True)
        frame.pack(fill='x', expand=True)
        # Remove the chosen control/panel from the list of available ones
        self.choices.remove(chosen)
        self.chooser.pack()

    def remove(self, option):
        """Remove a given option's control from the interface."""
        frame = self.controls[option].master
        frame.pack_forget()
        frame.destroy()
        # Make this option available in the dropdown
        self.choices.append(option)

    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for control in self.contents:
            if control.active:
                args += control.get_args()
        return args


### --------------------------------------------------------------------

class Drawer (Widget):
    """Like a Panel, but may be hidden or "closed" like a drawer."""
    def __init__(self, title='', *contents):
        Widget.__init__(self)
        self.panel = Panel(title, *contents)
        self.visible = False
        
    def draw(self, master):
        Widget.draw(self, master)
        # Checkbutton
        button = tk.Button(self, text=self.panel.title,
                           command=self.show_hide)
        button.pack(anchor='nw', fill='x', expand=True)
        # Draw panel, but don't pack
        self.panel.draw(self)

    def show_hide(self):
        # Hide if showing
        if self.visible:
            self.panel.pack_forget()
            self.visible = False
        # Show if hidden
        else:
            self.panel.pack(anchor='nw', fill='both', expand=True)
            self.visible = True
    
    def get_args(self):
        return self.panel.get_args()

### --------------------------------------------------------------------

class Tabs (Widget):
    """A widget with tab buttons that switch between several panels.
    """
    def __init__(self, *panels, **kwargs):
        """Create tabs that switch between several Panels.
        """
        Widget.__init__(self)
        self.index = 0
        self.panels = []
        for panel in panels:
            if not isinstance(panel, Panel):
                raise TypeError("Tabs may only contain Panels")
            self.panels.append(panel)

    def add(self, panel):
        """Add the given Panel to the Tabs.
        """
        self.panels.append(panel)

    def draw(self, master, side='top'):
        """Draw the Tabs widget in the given master."""
        Widget.draw(self, master)
        self.selected = tk.IntVar()
        self.side = side
        # Tkinter configuration common to all tab buttons
        config = {
            'variable': self.selected,
            'command': self.change,
            'selectcolor': 'white',
            'relief': 'sunken',
            'offrelief': 'groove',
            'indicatoron': 0,
            'padx': 4, 'pady': 4
            }
        # Frame to hold tab buttons
        self.buttons = tk.Frame(self)
        # For tabs on left or right, pack tab buttons vertically
        if self.side in ['left', 'right']:
            button_side = 'top'
            bar_anchor = 'n'
            bar_fill = 'y'
        else:
            button_side = 'left'
            bar_anchor = 'w'
            bar_fill = 'x'
        # Tab buttons, numbered from 0
        for index, panel in enumerate(self.panels):
            button = tk.Radiobutton(self.buttons, text=panel.title,
                                    value=index, **config)
            button.pack(anchor='nw', side=button_side,
                        fill='both', expand=True)
            panel.draw(self)
        self.buttons.pack(anchor=bar_anchor, side=self.side,
                          fill=bar_fill)
        # Activate the first tab
        self.selected.set(0)
        self.change()

    def change(self):
        """Switch to the selected tab's frame.
        """
        # Unpack the existing panel
        self.panels[self.index].pack_forget()
        # Pack the newly-selected panel
        selected = self.selected.get()
        self.panels[selected].pack(side=self.side, fill='both', expand=True)
        # Remember this tab's index
        self.index = selected

### --------------------------------------------------------------------
import tkMessageBox

class Application (Widget):
    """Graphical frontend for a command-line program
    """
    def __init__(self, program, panels=None, style=None):
        """Define a GUI application frontend for a command-line program.
        
            program: Command-line program that the GUI is a frontend for
            panels:  List of Panels (groups of widgets), containing controls
                     for the given program's options. Use [panel] to pass
                     a single panel. If there are multiple panels, a tabbed
                     application is created.

        After defining the Application, call run() to show/execute it.
        """
        Widget.__init__(self)
        self.program = program
        # TODO: Friendlier error-handling
        if not type(panels) == list or len(panels) == 0:
            raise TypeError("Application needs a list of Panels")
        self.panels = panels or []
        self.showing = False
        self.frame = None

    def draw(self, master):
        """Draw the Application in the given master.
        """
        Widget.draw(self, master)
        # Single-panel application
        if len(self.panels) == 1:
            panel = self.panels[0]
            panel.draw(self)
            panel.pack(anchor='n', fill='x', expand=True)
        # Multi-panel (tabbed) application
        else:
            tabs = Tabs(*self.panels)
            tabs.draw(self)
            tabs.pack(anchor='n', fill='x', expand=True)
        # "Run" button
        button = tk.Button(self, text="Run %s now" % self.program,
                           command=self.execute)
        button.pack(anchor='s', fill='x')

    def get_args(self):
        """Get a list of all command-line arguments from all panels.
        """
        if isinstance(self.panels, Panel):
            return self.panels.get_args()
        elif isinstance(self.panels, list):
            args = []
            for panel in self.panels:
                args += panel.get_args()
            return args

    def execute(self):
        """Run the program with all the supplied options.
        """
        args = self.get_args()
        command = Command(self.program, *args)

        print "Running command:", command
        # Verify with user
        if tkMessageBox.askyesno(message="Run %s now?" % self.program):
            # Kind of hackish...
            root = self.master.master
            root.withdraw()
            try:
                command.run()
            except KeyboardInterrupt:
                tkMessageBox.showerror(message="todisc was interrupted!")
            else:
                tkMessageBox.showinfo(message="todisc finished running!")
            root.deiconify()

### --------------------------------------------------------------------
from support import ConfigWindow, Style
import os
DEFAULT_CONFIG = os.path.expanduser('~/.metagui/config')

class GUI (tk.Tk):
    """GUI with one or more Applications
    """
    def __init__(self, title, applications, width=600, height=600,
                 inifile=None):
        """Create a GUI for the given applications.
        
            title:        Text shown in the title bar
            applications: List of Applications to included in the GUI
            width:        Initial width of GUI window in pixels
            height:       Initial height of GUI window in pixels
            inifile:      Name of an .ini-formatted file with GUI configuration
        """
        tk.Tk.__init__(self)
        self.geometry("%dx%d" % (width, height))
        self.title(title)
        # TODO: Friendlier error-handling
        if not type(applications) == list or len(applications) == 0:
            raise TypeError("GUI needs a list of Applications")
        self.apps = applications
        self.width = width
        self.height = height
        self.inifile = inifile or DEFAULT_CONFIG
        self.style = Style()
        if os.path.exists(self.inifile):
            print "Loading style from config file", self.inifile
            self.style.load(self.inifile)
        else:
            print "Creating config file", self.inifile
            self.style.save(self.inifile)
        # Show hidden file option in file dialogs
        self.tk.call('namespace', 'import', '::tk::dialog::file::')
        self.tk.call('set', '::tk::dialog::file::showHiddenBtn',  '1')
        self.tk.call('set', '::tk::dialog::file::showHiddenVar',  '0')

    def run(self):
        """Run the GUI"""
        self.draw()
        self.draw_menu(self)
        # Enter the main event handler
        self.mainloop()
        # TODO: Interrupt handling

    def draw(self):
        """Draw widgets."""
        self.style.apply(self)
        self.frame = tk.Frame(self, width=self.width, height=self.height)
        self.frame.pack(fill='both', expand=True)
        self.resizable(width=True, height=True)
        # Single-application GUI
        if len(self.apps) == 1:
            app = self.apps[0]
            app.draw(self.frame)
            app.pack(anchor='n', fill='both', expand=True)
        # Multi-application (tabbed) GUI
        else:
            tabs = Tabs(self.frame, 'top')
            for app in self.apps:
                app.draw(tabs)
                tabs.add(app.program, app)
            tabs.draw()
            tabs.pack(anchor='n', fill='both', expand=True)
        #self.frame.pack_propagate(False)
    
    def redraw(self):
        self.frame.destroy()
        self.draw()

    def draw_menu(self, window):
        """Draw a menu bar in the given top-level window.
        """
        # Create and add the menu bar
        menubar = tk.Menu(window)
        window.config(menu=menubar)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Config", command=self.show_config)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def show_config(self):
        """Open the GUI configuration dialog."""
        config = ConfigWindow(self, self.style)
        if config.result:
            self.style = config.result
            print "Saving configuration to", self.inifile
            self.style.save(self.inifile)
            self.style.apply(self)
            self.redraw()

### --------------------------------------------------------------------


#! /usr/bin/env python
# main.py

__all__ = [
    # Main GUI creation interface
    'Panel',
    'HPanel',
    'VPanel',
    'Drawer',
    'Application',
    'GUI']

import Tkinter as tk
from control import Control
from support import Tabs
from cli import Command

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
            if isinstance(item, Control) \
               or isinstance(item, Panel) \
               or isinstance(item, Drawer):
                self.contents.append(item)
            else:
                raise "Panel may only contain Controls, Panels, or Drawers."

    def draw(self, master, side='top'):
        """Draw Controls in a Frame with the given master.
        """
        if self.title:
            tk.LabelFrame.__init__(self, master, text=self.title,
                                   padx=8, pady=4)
        else:
            tk.LabelFrame.__init__(self, master, bd=0, text='')
        for item in self.contents:
            item.draw(self)
            item.pack(side=side, anchor='nw', fill='both', expand=True)

    def get_options(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for item in self.contents:
            args += item.get_options()
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

class Drawer (tk.Frame):
    """Like a Panel, but may be hidden or closed."""
    def __init__(self, title='', *contents):
        self.panel = Panel(title, *contents)
        self.visible = False
        
    def draw(self, master):
        tk.Frame.__init__(self, master)
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
            panel.pack(anchor='n', fill='both', expand=True)
        # Multi-panel (tabbed) application
        else:
            tabs = Tabs(self)
            for panel in self.panels:
                panel.draw(tabs)
                tabs.add(panel.title, panel)
            tabs.draw()
            tabs.pack(anchor='n', fill='both', expand=True)
        # "Run" button
        button = tk.Button(self, text="Run %s now" % self.program,
                           command=self.execute)
        button.pack(fill='x', expand=True)

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
            app = self.apps[0]
            app.draw(self.frame)
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


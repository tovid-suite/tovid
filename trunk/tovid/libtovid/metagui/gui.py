#! /usr/bin/env python
# gui.py

"""Top-level GUI classes.
"""

__all__ = [
    'Application',
    'GUI',
]

import os
import sys
import Tkinter as tk

from widget import Widget
from panel import Panel, Tabs
from support import ensure_type, exit_with_traceback
from libtovid.cli import Command

DEFAULT_CONFIG = os.path.expanduser('~/.metagui/config')

### --------------------------------------------------------------------
import tkMessageBox

class Application (Widget):
    """Graphical frontend for a command-line program
    """
    def __init__(self, program, *panels):
        """Define a GUI application frontend for a command-line program.
        
            program: Command-line program that the GUI is a frontend for
            panels:  One or more Panels, containing controls for the given
                     program's options. For multiple panels, a tabbed
                     application is created.

        After defining the Application, call run() to show/execute it.
        """
        # Ensure that one or more Panel instances were provided
        ensure_type("Application needs Panel instances", Panel, *panels)

        # Initialize
        Widget.__init__(self)
        self.program = program
        self.panels = panels
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
            tabs = Tabs('', *self.panels)
            tabs.draw(self)
            tabs.pack(anchor='n', fill='x', expand=True)


    def get_args(self):
        """Get a list of all command-line arguments from all panels.
        """
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

class GUI (tk.Tk):
    """GUI with one or more Applications
    """
    def __init__(self, title, width, height, *applications, **kwargs):
        """Create a GUI for the given applications.
        
            title:        Text shown in the title bar
            width:        Initial width of GUI window in pixels
            height:       Initial height of GUI window in pixels
            applications: Applications to included in the GUI
        
        Keywords arguments accepted:

            inifile:      Name of an .ini-formatted file with GUI configuration
        """

        # Ensure that one or more Application instances were provided
        if not applications:
            exit_with_traceback("GUI needs one or more Applications")
        ensure_type("GUI needs Applications", Application, *applications)
        self.apps = applications

        tk.Tk.__init__(self)

        self.geometry("%dx%d" % (width, height))
        self.title(title)
        self.width = width
        self.height = height
        # Get style configuration from INI file
        if 'inifile' in kwargs:
            self.inifile = inifile
        else:
            self.inifile = DEFAULT_CONFIG
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
        # handle user closing window with window manager or ctrl-q
        self.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit(self.apps[0]))
        self.bind('<Control-q>', lambda e, : self.confirm_exit(self.apps[0]))


    def run(self):
        """Run the GUI"""
        self.draw()
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
            self.draw_toolbar(app)
        # Multi-application (tabbed) GUI
        else:
            tabs = Tabs('', self.frame, 'top')
            for app in self.apps:
                self.draw_toolbar(app)
                app.draw(tabs)
                tabs.add(app.program, app)
            tabs.draw()
            tabs.pack(anchor='n', fill='both', expand=True)
        #self.frame.pack_propagate(False)


    def redraw(self):
        self.frame.destroy()
        self.draw()


    def draw_toolbar(self, app):
        """Draw a toolbar at the bottom of the application(s).
        """
        app.config_button = tk.Button(app, text="Config",
                        command=self.show_config)
        app.config_button.pack(anchor='w', side='left', fill='x')
        app.run_button = tk.Button(app, text="Run %s now" % app.program,
                                            command=app.execute)
        app.run_button.pack(anchor='e', side='left', fill='x', expand=True,
                                                            padx=32)
        app.exit_button = tk.Button(app, text="Exit",
                            command=lambda:self.confirm_exit(app))
        app.exit_button.pack(anchor='e', side='right', fill='x')

        
    def show_config(self):
        """Open the GUI configuration dialog."""
        config = ConfigWindow(self, self.style)
        if config.result:
            self.style = config.result
            print "Saving configuration to", self.inifile
            self.style.save(self.inifile)
            self.style.apply(self)
            self.redraw()

 
    def confirm_exit(self, app):
        if tkMessageBox.askyesno(message="Exit %s now?" % app.program):
            self.quit()

### --------------------------------------------------------------------

if __name__ == '__main__':
    pass


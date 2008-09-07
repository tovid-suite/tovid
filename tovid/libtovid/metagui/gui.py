#! /usr/bin/env python
# gui.py

"""Top-level GUI classes.
"""

__all__ = [
    'Executor',
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
from ScrolledText import ScrolledText

class Executor (Widget):
    """A widget for executing and viewing the output of a command-line program.
    """
    def __init__(self, name='Log'):
        Widget.__init__(self, name)
        self.command = None
        self.log = None
        self.file = None
        self.size = 0


    def execute(self, command):
        """Execute the given command.
        """
        if not isinstance(command, Command):
            raise TypeError("execute() requires a Command instance.")

        self.command = command

        # Create a temporary file to hold command output, and open it
        self.log = tempfile.NamedTemporaryFile(prefix=self.command.program)
        self.file = open(self.log.name, 'r')
        self.size = 0

        # Run the command, directing output to temporary file
        self.command.run_redir(stdout=self.log)

        # Poll until command finishes (or is interrupted)
        self.poll()


    def draw(self, master):
        """Draw the Executor in the given master widget.
        """
        Widget.draw(self, master)
        self.text = ScrolledText(self, width=80, height=32)
        # text area is not editable. ctrl-q and alt-f4 still quit parent
        self.text.bind("<Key>", lambda e: "break")
        self.text.pack(fill='both', expand=True)


    def poll(self):
        """Poll for process completion, and update the output window.
        """
        # Update the output window with tempfile
        if self.file and os.path.getsize(self.log.name) > self.size:
            data = self.file.read()
            if len(data) > 0:
                self.text.insert('end', data)
                self.text.see('end')            

        # Stop if command is done, or poll again
        if self.command.done():
            self.file.close()
            self.write("Done executing!")
        else:
            self.after(100, self.poll)


    def write(self, output):
        """Write literal output to the LogViewer window
        (inserted wherever the cursor currently is).
        """
        self.text.insert('end', output)


### --------------------------------------------------------------------
import tkMessageBox
import tempfile

class Application (Widget):
    """Graphical frontend for a command-line program
    """
    def __init__(self, program, *panels):
        """Define a GUI application frontend for a command-line program.
        
            program: Command-line program that the GUI is a frontend for
            panels:  One or more Panels, containing controls for the given
                     program's options.

        After defining the Application, call run() to show/execute it.
        """
        # Ensure that one or more Panel instances were provided
        ensure_type("Application needs Panel instances", Panel, *panels)

        # Initialize
        Widget.__init__(self)
        self.program = program
        self.panels = list(panels)
        self.showing = False
        self.frame = None


    def draw(self, master):
        """Draw the Application in the given master.
        """
        Widget.draw(self, master)
        # Add a LogViewer as the last panel
        self.panels.append(Executor())
        # Draw all panels as tabs
        self.tabs = Tabs('', *self.panels)
        self.tabs.draw(self)
        self.tabs.pack(anchor='n', fill='x', expand=True)


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

        # Show the Executor
        self.tabs.activate(len(self.panels)-1)
        executor = self.panels[-1]

        # Display the command to be executed
        executor.write("Running command:\n")
        executor.write(str(command) + '\n')

        # Show prompt asking whether to continue
        if tkMessageBox.askyesno(message="Run %s now?" % self.program):
            executor.execute(command)


### --------------------------------------------------------------------
from support import ConfigWindow, Style

class GUI (tk.Tk):
    """GUI with one or more Applications
    """
    def __init__(self, title, width, height, application, **kwargs):
        """Create a GUI for the given application.
        
            title:        Text shown in the title bar
            width:        Initial width of GUI window in pixels
            height:       Initial height of GUI window in pixels
            application:  Application to show in the GUI
        
        Keywords arguments accepted:

            inifile:      Name of an .ini-formatted file with GUI configuration
        """

        # Ensure that one or more Application instances were provided
        ensure_type("GUI needs Application", Application, application)
        self.application = application

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
        self.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit(self.application))
        self.bind('<Control-q>', lambda e, : self.confirm_exit(self.application))


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
        self.application.draw(self.frame)
        self.application.pack(anchor='n', fill='both', expand=True)
        self.draw_toolbar(self.application)
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


"""Top-level GUI classes.
"""

__all__ = [
    'Executor',
    'Application',
    'GUI',
]

import os
import tempfile
import shlex
import subprocess

# Python < 3.x
try:
    import Tkinter as tk
    from ScrolledText import ScrolledText
    from tkFileDialog import \
        (asksaveasfilename, askopenfilename)
    from tkMessageBox import showinfo
# Python 3.x
except ImportError:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from tkinter.filedialog import \
        (asksaveasfilename, askopenfilename)
    from tkinter.messagebox import showinfo

# Absolute imports
from libtovid import cli
# Relative imports
from libtovid.metagui.widget import Widget
from libtovid.metagui.panel import Panel, Tabs
from libtovid.metagui.support import \
    (ConfigWindow, Style, ensure_type, askyesno)
from libtovid.metagui.control import Control


DEFAULT_CONFIG = os.path.expanduser('~/.metagui/config')

class Executor (Widget):
    """Executes a command-line program, shows its output, and allows input.
    """
    def __init__(self, name='Executor'):
        Widget.__init__(self, name)
        self.command = None
        self.outfile = None
        # Defined in draw()
        self.text = None
        self.callback = None
        self.stdin_text = None
        self.kill_button = None
        self.save_button = None


    def draw(self, master):
        """Draw the Executor in the given master widget.
        """
        Widget.draw(self, master)
        # Log output text area
        self.text = ScrolledText(self, width=1, height=1,
            highlightbackground='gray', highlightcolor='gray', relief='groove',
            font=('Courier', 12, 'normal'))
        self.text.pack(fill='both', expand=True)
        # Bottom frame to hold the next four widgets
        frame = tk.Frame(self)
        # Text area for stdin input to the program
        label = tk.Label(frame, text="Input:")
        label.pack(side='left')
        self.stdin_text = tk.Entry(frame)
        self.stdin_text.pack(side='left', fill='x', expand=True)
        self.stdin_text.bind('<Return>', self.send_stdin)
        # Button to stop the process
        self.kill_button = tk.Button(frame, text="Kill", command=self.kill)
        self.kill_button.pack(side='left')
        # Button to save log output
        self.save_button = tk.Button(frame, text="Save log",
                                     command=self.save_log)
        self.save_button.pack(side='left')
        # Pack the bottom frame
        frame.pack(anchor='nw', fill='x')
        # Disable stdin box and kill button until execution starts
        self.stdin_text.config(state='disabled')
        self.kill_button.config(state='disabled')


    def send_stdin(self, event):
        """Send text to the running program's stdin.
        """
        text = self.stdin_text.get()
        # Write the entered text to the command's stdin pipe
        self.command.proc.stdin.write(text + '\n')
        self.command.proc.stdin.flush()
        # Show what was typed in the log window
        self.write(text)
        # Clear the stdin box
        self.stdin_text.delete(0, 'end')


    def execute(self, command, callback=lambda x:x):
        """Execute the given command, and call the given callback when done.
        """
        if not isinstance(command, cli.Command):
            raise TypeError("execute() requires a Command instance.")
        else:
            self.command = command
        if not hasattr(callback, '__call__'):
            raise TypeError("execute() callback must be a function")
        else:
            self.callback = callback

        # Temporary file to hold stdout/stderr from command
        name = self.command.program
        self.outfile = tempfile.NamedTemporaryFile(
            mode='a+', prefix=name + '_output')

        # Run the command, directing stdout/err to the temporary file
        # (and piping stdin so send_stdin will work)
        output = open(self.outfile.name, 'w')
        self.command.run_redir(stdin=subprocess.PIPE,
                               stdout=output,
                               stderr=output)

        # Enable the stdin entry box and kill button
        self.stdin_text.config(state='normal')
        self.kill_button.config(state='normal')

        # Set focus in the stdin entry box
        self.stdin_text.focus_set()

        # Poll until command finishes (or is interrupted)
        self.poll()


    def kill(self):
        """Kill the currently-running command process.
        """
        if self.command:
            self.notify("Killing command: %s" % self.command)
            self.command.kill()


    def poll(self):
        """Poll for process completion, and update the output window.
        """
        # Read from output file and print to log window
        data = self.outfile.read()
        if data:
            # Split on newlines (but not on \r)
            lines = data.split('\n')
            for line in lines:
                self.write(line)

        # Stop if command is done, or poll again
        if self.command.done():
            self.notify("Done executing!")
            self.kill_button.config(state='disabled')
            self.stdin_text.config(state='disabled')
            self.callback()
        else:
            self.after(100, self.poll)


    def notify(self, text):
        """Print a notification message to the Executor.
        Adds newlines and brackets.
        """
        self.write("\n[[ %s ]]\n" % text)



    def write(self, line):
        """Write a line of text to the end of the log.
        If the line contains '\r', overwrite the current line.
        """
        if '\r' in line:
            curline = self.text.index('end-1c linestart')
            for part in line.split('\r'):
                if part.strip(): # Don't overwrite with an empty line
                    self.text.delete(curline, curline + ' lineend')
                    self.text.insert(curline, part.strip())
        else:
            self.text.insert('end', '\n' + line)

        self.text.see('end')


    def clear(self):
        """Clear the log window.
        """
        self.text.delete('1.0', 'end')


    def save_log(self):
        """Save log window contents to a file.
        """
        filename = asksaveasfilename(parent=self,
            title='Save log window output',
            initialfile='%s_output.log' % self.name)
        if filename:
            outfile = open(filename, 'w')
            outfile.write(self.text.get('1.0', 'end'))
            outfile.close()
            self.notify("Output saved to '%s'" % filename)

class Application (Widget):
    """Graphical frontend for a command-line program
    """
    def __init__(self, program, *panels):
        """Define a GUI application frontend for a command-line program.

            program
                Command-line program that the GUI is a frontend for
            panels
                One or more Panels, containing controls for the given
                program's options

        After defining the Application, call run() to show/execute it.
        """
        # Ensure that one or more Panel instances were provided
        ensure_type("Application needs Panel instances", Panel, *panels)

        # Initialize
        Widget.__init__(self)
        self.program = program
        self.showing = False
        self.frame = None
        self.panels = list(panels)
        # Add a LogViewer as the last panel
        self.executor = Executor("Log")
        self.panels.append(self.executor)
        # Defined in draw()
        self.tabs = None
        # Defined in draw_toolbar
        self.toolbar = None


    def draw(self, master):
        """Draw the Application in the given master.
        """
        Widget.draw(self, master)
        # Draw all panels as tabs
        self.tabs = Tabs('', *self.panels)
        self.tabs.draw(self)
        self.tabs.pack(anchor='n', fill='both', expand=True)


    def draw_toolbar(self, config_function, exit_function):
        """Draw a toolbar at the bottom of the application.
        """
        self.toolbar = Widget()
        self.toolbar.draw(self)
        # Create the buttons
        config_button = tk.Button(self.toolbar, text="Config",
                                  command=config_function)
        run_button = tk.Button(self.toolbar, text="Run %s now" % self.program,
                               command=self.execute)
        save_button = tk.Button(self.toolbar, text="Save script",
                                command=self.save_script)
        load_button = tk.Button(self.toolbar, text="Load script",
                                command=self.load_script)
        exit_button = tk.Button(self.toolbar, text="Exit",
                                command=exit_function)
        # Pack the buttons
        config_button.pack(anchor='w', side='left', fill='x')
        load_button.pack(anchor='w', side='left', fill='x')
        run_button.pack(anchor='w', side='left', fill='x', expand=True)
        save_button.pack(anchor='w', side='left', fill='x')
        exit_button.pack(anchor='e', side='right', fill='x')
        # Pack the toolbar
        self.toolbar.pack(fill='x', anchor='sw')


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
        self.toolbar.disable()
        self.executor.clear()

        # Get args and assemble command-line
        args = self.get_args()
        command = cli.Command(self.program, *args)

        # Display the command to be executed
        self.executor.notify("Running command: " + str(command))

        # Show the Executor panel
        self.tabs.activate(self.executor)

        # Show prompt asking whether to continue
        if askyesno(message="Run %s now?" % self.program):
            self.executor.execute(command, self.toolbar.enable)
        else:
            self.executor.notify("Cancelled.")
            self.toolbar.enable()


    def save_script(self):
        """Save the current command as a bash script.
        """
        # TODO: Make initialfile same as last saved script, if it exists
        filename = asksaveasfilename(parent=self,
            title="Select a filename for the script",
            initialfile='%s_commands.bash' % self.program)
        if filename:
            args = self.get_args()
            command = cli.Command(self.program, *args)
            outfile = open(filename, 'w')
            outfile.write(command.to_script())
            outfile.close()
            showinfo(title="Script saved",
                     message="Saved '%s'" % filename)


    def load_script(self):
        """Load current Control settings from a text file.
        """
        filename = askopenfilename(parent=self,
            title="Select a shell script or text file to load")
        if not filename:
            return

        # Clear all controls of existing values
        for control in Control.all.values():
            control.reset()
        # Read nonempty, non-comment lines from the given file
        infile = open(filename, 'r')
        lines = [line.strip() for line in infile.readlines()
                 if line.strip()
                 and not line.strip().startswith('#')]
        infile.close()
        # Join backslash-escaped lines to form the complete command
        command = ''
        for line in lines:
            if line.endswith('\\'):
                command += line.rstrip('\\')
        # Parse the command to find options matching Controls in the GUI
        options = Control.all.keys()
        tokens = shlex.split(command)
        # Ensure the expected program is being run
        program = tokens.pop(0)
        if program != self.program:
            print("This script runs '%s', expected '%s'" %
                  (program, self.program))
        control = None
        while tokens:
            tok = tokens.pop(0)
            if tok not in options:
                print("Unrecognized token: %s" % tok)
            else:
                print("Found option: %s" % tok)
                control = Control.by_option(tok)
                if control.vartype == bool:
                    print("  Setting flag to True")
                    control.set(True)
                    control.enabler()
                elif control.vartype == list:
                    items = []
                    while tokens and not tokens[0].startswith('-'):
                        items.append(tokens.pop(0))
                    print("  Setting list to: %s" % items)
                    control.set(items)
                elif control.vartype in (int, float, str):
                    value = tokens.pop(0)
                    print("  Setting value to: %s" % value)
                    control.set(control.vartype(value))

        print("Done reading '%s'" % filename)


class GUI (tk.Tk):
    """GUI with one or more Applications
    """
    def __init__(self, title, width, height, application, **kwargs):
        """Create a GUI for the given application.

            title
                Text shown in the title bar
            width
                Initial width of GUI window in pixels
            height
                Initial height of GUI window in pixels
            application
                Application to show in the GUI

        Keywords arguments accepted:

            inifile:      Name of an .ini-formatted file with GUI configuration
        """
        tk.Tk.__init__(self)

        # Ensure that one or more Application instances were provided
        ensure_type("GUI needs Application", Application, application)
        self.application = application

        # Set main window attributes
        self.geometry("%dx%d" % (width, height))
        self.title(title)
        self.width = width
        self.height = height

        # Get style configuration from INI file
        if 'inifile' in kwargs:
            self.inifile = kwargs['inifile']
        else:
            self.inifile = DEFAULT_CONFIG
        self.style = Style()
        if os.path.exists(self.inifile):
            print("Loading style from config file: '%s'" % self.inifile)
            self.style.load(self.inifile)
        else:
            print("Creating config file: '%s'" % self.inifile)
            self.style.save(self.inifile)

        # Show hidden file option in file dialogs
        self.tk.call('namespace', 'import', '::tk::dialog::file::')
        self.tk.call('set', '::tk::dialog::file::showHiddenBtn',  '1')
        self.tk.call('set', '::tk::dialog::file::showHiddenVar',  '0')

        # Handle user closing window with window manager or ctrl-q
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.bind('<Control-q>', self.confirm_exit)


    def run(self):
        """Run the GUI.
        """
        self.draw()
        # Enter the main event handler
        self.mainloop()


    def draw(self):
        """Draw widgets.
        """
        self.style.apply(self)
        self.frame = tk.Frame(self, width=self.width, height=self.height)
        self.frame.pack(fill='both', expand=True)
        self.resizable(width=True, height=True)
        # Draw the application
        self.application.draw(self.frame)
        self.application.pack(anchor='n', fill='both', expand=True)
        # Draw the toolbar
        self.application.draw_toolbar(self.show_config, self.confirm_exit)


    def redraw(self):
        """Destroy and re-draw the GUI.
        """
        self.frame.destroy()
        self.draw()


    def show_config(self):
        """Open the GUI configuration dialog.
        """
        config = ConfigWindow(self, self.style)
        if config.result:
            self.style = config.result
            print("Saving configuration to: '%s'" % self.inifile)
            self.style.save(self.inifile)
            self.style.apply(self)
            self.redraw()


    def confirm_exit(self, evt=None):
        """Exit the GUI, with confirmation prompt.
        """
        if askyesno(message="Exit?"):
            self.quit()



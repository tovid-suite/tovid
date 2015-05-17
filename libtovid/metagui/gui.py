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
from sys import exit, argv

# Python < 3.x
try:
    import Tix
    import Tkinter as tk
    from ScrolledText import ScrolledText
    from tkMessageBox import showinfo, showerror
    from tkFileDialog import (
      asksaveasfilename, askopenfilename
      )

# Python 3.x
except ImportError:
    import tkinter as tk
    import tkinter.tix as Tix
    from tkinter.scrolledtext import ScrolledText
    from tkinter.messagebox import showinfo, showerror
    from tkinter.filedialog import (
      asksaveasfilename, askopenfilename
      )

from libtovid import cli
from libtovid.metagui.widget import Widget
from libtovid.metagui.panel import Panel, Tabs
from libtovid.metagui.control import Control, NoSuchControl
from libtovid.metagui.support import (
  ConfigWindow, Style, ensure_type, askyesno, get_photo_image, show_icons
  )


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
            font=('Nimbus Sans L', 12, 'normal'))
        self.text.pack(fill='both', expand=True)
        # Bottom frame to hold the next four widgets
        self.frame = tk.Frame(self)
        # Text area for stdin input to the program
        label = tk.Label(self.frame, text="Input:")
        label.pack(side='left')
        self.stdin_text = tk.Entry(self.frame)
        self.stdin_text.pack(side='left', fill='x', expand=True)
        self.stdin_text.bind('<Return>', self.send_stdin)
        # Button to stop the process
        self.kill_button = tk.Button(self.frame, text="Kill", command=self.kill)
        self.kill_button.pack(side='left')
        # Button to save log output
        self.save_button = tk.Button(self.frame, text="Save log",
                                     command=self.save_log)
        self.save_button.pack(side='left')
        # Pack the bottom frame
        self.frame.pack(anchor='nw', fill='x')
        # Disable stdin box and kill button until execution starts
        self.stdin_text.config(state='disabled')
        self.kill_button.config(state='disabled')


    def send_stdin(self, event):
        """Send text to the running program's stdin.
        """
        text = self.stdin_text.get()
        # Write the entered text to the command's stdin pipe
        #self.command.proc.stdin.write(text + '\n')
        # python 3 compatibility
        self.command.proc.stdin.write(bytearray(text + "\n", "ascii"))
        self.command.proc.stdin.flush()
        # Show what was typed in the log window
        self.write(text)
        # Clear the stdin box
        self.stdin_text.delete(0, 'end')


    def execute(self, command, callback=None):
        """Execute the given `~libtovid.cli.Command`, and call the given callback when done.
        """
        if not isinstance(command, cli.Command):
            raise TypeError("execute() requires a Command instance.")
        if not callable(callback):
            raise TypeError("execute() callback must be callable")

        self.command = command
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
        self.outfile.close()


    def poll(self):
        """Poll for process completion, and update the output window.
        """
        # Read from output file and print to log window
        try:
            data = self.outfile.read()
            if data:
                # Split on newlines (but not on \r)
                lines = data.split('\n')
                for line in lines:
                    self.write(line)
        except ValueError:
            pass

        # Stop if command is done, or poll again
        if self.command.done():
            self.notify("Done executing!")
            self.kill_button.config(state='disabled')
            self.stdin_text.config(state='disabled')
            self.callback()
            self.outfile.close()
        else:
            self.after(100, self.poll)


    def notify(self, text):
        """Print a notification message to the Executor.
        Adds newlines and brackets.
        """
        self.write("\n[[ %s ]]\n" % text)


    def write(self, line):
        """Write a line of text to the end of the log.
        If the line contains ``\\r``, overwrite the current line.
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


from textwrap import dedent
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
        self.master = master
        # Draw all panels as tabs
        self.tabs = Tabs('', *self.panels)
        self.tabs.draw(self)
        self.tabs.pack(anchor='n', fill='both', expand=True)
        # need to wait until draw is called before setting this variable
        self.script = tk.StringVar()
        self.script.set('')


    def draw_toolbar(self, config_function, exit_function):
        """Draw a toolbar at the bottom of the application.
        """
        self.toolbar = Widget()
        self.toolbar.draw(self)
        # Create the buttons
        config_button = tk.Button(
            self.toolbar, text="Config", command=config_function)
        run_button = tk.Button(
            self.toolbar, text="Run %s now" % self.program, command=self.execute)
        save_button = tk.Button(
            self.toolbar, text="Save script", command=self.prompt_save_script)
        load_button = tk.Button(
            self.toolbar, text="Load script", command=self.prompt_load_script)
        exit_button = tk.Button(
            self.toolbar, text="Exit", command=exit_function)
        # Pack the buttons
        config_button.pack(anchor='w', side='left', fill='x')
        load_button.pack(anchor='w', side='left', fill='x')
        run_button.pack(anchor='w', side='left', fill='x', expand=True)
        save_button.pack(anchor='w', side='left', fill='x')
        exit_button.pack(anchor='e', side='right', fill='x')
        # Pack the toolbar
        self.toolbar.pack(fill='x', anchor='sw')
        # hack to allow wizard to use less clicks and remove uneeded commmands
        if os.getenv('METAGUI_WIZARD'):
            save_button.pack_forget()
            load_button.pack_forget()
            load_button.pack(anchor='w', side='left', fill='x', expand=True)
            save_button.pack(anchor='w', side='left', fill='x', expand=True)
            save_button.config(command=self.save_exit, text='Save to wizard')
            run_button.pack_forget()
            #exit_button.pack_forget()


    def get_args(self):
        """Get a list of all command-line arguments from all panels.
        """
        args = []
        for panel in self.panels:
            args += panel.get_args()
        return args


    def set_args(self, args):
        """Load application settings from a list of command-line arguments.
        The list of args is modified in-place; if all args are successfully
        parsed and loaded, the list will be empty when this method returns.
        """
        for panel in self.panels:
            panel.set_args(args)


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

    def set_scriptname(self, name):
        """Set script filename.  Called externally, this sets the variable
        that used used for save_exit() as well as the 'initial file' for
        prompt_save_script().
        """
        self.script.set(name)


    def prompt_save_script(self):
        """Prompt for a script filename, then save the current
        command to that file.
        """
        # TODO: Make initialfile same as last saved script, if it exists
        filename = asksaveasfilename(parent=self,
            title="Select a filename for the script",
            #initialfile='%s_commands.bash' % self.program)
            initialfile=self.script.get() or '%s_commands.bash' % self.program)

        if not filename:
            return

        try:
            self.save_script(filename)
        except:
            showerror(title="Error", message="Failed to save '%s'" % filename)
            raise
        else:
            saved_script = os.path.split(filename)[1]
            showinfo(title="Script saved", message="Saved '%s'" % filename)


    def save_exit(self):
        """Save current command to script and exit, without prompt
        """
        # hack for titleset wizard to get gui's screen position
        from sys import stderr
        stderr.write("%s %+d%+d" 
          %('gui position', self._root().winfo_x(), self._root().winfo_y()))

        default = os.getcwd() + os.path.sep + '%s_commands.bash' % self.program
        filename = self.script.get() or default
        self.save_script(filename)
        exit()


    def prompt_load_script(self):
        """Prompt for script filename; reload gui with current Control settings
        """
        #"""Prompt for a script filename, then load current Control settings
        #from that file.
        #"""
        # Hack: This is broken (commented section), presumably because of
        # load_args limitations. This hack fixes it for libtovid, but does not
        # belong in metagui.  So refactor this when load_args is fixed.
        # see https://github.com/tovid-suite/tovid/issues/121
        filename = askopenfilename(parent=self,
            title="Select a shell script or text file to load",
            filetypes=[('Shell scripts', '*.sh *.bash'),
            ('All files', '*.*')])

        if not filename:
            return
        # begin Hack
        geometry = self._root().winfo_x(), self._root().winfo_y()
        command = argv[0]
        try:
            cmd = command, '--position', '+%s+%s' %geometry, filename
            os.execlp(cmd[0], *cmd)
        except:
            showerror(title="Error", message="Failed load '%s'" %filename)
            raise
        #try:
        #    self.reset()
        #    self.load_script(filename)
        #except:
        #    showerror(title="Error", message="Failed to load '%s')
        #    raise
        #else:
        #    showinfo(title="Script loaded", message="Loaded '%s'" % filename)


    def save_script(self, filename):
        """Save the current command as a bash script.
        """
        args = self.get_args()
        command = cli.Command(self.program, *args)
        outfile = open(filename, 'w')
        outfile.write(command.to_script())
        outfile.close()


    def reset(self):
        """Reset all controls back to their defaults.
        """
        # Clear all controls of existing values
        for control in Control.all.values():
            control.reset()


    def load_script(self, filename):
        # this is now disabled and its functionality passed to guis.helpers.py
        # see https://github.com/tovid-suite/tovid/issues/121
        pass
        #"""Load current Control settings from a text file.
        #"""
        # Read lines from the file and reassemble the command
        #command = ''
        #for line in open(filename, 'r'):
        #    line = line.strip()
            # Discard comment lines and PATH assignment
        #    if line and not (line.startswith('#') or line.startswith('PATH=')):
        #        command += line.rstrip('\\')
        # Split the full command into arguments, according to shell syntax
        #args = shlex.split(command)

        # Ensure the expected program is being run
        #program = args.pop(0)
        #if program != self.program:
        #    raise ValueError("This script runs '%s', expected '%s'" %
        #          (program, self.program))
        # Load the rest of the arguments
        #self.load_args(args)
        #print("Done reading '%s'" % filename)


    # TODO: Relocate all this stuff into Control and its subclasses
    def load_args(self, args):
        """Load settings from a list of command-line arguments.
        """
        # Examine each arg to find those that are option strings
        while args:
            arg = args.pop(0)
            # See if this is a valid option string; if not,
            # print an error and continue
            try:
                control = Control.by_option(arg)
            except NoSuchControl:
                print("Unrecognized argument: %s" % arg)
                continue
            else:
                print("Found option: %s" % arg)

            # If this control expects a boolean option,
            # it's probably a flag
            if control.vartype == bool:
                print("  Setting flag to True")
                control.set(True)
                control.enabler()

            # If this control expects a list, get all
            # the arguments for the list and set them
            elif control.vartype == list:
                items = []
                while args and not args[0].startswith('-'):
                    items.append(args.pop(0))
                print("  Setting list to: %s" % items)
                control.set(items)

            # Otherwise, set a single-value option
            elif control.vartype in (int, float, str):
                value = args.pop(0)
                print("  Setting value to: %s" % value)
                control.set(control.vartype(value))


# This uses Tix.Tk as a base class, to allow Tix widgets within
# (since for some reason a Tix.ComboBox doesn't like to be inside
# a Tkinter.Tk root window)
class GUI (Tix.Tk):
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

            inifile
                Name of an .ini-formatted file with GUI configuration
            icon
                Full path to an image to use as the titlebar icon
            position
                position on screen: '+X+Y'
        """
        Tix.Tk.__init__(self)

        # Ensure that one or more Application instances were provided
        ensure_type("GUI needs Application", Application, application)
        self.application = application

        # Get keyword arguments
        self.inifile = kwargs.get('inifile', DEFAULT_CONFIG)
        self.icon_file = kwargs.get('icon', None)
        self.position = kwargs.get('position', '')

        # Set main window attributes
        self.geometry("%dx%d%s" % (width, height, self.position))
        self.title(title)
        self.width = width
        self.height = height

        self.style = Style()
        if os.path.exists(self.inifile):
            print("Loading style from the config file: '%s'" % self.inifile)
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


    def run(self, args=None, script=''):
        """Run the GUI and enter the main event handler.
        This function does not return until the GUI is closed.
        args: arguments to the programe being run
        script: a filename to save the GUI command output to
        """
        self.draw()
        
        if args:
            # If first argument looks like a filename, load
            # a script from that file
            if os.path.isfile(args[0]):
                filename = args.pop(0)
                print("Loading script file '%s'" % filename)
                try:
                    self.application.load_script(filename)
                except:
                    print("!!! Failed to load '%s'" % filename)
                    raise
                else:
                    print(":-) Successfully loaded '%s'" % filename)

            # If more args remain, load those too
            if args:
                self.application.load_args(args)
            # if a script/project name was provided, set it in 'application'
        if script:
            self.application.set_scriptname(script)

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
        # Set the application icon, if provided
        if self.icon_file:
            show_icons(self, self.icon_file)


    def show_config(self):
        """Open the GUI configuration dialog.
        """
        config = ConfigWindow(self, self.style)
        if config.result:
            self.style = config.result
            print("Saving configuration to: '%s'" % self.inifile)
            self.style.save(self.inifile)
            showinfo("Configuration saved",
                "Saved configuration to '%s'. Please restart the GUI for the"
                " changes to take effect. You may want to 'Save script' before"
                " quitting." % self.inifile)



    def confirm_exit(self, event=None):
        """Exit the GUI, with confirmation prompt.
        """
        # Hack to sync titleset wizard's position with exiting GUI's position
        if os.getenv('METAGUI_WIZARD'):
            from sys import stderr
            stderr.write("%s %+d%+d" 
            %('gui position', self._root().winfo_x(), self._root().winfo_y()))
        if askyesno(message="Exit?"):
            self.quit()



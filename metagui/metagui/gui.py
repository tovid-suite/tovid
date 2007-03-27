#! /usr/bin/env python
# gui.py

__all__ = [
    # Main GUI creation interface
    'Panel',
    'HPanel',
    'VPanel',
    'Dropdowns',
    'Drawer',
    'Application',
    'GUI',
    'Style']

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
        if type(title) != str:
            raise TypeError("First argument to Panel must be a text label.")
        self.title = title
        self.contents = []
        for item in contents:
            if isinstance(item, Control) \
               or isinstance(item, Panel) \
               or isinstance(item, Drawer):
                self.contents.append(item)
            else:
                raise "Panel may only contain Controls, Panels,"\
                      " or Drawers (got %s instead)" % type(item)

    def draw(self, master, side='top'):
        """Draw Controls in a Frame with the given master.
        """
        if self.title:
            tk.LabelFrame.__init__(self, master, text=self.title,
                                   padx=8, pady=8)
        else:
            tk.LabelFrame.__init__(self, master, bd=0, text='',
                                   padx=8, pady=8)
        for item in self.contents:
            item.draw(self)
            item.pack(side=side, anchor='nw', fill='x', expand=True)

    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for item in self.contents:
            args += item.get_args()
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
from metagui.support import ComboBox
from metagui.control import Control
from metagui.odict import Odict

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
        for control in contents:
            if not isinstance(control, Control):
                # TODO: Make this sentence untrue:
                raise TypeError("Dropdowns panel currently only supports"\
                                " Control subclasses (no nested Panels"\
                                " or Drawers).")
            self.controls[control.option] = control
            
    def draw(self, master):
        if self.title:
            tk.LabelFrame.__init__(self, master, text=self.title,
                                   padx=8, pady=8)
        else:
            tk.LabelFrame.__init__(self, master, bd=0, text='',
                                   padx=8, pady=8)
        choices = self.controls.keys()
        self.chosen = tk.StringVar()
        self.chooser = ComboBox(self, choices, variable=self.chosen,
                                command=self.choose_new)
        self.chooser.pack(fill='both', expand=True)

    def choose_new(self, event=None):
        """Create and display the chosen control."""
        self.chooser.pack_forget()
        # Put control and remove button in a frame
        frame = tk.Frame(self)
        button = tk.Button(frame, text="X",
                           command=lambda:self.remove(frame))
        button.pack(side='left')
        control = self.controls[self.chosen.get()]
        control.draw(frame)
        control.pack(side='left', fill='x', expand=True)
        frame.pack(fill='x', expand=True)
        self.chooser.pack()

    def remove(self, widget):
        """Remove a widget from the interface."""
        assert isinstance(widget, tk.Widget)
        widget.pack_forget()
        widget.destroy()

    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for item in self.contents:
            # Ignore errors from uninitialized controls
            # (the draw() before get() thing)
            try:
                args += item.get_args()
            except:
                pass
        return args


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
    
    def get_args(self):
        return self.panel.get_args()

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
        print "Running command:", str(command)
        print "(not really)"

### --------------------------------------------------------------------

class GUI (tk.Tk):
    """GUI with one or more Applications
    """
    def __init__(self, title, applications, width=500, height=400,
                 style=None):
        """Create a GUI for the given applications.
        
            title:        Text shown in the title bar
            applications: List of Applications to included in the GUI
        """
        tk.Tk.__init__(self)
        self.title(title)
        self.apps = applications
        self.width = width
        self.height = height
        self.style = style or Style()

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
        #self.frame = tk.Frame(self, width=self.width, height=self.height)
        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=True)
        self.resizable(width=True, height=True)
        # Single-application GUI
        if len(self.apps) == 1:
            app = self.apps[0]
            app.draw(self.frame)
            app.pack(anchor='n', fill='both', expand=True)
        # Multi-application (tabbed) GUI
        else:
            tabs = Tabs(self.frame, 'top', ('Helvetica', 14, 'bold'))
            for app in self.apps:
                app.draw(tabs)
                tabs.add(app.program, app)
            tabs.draw()
            tabs.pack(anchor='n', fill='both', expand=True)
        #self.frame.pack_propagate(False)
        
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

class Style:
    """Generic widget style definitions."""
    def __init__(self,
                 bgcolor='white',
                 fgcolor='grey',
                 textcolor='black',
                 font=('Helvetica', 12),
                 relief='groove'):
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.textcolor = textcolor
        self.font = font
        self.relief = relief

    def apply(self, root):
        """Apply the current style to the given Tkinter root window."""
        root.option_clear()
        # Background color
        root.option_add("*Scale.troughColor", self.bgcolor)
        root.option_add("*Spinbox.background", self.bgcolor)
        root.option_add("*Entry.background", self.bgcolor)
        root.option_add("*Listbox.background", self.bgcolor)
        # Relief
        root.option_add("*Entry.relief", self.relief)
        root.option_add("*Spinbox.relief", self.relief)
        root.option_add("*Listbox.relief", self.relief)
        root.option_add("*Button.relief", self.relief)
        root.option_add("*Menu.relief", self.relief)
        # Font
        root.option_add("*font", self.font)
        root.option_add("*Radiobutton.selectColor", "#8888FF")
        root.option_add("*Checkbutton.selectColor", "#8888FF")
        # Mouse-over effects
        root.option_add("*Button.overRelief", 'raised')
        root.option_add("*Checkbutton.overRelief", 'groove')
        root.option_add("*Radiobutton.overRelief", 'groove')

### --------------------------------------------------------------------


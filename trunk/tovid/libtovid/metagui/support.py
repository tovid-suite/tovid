#! /usr/bin/env python
# support.py

"""Supporting classes for metagui"""

__all__ = [
    'ListVar',
    'ScrollList',
    'DragList',
    'ComboBox',
    'FontChooser',
    'ConfigWindow',
    'ScrolledWindow',
    'Style']

import os
import Tkinter as tk
import tkSimpleDialog

### --------------------------------------------------------------------

class ListVar (tk.Variable):
    """A tk Variable suitable for associating with Listboxes.
    """
    def __init__(self, master=None, items=None):
        """Create a ListVar with a given master and initial list of items.
        """
        tk.Variable.__init__(self, master)
        if items:
            self.set(items)
    
    def __getitem__(self, index):
        """Get a list value using list-index syntax (listvar[index]).
        """
        return self.get()[index]

    def __setitem__(self, index, value):
        """Set a list value using list-index syntax (listvar[index] = value).
        """
        current = self.get()
        current[index] = value
        self.set(current)

    def get(self):
        return list(tk.Variable.get(self))
    
    def set(self, new_list):
        tk.Variable.set(self, tuple(new_list))

    def remove(self, item):
        """Remove the item from the list, if it exists.
        """
        items = self.get()
        items.remove(item)
        self.set(items)

    def append(self, item):
        """Append an item to the list.
        """
        items = self.get()
        self.set(items + [item])

### --------------------------------------------------------------------

class ScrollList (tk.Frame):
    """A Listbox with a scrollbar.

    Similar to a tk.Listbox, a ScrollList shows a list of items. tk.Variables
    may be associated with both the list of available choices, and the one
    that is currently chosen/highlighted.
    """
    def __init__(self, master=None, choices=None,
                 chosen=None, command=None):
        """Create a ScrollList widget.
        
            master:   Tkinter widget that will contain the ScrollList
            choices:  ListVar or Python list of choices to show in listbox
            chosen:   Tk StringVar to store currently selected choice in
            command:  Function to call when a list item is clicked
        """
        tk.Frame.__init__(self, master)
        if type(choices) == list:
            choices = ListVar(self, choices)
        self.choices = choices or ListVar()
        self.chosen = chosen or tk.StringVar()
        self.command = command
        self.curindex = 0
        self.linked = None
        # Draw listbox and scrollbar
        self.scrollbar = tk.Scrollbar(self, orient='vertical',
                                      command=self.scroll)
        self.listbox = tk.Listbox(self, width=30, listvariable=self.choices,
                                  yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='left', fill='y')
        self.listbox.bind('<Button-1>', self.select)

    def add(self, *values):
        """Add the given values to the list.
        """
        for value in values:
            self.listbox.insert('end', value)

    def insert(self, index, *values):
        """Insert values at a given index.
        """
        self.listbox.insert(index, *values)

    def delete(self, first, last=None):
        """Delete values in a given index range (first, last), not including
        last itself. If last is None, delete only the item at first index.
        """
        self.listbox.delete(first, last=None)

    def scroll(self, *args):
        """Event handler when the list is scrolled.
        """
        apply(self.listbox.yview, args)
        if self.linked:
            apply(self.linked.listbox.yview, args)

    def select(self, event):
        """Event handler when an item in the list is selected.
        """
        self.curindex = self.listbox.nearest(event.y)
        self.chosen.set(self.listbox.get(self.curindex))

    def get(self):
        """Return a list of all entries in the list.
        """
        return self.choices.get()
    
    def set(self, values):
        """Set the list values to those given.
        """
        self.choices.set(values)

    def swap(self, index_a, index_b):
        """Swap the element at index_a with the one at index_b.
        """
        item_a = self.choices[index_a]
        item_b = self.choices[index_b]
        self.choices[index_a] = item_b
        self.choices[index_b] = item_a

    def link(self, scrolllist):
        """Link this list to another, so they scroll in unison."""
        if not isinstance(scrolllist, ScrollList):
            raise TypeError("Can only link to a ScrollList.")
        self.linked = scrolllist

### --------------------------------------------------------------------

class DragList (ScrollList):
    """A scrollable listbox with drag-and-drop support"""
    def __init__(self, master=None, choices=None,
                 chosen=None, command=None):
        """Create a DragList widget.
        
            master:   Tkinter widget that will contain the DragList
            choices:  ListVar or Python list of choices to show in listbox
            chosen:   Tk StringVar to store currently selected choice in
            command:  Function to call when a list item is clicked
        """
        ScrollList.__init__(self, master, choices, chosen, command)
        # Add bindings for drag/drop
        self.listbox.bind('<Button-1>', self.select)
        self.listbox.bind('<B1-Motion>', self.drag)
        self.listbox.bind('<ButtonRelease-1>', self.drop)

    def select(self, event):
        """Event handler when an item in the list is selected.
        """
        # Set currently selected item and change the cursor to a double-arrow
        ScrollList.select(self, event)
        if self.linked:
            self.linked.curindex = self.curindex
        self.config(cursor="double_arrow")
    
    def drag(self, event):
        """Event handler when an item in the list is dragged.
        """
        # If item is dragged to a new location, delete/insert
        loc = self.listbox.nearest(event.y)
        if loc != self.curindex:
            #item = self.listbox.get(self.curindex)
            #self.listbox.delete(self.curindex)
            #self.listbox.insert(loc, item)
            self.swap(self.curindex, loc)
            # Drag in linked listbox
            if self.linked:
                self.linked.swap(self.curindex, loc)
                self.linked.curindex = loc
            self.curindex = loc
    
    def drop(self, event):
        """Event handler when an item in the list is "dropped".
        """
        # Change the mouse cursor back to the default arrow.
        self.config(cursor="")

### --------------------------------------------------------------------

class ComboBox (tk.Frame):
    """A dropdown menu with several choices.
    """
    def __init__(self, master, choices=None,
                 variable=None, command=None):
        """Create a ComboBox.
            
            master:     Tk Widget that will contain the ComboBox
            choices:    ListVar or Python list of available choices
            variable:   Tk StringVar to store currently selected choice in
            command:    Function to call after an item in the list is chosen
        """
        tk.Frame.__init__(self, master)
        if type(choices) == list:
            choices = ListVar(self, choices)
        self.choices = choices or ListVar()
        self.variable = variable or tk.StringVar()
        self.command = command
        self._draw()

    def _draw(self):
        """Draw and configure contained widgets.
        """
        # Text and button
        self.text = tk.Entry(self, textvariable=self.variable)
        self.text.grid(row=0, column=0)
        self.button = tk.Button(self, text="<", command=self.open)
        self.button.grid(row=0, column=1)

        # Dropdown list, displayed when button is clicked
        self.dropdown = tk.Toplevel(self)
        # Don't draw window manager frame around the dropdown
        self.dropdown.wm_overrideredirect(1)
        # Hide until later
        self.dropdown.withdraw()

        # List of choices
        self.chooser = tk.Listbox(self.dropdown, background='white',
                                  listvariable=self.choices)
        #for choice in self.choices:
        #    self.chooser.insert('end', choice)
        self.chooser.bind('<Button-1>', self.choose)
        self.chooser.grid()
    
    def open(self):
        """Open/close a panel showing the list of choices.
        """
        if self.dropdown.winfo_viewable():
            self.dropdown.withdraw()
        else:
            # Align dropdown list with the text box
            x = self.text.winfo_rootx()
            y = self.text.winfo_rooty()
            self.dropdown.wm_geometry("+%d+%d" % (x, y))
            # Show list
            self.dropdown.deiconify()
    
    def choose(self, event=None):
        """Make a selection from the list, and set the variable.
        """
        self.curindex = self.chooser.nearest(event.y)
        self.variable.set(self.chooser.get(self.curindex))
        self.dropdown.withdraw()
        # Callback, if any
        if self.command:
            self.command()

### --------------------------------------------------------------------

class FontChooser (tkSimpleDialog.Dialog):
    """A widget for choosing a font"""
    def __init__(self, master=None):
        tkSimpleDialog.Dialog.__init__(self, master, "Font chooser")

    def get_fonts(self):
        """Return a list of font names available in ImageMagick.
        """
        find = "convert -list type | sed '/Path/,/---/d' | awk '{print $1}'"
        return [line.rstrip('\n') for line in os.popen(find).readlines()]

    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        tk.Label(master, text="Available fonts").pack(side='top')
        self.fontlist = ScrollList(master, self.get_fonts())
        self.fontlist.pack(side='top', fill='both', expand=True)
        # Return widget with initial focus
        return self.fontlist
    
    def apply(self):
        """Set the selected font.
        """
        self.result = self.fontlist.chosen.get()

### --------------------------------------------------------------------
from ConfigParser import ConfigParser

class Style:
    """Generic widget style definitions."""
    def __init__(self,
                 bgcolor='white',
                 fgcolor='grey',
                 textcolor='black',
                 font=('Helvetica', 10, 'normal'),
                 relief='groove'):
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.textcolor = textcolor
        self.font = font
        self.relief = relief

    def apply(self, root):
        """Apply the current style to the given Tkinter root window."""
        assert isinstance(root, tk.Tk)
        root.option_clear()
        # Font
        root.option_add("*font", self.font)
        # Background color
        root.option_add("*Scale.troughColor", self.bgcolor)
        root.option_add("*Spinbox.background", self.bgcolor)
        root.option_add("*Entry.background", self.bgcolor)
        root.option_add("*Listbox.background", self.bgcolor)
        # Button colors
        root.option_add("*Radiobutton.selectColor", "#8888FF")
        root.option_add("*Checkbutton.selectColor", "#8888FF")
        # Relief
        root.option_add("*Entry.relief", self.relief)
        root.option_add("*Spinbox.relief", self.relief)
        root.option_add("*Listbox.relief", self.relief)
        root.option_add("*Button.relief", self.relief)
        root.option_add("*Menu.relief", self.relief)
        # Mouse-over effects
        root.option_add("*Button.overRelief", 'raised')
        root.option_add("*Checkbutton.overRelief", 'groove')
        root.option_add("*Radiobutton.overRelief", 'raised')

    def save(self, filename):
        """Save the current style settings to an .ini-formatted config file.
        """
        # Load existing config file
        config = ConfigParser()
        config.read(filename)

        # Save font settings
        if 'font' not in config.sections():
            config.add_section('font')
        family, size, style = self.font
        config.set('font', 'family', family)
        config.set('font', 'size', size)
        config.set('font', 'style', style)
        
        # TODO: Save other style settings
        
        # Yuck...
        outfile = open(filename, 'w')
        config.write(outfile)
        outfile.close()

    def load(self, filename):
        """Load style settings from an .ini-formatted config file.
        """
        config = ConfigParser()
        config.read(filename)
        font = dict(config.items('font'))
        self.font = (font['family'], int(font['size']), font['style'])

### --------------------------------------------------------------------
from tkMessageBox import showinfo

class ConfigWindow (tkSimpleDialog.Dialog):
    """Configuration settings dialog box.
    """
    def __init__(self, master=None, style=None):
        """Create and display a configuration window.
        
            inifile:  An .ini-style file to load/save settings from
        """
        self.style = style or Style()
        tkSimpleDialog.Dialog.__init__(self, master, "Configuration")

    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        # Font family
        tk.Label(master, text="Font family").pack(side='top')
        self.fontfamily = ComboBox(master,
                                   choices=['Helvetica', 'Courier', 'Times'])
        self.fontfamily.pack(side='top', fill='both', expand=True)
        # Font size
        tk.Label(master, text="Font size").pack(side='top')
        self.fontsize = ComboBox(master, choices=[8, 10, 12, 15, 18, 24])
        self.fontsize.pack(side='top')
        # Font style
        tk.Label(master, text="Font style").pack(side='top')
        self.fontstyle = ComboBox(master, choices=['normal', 'bold'])
        self.fontstyle.pack(side='top')
        # Use initial values loaded from .ini file
        family, size, style = self.style.font
        self.fontfamily.variable.set(family)
        self.fontsize.variable.set(size)
        self.fontstyle.variable.set(style)
        # Return widget with initial focus
        return self.fontfamily

    def apply(self):
        """Apply the selected configuration settings.
        """
        self.style.font = (self.fontfamily.variable.get(),
                           self.fontsize.variable.get(),
                           self.fontstyle.variable.get())
        self.result = self.style

### --------------------------------------------------------------------

class ScrolledWindow (tk.Tk):
    """A top-level window with scrollbars.
    
    To use as a container for other widgets, do:
    
        window = ScrolledWindow()
        button = tk.Button(window.frame, text="Click me", ...)
        entry = tk.Entry(window.frame, ...)
        window.draw()
    
    That is, use window.frame as the master of child widgets, instead of
    window itself. (TODO: Eliminate this requirement.)
    """
    def __init__(self, width, height):
        tk.Tk.__init__(self)
        self.width = width
        self.height = height
        # Frame inside canvas, fills all available space
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.frame = tk.Frame(self.canvas)
        # Grid fills all available window space
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def draw(self):
        """Draw the scrollbars and container frame.
        """
        # Put the container frame in the Canvas
        self.canvas.create_window(0, 0, window=self.frame, anchor='nw')
        # Canvas scrollable area
        self.canvas.configure(scrollregion=(0, 0, self.width, self.height))
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.draw_scrollbars()

    def draw_scrollbars(self):
        # Attach scrollbars to the Canvas
        h_scroll = tk.Scrollbar(self, orient='horizontal',
                                command=self.canvas.xview)
        v_scroll = tk.Scrollbar(self, orient='vertical',
                                command=self.canvas.yview)
        h_scroll.grid(row=1, column=0, sticky='we')
        v_scroll.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(xscrollcommand=h_scroll.set,
                              yscrollcommand=v_scroll.set)

### --------------------------------------------------------------------

#! /usr/bin/env python
# support.py

"""Supporting classes for metagui"""

__all__ = [
    'FontChooser',
    'Optional',
    'Tabs',
    'ScrolledWindow'
    ]

import os
import Tkinter as tk
import tkSimpleDialog
from libtovid import log

log.level = 'debug'

### --------------------------------------------------------------------

class FontChooser (tkSimpleDialog.Dialog):
    """A widget for choosing a font"""
    def __init__(self, master=None):
        tkSimpleDialog.Dialog.__init__(self, master, "Font chooser")

    def get_fonts(self):
        """Return a list of font names available in ImageMagick."""
        find = "convert -list type | sed '/Path/,/---/d' | awk '{print $1}'"
        return [line.rstrip('\n') for line in os.popen(find).readlines()]

    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        self.fontlist = ScrollList(master, "Available fonts",
                                   self.get_fonts())
        self.fontlist.pack(fill='both', expand=True)
        return self.fontlist
    
    def apply(self):
        """Set the selected font.
        """
        self.result = self.fontlist.selected.get()

### --------------------------------------------------------------------

class Optional (tk.Frame):
    """Container that shows/hides an optional Control"""
    def __init__(self,
                 control=None,
                 label='Option',
                 *args):
        """Create an Optional widget.

            control: A Control to show or hide
            label:   Label for the optional widget
        """
        self.control = control('', *args)
        self.label = label
        self.active = tk.BooleanVar()

    def draw(self, master):
        """Draw optional checkbox and control widgets in the given master."""
        tk.Frame.__init__(self, master)
        # Create and pack widgets
        self.check = tk.Checkbutton(self, text=self.label, variable=self.active,
                                    command=self.showHide, justify='left')
        self.check.pack(side='left')
        self.control.draw(self)
        self.control.pack(side='left', expand=True, fill='x')
        self.control.disable()
        self.active.set(False)
    
    def showHide(self):
        """Show or hide the sub-widget."""
        if self.active.get():
            self.control.enable()
        else:
            self.control.disable()

    def get(self):
        """Return the sub-widget's value if active, or None if inactive."""
        if self.active.get():
            return self.control.get()
        else:
            return None
    
    def set(self, value):
        """Set sub-widget's value."""
        self.control.set(value)

### --------------------------------------------------------------------

class Tabs (tk.Frame):
    """A tabbed frame, with tab buttons that switch between several frames.
    """
    def __init__(self, master, side='top', font=('Helvetica', 12, 'normal')):
        """Create a tabbed frame widget.
        
            master: Tkinter widget to draw the Tabs in
            side:   Side to show the tab controls on
                    ('top', 'bottom', 'left', or 'right')
            font:   Tkinter font spec for tab-button font
        
        Tabs are added to the tab bar via the add() method. The added frames
        should have the Tabs frame as their master. For example:
        
            tabs = Tabs(self)
            spam = tk.Frame(tabs, ...)
            tabs.add("Spam", spam)
            eggs = tk.Frame(tabs, ...)
            tabs.add("Eggs", eggs)
            tabs.draw()
            tabs.pack(...)
        
        Tabs are drawn in the order they are added, with the first being
        initially active.
        """
        tk.Frame.__init__(self, master)
        self.side = side
        self.font = font
        self.labels = []
        self.frames = []
        self.selected = tk.IntVar()
        self.index = 0
    
    def add(self, label, frame):
        """Add a new tab for the given frame.

            label: Label shown in the tab
            frame: tk.Frame shown when the tab is activated
        """
        self.labels.append(label)
        self.frames.append(frame)

    def draw(self):
        """Draw the tab bar and the first enclosed frame.
        """
        # Tkinter configuration common to all tab buttons
        config = {
            'variable': self.selected,
            'command': self.change,
            'selectcolor': 'white',
            'relief': 'sunken',
            'offrelief': 'groove',
            'font': self.font,
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
        for index, label in enumerate(self.labels):
            button = tk.Radiobutton(self.buttons, text=label, value=index,
                                    **config)
            button.pack(anchor='nw', side=button_side,
                        fill='both', expand=True)
        self.buttons.pack(anchor=bar_anchor, side=self.side,
                          fill=bar_fill, expand=True)
        # Activate the first tab
        self.selected.set(0)
        self.change()

    def change(self):
        """Switch to the selected tab's frame.
        """
        # Unpack the existing frame
        self.frames[self.index].pack_forget()
        # Pack the newly-selected frame
        selected = self.selected.get()
        self.frames[selected].pack(side=self.side, fill='both')
        # Remember this tab's index
        self.index = selected

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

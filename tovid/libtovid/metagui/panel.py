#! /usr/bin/env python
# panel.py

"""GUI widgets for grouping Controls together and defining layout.
"""

__all__ = [
    'Panel',
    'HPanel',
    'VPanel',
    'Dropdowns',
    'Drawer',
    'Tabs',
    'FlagGroup',
    'RelatedList',
]

import Tkinter as tk
import sys

from widget import Widget
from control import Control, MissingOption, Flag
from support import ensure_type, divide_list

### --------------------------------------------------------------------

class Panel (Widget):
    """A group of Widgets in a rectangular frame, with an optional label.
    """
    def __init__(self,
                 name='',
                 *widgets,
                 **kwargs):
        """Create a Panel containing one or more widgets or sub-panels.
        
            name
                Name (label) for panel, or '' for no label
            widgets
                One or more Widgets (Controls, Panels, Drawers etc.)
        """
        Widget.__init__(self, name)

        # Ensure that Widgets were provided
        ensure_type("Panels may only contain Widgets.", Widget, *widgets)
        self.widgets = list(widgets)


    def draw(self, master, labeled=True):
        """Draw the Panel, but not any contained widgets.
        If labeled is True, and panel has a name, use a LabelFrame.
        """
        Widget.draw(self, master)
        # Get a labeled or unlabeled frame
        if self.name != '' and labeled == True:
            self.frame = tk.LabelFrame(self, text=self.name,
                                       padx=8, pady=8)
        else:
            self.frame = tk.Frame(self)
        # Pack the frame
        self.frame.pack(fill='both', expand=True)


    def draw_widgets(self, side='top'):
        """Draw contained widgets in self.frame,
        packed on the given side ('top' or 'left').
        """
        for widget in self.widgets:
            widget.draw(self.frame)
            widget.pack(side=side, anchor='nw', fill='both',
                        expand=True, padx=4, pady=2)


    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        Print error messages if any required options are missing.
        """
        if not self.widgets:
            return []
        args = []
        for widget in self.widgets:
            try:
                args += widget.get_args()
            except MissingOption, missing:
                print "Missing a required option: " + missing.option
        return args


    def enable(self, enabled=True):
        for widget in self.widgets:
            widget.enable(enabled)


### --------------------------------------------------------------------

class HPanel (Panel):
    """A group of widgets or sub-panels, packed horizontally (left-to-right).

    For example:

        HPanel("General",
            Filename(...),
            Flag(...),
            Number(...)
            )
    """
    def __init__(self, name='', *widgets, **kwargs):
        Panel.__init__(self, name, *widgets, **kwargs)
 
    def draw(self, master, **kwargs):
        """Draw all widgets in the Panel, packed horizontally.
        """
        Panel.draw(self, master, **kwargs)
        self.draw_widgets('left')

### --------------------------------------------------------------------

class VPanel (Panel):
    """A group of widgets or sub-panels, packed vertically (top-to-bottom).

    For example:

        VPanel("General",
            Filename(...),
            Flag(...),
            Number(...)
            )
    """
    def __init__(self, name='', *widgets, **kwargs):
        Panel.__init__(self, name, *widgets, **kwargs)

    def draw(self, master, **kwargs):
        """Draw all widgets in the Panel, packed vertically.
        """
        Panel.draw(self, master, **kwargs)
        self.draw_widgets('top')


### --------------------------------------------------------------------
from support import ComboBox
from variable import ListVar
from libtovid.odict import Odict

class Dropdowns (Panel):
    """A Panel with Controls that are shown/hidden using a dropdown list.
    
    The Dropdowns panel initially displays a single dropdown list, with
    one entry for each Control. When a dropdown entry is selected, the
    corresponding Control is displayed, along with a "remove" button to
    discard the control.
    """
    def __init__(self, name='', *widgets):
        Panel.__init__(self, name, *widgets)
        ensure_type("Dropdown contents must be Controls", Control, *widgets)
        # Controls, indexed by label
        self.controls = Odict()
        for control in self.widgets:
            self.controls[control.label] = control


    def draw(self, master, **kwargs):
        """Draw the Dropdowns widget in the given master.
        """
        Panel.draw(self, master, **kwargs)
        # List of Controls and chosen item
        self.choices = ListVar(items=self.controls.keys())
        self.chosen = tk.StringVar()
        # ComboBox to choose Controls from
        self.chooser = ComboBox(self.frame, self.choices, variable=self.chosen,
                                command=self.choose_new)
        self.chooser.pack(anchor='nw')


    def choose_new(self, event=None):
        """Create and display the chosen control."""
        chosen = self.chosen.get()
        if chosen == '':
            return
        self.chooser.pack_forget()
        # Put control and remove button in a frame inside self.frame
        control_frame = tk.Frame(self.frame)
        button = tk.Button(control_frame, text="X",
                           command=lambda:self.remove(chosen))
        button.pack(side='left')
        control = self.controls[chosen]
        control.draw(control_frame)
        control.pack(side='left', fill='x', expand=True)
        control_frame.pack(fill='x', expand=True)
        # Remove the chosen control/panel from the list of available ones
        self.choices.remove(chosen)
        self.chooser.pack(anchor='nw')


    def remove(self, control_label):
        """Remove a given Control from the interface."""
        frame = self.controls[control_label].master
        frame.pack_forget()
        frame.destroy()
        # Make this control available in the dropdown again
        self.choices.append(control_label)


    def get_args(self):
        """Return a list of command-line options from all active Controls.
        """
        args = []
        for control in self.widgets:
            if control.active:
                args += control.get_args()
        return args


### --------------------------------------------------------------------

class Drawer (Panel):
    """A Panel that may be hidden or "closed" like a drawer.
    """
    def __init__(self, name='', *widgets):
        Panel.__init__(self, name, *widgets)
        self.visible = False


    def draw(self, master, **kwargs):
        # Draw the base panel and contained widgets
        Panel.draw(self, master, **kwargs)
        self.frame.pack_forget()
        self.draw_widgets()
        # Add a checkbutton for showing/hiding
        button = tk.Button(self, text=self.name,
                           command=self.show_hide)
        button.pack(anchor='nw', fill='x', expand=True)


    def show_hide(self):
        # Hide if showing
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        # Show if hidden
        else:
            self.frame.pack(anchor='nw', fill='both', expand=True)
            self.visible = True

### --------------------------------------------------------------------

class Tabs (Panel):
    """A Panel with tab buttons that switch between several widgets.
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create a tabbed panel that switch between several widgets.
        """
        Panel.__init__(self, name, *widgets, **kwargs)
        # Index of selected tab
        self.index = 0


    def draw(self, master, side='top', **kwargs):
        """Draw the Tabs widget in the given master.
        """
        Panel.draw(self, master, **kwargs)
        self.side = side
        # Selected tab index
        self.selected = tk.IntVar()
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
        self.buttons = tk.Frame(self.frame)
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
        for index, widget in enumerate(self.widgets):
            button = tk.Radiobutton(self.buttons, text=widget.name,
                                    value=index, **config)
            button.pack(anchor='nw', side=button_side,
                        fill='both', expand=True)
            # If widget is a Panel, draw it without a label
            if isinstance(widget, Panel):
                widget.draw(self.frame, labeled=False)
            else:
                widget.draw(self.frame)
        self.buttons.pack(anchor=bar_anchor, side=self.side,
                          fill=bar_fill)
        # Activate the first tab
        self.selected.set(0)
        self.change()


    def change(self):
        """Event handler for switching tabs
        """
        # Unpack the existing widget
        self.widgets[self.index].pack_forget()
        # Pack the newly-selected widget
        selected = self.selected.get()
        self.widgets[selected].pack(side=self.side, fill='both', expand=True)
        # Remember this tab's index
        self.index = selected


    def activate(self, index):
        """Activate (display) the given tab index.
        """
        self.selected.set(index)
        self.change()


### --------------------------------------------------------------------

class FlagGroup (Panel):
    """A Panel that shows a group of several Flag controls,
    optionally making them mutually-exclusive.
    """
    def __init__(self,
                 name='',
                 state='normal',
                 *flags,
                 **kwargs):
        """Create a FlagGroup with the given label and state.
        
            name
                Name/label for the group
            state
                'normal' for independent Flags, 'exclusive' for
                mutually-exclusive Flags (more like a Choice)
            *flags
                One or more Flag controls to include in the group
        
        These keyword arguments are accepted:
        
            side:     'top' or 'left', to pack Flags vertically or horizontally
            rows:     For 'left' packing, number of rows to split flags into
            columns:  For 'top' packing, number of columns to split flags into
        """
        Panel.__init__(self, name)
        ensure_type("FlagGroup may only contain Flag instances", Flag, *flags)
        self.flags = flags
        self.state = state
        # Keyword arguments
        self.side = 'top'
        if 'side' in kwargs:
            self.side = kwargs['side']
            if self.side not in ['top', 'left']:
                raise ValueError("FlagGroup 'side' must be 'top' or 'left'.")
        self.columns = 1
        if 'columns' in kwargs:
            self.columns = kwargs['columns']
        self.rows = 1
        if 'rows' in kwargs:
            self.rows = kwargs['rows']
    

    def draw(self, master, **kwargs):
        """Draw the FlagGroup in the given master widget.
        """
        Panel.draw(self, master, **kwargs)

        if self.side == 'top':
            num_strips = self.columns
            strip_side = 'left'
        else:
            num_strips = self.rows
            strip_side = 'top'

        # Divide flags into rows or columns
        for flags in divide_list(self.flags, num_strips):
            subframe = tk.Frame(self.frame)
            # Draw all Flags in the row/column
            for flag in flags:
                flag.draw(subframe)
                flag.check.bind('<Button-1>', self.select)
                flag.pack(anchor='nw', side=self.side, fill='x', expand=True)
            # Pack the frame for the current row/column
            subframe.pack(anchor='nw', side=strip_side)


    def select(self, event):
        """Event handler called when a Flag is selected.
        """
        # For normal flags, nothing to do
        if self.state != 'exclusive':
            return
        # For exclusive flags, clear all but the clicked Flag
        for flag in self.flags:
            if flag.check != event.widget:
                flag.set(False)
            flag.enabler()


    def get_args(self):
        """Return a list of arguments for setting the relevant flag(s).
        """
        args = []
        for flag in self.flags:
            if flag.option != 'none':
                args.extend(flag.get_args())
        return args


### --------------------------------------------------------------------
from support import ScrollList
from control import List

class RelatedList (Panel):
    """A Panel showing two Lists, where one is related to the other.

    Relates a parent list to a child Control, with a parent:child
    relationship of 1:1 (each parent item has one child item)
    or 1:* (each parent item has a list of child items).
    
    One to one:

        - Each item in parent list maps to an item in the child list
        - Parent copy and child list scroll in unison
        - If item in child is selected, parent item is selected also
        - Drag/drop is not allowed (parent Control determines order)

    One to many:

        - Each item in parent list maps to a list of items in the child list
        - Parent copy and child list do NOT scroll in unison
        - If item in child is selected, parent is unaffected
        - Drag/drop is allowed in the child Control

    Assumptions:

        - Child Control is shown to the right of a read-only copy of the parent
        - If item in parent is selected, child item/list is selected also
        - It item is added to parent, new child item/list is added also
        - If item in parent is deleted, child item/list is deleted also
        - Child option string is only passed once
    
    """
    
    def __init__(self,
                 parent,
                 correspondence,
                 child_control,
                 **kwargs):
        """Create a 1:1 or 1:* correspondence between two lists.

            parent
                Parent List (a Control instance), or the option string
                of the parent List control declared elsewhere
            correspondence
                Either 'one' or 'many'
            child_list
                List control for the child

        Examples:

            RelatedList('-files', 'one',
                List('Video titles', '-titles', Text()))
            RelatedList('-files', 'many',
                List('Grouped videos', '-group', Filename()))
        """
        if correspondence not in ['one', 'many']:
            raise ValueError("Correspondence must be 'one' or 'many'.")
        if not isinstance(child_control, List):
            raise TypeError("Child must be a List instance.")
        Panel.__init__(self, child_control.name)
        self.parent = parent
        self.correspondence = correspondence
        self.child = child_control
        self.mapped = []

        if 'filter' in kwargs:
            if not callable(kwargs['filter']):
                raise TypeError("Translation filter must be a function.")
            self.filter = kwargs['filter']
        else:
            self.filter = lambda x: x


    def draw(self, master, **kwargs):
        """Draw the parent copy and related list Control,
        side by side in the given master.
        """
        Panel.draw(self, master, **kwargs)

        # Lookup the parent Control by option
        if type(self.parent) == str:
            self.parent = Control.by_option(self.parent)
            self.draw_copy = True
        else:
            self.draw_copy = False

        # Ensure parent control exists and is a List
        if not self.parent:
            raise Exception("Control for '%s' does not exist" % self.option)
        ensure_type("RelatedList parent must be a List", List, self.parent)

        # Draw the read-only copy of parent's values
        if self.draw_copy:
            self.selected = tk.StringVar()
            frame = tk.LabelFrame(self.frame, text="%s (copy)" % self.parent.label)
            self.listbox = ScrollList(frame, self.parent.variable, self.selected)
            self.listbox.pack(expand=True, fill='both')
            frame.pack(side='left', anchor='nw', expand=True, fill='both')
        else:
            self.parent.draw(self.frame)
            self.parent.pack(side='left', anchor='nw', expand=True, fill='both')
            self.listbox = self.parent.listbox

        # Draw the child control
        # 1:1, add/remove in child is NOT allowed, and lists are linked
        if self.correspondence == 'one':
            self.child.draw(self.frame, edit_only=True)
            self.listbox.link(self.child.listbox)
        # 1:many, add/remove in child is allowed
        else:
            self.child.draw(self.frame)
        # Pack the child control to the right of the parent copy
        self.child.pack(side='left', anchor='nw', expand=True, fill='both')

        # Add callbacks to handle changes in parent
        self.add_callbacks()


    def add_callbacks(self):
        """Add callback functions for add/remove in the parent Control.
        """
        if self.correspondence == 'one':
            # insert/remove callbacks for the parent listbox
            def insert(index, value):
                print("%s, Inserting %d: %s" % (self.child.option, index, value))
                self.child.variable.insert(index, self.filter(value))
            def remove(index, value):
                print("%s, Removing %d: %s" % (self.child.option, index, value))
                self.child.variable.pop(index)
            def swap(index_a, index_b):
                print("%s, Swapping %d and %d" % (self.child.option, index_a, index_b))
                self.child.listbox.swap(index_a, index_b)
            def select(index, value):
                print("%s, Selected %d: %s" % (self.child.option, index, value))
                pass # already handled by listboxes being linked??

        else: # 'many'
            # insert/remove/swap callbacks for the parent listbox
            def insert(index, value):
                print("%s, Inserting %d: %s" % (self.child.option, index, value))
                self.mapped.insert(index, ListVar())
            def remove(index, value):
                print("%s, Removing %d: %s" % (self.child.option, index, value))
                self.mapped.pop(index)
            def swap(index_a, index_b):
                print("%s, Swapping %d and %d" % (self.child.option, index_a, index_b))
                a_var = self.mapped[index_a]
                self.mapped[index_a] = self.mapped[index_b]
                self.mapped[index_b] = a_var
            def select(index, value):
                print("%s, Selected %d: %s" % (self.child.option, index, value))
                self.child.set_variable(self.mapped[index])

        self.listbox.callback('select', select)
        self.parent.listbox.callback('insert', insert)
        self.parent.listbox.callback('remove', remove)
        self.parent.listbox.callback('swap', swap)


    def get_args(self):
        args = []
        # Add parent args, if parent was defined here
        if not self.draw_copy:
            args.extend(self.parent.get_args())
        # Add child args, for one or many children
        if self.correspondence == 'many':
            for list_var in self.mapped:
                args.extend(self.child.get_args(list_var))
        else: # 'one'
            args.extend(self.child.get_args())
        return args


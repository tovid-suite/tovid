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
from control import Control, MissingOption
from support import ensure_type

### --------------------------------------------------------------------

class Panel (Widget):
    """A group of Widgets in a rectangular frame, with an optional label.
    """
    def __init__(self,
                 name='',
                 *widgets,
                 **kwargs):
        """Create a Panel containing one or more widgets or sub-panels.
        
            name:     Name (label) for panel, or '' for no label
            widgets:  One or more Widgets (Controls, Panels, Drawers etc.)
        """
        Widget.__init__(self, name)

        # Ensure that Widgets were provided
        ensure_type("Panels may only contain Widgets.", Widget, *widgets)
        self.widgets = widgets


    def draw(self, master):
        """Draw the Panel, but not any contained widgets.
        """
        Widget.draw(self, master)
        # Get a labeled or unlabeled frame
        if self.name != '':
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
            widget.pack(side=side, anchor='nw', fill='x',
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
 
    def draw(self, master):
        """Draw all widgets in the Panel, packed horizontally.
        """
        Panel.draw(self, master)
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

    def draw(self, master):
        """Draw all widgets in the Panel, packed vertically.
        """
        Panel.draw(self, master)
        self.draw_widgets('top')


### --------------------------------------------------------------------
from support import ComboBox, ListVar
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


    def draw(self, master):
        """Draw the Dropdowns widget in the given master.
        """
        Panel.draw(self, master)
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


    def draw(self, master):
        # Draw the base panel and contained widgets
        Panel.draw(self, master)
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
    def __init__(self, *widgets, **kwargs):
        """Create a tabbed panel that switch between several widgets.
        """
        Panel.__init__(self, '', *widgets, **kwargs)
        self.index = 0


    def draw(self, master, side='top'):
        """Draw the Tabs widget in the given master.
        """
        Panel.draw(self, master)
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
            widget.draw(self.frame)
        self.buttons.pack(anchor=bar_anchor, side=self.side,
                          fill=bar_fill)
        # Activate the first tab
        self.selected.set(0)
        self.change()


    def change(self):
        """Switch to the selected tab's frame.
        """
        # Unpack the existing widget
        self.widgets[self.index].pack_forget()
        # Pack the newly-selected widget
        selected = self.selected.get()
        self.widgets[selected].pack(side=self.side, fill='both', expand=True)
        # Remember this tab's index
        self.index = selected


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
        
            name:     Name/label for the group
            state:    'normal' for independent Flags, 'exclusive' for
                      mutually-exclusive Flags (more like a Choice)
            *flags:   One or more Flag controls to include in the group
        """
        Panel.__init__(self, name)
        self.flags = flags
        self.state = state
        self.side = 'top'
        if 'side' in kwargs:
            self.side = kwargs['side']
    

    def draw(self, master):
        """Draw the FlagGroup in the given master widget.
        """
        Panel.draw(self, master)
        for flag in self.flags:
            flag.draw(self.frame)
            flag.check.bind('<Button-1>', self.select)
            flag.pack(anchor='nw', side=self.side, fill='x', expand=True)


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
    """A Panel showing a list Control that's related to another list.

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
                 parent_option,
                 correspondence,
                 child_control,
                 **kwargs):
        """Create a 1:1 or 1:* correspondence between two lists.

            parent_option:  Option string of parent list
            correspondence: Either 'one' or 'many'
            child_list:     List control for the child

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
        self.parent_option = parent_option
        self.correspondence = correspondence
        self.child = child_control

        if 'filter' in kwargs:
            if not callable(kwargs['filter']):
                raise TypeError("Translation filter must be a function.")
            self.filter = kwargs['filter']
        else:
            self.filter = lambda x: x


    def draw(self, master):
        """Draw the parent copy and related list Control,
        side by side in the given master.
        """
        Panel.draw(self, master)

        # Copy of parent list's values
        self.last_copy = ListVar(self)

        # Lookup the parent Control by option
        self.parent = Control.by_option(self.parent_option)
        # Ensure parent control exists and is a List
        if not self.parent:
            raise Exception("Control for '%s' does not exist" % self.option)
        ensure_type("RelatedList parent must be a List", List, self.parent)
        
        # Draw the read-only copy of parent's values
        self.selected = tk.StringVar()
        frame = tk.LabelFrame(self.frame, text="%s (copy)" % self.parent.label)
        self.listbox = ScrollList(frame, self.parent.variable, self.selected)
        self.listbox.pack(expand=True, fill='both')
        frame.pack(side='left', anchor='nw', expand=True, fill='both')

        # Draw the child control (without Add/Remove buttons)
        self.child.draw(self.frame, edit_only=True)
        self.child.pack(side='left', anchor='nw', expand=True, fill='both')

        # Link parent copy to child list
        self.listbox.link(self.child.listbox)

        # Add callback to sync parent with child
        def _parent_changed(name, index, mode):
            self.parent_changed()
        self.parent.variable.trace_variable('w', _parent_changed)


    def parent_changed(self):
        """Event handler for when the parent variable changes.
        """
        old_value = self.last_copy.get()
        new_value = self.parent.variable.get()

        # FIXME: Most of this is 1:1-specific...

        # Value stayed the same?
        if old_value == new_value:
            return

        # Item contents changed or were reordered?
        elif len(new_value) == len(old_value):
            # Check for swapped items
            for index in range(0, len(old_value)-1):
                # This will handle pairwise adjacent swaps only
                if old_value[index] == new_value[index+1] and \
                   old_value[index+1] == new_value[index]:
                    item = self.child.variable.pop(index+1)
                    self.child.variable.insert(index, item)

        # Items were added to parent?
        elif len(new_value) > len(old_value):
            # Add child items at the same index
            for item in (set(new_value) - set(old_value)):
                self.child.variable.insert(new_value.index(item),
                                           self.filter(item))

        # Items were deleted from parent?
        else:
            # Delete child items at same index
            for item in (set(old_value) - set(new_value)):
                self.child.variable.pop(old_value.index(item))

        # Save new value to last_copy
        self.last_copy.set(new_value)


    def get_args(self):
        if self.correspondence == 'many':
            # TODO
            return []
        else:
            return self.child.get_args()



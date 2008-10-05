#! /usr/bin/env python
# widget.py

"""A generic GUI widget class, wrapper for tk.Frame.
"""

__all__ = ['Widget']

import Tkinter as tk

### --------------------------------------------------------------------
class Widget (tk.Frame):
    """Generic metagui widget, suitable for Controls, Panels, etc.
    """
    def __init__(self, name='', toggles=False, enabled=True):
        """Create a Widget.
        
        name
            Unique name for the widget, or '' for an anonymous widget
        toggles
            True to include a toggle button for enable/disable
        enabled
            True if Widget is enabled by default, False if disabled
        """
        if type(name) != str:
            raise TypeError("Widget name must be a string.")
        
        self.name = name
        self.enabled = enabled
        self.toggles = toggles
        self.active = False
        self.enabled_var = None


    def draw(self, master):
        tk.Frame.__init__(self, master)
        self.active = True
        self.enabled_var = tk.BooleanVar(self)
        # Draw the toggle checkbox if needed
        if self.toggles:
            self.check = tk.Checkbutton(self, text='',
                                        variable=self.enabled_var,
                                        command=self.toggle)
            self.check.pack(side='left')


    def toggle(self):
        """Enable/disable the Widget when self.check is toggled.
        """
        if self.enabled_var.get():
            self.enable()
        else:
            self.disable()
            self.check.config(state='normal')


    def enable(self, enabled=True):
        """Enable or disable all sub-widgets (but not the current widget)."""
        if enabled:
            state = 'normal'
        else:
            state = 'disabled'
        self.enabled = enabled
        self.enabled_var.set(enabled)
        # Change all child widgets that allow state changes
        for widget in self.winfo_children():
            if 'state' in widget.config():
                widget.config(state=state)


    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)


    def destroy(self):
        tk.Frame.destroy(self)
        self.active = False


    def get_args(self):
        """Return a list of command-line options for this widget.
        """
        return []

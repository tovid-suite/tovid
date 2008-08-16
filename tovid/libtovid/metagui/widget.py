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
    def __init__(self, name=''):
        if type(name) != str:
            raise TypeError("Widget name must be a string.")
        self.name = name
        self.active = False
    
    def draw(self, master):
        tk.Frame.__init__(self, master)
        self.active = True

    def destroy(self):
        tk.Frame.destroy(self)
        self.active = False

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets."""
        if enabled:
            newstate = 'normal'
        else:
            newstate = 'disabled'
        # Change all child widgets that allow state changes
        for widget in self.children.values():
            if 'state' in widget.config():
                widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)

    def get_args(self):
        """Return a list of command-line options for this widget.
        """
        return []

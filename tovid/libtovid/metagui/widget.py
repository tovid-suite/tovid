#! /usr/bin/env python
# widget.py

__all__ = ['Widget']

import Tkinter as tk

### --------------------------------------------------------------------
class Widget (tk.Frame):
    """Generic metagui widget, suitable for Controls, Panels, etc."""
    def __init__(self):
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
        for widget in self.children.values():
            # Some widgets don't support state changes
            if 'state' in widget.config():
                widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)

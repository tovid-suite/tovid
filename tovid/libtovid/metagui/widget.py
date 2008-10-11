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
        """Create a Widget.
        
        name
            Unique name for the widget, or '' for an anonymous widget
        """
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


    def get_args(self):
        """Return a list of command-line options for this widget.
        """
        return []


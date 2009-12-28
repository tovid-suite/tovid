"""A generic GUI widget class, wrapper for tk.Frame.
"""

__all__ = ['Widget']

import Tkinter as tk
import time

class Widget (tk.Frame):
    """Generic metagui widget, suitable for Controls, Panels, etc.
    """
    def __init__(self, name='', **kwargs):
        """Create a Widget.

            name
                Unique name for the widget, or '' for an anonymous widget
        """
        if type(name) != str:
            raise TypeError("Widget name must be a string.")

        self.name = name
        self.enabled = True
        self.is_drawn = False


    def draw(self, master, **kwargs):
        """Initialize the base tk.Frame class.
        """
        tk.Frame.__init__(self, master)
        self.is_drawn = True


    def destroy(self):
        """Destroy the widget.
        """
        tk.Frame.destroy(self)
        self.is_drawn = False


    def get_args(self):
        """Return a list of command-line options for this widget.
        """
        return []


    def enable(self, enabled=True):
        """Enable or disable the Widget and all its children.
        """
        self.enabled = enabled
        # Enable/disable all child widgets that allow state changes
        for widget in self.winfo_children():
            if 'state' in widget.config():
                if enabled:
                    widget.config(state='normal')
                else:
                    widget.config(state='disabled')


    def disable(self):
        """Disable the Widget.
        """
        self.enable(False)


    def blink(self):
        """Cause the Widget to "blink" by briefly changing its background color.
        """
        bgcolor = self.cget('background')
        self.config(background='#C0C0F0')
        self.update()
        time.sleep(1)
        self.config(background=bgcolor)


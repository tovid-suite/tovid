"""GUI widgets for grouping Controls together and defining layout.
"""

__all__ = [
    'Label',
    'Panel',
    'HPanel',
    'VPanel',
    'Dropdowns',
    'Drawer',
    'Tabs',
    'FlagGroup',
]

# Python < 3.x
try:
    import Tkinter as tk
# Python 3.x
except ImportError:
    import tkinter as tk

from libtovid import cli
from libtovid.odict import Odict
from libtovid.metagui.widget import Widget
from libtovid.metagui.control import Control, Flag
from libtovid.metagui.support import \
    (ComboBox, ensure_type, divide_list, get_photo_image)
from libtovid.metagui.variable import ListVar
from base64 import b64encode


class Label (Widget):
    """A widget with a text label.
    """
    def __init__(self,
                 text='',
                 justify='left',
                 image_file='',
                 image_width=0,
                 image_height=0):
        """Create a Label with the given text.

            text
                String to appear in the Label
            justify
                Text justification: 'left', 'center', or 'right'
            image_file
                Full path to image file. May be in any format that
                'convert' supports.
            image_width
                Width in pixels to resize the image to
            image_height
                Height in pixels to resize the image to

        Width and height may be used to scale the image in different ways:

            width == 0, height == 0
                Preserve the original image's size
            width > 0, height == 0
                Resize to the given width; height automatically
                adjusts to maintain aspect ratio
            width == 0, height > 0
                Resize to the given height; width automatically
                adjusts to maintain aspect ratio
            width > 0, height > 0
                Resize to exactly the given dimensions
        """
        Widget.__init__(self, text)
        self.text = text
        if justify not in ['left', 'center', 'right']:
            raise ValueError("Label justify argument must be 'left', 'center', "
                             "or 'right' (got '%s' instead)." % justify)
        self.justify = justify
        # Image attributes
        self.image_file = image_file
        self.image_width = image_width
        self.image_height = image_height
        # Will be set by draw()
        self.label = None
        self.image = None


    def draw(self, master, **kwargs):
        """Draw the Label in the given master.
        """
        Widget.draw(self, master, **kwargs)
        # If an image filename was provided, get a PhotoImage
        if self.image_file:
            photo_image = get_photo_image(self.image_file,
                self.image_width, self.image_height, self.cget('background'))
            # Keep a reference to the PhotoImage to prevent garbage collection
            self.photo = photo_image
            image_frame = tk.Frame(self, padx=4, pady=4)
            self.image = tk.Label(image_frame, image=photo_image)
            self.image.pack()
            image_frame.pack(side='left', expand=False)

        # Create and pack the label
        self.label = tk.Label(self, text=self.text, justify=self.justify, padx=8)
        # Set appropriate anchoring based on justification
        _anchors = {'left': 'w', 'center': 'center', 'right': 'e'}
        self.label.pack(expand=True, anchor=_anchors[self.justify])


class Panel (Widget):
    """A group of Widgets in a rectangular frame, with an optional label.
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create a Panel containing one or more widgets or sub-panels.

            name
                Name (label) for panel, or '' for no label
            widgets
                One or more Widgets (Controls, Panels, Drawers etc.)
        """
        Widget.__init__(self, name, **kwargs)

        # Ensure that Widgets were provided
        ensure_type("Panels may only contain Widgets.", Widget, *widgets)
        self.widgets = list(widgets)
        # Defined by draw()
        self.frame = None


    def draw(self, master, **kwargs):
        """Draw the Panel, but not any contained widgets.

            labeled
                True (default) to use a LabelFrame with the panel's name,
                False to draw the panel without a label.

        Panel subclasses must pack the contained widgets, or
        call ``draw_widgets`` to pack them.
        """
        Widget.draw(self, master, **kwargs)
        # Get a labeled or unlabeled frame (labeled by default)
        if self.name and kwargs.get('labeled', True):
            self.frame = tk.LabelFrame(self, text=self.name,
                                       padx=4, pady=4)
        else:
            self.frame = tk.Frame(self)
        # Pack the frame
        self.frame.pack(side='top', fill='both', expand=True)


    def draw_widgets(self, side='top', expand=False):
        """Draw contained widgets in self.frame.

            side
                'top' or 'left', to pack widgets on that side
            expand
                True to make widgets fill all available space

        Panel subclasses may call this method to pack widgets,
        or do custom packing (and not call this method).
        """
        for widget in self.widgets:
            widget.draw(self.frame)
            widget.pack(side=side, expand=expand, anchor='nw',
                        fill='both', padx=4, pady=2)


    def get_args(self):
        """Return a list of all command-line options from contained widgets.
        """
        args = []
        for widget in self.widgets:
            args += widget.get_args()
        return args


    def set_args(self, args):
        """Set panel options from the given list of command-line arguments,
        and remove any successfully parsed options and arguments from ``args``.
        """
        for widget in self.widgets:
            widget.set_args(args)


    def enable(self, enabled=True):
        """Enable all widgets in the Panel.
        """
        for widget in self.widgets:
            widget.enable(enabled)


class HPanel (Panel):
    """A group of widgets or sub-panels, packed horizontally (left-to-right).

    For example::

        HPanel("General",
            Filename(...),
            Flag(...),
            Number(...)
            )
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create an HPanel to show the given widgets in a horizontal layout.
        """
        Panel.__init__(self, name, *widgets, **kwargs)


    def draw(self, master, **kwargs):
        """Draw the HPanel and its contained widgets in the given master.
        """
        Panel.draw(self, master, **kwargs)
        self.draw_widgets(side='left', expand=True)


class VPanel (Panel):
    """A group of widgets or sub-panels, packed vertically (top-to-bottom).

    For example::

        VPanel("General",
            Filename(...),
            Flag(...),
            Number(...)
            )
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create a VPanel to show the given widgets in a vertical layout.
        """
        Panel.__init__(self, name, *widgets, **kwargs)


    def draw(self, master, **kwargs):
        """Draw the VPanel and its contained widgets in the given master.
        """
        Panel.draw(self, master, **kwargs)
        # Avoid unnecessary vertical expansion
        self.draw_widgets(side='top', expand=False)


class Dropdowns (Panel):
    """A Panel with Controls that are shown/hidden using a dropdown list.

    The Dropdowns panel initially displays a single dropdown list, with
    one entry for each Control. When a dropdown entry is selected, the
    corresponding Control is displayed, along with a "remove" button to
    discard the control.
    """
    def __init__(self, name='', *controls, **kwargs):
        Panel.__init__(self, name, *controls, **kwargs)
        ensure_type("Dropdown contents must be Controls", Control, *controls)
        # Controls, indexed by label
        self.controls = Odict()
        for control in self.widgets:
            self.controls[control.label] = control
        # Set by draw()
        self.choices = None
        self.chosen = None
        self.chooser = None


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
            if control.is_drawn:
                args += control.get_args()
        return args


class Drawer (Panel):
    """A Panel that may be hidden or "closed" like a drawer.
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create a Drawer containing the given widgets.
        """
        Panel.__init__(self, name, *widgets, **kwargs)
        self.visible = False
        # Set by draw()
        self.button = None


    def draw(self, master, **kwargs):
        """Draw the Drawer, with contained widgets initially hidden.
        """
        # Draw the base panel and contained widgets
        Panel.draw(self, master, **kwargs)
        self.frame.pack_forget()
        self.draw_widgets()
        # Add a checkbutton for showing/hiding
        self.button = tk.Button(self, text=self.name, relief='groove',
                           command=self.show_hide)
        self.button.pack(anchor='nw', fill='x', expand=True)


    def show_hide(self):
        """Show or hide the widgets in the Drawer.
        """
        # Hide if showing
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
            self.button.config(relief='groove')
        # Show if hidden
        else:
            self.frame.pack(anchor='nw', fill='both', expand=True)
            self.visible = True
            self.button.config(relief='sunken')


class Tabs (Panel):
    """A Panel with tab buttons that switch between several widgets.
    """
    def __init__(self, name='', *widgets, **kwargs):
        """Create a tabbed panel that switch between several widgets.
        """
        Panel.__init__(self, name, *widgets, **kwargs)
        # Index of selected tab
        self.index = 0
        self.side = kwargs.get('side', 'top')
        # Set by draw()
        self.buttons = None
        self.selected = None


    def draw(self, master, **kwargs):
        """Draw the Tabs widget in the given master.
        """
        Panel.draw(self, master, **kwargs)
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
            # For Panels, hide the panel's own label
            if isinstance(widget, Panel):
                widget.draw(self.frame, labeled=False)
            else:
                widget.draw(self.frame)
        self.buttons.pack(anchor=bar_anchor, side=self.side, fill=bar_fill)
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


    def activate(self, tab):
        """Display the given tab (either by index or Widget instance).
        """
        # Get index by Widget instance
        if isinstance(tab, Widget):
            if tab in self.widgets:
                index = list(self.widgets).index(tab)
            else:
                raise ValueError("Widget '%s' not in Tabs" % tab.name)
        # Or use index directly
        else:
            index = int(tab)
        # Switch to the given tab index
        self.selected.set(index)
        self.change()


class FlagGroup (Panel):
    """A Panel that shows a group of several Flag controls,
    optionally making them mutually-exclusive.
    """
    def __init__(self,
                 name='',
                 kind='normal',
                 *flags,
                 **kwargs):
        """Create a FlagGroup with the given label and state.

            name
                Name/label for the group
            kind
                'normal' for independent Flags, 'exclusive' for
                mutually-exclusive Flags (more like a Choice)
            flags
                One or more Flag controls to include in the group

        These keyword arguments are accepted:

            side
                'top' or 'left', to pack Flags vertically or horizontally
            rows
                For 'left' packing, number of rows to split flags into
            columns
                For 'top' packing, number of columns to split flags into
        """
        Panel.__init__(self, name, **kwargs)
        ensure_type("FlagGroup may only contain Flag instances", Flag, *flags)
        self.flags = flags
        self.kind = kind
        # Keyword arguments
        self.side = kwargs.get('side', 'top')
        if self.side not in ['top', 'left']:
            raise ValueError("FlagGroup 'side' must be 'top' or 'left'.")
        self.columns = kwargs.get('columns', 1)
        self.rows = kwargs.get('rows', 1)


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
                flag.add_callback(self.modified)
                flag.pack(anchor='nw', side=self.side, fill='x', expand=True)
            # Pack the frame for the current row/column
            subframe.pack(anchor='nw', side=strip_side)


    def modified(self, flag):
        """Called when a flag is modified.
        """
        # For normal flags, do nothing
        if self.kind != 'exclusive':
            return
        # If the flag is unchecked, do nothing
        if not flag.get():
            return
        # Otherwise, uncheck all other flags
        for _flag in self.flags:
            if _flag != flag:
                _flag.set(False)


    def get_args(self):
        """Return a list of arguments for setting the relevant flag(s).
        """
        args = []
        for flag in self.flags:
            # Include only if set to a non-default value
            if flag.option != 'none' and flag.get() != flag.default:
                args.extend(flag.get_args())
        return args




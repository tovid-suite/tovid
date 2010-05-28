"""Supporting classes for metagui"""

__all__ = [
    # Functions
    'exit_with_traceback',
    'ensure_type',
    'divide_list',
    'get_photo_image',
    # Others
    'ScrollList',
    'DragList',
    'ComboBox',
    'FontChooser',
    'PopupScale',
    'ConfigWindow',
    'ScrolledWindow',
    'Style',
]

import os
import sys
import traceback
import math
import base64
import re

# Python < 3.x
try:
    import Tkinter as tk
    from tkSimpleDialog import Dialog
    import tkMessageBox
    from ConfigParser import ConfigParser
# Python 3.x
except ImportError:
    import tkinter as tk
    from tkinter.simpledialog import Dialog
    import tkinter.messagebox as tkMessageBox
    from configparser import ConfigParser

from libtovid import cli
from libtovid.util import imagemagick_fonts
from libtovid.metagui.variable import ListVar

### --------------------------------------------------------------------
### Supporting functions
### --------------------------------------------------------------------
def exit_with_traceback(error_message):
    """Exit with a traceback, and print a custom error message.
    """
    # Print helpful info from stack trace
    last_error = traceback.extract_stack()[0]
    traceback.print_stack()
    filename, lineno, foo, code = last_error

    print("Error on line %(lineno)s of %(filename)s:" % vars())
    print("    %s" % code)
    print(error_message)
    sys.exit(1)


def ensure_type(message, required_type, *objects):
    """Ensure that the given objects are of the required type.
    If not, print a message and exit_with_traceback.
    """
    for obj in objects:
        if not isinstance(obj, required_type):
            type_message = "Expected %s, got %s instead" % \
                         (required_type, obj.__class__.__name__)
            exit_with_traceback(type_message + '\n' + message)


def divide_list(items, pieces):
    """Divide a list of things into several pieces, of roughly equal size.
    """
    # Can't divide into fewer than 2 pieces
    if pieces < 2:
        return [items]
    else:
        # N = number of items in each piece
        N = int(math.ceil(float(len(items)) / pieces))
        # For each piece p, extract N items
        return [items[N*p : N*p+N] for p in range(pieces)]


def askyesno(title=None, message=None, **options):
    """Show a popup with Yes / No options. Return True if Yes was clicked,
    False if No was clicked.

    This function is to work around a bug in Tkinter 8.5 / Python 2.6, where
    the askyesno function always returns False after a file dialog has been
    displayed.
    """
    result = tkMessageBox._show(title, message,
        tkMessageBox.QUESTION, tkMessageBox.YESNO,
        **options)
    if str(result) == 'yes':
        return True
    else:
        return False


def get_photo_image(filename, width=0, height=0, background='', dither=False):
    """Get a tk.PhotoImage from a given image file.

        filename
            Full path to the image file, in any format that 'convert'
            understands
        width
            Desired image width in pixels
        height
            Desired image height in pixels
        background
            An '#RRGGBB' string for the desired background color.
            Only effective for images with transparency.
        dither
            True to dither the image. May increase graininess.
            Smallish images usually look better without dithering.

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
    # Convert the image file to gif using 'convert'
    cmd = cli.Command('convert')

    # Pre-processing
    # Dither if requested, otherwise disable
    if dither:
        cmd.add('-dither')
    else:
        cmd.add('+dither')
    # Set the background color, if provided
    if background:
        cmd.add('-background', background)

    cmd.add(filename)

    # Post-processing
    # Scale appropriately
    if width > 0 and height == 0:
        cmd.add('-resize', '%dx' % width)
    elif width == 0 and height > 0:
        cmd.add('-resize', 'x%d' % height)
    elif width > 0 and height > 0:
        cmd.add('-resize', '%dx%d!' % (width, height))

    # If background color was set, flatten the image
    if background:
        cmd.add('-flatten')

    # Convert to gif data
    cmd.add('gif:-')

    # Run the command, capturing the gif data from standard output
    cmd.run(capture=True, silent=True)
    gif_data = cmd.get_output()
    # Create and return the PhotoImage from the gif data
    return tk.PhotoImage(data=base64.b64encode(gif_data))

def show_icons(window, image):
    '''Show window manager icons for window, if supported.
    The icon argument is full path to the image to be used.
    '''
    icon = get_photo_image(image, 32, 32)
    try:
        window.tk.call('wm', 'iconphoto', window._w, icon)
    except tk.TclError:
        print("Could not set window manager icons.  Maybe your "
              "Tkinter (Tcl) is too old? Continuing anyway.")   



### --------------------------------------------------------------------
### Classes
### --------------------------------------------------------------------

class ScrollList (tk.Frame):
    """A Listbox with a scrollbar.

    Similar to a tk.Listbox, a ScrollList shows a list of items. tk.Variables
    may be associated with both the list of items, and the one that is currently
    selected.
    """
    def __init__(self, master=None, items=None,
                 selected=None):
        """Create a ScrollList widget.

            master
                Tkinter widget that will contain the ScrollList
            items
                ListVar or Python list of items to show in listbox
            selected
                Tk StringVar to store currently selected choice in
        """
        tk.Frame.__init__(self, master)

        if type(items) == list:
            items = ListVar(self, items)
        self.items = items or ListVar()

        self.selected = selected or tk.StringVar()
        self.curindex = 0
        self.linked = None
        # Draw listbox and scrollbar
        self.scrollbar = tk.Scrollbar(self, orient='vertical',
                                      command=self.scroll)
        self.listbox = tk.Listbox(self, listvariable=self.items,
                                  width=45, height=7,
                                  yscrollcommand=self.scrollbar.set,
                                  exportselection=0)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='left', fill='y')
        #self.listbox.bind('<Button-1>', self.select)
        # use ButtonRelease so drag/drop functions don't mess with focus_set
        self.listbox.bind('<ButtonRelease-1>', self.select)
        self.listbox.bind('<Return>', self.next_item)
        # Callback methods for the various list-modification actions
        self.callbacks = {'insert': [], 'remove': [], 'select': [], 'swap': []}


    def set_variable(self, listvar):
        """Set the ScrollList to use the given ListVar for its items.
        """
        if not isinstance(listvar, ListVar):
            raise TypeError("ScrollList.set_variable requires a ListVar "
                            "(got %s instead)" % listvar.__class__.__name__)
        self.items = listvar
        self.listbox.config(listvariable=self.items)


    def scroll(self, *args):
        """Event handler when the list is scrolled.
        """
        self.listbox.yview(*args)
        # Scroll in the linked list also
        if self.linked:
            self.linked.listbox.yview(*args)


    def add(self, *values):
        """Add the given values to the end of the list.
        Calls ``insert`` callbacks for each added item.
        """
        for value in values:
            self.summon_callbacks('insert', self.items.count(), value)
            self.listbox.insert('end', value)
        self.select_index(-1)


    def insert(self, index, *values):
        """Insert values at a given index.
        Calls ``insert`` callbacks for each added item.
        """
        for offset, value in enumerate(values):
            self.listbox.insert(index+offset, value)
            self.summon_callbacks('insert', index+offset, value)
        self.select_index(index)


    def delete(self, first, last=None):
        """Delete values in a given index range (first, last), not including
        last itself. If last is None, delete only the item at first index.
        Calls ``remove`` callbacks for each removed item.
        """
        if first == last:
            return
        # Summon callbacks for each item/value about to be deleted
        for index in reversed(range(first, last or first+1)):
            value = self.items[index]
            self.summon_callbacks('remove', index, value)
        # Delete items from the listbox
        self.listbox.delete(first, last)
        self.select_index(first)


    def swap(self, index_a, index_b):
        """Swap the element at index_a with the one at index_b.
        Calls ``swap`` callbacks for the swapped items.
        """
        # Use a temporary list, so self.items is only modified once
        temp_list = self.items.get()
        item_a = temp_list[index_a]
        item_b = temp_list[index_b]
        temp_list[index_a] = item_b
        temp_list[index_b] = item_a
        # Set the updated list
        self.items.set(temp_list)
        # Summon 'swap' callbacks
        self.summon_callbacks('swap', index_a, index_b)


    def select(self, event):
        """Event handler when an item in the list is selected.
        """
        index = self.listbox.nearest(event.y)
        self.select_index(index)


    def next_item(self, event):
        """Event handler when <Return> is pressed
        """
        self.curindex += 1
        if self.linked:
            self.linked.curindex = self.curindex
        self.select_index(self.curindex)


    def select_index(self, index, select_in_linked=True):
        """Select (highlight) the list item at the given index.
        Calls ``select`` callbacks for the selected item.
        """
        item_count = self.items.count()
        if item_count == 0:
            return
        # If index is negative, or past the end, cycle or select last item
        if index < 0 or index >= item_count:
            # allow cycling (any unforeseen consequences ?)
            if self.listbox.get(index-1):
                index = 0
            else:
                index = item_count - 1
        # Clear selection, and select only the given index
        self.listbox.selection_clear(0, item_count)
        self.listbox.selection_set(index)
        # Set selected variable
        self.selected.set(self.listbox.get(index))
        self.curindex = index
        # Summon 'select' callbacks
        self.summon_callbacks('select', index, self.selected.get())
        # Select same index in linked ScrollList
        if self.linked and select_in_linked:
            self.linked.select_index(index, False)


    def get(self):
        """Return a list of all entries in the list.
        """
        return self.items.get()


    def set(self, values):
        """Set the list values to those given.
        """
        # Use delete / add so the relevant callbacks are summoned
        self.delete(0, self.items.count())
        self.add(*values)


    def link(self, scrolllist):
        """Link to another ScrollList, so they scroll and select in unison.
        """
        if not isinstance(scrolllist, ScrollList):
            raise TypeError("Can only link to a ScrollList.")
        self.linked = scrolllist
        scrolllist.linked = self


    def callback(self, action, function):
        """Add a callback function for the given action.

            action
                May be 'insert', 'remove', 'select', or 'swap'
            function
                Callback function, taking (index, value) arguments
                index is 0-based; passes -1 for the last item

        All callback functions (except 'swap') must take (index, value)
        parameters. The 'swap' callback should accept (index_a, index_b).
        """
        if action not in ['insert', 'remove', 'select', 'swap']:
            raise ValueError("List callback action must be"
                             " 'insert', 'remove', 'select', or 'swap'.")
        if not hasattr(function, '__call__'):
            raise TypeError("List callback function must be callable.")
        self.callbacks[action].append(function)


    def summon_callbacks(self, action, index, item):
        """Summon callbacks for the given action,
        passing index and item to each.
        """
        if action not in ['insert', 'remove', 'select', 'swap']:
            raise ValueError("Callback action must be"
                             " 'insert', 'remove', 'select', or 'swap'")
        for function in self.callbacks[action]:
            function(index, item)



class DragList (ScrollList):
    """A scrollable listbox with drag-and-drop support.
    """
    def __init__(self, master=None, items=None,
                 selected=None):
        """Create a DragList widget.

            master
                Tkinter widget that will contain the DragList
            items
                ListVar or Python list of items to show in listbox
            selected
                Tk StringVar to store currently selected list item
        """
        ScrollList.__init__(self, master, items, selected)
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
        # If item is dragged to a new location, swap
        loc = self.listbox.nearest(event.y)
        if loc != self.curindex and self.items.count() > 0:
            self.swap(self.curindex, loc)
            self.curindex = loc


    def drop(self, event):
        """Event handler when an item in the list is "dropped".
        """
        # Change the mouse cursor back to the default arrow.
        self.config(cursor="")
        # make sure drop doesn't mess with focus_set
        self.select_index(self.curindex)


class ComboBox (tk.Frame):
    """A dropdown menu with several choices.
    """
    def __init__(self, master, choices=None,
                 variable=None, command=None):
        """Create a ComboBox.

            master
                Tk Widget that will contain the ComboBox
            choices
                ListVar or Python list of available choices
            variable
                Tk StringVar to store currently selected choice in
            command
                Function to call when an item in the list is selected
        """
        tk.Frame.__init__(self, master)
        if type(choices) == list:
            choices = ListVar(self, choices)
        self.choices = choices or ListVar()
        self.variable = variable or tk.StringVar()
        self.command = command
        self.curindex = 0

        # Text and button
        # Fit to width of longest choice
        _width = max([len(str(c)) for c in self.choices.get()])
        self.text = tk.Entry(self, textvariable=self.variable, width=_width)
        self.text.pack(side='left', expand=True, fill='both')
        self.button = tk.Button(self, text="...", command=self.open)
        self.button.pack(side='left')

        # Dropdown list, displayed when button is clicked
        self.dropdown = tk.Toplevel(self)
        # Don't draw window manager frame around the dropdown
        self.dropdown.wm_overrideredirect(1)
        # Hide until later
        self.dropdown.withdraw()

        # List of choices
        self.chooser = tk.Listbox(self.dropdown, background='#ffffff',
                                  listvariable=self.choices, width=_width,
                                  height=self.choices.count())
        # Use alternating white/gray for choices
        #for index in range(0, len(self.choices), 2):
        #    self.chooser.itemconfig(index, bg='LightGray')
        self.chooser.bind('<Button-1>', self.choose, '+')
        self.bind_all('<Button>', self.close, '+')
        self.chooser.bind('<Motion>', self.highlight)
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

        # Highlight the current selection
        self.chooser.itemconfig(self.curindex, background='LightGray')


    def close(self, event=None):
        """Close the panel showing the list of choices.
        """
        try:
            if self.dropdown.winfo_viewable():
                self.dropdown.withdraw()
        except tk.TclError:
            pass


    def highlight(self, event=None):
        """Event handler to highlight an entry on mouse-over.
        """
        for index in range(self.choices.count()):
            self.chooser.itemconfig(index, background='White')
        index = self.chooser.nearest(event.y)
        self.chooser.itemconfig(index, background='LightGray')


    def choose(self, event=None):
        """Make a selection from the list, and set the variable.
        """
        self.curindex = self.chooser.nearest(event.y)
        self.variable.set(self.chooser.get(self.curindex))
        self.close()
        # Callback, if any
        if self.command:
            self.command()


class FontChooser (Dialog):
    """A widget for choosing a font.
    """
    # Cache of PhotoImage previews, indexed by font name
    _cache = {}

    def __init__(self, parent=None):
        Dialog.__init__(self, parent, "Font chooser")
        # Defined in body()
        self.fontlist = None
        self.preview = None


    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        tk.Label(master, text="Available fonts").pack(side='top')

        # List of fonts available to ImageMagick
        available_fonts = imagemagick_fonts()
        self.fontlist = ScrollList(master, available_fonts)
        self.fontlist.callback('select', self.refresh)
        self.fontlist.pack(side='top', fill='both', expand=True)

        # Font preview area
        self.preview = tk.Label(master, image=None, width=500)
        self.preview.pack(fill='both', expand=True)

        # Draw the initial preview
        self.refresh()

        # Return widget with initial focus
        return self.fontlist


    def apply(self):
        """Set the selected font. Called by base Dialog when "OK" is pressed.
        """
        self.result = self.fontlist.selected.get()


    def refresh(self, index=0, fontname='Helvetica'):
        """Redraw the preview using the current font and size.
        """
        # Cache a PhotoImage for this font name
        if fontname not in self._cache:
            self._cache[fontname] = self.render_font(fontname)
        # Get the PhotoImage from the cache
        photo_image = self._cache[fontname]
        self.preview.configure(image=photo_image, height=photo_image.height())


    def render_font(self, fontname):
        """Return a tk.PhotoImage preview of the given font.
        """
        cmd = cli.Command('convert')
        cmd.add('-size',  '500x60')
        cmd.add("xc:#EFEFEF")
        cmd.add('-font', fontname, '-pointsize', 24)
        cmd.add('-gravity', 'center', '-annotate', '+0+0', fontname)
        cmd.add('gif:-')
        cmd.run(capture=True)
        image_data = cmd.get_output()
        return tk.PhotoImage(data=base64.b64encode(image_data))


class PopupScale (Dialog):
    """A popup widget with a scale for choosing a number.
    """
    def __init__(self, parent=None):
        """Create the scale dialog with the given Number control as a parent.
        """
        Dialog.__init__(self, parent, parent.label or 'Scale')
        # Set by body()
        self.scale = None


    def body(self, master):
        """Draw the popup dialog and return the widget that should have the
        initial focus.
        """
        num = self.parent
        frame = tk.Frame(self, relief=tk.GROOVE, borderwidth=3)
        frame.pack(side='top', fill='both', expand=True, pady=6)
        self.scale = tk.Scale(frame, from_=num.min, to=num.max,
                               resolution=num.step,
                               tickinterval=(num.max - num.min),
                               orient='horizontal')
        self.scale.pack(side='left', fill='both', expand=True)
        tk.Label(frame, name='units', text=num.units).pack(side='left')
        # Set scale to parent Number's value initially
        self.scale.set(num.variable.get())


    def apply(self):
        """Set the result to the current scale value. Called when "OK" is
        pressed.
        """
        self.result = self.scale.get()


class Style:
    """Generic widget style definitions.
    """
    def __init__(self,
                 bgcolor='#ffffff',
                 fgcolor='#d9d9d9',
                 textcolor='#000000',
                 font=('Helvetica', 10, 'normal'),
                 relief='groove'):
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.textcolor = textcolor
        self.font = font
        self.relief = relief


    def apply(self, root):
        """Apply the current style to the given Tkinter root window.
        """
        assert isinstance(root, tk.Tk)
        root.option_clear()
        # Font
        root.option_add("*font", self.font)
        #root.option_add("*Text.font", ('Courier', 10, 'normal'))
        root.option_add("*Text.font", self.font)
        # Background color
        root.option_add("*Scale.troughColor", self.bgcolor)
        root.option_add("*Spinbox.background", self.bgcolor)
        root.option_add("*Entry.background", self.bgcolor)
        root.option_add("*Listbox.background", self.bgcolor)
        root.option_add("*Text.background", self.bgcolor)
        # Button colors
        root.option_add("*Radiobutton.selectColor", "#ffffff")
        root.option_add("*Checkbutton.selectColor", "#ffffff")
        # Relief
        root.option_add("*Entry.relief", self.relief)
        root.option_add("*Spinbox.relief", self.relief)
        root.option_add("*Listbox.relief", self.relief)
        root.option_add("*Button.relief", self.relief)
        root.option_add("*Menu.relief", self.relief)
        # Mouse-over effects
        root.option_add("*Button.overRelief", 'raised')
        root.option_add("*Checkbutton.overRelief", 'raised')
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
        dirname, fname = os.path.split(filename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
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


class ConfigWindow (Dialog):
    """Configuration settings dialog box.
    """
    def __init__(self, master=None, style=None):
        """Create and display a configuration window.

            inifile
                An .ini-style file to load/save settings from
        """
        self.style = style or Style()
        Dialog.__init__(self, master, "Configuration")
        # Defined in body()
        self.fontfamily = None
        self.fontsize = None
        self.fontstyle = None


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
        # Attach scrollbars to the Canvas
        h_scroll = tk.Scrollbar(self, orient='horizontal',
                                command=self.canvas.xview)
        v_scroll = tk.Scrollbar(self, orient='vertical',
                                command=self.canvas.yview)
        h_scroll.grid(row=1, column=0, sticky='we')
        v_scroll.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(xscrollcommand=h_scroll.set,
                              yscrollcommand=v_scroll.set)


class PrettyLabel (tk.Text):
    """Like a Label, with automatic word-wrapping of paragraphs, and inference
    of headings and preformatted text from basic markup cues.

    """
    def __init__(self, master, text, font=None):
        """Create a pretty label for displaying the given text.
        """
        # Text widget with the same background color as the master
        tk.Text.__init__(self, master, wrap='word', borderwidth=0, padx=10)
        if font:
            self.config(font=font)
        # Add the text with formatting applied
        self.set_text(text)
        # background and unfocused border color same as master's background
        bg = master.cget('background')
        self.config(background=bg, highlightbackground=bg)
        # Make the text widget read-only
        self.config(state='disabled')


    def rewrap(self, text):
        """Rewrap the given text, by joining regular paragraphs into
        single lines, and leaving preformatted text and headings alone.
        """
        # Start by splitting into chunks at double-line-breaks
        lines = []
        chunks = text.strip().split('\n\n')
        for chunk in chunks:
            # If this chunk contains newlines, they could be in paragraphs
            # (which should wrap) or preformatted text (which should not be
            # wrapped)
            if '\n' in chunk:
                parts = chunk.split('\n')
                # Preformatted - append each line individually
                if all(line.startswith(' ') for line in parts):
                    lines.extend(parts)
                # Paragraph - join lines with spaces
                else:
                    lines.append(' '.join(parts))
            # No newline in chunk -- It's either a heading or a
            # one-line paragraph, so append it as-is
            else:
                lines.append(chunk)
            # Include an empty line where the \n\n was before
            lines.append('')
        return lines


    def set_text(self, text):
        """Set the widget to contain the given text, with formatting applied.
        """
        heading_re = re.compile('^[ A-Z()]+$')
        pre_re = re.compile('^ +(.+)$')

        # Parse each logical (wrapped) line in the text
        lineno = 1
        for line in self.rewrap(text):
            L = str(lineno)
            # Heading line
            if heading_re.match(line):
                # Capitalize each word in the heading
                heading = ' '.join(word.capitalize() for word in line.split(' '))
                self.insert('end', heading)
                # Unique tag name for this heading
                tag = 'heading' + L
                self.tag_add(tag, L+'.0', L+'.end')
                self.tag_config(tag, font=self.get_heading_font())
            # Preformatted line
            elif pre_re.match(line):
                self.insert('end', line)
                # Unique tag name for this line
                tag = 'pre' + L
                self.tag_add(tag, L+'.0', L+'.end')
                self.tag_config(tag, font=self.get_monospace_font())
            # Paragraph
            else:
                self.insert('end', line)
            # Newline to separate each logical line
            self.insert('end', '\n')
            lineno += 1


    def get_heading_font(self):
        """Return a bold font, in the current font family.
        """
        # The config('font') method returns a 5-tuple, where the last
        # item is the font descriptor tuple, or 'TkFixedFont' as a default
        font = self.config('font')[-1]
        # If font is (family, height, style), increase size and make it bold
        if isinstance(font, tuple) and len(font) == 3:
            family, height, style = font
            return (family, int(height)+6, 'bold')
        # Default font
        else:
            return ('Helvetica', 16, 'bold')


    def get_monospace_font(self):
        """Return a monospace font, with the current font size and style.
        """
        font = self.config('font')[-1]
        # If font is (family, height, style), change family to Courier
        if isinstance(font, tuple) and len(font) == 3:
            family, height, style = font
            return ('Courier', int(height), style)
        # Default font
        else:
            return ('Courier', 12, 'normal')


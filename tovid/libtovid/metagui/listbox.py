#! /usr/bin/env python
# listbox.py
# Based on grepper's ListBoxes
# under adaptation to metagui Controls

"""

Files <-> Titles (map filename to title)
Files <-> Submenu audio files (map filename to list)
Files <-> Seek values (map filename to number)

When filename in list is selected, a new control may be displayed for
setting the filename's associated attribute (title, seek, etc.)

Filenames->associated values are maintained in an Odict. Only one file's
associated-value control may be shown at a time.

When current file's associated control is updated with <Enter>, the next
filename is selected and the associated control focused.

Q. How are args assembled for associated controls? Can call get_args for
each in order, should be possible to define (at metagui top level) how they
pass options.

Speaking of top-level:

Panel("...",
    FileList('-files', "Input video files", '',
        map=Text('-titles', "Title for FILE", '')), ...
)

"""

__all__ = [
    'ListBoxes',
    'FilesTitles',
    'MappedEntry',
    'MappedFiles',
    'MappedGroups',
    'MappedNumbers',
    'MappedTitles']

import os
import sys
import time
import re
import copy
import shlex
import Tkinter as tk
import tkFileDialog
import tkMessageBox

from libtovid.metagui import *

### --------------------------------------------------------------------
### Exceptions
### --------------------------------------------------------------------

class UserError (Exception):
    """Raised when a required command-line option was not specified.

        message: Brief description of the missing option
        widget: A tkinter Widget where the option can be set
    """
    def __init__(self, message, widget=None):
        self.message = message
        self.widget = widget


### --------------------------------------------------------------------
### Helper functions
### --------------------------------------------------------------------

def blink(widget):
    """Cause a widget to "blink" by briefly changing its background color.
    """
    if widget == None:
        return
    assert isinstance(widget, tk.Widget)
    widget.config(background='#C0C0F0')
    widget.update()
    time.sleep(1)
    widget.config(background='white')


### --------------------------------------------------------------------
### Frames containing related control widgets
### --------------------------------------------------------------------

class ListBoxes (tk.Frame):
    """A frame containing a list of filenames, and controls to add or delete
    files from the list.
    """
    def __init__(self):
        self.curentry = tk.StringVar()  # currently selected mapped list entry
        self.varFiles = tk.Variable()   # List of current files
        self.varMappedList = tk.Variable()  # Current mapped list entries
        self.varUsage = tk.StringVar()  # String describing current space usage
        
        self.filesTitle = tk.StringVar()  # Title for left box ('Files' or 'Current Files')
        self.filesTitle.set('Current Files')
        
        self.mappedTitle = tk.StringVar()  # Title for the right box (mapped files)
        self.mappedTitle.set('')
        self.curindex = 0  # initialize index of currently selected file to 0
        self.puller = []  # a list of instances that the FilesTitles instance needs to sync with
        self.variable = tk.IntVar()
        self.msgSingle = tk.StringVar()
        self.msgSingle.set('')
        self.filesList = ''

    def draw(self, master):
        """Draw all the widgets in this frame."""
        tk.Frame.__init__(self, master)
        # Scrollbar to control both listboxes
        self.scrollbar = tk.Scrollbar(self, orient='vertical')
        self.scrollbar.grid(row=1, column=3, sticky='ns')
        self.scrollbar.config(command=self.scroll)
        # File list box and add/remove buttons
        self.lblFiles = tk.Label(self, textvariable=self.filesTitle)
        self.lblFiles.grid(row=0, column=0, columnspan=2, sticky='w')
        self.lstFiles = tk.Listbox(self, width=30, height=5,
                                   background='#EFEFEF',
                                   listvariable=self.varFiles,
                                   yscrollcommand=self.scrollbar.set)
        self.lstFiles.bind('<Button-1>', self.select)
        self.lstFiles.grid(row=1, column=0, columnspan=2, sticky='w')

        # Title list box and editing field
        self.lblTitles = tk.Label(self, textvariable=self.mappedTitle)
        self.lblTitles.grid(row=0, column=2, sticky='w')
        self.lstMapped = tk.Listbox(self, width=30, height=5,
                                    listvariable=self.varMappedList,
                                    yscrollcommand=self.scrollbar.set)
        self.lstMapped.grid(row=1, column=2)

    def scroll(self, *args):
        """Event handler when scrollbar is moved."""
        apply(self.lstFiles.yview, args)
        apply(self.lstMapped.yview, args)

    def select(self, event):
        """Event handler when a filename or title in the list is selected.
        Set the title box for editing and change the mouse cursor."""
        self.curindex = self.lstFiles.nearest(event.y)
        self.curentry.set(self.lstMapped.get(self.curindex))

    def makeEntry(self, event):
        """Event handler when Enter is pressed after editing a title."""
        newtitle = self.curentry.get()
        log.debug("Setting title to '%s'" % newtitle)
        self.lstMapped.delete(self.curindex)
        self.lstMapped.insert(self.curindex, newtitle)
        if self.lstFiles.get(self.curindex + 1):
            self.lstFiles.selection_clear(self.curindex)
            self.curindex = self.curindex + 1
            self.lstFiles.selection_set (self.curindex)
            self.curentry.set(self.lstMapped.get(self.curindex))

    def enableList(self):
        if self.variable.get() == 1:
            self.lstFiles.config(state='normal')
            self.syncFiles(self.filesList)
        else:
            self.lstFiles.delete(0, 'end')
            self.lstFiles.insert('end', self.msgSingle.get())
            self.lstFiles.config(state='disable')
            if self.lstMapped.get(0):
                single = self.lstMapped.get(0)
                self.lstMapped.delete(0, 'end')
                self.lstMapped.insert(0, single)
                self.curindex = 0


class FilesTitles (ListBoxes):
    """ a frame containing a listbox to show (readonly) loaded files,
    and a listbox to display and edit titles"""
    def __init__(self):
        ListBoxes.__init__(self)
        self.filesTitle.set("Files")
        self.mappedTitle.set("Titles")

    def draw(self, master):
        """Draw all the widgets in this frame."""
        ListBoxes.draw(self, master)
        self.lstMapped.bind('<B1-Motion>', self.drag)
        self.lstMapped.bind('<ButtonRelease-1>', self.drop)
        self.lstFiles.bind('<B1-Motion>', self.drag)
        self.lstFiles.bind('<ButtonRelease-1>', self.drop)
        self.lstMapped.bind('<Button-1>', self.select)
        self.lstFiles.bind('<Return>', self.makeEntry)
        self.entTitle = tk.Entry(self, width=30,
            textvariable=self.curentry)
        self.entTitle.bind('<Return>', self.makeEntry)
        self.entTitle.grid(row=2, column=2)
        self.btnAdd = tk.Button(self, text="Add...", command=self.addFiles)
        self.btnAdd.grid(row=2, column=0, sticky='ew')
        self.btnRemove = tk.Button(self, text="Remove",
                                   command=self.removeFiles)
        self.btnRemove.grid(row=2, column=1, sticky='ew')
        self.lstFiles.config(background='white')
        # Disc usage total
        self.lblUsage = tk.Label(self, textvariable=self.varUsage)
        self.lblUsage.grid(row=0, column=1, columnspan=2, sticky='e')
        self.updateUsage()

    def addFiles(self):
        """Event handler for adding files to the list box"""
        files = tkFileDialog.askopenfilenames(parent=self, title='Add files')
        for file in files:
            log.debug("Adding '%s' to the file list" % file)
            self.lstFiles.insert('end', file)
            # Add a dummy title (with pathname and extension removed)
            title = os.path.basename(file)[0:-4]
            self.lstMapped.insert('end', title)
        self.updateUsage()
        self.syncFilesList()

    def removeFiles(self):
        """Event handler for removing files from the list box"""
        selection = self.lstFiles.curselection() \
                  or self.lstMapped.curselection()
        # Using reverse order prevents reflow from messing up indexing
        if selection:
            for line in reversed(selection):
                log.debug("Removing '%s' from the file list" %\
                          self.lstFiles.get(line))
                self.lstFiles.delete(line)
                self.lstMapped.delete(line)
            self.updateUsage()
            self.syncFilesList()
            for instance_ in self.puller:
                instance_.popList(int(line))

    def addPuller(self, inst):
        """Add inst to a list of instances that sync with list of files"""
        self.puller.append(inst)

    def syncFilesList(self):
        """Sync caller instance with this instances files list"""
        for instance_ in self.puller:
            instance_.syncFiles(self.lstFiles.get(0, 'end'))

    def select(self, event):
        """Event handler when a filename or title in the list is selected.
        Set the title box for editing and change the mouse cursor."""
        self.entTitle.focus_set()
        self.curindex = self.lstFiles.nearest(event.y)
        self.curentry.set(self.lstMapped.get(self.curindex))
        self.config(cursor="double_arrow")

    def drag(self, event):
        """Event handler to move a file/title to another position in the list"""
        loc = self.lstFiles.nearest(event.y)
        if loc != self.curindex:
            file = self.lstFiles.get(self.curindex)
            mapped = self.lstMapped.get(self.curindex)
            self.lstFiles.delete(self.curindex)
            self.lstMapped.delete(self.curindex)
            self.lstFiles.insert(loc, file)
            self.lstMapped.insert(loc, mapped)
            self.curindex = loc
            self.syncFilesList()
            self.update_idletasks()

    def drop(self, event):
        """Event handler called when an item is "dropped" (mouse-release).
        Change the mouse cursor back to the default arrow.
        """
        self.config(cursor="")

    def getUsage(self):
        """Return the total size, in bytes, consumed by the current list
        of files."""
        total = 0
        for file in self.varFiles.get():
            total += os.path.getsize(file)
        return total

    def updateUsage(self):
        """Update the disc space usage label."""
        usage = self.getUsage() / (1024 * 1024)
        self.varUsage.set("%s MB used" % usage)

    def get_args(self):
        """Return todisc arguments for setting files and titles."""
        files = self.varFiles.get()
        titles = self.varMappedList.get()
        if len(files) != len(titles):
            # Should never happen, if the listboxes are properly in sync
            raise Exception, "Number of files and titles do not match"
        if len(files) == 0:
            raise UserError("File list (-files)", self.lstFiles)
        if len(titles) == 0:
            raise UserError("Title list (-titles)", self.lstMapped)
        return ['-files'] + files + ['-titles'] + titles


class MappedTitles (ListBoxes):
    """A frame containing a listbox to show (readonly) loaded files,
    and a listbox to display and edit corresponding submenu titles"""
    def __init__(self, master=None):
        ListBoxes.__init__(self)
        self.mappedTitle.set("Submenu titles")
        self.mappedfiles = []

    def draw(self, master):
        """Draw all the widgets in this frame."""
        ListBoxes.draw(self, master)
        self.entTitle = tk.Entry(self, width=30,
            textvariable=self.curentry)
        self.entTitle.bind('<Return>', self.makeEntry)
        self.lstMapped.bind('<Button-1>', self.select)
#        self.lstFiles.bind('<Double-1>', do_something)
        self.entTitle.grid(row=2, column=2)

    def syncFiles(self, filesList):
        """Sync caller instance with this instances files list"""
        self.filesList = filesList
        self.lstFiles.delete(0, 'end')
        for file in self.filesList:
            self.lstFiles.insert('end', file)
        titles = self.varMappedList.get()
        if len(titles) == 0:
            for file in filesList:
                self.lstMapped.insert('end', '')

    def select(self, event=None):
        """Event handler when a filename or title in the list is selected.
        Set the title box for editing and change the mouse cursor."""
        self.curindex = self.lstFiles.nearest(event.y)
        self.curentry.set(self.lstMapped.get(self.curindex))
        self.entTitle.focus_set()

    def popList(self, index_):
        """remove item from lstMapped list - call from FilesTitles instance"""
        self.index_ = index_
        self.lstMapped.delete(self.index_)

    def get_args(self):
        """Return todisc arguments for setting submenu titles."""
        args = []
        for title in self.varMappedList.get():
            if title:
                args.append(title)
            else:
                args.append("' '")
        return ['-submenu-titles'] + args


class MappedFiles (ListBoxes):
    """ a frame containing a listbox to show (readonly) loaded files,
    and a listbox to load files coresponding to the readonly file list"""
    def __init__(self, master=None):
        ListBoxes.__init__(self)
        self.mappedTitle.set("Submenu audio files")
        self.msgSingle.set('Use this audio file for all videos')
        self.lstFiles.insert('end', 'Use this audio file for all videos')
        self.lstFiles.config(state='disable')
        self.lstFiles.config(disabledforeground='black')

    def draw(self, master):
        """Draw all the widgets in this frame."""
        ListBoxes.draw(self, master)
        val = ''
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row=3, column=2, sticky='ew')
        self.btnAdd = tk.Button(buttonFrame, text="Add...",
                                    command=self.addFiles)
        self.btnAdd.pack(side='left', fill='x', expand=1)
        self.btnRemove = tk.Button(buttonFrame, text="Remove",
                                   command=self.removeFiles)
        self.btnRemove.pack(side='left', fill='x', expand=1)
        buttonFrame2 = tk.Frame(self)
        buttonFrame2.grid(row=3, column=0, columnspan=4, sticky='w')
        self.btnMultiple = tk.Checkbutton(buttonFrame2, text="Use multiple audio files",
                                variable=self.variable, command=self.enableList)
        self.btnMultiple.pack(side='left', fill='x', expand=1)

        self.lstFiles.bind('<Double-1>', self.addFiles)
        print self.variable.get()

    def syncFiles(self, filesList):
        """Sync list of files (lstFiles) with FilesTitles instance"""
        self.filesList = filesList
        self.lstFiles.delete(0, 'end')
        for file in self.filesList:
            self.lstFiles.insert('end', file)
        self.files = self.varMappedList.get()
        if len(self.files) == 0:
            for file in filesList:
                self.lstMapped.insert('end', '')

    def addFiles(self, event=None):
        """Event handler for adding files to the list box"""
        if not self.filesList:
            raise UserError("Load some video files first", self.lstFiles)
        else:
            self.file = tkFileDialog.askopenfilename(parent=self,
                                              title='Add files')
            this_list = list(self.varMappedList.get())
            items = len(this_list) - this_list.count('')
            if items > len(self.filesList):
                raise UserError("You have more audio files than videos!",
                                                        self.lstMapped)
            else:
                log.debug("Adding '%s' to the mapped file list" % file)
                # append files to lstMapped list for filemap
                self.lstMapped.delete(self.curindex)
                self.lstMapped.insert(self.curindex, self.file)
            # set cursor selection and index to the next file in list
            if self.lstFiles.get(self.curindex + 1):
                self.lstFiles.selection_set (self.curindex + 1)
                self.curindex = self.curindex + 1

    def removeFiles(self):
        """Event handler for removing files from the list box"""
        selection = self.lstMapped.curselection()
        # Using reverse order prevents reflow from messing up indexing
        for line in reversed(selection):
            log.debug("Removing '%s' from the file list" %\
                      self.lstFiles.get(line))
            self.lstMapped.delete(line)
            self.lstMapped.insert(line, '')

    def popList(self, index_):
        """remove item from lstMapped list - call from FilesTitles instance"""
        self.index_ = index_
        self.audiofiles = list(self.lstMapped.get(0, 'end'))
        self.numfiles = len(self.audiofiles) - self.audiofiles.count('')
        if self.numfiles != 1 or len(self.filesList) == 0:
            self.lstMapped.delete(self.index_)

    def get_args(self):
        """Return todisc arguments for setting submenu audio files."""
        self.audiofiles = list(self.lstMapped.get(0, 'end'))
        self.numfiles = len(self.audiofiles) - self.audiofiles.count('')
        if self.numfiles != 1:
            self.audio = []
            for file in self.varMappedList.get():
                if file:
                    self.audio.append(file)
                else: self.audio.append('none')
        else:
            self.audio = self.varMappedList.get()
        return ['-submenu-audio'] + self.audio


class MappedGroups (ListBoxes):
    """ a frame containing a listbox to show (readonly) loaded files, and
    a listbox to load grouped files coresponding to the readonly file list"""
    def __init__(self, master=None):
        ListBoxes.__init__(self)
        self.mappedTitle.set("These files will be grouped together")
        self.mappedfiles=[]
        self.shownIndex = 0

    def draw(self, master):
        """Draw all the widgets in this frame."""
        ListBoxes.draw(self, master)
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row=3, column=2, sticky='ew')

        self.btnAdd = tk.Button(buttonFrame, text="Add...",
                                    command=self.addFiles)
        self.btnAdd.pack(side='left', fill='x', expand=1)
        self.btnRemove = tk.Button(buttonFrame, text="Remove",
                                   command=self.removeFiles)
        self.btnRemove.pack(side='left', fill='x', expand=1)
        self.lstFiles.bind('<Double-1>', self.addFiles)
        self.lstFiles.bind('<Return>', self.addFiles)

    def select(self, event):
        """Event handler when a filename or title in the list is selected.
        A list of lists is used to allow each video to have its own group"""
        self.curindex = self.lstFiles.nearest(event.y)
        self.shownIndex = self.curindex
        # clear the tk var listMapped
        self.lstMapped.delete(0, 'end')
        # add currently selected video to group list ( ignored for cmd parsing )
        if not self.mappedfiles[self.curindex]:
            self.mappedfiles[self.curindex] = [self.filesList[self.curindex]]
        # repopulate the widget
        for file in self.mappedfiles[self.curindex]:
            if file:
                self.lstMapped.insert('end', file)

    def syncFiles(self, filesList):
        """Sync list of files (lstFiles) with FilesTitles instance"""
        self.filesList = filesList
        self.lstFiles.delete(0, 'end')
        for file in self.filesList:
            self.lstFiles.insert('end', file)
        if not self.mappedfiles:
            num_files = len(self.varFiles.get())
            self.mappedfiles = [[] for i in range( num_files)]

    def addFiles(self, event=None):
        """Event handler for adding files to the list box"""
        # clear the list for this index
        self.lstMapped.delete(0, 'end')
        if not self.filesList:
            raise UserError("Load some video files first", self.lstFiles)
        else:
            files = tkFileDialog.askopenfilenames(parent=self, title='Add files')
            for file in files:
                log.debug("Adding '%s' to the mapped file list" % file)
            # append the file to the mappedfiles list of lists
                self.mappedfiles[self.curindex].append(file)
            # update the mappedFiles widget
            for file in self.mappedfiles[self.curindex]:
                self.lstMapped.insert('end', file)
            # highlight selection to make clear which video is being grouped
            self.lstFiles.selection_set (self.curindex)

    def removeFiles(self):
        """Event handler for removing files from the list box"""
        selection = self.lstMapped.curselection()
        # Using reverse order prevents reflow from messing up indexing
        for line in reversed(selection):
            log.debug("Removing '%s' from the file list" %\
                      self.lstFiles.get(line))
            self.lstMapped.delete(0, 'end')
            self.mappedfiles[self.curindex].pop(int(line))
            file = self.mappedfiles[self.curindex]
            self.lstMapped.insert('end', *file)

    def popList(self, _index):
        """remove item from lstMapped list - call from FilesTitles instance"""
        self._index = _index
        self.mappedfiles.pop(self._index)
        if self.shownIndex == self._index:
            self.lstMapped.delete(0, 'end')

    def get_args(self):
        """Return todisc arguments for setting groups."""
        args = []
        for index, item in enumerate(self.mappedfiles):
            if item:
                args.extend(['-group', index+1] + item)

### --------------------------------------------------------------------

class MappedNumbers (ListBoxes):
    def __init__(self, master=None):
        ListBoxes.__init__(self)
        self.mappedTitle.set('Seek')
        self.lstFiles.config(disabledforeground='black')
        self.msgSingle.set('Use this seek value for all videos')
        self.lstMapped.insert(0, 2.0)

    def draw(self, master):
        ListBoxes.draw(self, master)
        self.var = tk.DoubleVar()
        self.var.set(2)
        self.curentry = tk.DoubleVar()
        self.lstMapped.config(width=6)
        NumberFrame = tk.Frame(self)
        NumberFrame.grid(row=1, column=4, sticky='ew', columnspan=2)
        self.spacer = tk.Label(NumberFrame, text="", padx=15)
        self.spacer.pack(side='left')
        self.number = tk.Scale(NumberFrame, from_=0, to=900,
                                   tickinterval=450,
                                   orient='horizontal', variable=self.var)
        self.number.pack(padx=2)
        self.entTitle = tk.Entry(NumberFrame, width=10,
            textvariable=self.var)
        self.entTitle.bind('<Return>', self.makeEntry)
        self.lstMapped.bind('<Button-1>', self.select)
        self.entTitle.pack(fill=tk.BOTH, expand=1, padx=2)
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row=2, column=0, columnspan=4, sticky='w')
        self.lstFiles.insert('end', 'Use this seek value for all videos')
        self.btnMultiple = tk.Checkbutton(buttonFrame, text="Use multiple seek values",
                                variable=self.variable, command=self.enableList)
        self.btnMultiple.pack(side='left', fill='x', expand=1)
        self.spacer1 = tk.Label(self, text="", padx=20)
        self.spacer1.grid(row=1, column=6)
        self.lstFiles.config(state='disable')
        
    def makeEntry(self, event):
        """Event handler when Enter is pressed after editing a title."""
        newtitle = self.var.get()
        log.debug("Setting title to '%s'" % newtitle)
        self.lstMapped.delete(self.curindex)
        self.lstMapped.insert(self.curindex, newtitle)
        if self.lstFiles.get(self.curindex + 1):
            self.lstFiles.selection_clear(self.curindex)
            self.curindex = self.curindex + 1
            self.lstFiles.selection_set(self.curindex)
            self.curentry.set(self.lstMapped.get(self.curindex))

    def select(self, event=None):
        """Event handler when a filename or title in the list is selected.
        Set the title box for editing and change the mouse cursor."""
        self.curindex = self.lstFiles.nearest(event.y)
        if self.lstMapped.get(self.curindex):
            self.var.set(float(self.lstMapped.get(self.curindex)))
        self.entTitle.focus_set()

    def popList(self, index_):
        """remove item from lstMapped list - call from FilesTitles instance"""
        self.index_ = index_
        self.lstMapped.delete(self.index_)
        
    def syncFiles(self, filesList):
        """Sync list of files (lstFiles) with FilesTitles instance"""
        self.filesList = filesList
        self.lstFiles.delete(0, 'end')
        for file in self.filesList:
            self.lstFiles.insert('end', file)

    def get_args(self):
        """Return todisc arguments for setting seek."""
        seeks = list(self.varMappedList.get())
        return ['-seek'] + seeks

### --------------------------------------------------------------------

class MappedEntry(ListBoxes):
    def __init__(self, master=None):
        ListBoxes.__init__(self)
        self.lstFiles.config(selectmode=tk.MULTIPLE)
        self.filesTitle.set('Select Files to chain together')
        self.mappedTitle.set('Files to be chained together')

    def draw(self, master):
        ListBoxes.draw(self, master)
        self.varChained = tk.Variable()
        self.btnAdd = tk.Button(self, text="OK", command=self.enterIndexes)
        self.btnAdd.grid(row=4, column=0, sticky='ew', columnspan=2)
        self.spacer = tk.Label(self, text="")
        self.spacer.grid(row=0, column=4, padx=2)

    def enterIndexes(self):
        self.lstMapped.delete(0, 'end')
        for i in range(0, len(self.lstFiles.get(0, 'end'))):
            self.lstMapped.insert(i, '')
        chained = ''
        self.selected = self.lstFiles.curselection()
        for index in self.selected:
            chained = chained + ' ' + str(int(index)+1)
            self.varChained.set(chained)
            self.lstMapped.delete(int(index))
            self.lstMapped.insert(int(index), self.lstFiles.get(int(index)))
        self.setHighlights()
        self.lstFiles.selection_clear(0, 'end')

    def setHighlights(self):
        mapped = self.varMappedList.get()
        for index, item in enumerate(mapped):
            if item:
                self.lstMapped.itemconfig(index, bg='#E9E7E2')

    def syncFiles(self, filesList):
        """Sync list of files (lstFiles) with FilesTitles instance"""
        self.filesList = filesList
        self.lstFiles.delete(0, 'end')
        for file in self.filesList:
            self.lstFiles.insert('end', file)

    def popList(self, index_):
        """remove item from lstMapped list - call from FilesTitles instance"""
        self.index_ = index_
        self.lstMapped.delete(self.index_)

    def get_args(self):
        """Return todisc arguments for setting chained videos."""
        chained = list(self.varChained.get())
        return ['-chain-videos'] + chained


### --------------------------------------------------------------------
### Main application window
### --------------------------------------------------------------------

class GUI (tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.draw()

    def draw(self, master):
        """Draw all the widgets in this frame."""
        group = tk.Frame(self)
        group.pack(side='left', padx=6, pady=7)
        # Pack widgets in main frame

        self.filestitles = FilesTitles(group)
        self.filestitles.pack()
        self.spacer1 = tk.Label(group, text="")
        self.spacer1.pack()
        self.submenutitles = MappedTitles(group)
        self.submenutitles.pack()
        self.spacer2 = tk.Label(group, text="")
        self.spacer2.pack()
        self.submenuaudio = MappedFiles(group)
        self.submenuaudio.pack()
#        self.spacer3 = tk.Label(group, text="")
#        self.spacer3.pack()
        self.groupedfiles = MappedGroups(self)
        self.groupedfiles.pack(pady=7)
        self.spacer4 = tk.Label(self, text="")
        self.spacer4.pack()
        self.mappednumbers = MappedNumbers(self)
        self.mappednumbers.pack()
        self.spacer5 = tk.Label(self, text="")
        self.spacer5.pack(pady=7)
        self.mappedentry = MappedEntry(self)
        self.mappedentry.pack()
        for instance in [self.submenutitles, self.mappednumbers, self.submenuaudio,
                         self.groupedfiles, self.submenutitles, self.mappedentry]:
            self.filestitles.addPuller(instance)

        # Add the menu
        self.makeMenu()

    def makeMenu(self):
        """Create the menu for the application"""
        # create a menubar
        menubar = tk.Menu(self)
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        runmenu = tk.Menu(menubar, tearoff=False)
        runmenu.add_command(label="Run todisc now !", command=self.runCommand)
        menubar.add_cascade(label="Run", menu=runmenu)

        root.config(menu=menubar)

    def getCommand(self):
        """Return the complete todisc command."""
        cmd = Command('todisc')
        frames = [
            self.filestitles,
            self.submenuaudio,
            self.groupedfiles,
            self.mappedentry,
            self.mappednumbers,
            self.submenutitles]
        for frame in frames:
            try:
                cmd.add(*frame.get_args())
            except UserError, err:
                log.error("Missing a required option: %s" % err.message)
                raise
        cmd.add('-out')
        cmd.add('foo1234')
        return cmd

    def runCommand(self):
        """Run the todisc command."""
        try:
            cmd = self.getCommand()
        except UserError, err:
            tkMessageBox.showerror("Missing option",
                                   "Missing a required option: %s" % err.message)
            blink(err.widget)
            return
        # Show pretty-printed command
        pretty_cmd = pretty_todisc(cmd)
        log.info("Running command:")
        log.info(pretty_cmd)
        # Verify with user
        if tkMessageBox.askyesno(message="Run todisc now?"):
            root.withdraw()
            try:
                cmd.run()
            except KeyboardInterrupt:
                tkMessageBox.showerror(message="todisc was interrupted!")
            else:
                tkMessageBox.showinfo(message="todisc finished running!")
            root.deiconify()


### --------------------------------------------------------------------
### Entry point
### --------------------------------------------------------------------

root = tk.Tk()
if __name__ == '__main__':
    # Single argument: theme name 'default' or 'light'
    theme = 'light'
    if len(sys.argv) > 1:
        theme = sys.argv[1]

    root.title("todisc GUI")
    app = GUI(root)
    root.update_idletasks()
    root.mainloop()

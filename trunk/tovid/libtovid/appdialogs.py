#!/usr/bin/env python
# appdialogs.py

from Tkinter import *
import sys, os
from libtovid.metagui import Style


class AppDialog(Frame):
    """This is a 'work in progress' demo of getting a log viewer, a counter, 
    and dialogs into metagui, as well as a system of IPC so a script and
    the gui can communicate.  
    Some thoughts on how it might work:
        The Application class gets the PID of the program it runs, and
        passes that onto the appdialog class.  Then two fifos are
        created in /tmp using appname-PID-out and appname-PID-in.
        Naming them thusly would allow the program/script to start
        communicating right away by getting its own pid and commandline
        arg 0: ${0##*/}.
        The appname-PID-out fifo are written to by the program/script
        and read by the gui:
            It to send commands (like starting dialogs) to the gui.
        The appname-PID-in fifo is written to by the gui and read by
        the program/script:
            it is for sending exit codes or other commands like causing the
            script to exit.

        Commands passed are all interpreted ( no 'eval' or such )
    """
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        # get metagui font configuration
        self.inifile = os.path.expanduser('~/.metagui/config')
        self.style = Style()
        self.style.load(self.inifile)
        # make a few larger font sizes as well
        self.med_font = self.lrg_font = list(self.style.font)
        self.med_font[1] = self.style.font[1]+2
        self.lrg_font[1] = self.style.font[1]+4


class ConfirmDialog(AppDialog):
    """A generic dialog class that allows you to make a dialog with single or
    multiple buttons, and a choice of text or image (GIF only).  Providing
    text AND image makes a 2nd text label underneath the image label.  Example:

    from Tkinter import Tk
    from libtovid.appdialogs import ConfirmDialog

    btns='Preview OK ?, No'
    root = Tk()
    a = ConfirmDialog(root, 'Dialog', 'Menu Preview', btns, '/home/me/pv.gif')
    a.run()

    The exit codes of the buttons start at 0 and increment
    """
    def __init__(self, parent='', title='', text='', button_text='', image=''):
        AppDialog.__init__(self, parent)

        self.text = text
        self._title = title
        default_button_text = ['OK']
        if button_text:
            self.button_text =  []
            if type(button_text) == str:
                self.button_text.append(button_text)
            else:
                self.button_text.extend(button_text)
        else:
            self.button_text = default_button_text
        self.image = image

        root = Toplevel()
        self.master = root
        self.master.title(self._title)

        # draw the text and/or image
        if self.image:
            img = PhotoImage(file=self.image)
            self.im = img
            self.label1 = Label(self.master, bd=2, relief='groove', image=img)
            self.label1.pack(padx=20, pady=20, side='top')
            if self.text:
                label2 = Label(self.master, text=self.text, font=self.lrg_font, \
                justify='left', padx=20, pady=20)
                label2.pack(side='top', fill='both', expand=1)
        elif self.text:
            label2 = Label(self.master, text=self.text, font=self.style.font, \
            justify='left', padx=20, pady=20)
            label2.pack(side='top', fill='both', expand=1)

        # draw the button(s) in a frame
        frame = Frame(self.master)
        buttons = []
        for index, item in enumerate(self.button_text):
            button = Button(frame, text=item, relief='groove', overrelief='raised', \
            anchor='s', command=lambda index=index:self.exit_with_status(index), \
            font=self.style.font)
            button.pack(side='left')
        frame.pack(side='bottom')

    def exit_with_status(self, status):
        if self.parent:
            self.parent.dialog_status.set(str(status))
        else:
            print status
        self.master.destroy()


import time, tkMessageBox
from ScrolledText import ScrolledText

class LogViewer(AppDialog):
    """This class allows you to tail an application log which will be
    embedded in a tkinter window. It takes no parameters:

    """
    def __init__(self, parent):
        AppDialog.__init__(self,parent)

        self.text = ScrolledText(parent, width=80, height=32, \
        font=self.style.font)
        # text area is not editable. ctrl-q and alt-f4 still quit parent
        self.text.bind("<Key>", lambda e: "break")
        self.text.pack(fill=BOTH)

    def set(self, filename):
        self.filename = filename
        self.file = open(self.filename, 'r')
        data = self.file.read()
        self.size = len(data)
        self.text.insert(END, data)
        self.after(100, self.poll)

    def poll(self):
        if os.path.getsize(self.filename) > self.size:
            data = self.file.read()
            self.size = self.size + len(data)
            self.text.insert(END, data)
            self.text.yview_pickplace("end")
        self.after(100,self.poll)


from Tkinter import *
import linecache

class Counter(AppDialog):
    """This class provides a counter that reads data from a file in /tmp.
    It takes no options.

    The counter file must contain either a single number, or if you wish, the
    top and bottom labels are configurable by passing in label text as well.
    To do this the temp file must contain 2 or  more fields followed by a '|'
    separator, as in  count|label1|label2.  Field 1 is the count, and fields
    2 and 3 are the  new labels you  wish.  Example countfile contents:
    Using default labels:

            234

    Using configurable labels:

            3|Working on image|resizing

    Use '||' to clear the contents all labels (not suggested for non embedded
    counters as it will shrink the window and look strange).
        

    """
    def __init__(self, parent):
        AppDialog.__init__(self,parent)

        self.parent = parent
        self.w2text = StringVar()
        self.w1text = StringVar()
        self.w3text = StringVar()
        self.lastdata = ''
        # a label for the counter
        frame = Frame(self.parent, relief='groove')
        frame.pack(side='left', padx=5, pady=5)
        self.w1 = Label(frame, textvariable=self.w1text)
        self.w1.pack(side='left')
        self.w2 = Label(frame, textvariable=self.w2text, \
        font=self.lrg_font, width=4)
        self.w2.pack(side='left')
        self.w3 = Label(frame, textvariable=self.w3text)
        self.w3.pack(side='left')

    def set(self, filename):
        self.countfile= filename
        self.file = open(self.countfile, 'r')

        # poll file for data
        self.update_idletasks
        self.data = linecache.getline(self.countfile, 1)
        self.data = self.data.strip()
        self.after(100, self.poll)

    def label(self, args):
        self.w1text.set(args[0])
        if len(args) == 2:
            self.w3text.set(args[1])

    def poll(self):
        linecache.clearcache()
        self.data = linecache.getline(self.countfile, 1)
        self.data = self.data.strip()
        self.after(100,self.poll)
        if self.data == 'exit':
            self._exit()
        if self.data != self.lastdata:
            if not '|' in self.data: # just a number for the counter
                self.w2text.set(self.data)
            else: # set both labels AND the counter
                List = self.data.split( '|' )
                # set the text labels (w1 and w3)
                self.label(List[1:len(List)])
                # set the numeric counter (w2)
                self.w2text.set(List[0])
            self.lastdata = self.data


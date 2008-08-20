#!/usr/bin/env python
# confirmdialog.py

from Tkinter import *
import sys, os
from libtovid.metagui import Style


class ConfirmDialog(Tk):

    """A generic dialog class that allows you to make a dialog with single or
    multiple buttons, and a choice of text or image (GIF only). Example:

    btns='yes','no','maybe'
    a = ConfirmDialog('Dialog', 'Confirm please', btns, '/home/me/file.gif')

    The exit codes of the buttons start at 0 and increment
    """
    def __init__(self, title='', text='', button_text='Ok', image=''):
        Tk.__init__(self)
        self.text = text
        self._title = title
        self.button_text = []
        self.image = image
        if type(button_text) == str:
            self.button_text.append(button_text)
        else:
            self.button_text.extend(button_text)

        # get metagui font configuration
        self.inifile = os.path.expanduser('~/.metagui/config')
        self.style = Style()
        self.style.load(self.inifile)
        # draw the title
        self.title(self._title)

        # draw the text or image
        # for the moment the dialog can have text OR image, not both
        if self.image:
            img = PhotoImage(file=self.image)
            label1 = Label(image=img, bd=2, relief='groove')
            label1.pack(padx=20, pady=20, side='top')
        elif self.text:
            label2 = Label(text=self.text, font=self.style.font, \
            justify='left', padx=20, pady=20)
            label2.pack(side='top', fill='both', expand=1)

        # draw the button(s) in a frame
        frame = Frame(self)
        frame.pack(side='bottom')
        buttons = []
        for index, item in enumerate(self.button_text):
            button = Button(frame, text=item, relief='groove', overrelief='raised', \
            anchor='s', command=lambda index=index:sys.exit(index), \
            font=self.style.font)
            button.pack(side='left')

        self.mainloop()



import time, tkMessageBox
from ScrolledText import ScrolledText

class LogViewer(Tk):
    """This class allows you to tail an application log which will be
    embedded in a tkinter window. It takes the following parameters:
    filename: the application log to 'tail'.
    app: the application which this viewer is associated with.
    processes:  the pid of the application.  On pressing the exit button
    or closing the window using window manager methods, the pid will be
    killed if it is still active.
    TODO: allow embedding a counter in the window

    """
    def __init__(self, filename, app, processes):
        Tk.__init__(self)
        self.filename = filename
        self.app = app
        self.title(app)
        self.pids = []
        self.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit())
        self.bind('<Control-q>', lambda e, : self.confirm_exit())
        if type(processes) == tuple:
            self.pids.extend(processes)
        else:
            self.pids.append(processes)
        self.quit_msg = app + ' is still running !\nThis will exit from ' + app
        self.quit_msg = self.quit_msg + '\nExit now ?'
        self.inifile = os.path.expanduser('~/.metagui/config')
        self.style = Style()
        self.style.load(self.inifile)
        self.file = open(self.filename, 'r')
        self.data = self.file.read()
        self.size = len(self.data)

    def draw(self):
        self.button = Button(self, text='Exit', relief='groove', \
        overrelief='raised', anchor='s', command=self.confirm_exit, \
        font=self.style.font)
        self.button.pack(side='top')
        self.text = ScrolledText(self, width=100, height=50, \
        font=self.style.font)
        # text area is not editable. ctrl-q and alt-f4 still quit parent
        self.text.bind("<Key>", lambda e: "break")
        self.text.config(background='#000000')
        self.text.config(foreground='#EFEFEF')
        self.text.pack(fill=BOTH)
        self.text.insert(END, self.data)
        self.after(100, self.poll)

    def confirm_exit(self):
        try:
            os.kill(int(self.pids[0]), 0)
        except OSError:
            sys.exit(0)
        else:
            if tkMessageBox.askyesno(message=self.quit_msg):
                for pid in self.pids:
                    try:
                        os.kill(int(pid), 15)
                        os.wait()
                    except OSError:
                        pass
                if os.path.exists(self.filename):
                    os.remove(self.filename)
                sys.exit(1)

    def poll(self):
        if not os.path.exists(self.filename):
            sys.exit(1)
        if os.path.getsize(self.filename) > self.size:
            data = self.file.read()
            self.size = self.size + len(data)
            self.text.insert(END, data)
            self.text.yview_pickplace("end")
        self.after(100,self.poll)

    def run(self):
        self.draw()
        self.mainloop()


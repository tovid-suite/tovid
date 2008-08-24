#!/usr/bin/env python
# confirmdialog.py

from Tkinter import *
import sys, os
from libtovid.metagui import Style


class AppDialog(Frame):
    def __init__(self, parent):
        Frame.__init__(self,parent)

        self.parent = parent
        # get metagui font configuration
        self.inifile = os.path.expanduser('~/.metagui/config')
        self.style = Style()
        self.style.load(self.inifile)

    def run(self):
        self.mainloop()

class ConfirmDialog(AppDialog):
    """A generic dialog class that allows you to make a dialog with single or
    multiple buttons, and a choice of text or image (GIF only). Example:

    from Tkinter import Tk
    from libtovid.appdialogs import ConfirmDialog

    btns='yes','no','maybe'
    root = Tk()
    a = ConfirmDialog(root, 'Dialog', ', btns, '/home/me/file.gif')
    a.run()

    The exit codes of the buttons start at 0 and increment
    """
    def __init__(self, parent, title='', text='', button_text='', image=''):
        AppDialog.__init__(self,parent)

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

        # get metagui font configuration
        self.inifile = os.path.expanduser('~/.metagui/config')
        self.style = Style()
        self.style.load(self.inifile)
        # draw the title
        self.parent.title(self._title)

        # draw the text or image
        # for the moment the dialog can have text OR image, not both
        if self.image:
            self.label1 = Label(bd=2, relief='groove')
            self.label1.pack(padx=20, pady=20, side='top')
        elif self.text:
            label2 = Label(text=self.text, font=self.style.font, \
            justify='left', padx=20, pady=20)
            label2.pack(side='top', fill='both', expand=1)

        # draw the button(s) in a frame
        frame = Frame(self.parent)
        buttons = []
        for index, item in enumerate(self.button_text):
            button = Button(frame, text=item, relief='groove', overrelief='raised', \
            anchor='s', command=lambda index=index:sys.exit(index), \
            font=self.style.font)
            button.pack(side='left')
        frame.pack(side='bottom')

    def set_image(self):
        self.img = PhotoImage(file=self.image)
        self.label1.config(image=self.img)

    def run(self):
        if self.image:
            self.set_image()
        self.mainloop()


import time, tkMessageBox
from ScrolledText import ScrolledText

class LogViewer(AppDialog):
        """This class allows you to tail an application log which will be
        embedded in a tkinter window. It takes the following parameters:
        filename: the application log to 'tail'.
        app: the application which this viewer is associated with.
        processes:  the pid of the application.  On pressing the exit button
        or closing the window using window manager methods, the pid will be
        killed if it is still active.

        """
    def __init__(self, parent, filename, app, processes):
        AppDialog.__init__(self,parent)

        self.app = app
        self.parent.title(self.app)
        self.filename = filename
        self.pids = []
        self.parent.protocol("WM_DELETE_WINDOW", lambda:self.confirm_exit())
        self.parent.bind('<Control-q>', lambda e, : self.confirm_exit())
        if type(processes) == tuple:
            self.pids.extend(processes)
        else:
            self.pids.append(processes)
        self.file = open(self.filename, 'r')
        self.button = Button(text='Exit', relief='groove', overrelief='raised', \
        anchor='s', command=self.confirm_exit, font=self.style.font)
        self.button.pack(side='top')
        self.text = ScrolledText(parent, width=100, height=40, \
        font=self.style.font)
        # text area is not editable. ctrl-q and alt-f4 still quit parent
        self.text.bind("<Key>", lambda e: "break")
        self.text.pack(fill=BOTH)
        data = self.file.read()
        self.size = len(data)
        self.text.insert(END, data)
        self.after(100, self.poll)

    def confirm_exit(self):
        try:
            os.kill(self.pids[0], 0)
        except OSError:
            sys.exit(0)
        else:
            if tkMessageBox.askyesno(message=self.app + \
            " is still running,\nThis will quit the program !\nExit now?"):
                for pid in self.pids:
                    try:
                        os.kill(pid, 15)
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


from Tkinter import *
import linecache

class Counter(AppDialog):
    """This class provides a counter that reads data from a file in /tmp.
    The following options exist:
    filename:
        the name of the tmp file that your controlling script will
        use for the counts (only 1st line of file is read)
    total:
        the final number of the count.  The counter will exist when this
        is reached.
    embedded(boolean)
        for embedded counters, the labels are all on one line.  The default
        is 3 lines, with the count in a sunken frame.

    The counter file must contain either a single number, or if you wish, the
    top and bottom labels are configurable by passing in label text as well.
    To do this the temp file must contain 2 or  more fields followed by a '|'
    separator, as in  count|label1|label2.  Field 1 is the count, and fields
    2 and 3 are the  new labels you  wish.  Example countfile contents:
    Using default labels:

            234

    Using configurable labels:

            3|Working on image|resizing
        

    """
    def __init__(self, parent, filename, total, embedded=True):
        AppDialog.__init__(self,parent)

        self.parent.config(relief='sunken')
        self.countfile= filename
        self.file = open(self.countfile, 'r')
        self.total = total
        self.frames = 'of',total
        self.w2text = StringVar()
        self.w1text = StringVar()
        self.w3text = StringVar()
        self.lastdata = ''
        self.embedded = embedded
        if self.embedded:
            self.packside='left'
            self.relief=None
        else:
            self.packside='top'
            self.relief = 'sunken'
        # a label for the counter
        frame = Frame(self.parent, relief='groove')
        frame.pack(side=self.packside, padx=5, pady=5)
        self.w1 = Label(frame, textvariable=self.w1text)
        #self.w1text.set('processing frame')
        self.w1.pack(side=self.packside)
        cfont = list(self.style.font)
        c = int(self.style.font[1])+4
        cfont[1]=str(c)
        self.w2 = Label(frame, relief=self.relief, textvariable=self.w2text, \
        font=cfont, width=len(str(self.total)))
        self.w2.pack(side=self.packside)
        self.w3 = Label(frame, textvariable=self.w3text)
        #self.w3text.set(self.frames)
        self.w3.pack(side=self.packside)

        # poll file for data
        self.update_idletasks
        self.data = linecache.getline(self.countfile, 1)
        self.data = self.data.strip()
        self.after(100, self.poll)

    def _config(self, args):
        self.w1text.set(args[0])
        if len(args) == 2:
            self.w3text.set(args[1])

    def _exit(self):
        self.w2.update_idletasks()
        time.sleep(1)
        sys.exit(0)
        
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
                self._config(List[1:len(List)])
                # set the numeric counter (w2)
                self.w2text.set(List[0])
            self.lastdata = self.data

        if self.data == self.total:
            # reset counter to empty string
            f = open(self.countfile,"w")
            f.writelines('||')
            f.close()
            if not self.embedded:
                self._exit()

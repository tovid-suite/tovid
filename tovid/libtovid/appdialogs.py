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

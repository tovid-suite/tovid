#!/usr/bin/env python
# counter.py

from Tkinter import *
import sys, os, time, linecache

class Counter(Frame):
    """For the moment this is a command line script that provides
        a counter that reads data from a file in /tmp.
        The following options exist:
        filename:
            the name of the tmp file that your controlling script will
            use for the counts (only 1st line of file is read)
        total:
            the final number of the count.  The counter will exist when this
            is reached.
        label_mode:
            'static' mode:
                (the default), Only a single number is read
                from the text file.
                This would yield a counter like so:

                ____________________
                | Processing frame |
                |       ______     |
                |       | 234|     |
                |       -----      |
                |                  |
                |       of 600     |
                --------------------

            'dynamic' mmode:
                allows configuration of the 
                top and bottom labels and requires the tmp file to contain 1 or
                more fields followed by a ':' separator, as in count:label1:label2.
                Field 1 is the count, and fields 2 and 3 are the new labels you 
                wish.  Example countfile contents:

                3:working on image:resizing

                This would yeild a counter like so:
                _________________
                |working on image|
                |       _ ___    |
                |      |  3 |    |
                |       ----     |
                |                |
                |    resizing    |
                ------------------

    """
    def __init__(self, parent, filename, total, label_mode):
        Frame.__init__(self,parent)

        self.parent = parent
        self.parent.config(relief='sunken')
        self.parent.title('Count')
        self.countfile= filename
        self.label_mode = label_mode
        self.file = open(self.countfile, 'r')
        self.total = total
        self.frames = 'of',total
        self.w2text = StringVar()
        self.w1text = StringVar()
        self.w3text = StringVar()
        self.lastdata = ''
        # a label for the counter
        self.w1 = Label(textvariable=self.w1text)
        self.w1text.set('processing frame')
        self.w1.pack()
        self.w2 = Label(relief='sunken', textvariable=self.w2text, \
        font=('Helvetica', 20, 'bold'), width=len(str(self.total)))
        self.w2.pack()
        self.w3 = Label(textvariable=self.w3text)
        self.w3text.set(self.frames)
        self.w3.pack()

        # poll file for data
        self.update_idletasks
        self.data = linecache.getline(self.countfile, 1)
        #self.data = self.data.strip()
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
            if self.label_mode == 'static':
                self.w2text.set(self.data)
            else:
                List = self.data.split( ':' )
                # set the text labels (w1 and w3)
                self._config(List[1:len(List)])
                # set the numeric counter (w2)
                self.w2text.set(List[0])
            self.lastdata = self.data
        if self.data == self.total:
            # reset count file to empty string
            f = open(self.countfile,"w")
            f.writelines('')
            f.close()

            self._exit()

if __name__ == "__main__":
    root = Tk()
    counter = Counter(root, sys.argv[1], sys.argv[2], sys.argv[3])
    counter.mainloop()

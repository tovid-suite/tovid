#! /usr/bin/env python

# ===========================================================
# GOpts
# ===========================================================

# A little dumb test-GUI for TDL options

import Tkinter
import TDL

class GOpts:

    def __init__(self, master):

        frame = Tkinter.Frame(master)
        frame.pack()

        lang = TDL.TDL()

        # Create widgets for TDL element definitions
        # (For now, just MenuDef)
        curElem = lang.elemdefs[ 'Menu' ]
        
        self.widgets = []
        for opt in curElem.optiondefs:
            lbl = Tkinter.Label( frame, text = opt.name )
            lbl.pack( side = 'top' )
            # Show a checkbox for boolean options
            # Show a text box for unary options
            val = Tkinter.Entry( frame )
            val.pack( side = 'left' )

        self.button = Tkinter.Button(frame, text = "Quit", command=frame.quit)
        self.button.pack(side='left')


root = Tkinter.Tk()

app = GOpts(root)

root.mainloop()

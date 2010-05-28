#!/usr/bin/env python
# a scratchpad for developing a class based wizard from
# titleset-wizard.  Not much to look at here yet.
import os.path
import commands
import shlex
from Tkinter import *
from tkMessageBox import *
from base64 import b64encode
from subprocess import Popen, PIPE
from libtovid.metagui.support import \
  Style, get_photo_image, show_icons, PrettyLabel
from libtovid.util import trim

# Wizard is a base, unchanging frame hold the wizard pages commands that are
# processed and written out. It will hold the [Next] and [Exit] buttons as well
# as the functions they run. As such it will need to have a list of all of the
# pages so it can pack and unpack them.
class Wizard(Frame):
    
    def __init__(self, master, text, icon):
        Frame.__init__(self, master)
        self.pages = []
        self.index = 0
        self.text = text
        self.icon = icon
        self.master = master
        self.commands = []
        # button frame
        self.button_frame = Frame(master)
        self.button_frame.pack(side='bottom', fill=X, expand=1,  anchor='se')
        self.exit_button = Button(self.button_frame, text='Exit', \
          command=self.confirm_exit)
        self.exit_button.pack(side='left', anchor='sw')
        self.next_button = Button(self.button_frame, text='Next>>>', \
          command=self.next)
        self.next_button.pack(side='right', anchor='se')
        # frame for icon and status display
        self.frame1 = Frame(master)
        self.frame1.pack(side='left', anchor='nw', padx=10, pady=80)
        inifile = os.path.expanduser('~/.metagui/config')
        style = Style()
        style.load(inifile)
        self.font = style.font
        self.draw()

    def draw(self):
        # get fonts
        font = self.font
        heading_font = self.get_font(font, size=font[1]+8, _style='bold')
        lrg_font = self.get_font(font, size=font[1]+4, _style='bold')
        medium_font = self.get_font(font, size=font[1]+2)
        bold_font = self.get_font(font, _style='bold')
        if self.text:
            txt = self.text.split('\n')
            applabel1 = Label(self.frame1, text=txt[0], font=lrg_font)
            applabel1.pack(side='top', fill=BOTH, expand=1, anchor='nw')
        # icons and image
        if os.path.isfile(self.icon):
            background = self.master.cget('background')
            img = get_photo_image(self.icon, 0, 0, background)
            self.img = img
            # Display the image in a label on all pages
            img_label = Label(self.frame1, image=self.img)
            img_label.pack(side=TOP, fill=BOTH, expand=1, anchor='nw', pady=40)
            # If Tcl supports it, generate an icon for the window manager
            show_icons(self.master, img_file)
        # No image file? Print a message and continue
        else:
            print('%s does not exist' % img_file)
        # if 2 lines of text for image, split top and bottom
        if self.text and len(txt) > 1:
            applabel2 = Label(self.frame1, text=txt[1], font=lrg_font)    
            applabel2.pack(side='top', fill=BOTH, expand=1, anchor='nw')
            
        
    def make_widgets(self):
        pass

    def next(self):
        self.pages[self.index].hide_page()
        self.index += 1
        self.pages[self.index].frame.pack(side='right')
        self.pages[self.index].show_page()

    def set_pagelist(self, pages):
        '''Set list of wizard page objects in Controlling Wizard page'''
        self.pages = pages

    def get_font(self, font_descriptor, name='', size='', _style=''):
        """Get metagui font configuration
        """
        font = [name, size, _style]
        for i in range(len(font_descriptor)):
            if not font[i]:
                font[i] = font_descriptor[i]
        return tuple(font)

    def show_status(status):
        """Show status label on all pages, with timeout
        """
        if status == 0:
            text='\nOptions saved!\n'
        else:
            text='\nCancelled!\n'
        status_frame = Frame(frame1, borderwidth=1, relief=RAISED)
        status_frame.pack(pady=80)
        label1 = Label(status_frame, text=text, font=medium_font, fg='blue')
        label1.pack(side=TOP)
        label2 = Label(status_frame, text='ok', borderwidth=2, relief=GROOVE)
        label2.pack(side=TOP)
        tk.after(1000, lambda: label2.configure(relief=SUNKEN))
        tk.after(2000, lambda: status_frame.pack_forget())

    def confirm_exit(event=None):
        """Exit the GUI, with confirmation prompt.
        """
        if askyesno(message="Exit?"):
            # set is_running to false so the gui doesn't get run
            #is_running.set(False)
            # waitVar may cause things to hang, spring it
            #setVar()
            quit()


class WizardPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        Frame.pack(master)
        self.master = master
        wizard = self.master
        self.make_widgets()

    def make_widgets(self):
        pass
        
class Page1(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(wizard)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')
        # page1 is packed by default
        self.show_page()

    def show_page(self):
        text = '''INTRODUCTION

        Welcome to the tovid titleset wizard.  We will be making a complete DVD,
        with multiple levels of menus including a root menu (VMGM menu) and
        lower level titleset menus.  We will be using 'tovid gui', which uses
        the 'todisc' script.  Any of these menus can be either static or
        animated, and use thumbnail menu links or plain text links.  Titleset
        menus can also have chapter menus.

        Though the sheer number of options can be daunting when the GUI first
        loads, it is important to remember that there are very few REQUIRED
        options, and in all cases the required options are on the opening tab.  
        The required options will be listed for you for each run of the GUI.

        But please have fun exploring the different options using the preview
        to test.  A great many options of these menus are configurable, 
        including fonts, shapes and effects for thumbnails, fade-in/fade-out
        effects, "switched menus", the addition of a "showcased" image/video, 
        animated or static background image or video, audio background ... 
        etc.  There are also playback options including the supplying of
        chapter points, special navigation features like "quicknav", and
        configurable DVD button links.
        '''
        text = trim(text)
        self.label = PrettyLabel(self.frame, text, wizard.font)
        self.label.pack(fill=BOTH, expand=1, anchor='nw')

    def hide_page(self):
        self.frame.pack_forget()

class Page2(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(wizard)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')

    def show_page(self):
        text = '''GENERAL OPTIONS

        When you press the  [Next >>>]  button at the bottom of the wizard, we
        will start the GUI and begin with general options applying to all
        titlesets.  For example you may wish to have all menus share a common
        font and fontsize of your choosing, for the menu link titles and/or the
        menu title.

        The only REQUIRED option here is specifying an Output directory at the
        bottom of the GUI's main tab.  Options you enter will be overridden if
        you use the same option again later for titlesets.

        After making your selections, press [ Save to wizard ] in the GUI

        Press  [Next >>>]  to begin ...
        '''
        text = trim(text)
        self.label = PrettyLabel(self.frame, text, wizard.font)
        self.label.pack(fill=BOTH, expand=1, anchor='nw')

if __name__ == '__main__':
    tovid_prefix = commands.getoutput('tovid -prefix')
    img_file = os.path.join(tovid_prefix, 'lib', 'tovid', \
      'titleset-wizard.png')
    root = Tk()
    root.minsize(width=800, height=660)
    wizard = Wizard(root, 'Tovid\nTitleset Wizard', img_file)
    page1 = Page1(wizard)
    page2 = Page2(wizard)
    wizard.set_pagelist([page1, page2])
    mainloop()

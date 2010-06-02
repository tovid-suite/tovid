#!/usr/bin/env python
# a scratchpad for developing a class based wizard from
# titleset-wizard.  Not much to look at here yet.
import os.path
import shlex
import commands
from Tkinter import *
from tkSimpleDialog import askstring
from subprocess import Popen, PIPE
from libtovid.metagui import Style
from libtovid.metagui.support import PrettyLabel, show_icons, get_photo_image
from libtovid.cli import _enc_arg
from tkMessageBox import *
from time import sleep
from tempfile import mktemp
from sys import argv, exit
from base64 import b64encode
from libtovid.util import trim

# Wizard is a base, unchanging frame hold the wizard pages commands that are
# processed and written out. It will hold the [Next] and [Exit] buttons as well
# as the functions they run. As such it will need to have a list of all of the
# pages so it can pack and unpack them.
class Wizard(Frame):
    def __init__(self, master, text, icon):
        Frame.__init__(self, master)
        self.pages = []
        self.index = IntVar()
        self.text = text
        self.icon = icon
        self.master = master
        self.root = self._root()
        self.commands = []
        # is_running for cancelling run_gui if exit is called
        self.is_running = BooleanVar()
        self.is_running.set(True)
        # wait on [Next>>>] being pushed to continue titleset loop
        self.waitVar = BooleanVar()
        self.waitVar.set(False)
        # bindings for exit
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.root.bind('<Control-q>', self.confirm_exit)

        # button frame
        self.button_frame = Frame(master)
        self.button_frame.pack(side='bottom', fill='x', expand=1,  anchor='se')
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
        self.lrg_font = self.get_font(font, size=font[1]+4, _style='bold')
        self.medium_font = self.get_font(font, size=font[1]+2)
        self.heading_font = self.get_font(font, size=font[1]+8, _style='bold')
        if self.text:
            txt = self.text.split('\n')
            app_label1 = Label(self.frame1, text=txt[0], font=self.heading_font)
            app_label1.pack(side='top', fill=BOTH, expand=1, anchor='nw')
        # icons and image
        if os.path.isfile(self.icon):
            background = self.root.cget('background')
            img = get_photo_image(self.icon, 0, 0, background)
            self.img = img
            # Display the image in a label on all pages
            img_label = Label(self.frame1, image=self.img)
            img_label.pack(side=TOP, fill=BOTH, expand=1, anchor='nw', pady=20)
            # If Tcl supports it, generate an icon for the window manager
            show_icons(self.master, img_file)
        # No image file? Print a message and continue
        else:
            print('%s does not exist' % img_file)
        # if 2 lines of text for image, split top and bottom
        if self.text and len(txt) > 1:
            app_label2 = Label(self.frame1, text=txt[1], font=self.lrg_font)
            app_label2.pack(side='top', fill=BOTH, expand=1, anchor='nw')

    def make_widgets(self):
        pass

    def next(self):
        index = self.index.get()
        try:
            self.pages[index].hide_page()
            self.index.set(index + 1)
            self.pages[index+1].frame.pack(side='right')
            self.pages[index+1].show_page()
        except IndexError:
            pass

    def set_pages(self, pages):
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

    def show_status(self, status):
        """Show status label on all pages, with timeout
        """
        if status == 0:
            text='\nOptions saved!\n'
        else:
            text='\nCancelled!\n'
        font = self.medium_font
        status_frame = Frame(self.frame1, borderwidth=1, relief=RAISED)
        status_frame.pack(pady=40)
        label1 = Label(status_frame, text=text, font=font, fg='blue')
        label1.pack(side=TOP)
        label2 = Label(status_frame, text='ok', borderwidth=2, relief=GROOVE)
        label2.pack(side=TOP)
        self.root.after(1000, lambda: label2.configure(relief=SUNKEN))
        self.root.after(2000, lambda: status_frame.pack_forget())

    def confirm_exit(self, event=None):
        """Exit the GUI, with confirmation prompt.
        """
        if askyesno(message="Exit?"):
            # set is_running to false so the gui doesn't get run
            self.is_running.set(False)
            # waitVar may cause things to hang, spring it
            self.set_waitvar()
            quit()

    def set_waitvar(self):
        """Set a BooleanVar() so tk.wait_var can exit
        """
        self.waitVar.set(True)

class WizardPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        Frame.pack(master)
        self.master = master
        self.root = self._root()
        # a temp file name for the final script name if it exists already
        curdir = os.path.abspath('')
        self.newname = \
          mktemp(suffix='.bash', prefix='todisc_commands.', dir=curdir)
        # get tovid prefix
        tovid_prefix = commands.getoutput('tovid -prefix')
        self.tovid_prefix = os.path.join(tovid_prefix, 'lib', 'tovid')
        os.environ['PATH'] = self.tovid_prefix + os.pathsep + os.environ['PATH']
        # the script we will be using for options
        cur_dir = os.path.abspath('')
        self.script_file = cur_dir + '/todisc_commands.bash'
        # get script header
        shebang = '#!/usr/bin/env bash'
        _path = 'PATH=' + self.tovid_prefix + ':$PATH'
        _cmd = ['tovid', '--version']
        _version = Popen(_cmd, stdout=PIPE).communicate()[0].strip()
        identifier = '# tovid project script\n# tovid version %s' % _version
        self.header = '%s\n\n%s\n\n%s\n\n' % (shebang, identifier, _path )
        # initialize widgets, but don't show yet
        self.make_widgets()


    def make_widgets(self):
        pass

    def show_page(self):
        self.draw()

    def run_gui(self, args=[], index='', script=''):
        """Run the tovid GUI, collecting options, and saving to wizard
        """
        title = 'load saved script'
        script = 'todisc_commands.bash'
        set_env = []
        if index:
            print "DEBUG: setting os.environ['METAGUI_WIZARD'] =", "%s" %index
            os.environ['METAGUI_WIZARD'] = '%s' %index
        cmd = ['todiscgui'] + args
        todiscgui_cmd = Popen(cmd, stdout=PIPE)
        # sleep to avoid the 'void' of time before the GUI loads
        sleep(0.5)
        if self.root.state() is not 'withdrawn':
            self.root.withdraw()
        status = todiscgui_cmd.wait()
        if status == 200:
        # if script doesn't exist prompt for load.
            if os.path.exists(self.script_file):
                script = self.script_file
            else:
                err = 'A problem has occured with saving your options.\n'
                err += 'The saved script file was not found.\n'
                err += 'Please submit a bug report'
                showerror(message=err)
                return
            # Read lines from the file and reassemble the command
            todisc_opts = self.script_to_list(script)
            os.remove(script)
        else:
            todisc_opts  = []
        return todisc_opts

    def page_controller(self):
        self.master.next()

    def script_to_list(self, infile):
        """File contents to a list, trimming '-from-gui' and header
        """
        add_line = False
        command = ''
        for line in open(infile, 'r'):
            if line.startswith('-'):
                add_line = True
            if add_line and not line.startswith('-from-gui'):
                line = line.strip()
                command += line.rstrip('\\')
        return shlex.split(command)

    def write_script(self):
        """Write out the final script to todisc_commands.bash
        """
        commands = self.master.commands
        header = self.header
        cmdout = open(self.script_file, 'w')
        # add the shebang, PATH, and 'todisc \' lines
        cmdout.writelines(header)
        # flatten the list
        all_lines = [line for sublist in commands for line in sublist]
        # put the program name back into the beginning of the list
        all_lines.insert(0, 'todisc')
        words = [_enc_arg(arg) for arg in all_lines]
        all_lines = words
        # write every line with a '\' at the end, except the last
        for line in all_lines[:-1]:
            cmdout.write(line + ' \\\n')
        # write the last line
        cmdout.write(all_lines[-1])
        cmdout.close()

    def trim_list_header(self, cmds):
            """Trim header (items before 1st '-' type option) from a list
            """
            # remove shebang, identifier and PATH
            try:
                while not cmds[0].startswith('-'):
                    cmds.pop(0)
            except IndexError:
                pass
            return cmds

    def get_chunk(self, items, start, end):
        """Extract a chunk [start ... end] from a list, and return the chunk.
        The original list is modified in place.
        """
        # Find the starting index and test for 'end'
        try:
            index = items.index(start)
            items.index(end)
        # If start or end isn't in list, return empty list
        except ValueError:
            return []
        # Pop items until end is reached
        chunk = []
        while items and items[index] != end:
            chunk.append(items.pop(index))
        # Pop the last item (==end)
        chunk.append(items.pop(index))
        return chunk

    def get_list_args(self, items, option):
        """Get option arguments from a list (to next item starting with '-')
        """
        try:
            index = items.index(option)
        # If item isn't in list, return empty list
        except ValueError:
            return []
        # Append items until end is reached
        chunk = []
        try:
            while items and not items[index+1].startswith('-'):
                chunk.append(items[index+1])
                index += 1
        except IndexError:
            pass
        return chunk

    def see_me(self, widget):
        """Bring attention to widget by changing text colour
        """
        # 3000 and 4000 ms because show_status uses up 3000 already
        self.root.after(3000, lambda: widget.configure(foreground='blue'))
        widget.update()
        self.root.after(4000, lambda: widget.configure(foreground='black'))


    def refill_listbox(self, listbox, opts):
        """Repopulate the rerun listbox with option list titles
        """
        if '-titles' in opts:
            new_titles = self.get_list_args(opts, '-titles')
        else:
            new_titles = opts
        listbox.delete(0, END)
        # insert or reinsert options list into titleset listbox
        listbox.insert(END, 'General options')
        listbox.insert(END, 'Root menu')
        numtitles = len(new_titles)
        #listbox.configure(height=numtitles+2)
        for i in xrange(numtitles):
            listbox.insert(END, new_titles[i])

    def rename_script(self):
        # if todisc_commands.bash exists in current dir, prompt for rename
        rename_msg = 'The option file we will use:\n' + \
        'todisc_commands.bash\n' + \
        'exists in the current directory.\n' + \
        'It will be renamed to:\n' + \
        '%s' + \
        '\nProceed ?'
        rename_msg = rename_msg % (os.path.basename(self.newname))
        if askokcancel(message=rename_msg):
            os.rename(self.script_file, self.newname)
        else:
            self.master.show_status(1)
            return


        
class Page1(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(self.master)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')
        # page1 is packed by default
        if len(argv) < 2:
            self.draw()

    def draw(self):
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
        self.label = PrettyLabel(self.frame, text, self.master.font)
        self.label.pack(fill=BOTH, expand=1, anchor='nw')
        # set next button to page_controller()
        self.master.next_button.configure(command=self.page_controller)

    def page_controller(self):
        index = self.master.index.get()
        wizard = self.master
        wizard.next()

    def hide_page(self):
        self.frame.pack_forget()
    

class Page2(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(self.master)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')

    def draw(self):
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
        self.label = PrettyLabel(self.frame, text, self.master.font)
        self.label.pack(fill=BOTH, expand=1, anchor='nw')
        # set next button to page_controller()
        self.master.next_button.configure(command=self.page_controller)

    def page_controller(self):
        index = self.master.index.get()
        wizard = self.master
        move = True
        cmds = self.run_gui([], index)
        # append to list and go to next page unless GUI was cancelled out of
        if not cmds:
            status = 1
            move = False
        else:
            status = 0
            cmds = [l for l in cmds if l]
            wizard.commands.append(cmds)
        wizard.show_status(status)
        self.root.deiconify()
        if move:
            wizard.next()

    def hide_page(self):
        self.frame.pack_forget()

class Page3(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(self.master)
        self.frame.pack(side='right')

    def draw(self):
        text = '''ROOT MENU (VMGM)

        Now we will save options for your root (VMGM) menu.  The only REQUIRED
        option is the titleset titles.  Since you can not save titles in the
        GUI without loading videos you need to enter them here.  These titleset
        names will appear as menu titles for the respective menu in your DVD.

        Enter the names of your titlesets, one per line, pressing <ENTER> each
        time.  Do not use quotes unless you want them to appear literally in
        the title.

        Press  [Next >>>]  when you are finished, and the tovid gui will come
        up so you can enter any other options you want.  You can not enter
        video files here, but most other options can be used.  There are now no
        REQUIRED options however, as you will have already entered your root
        menu link titles.

        After making your selections, press [ Save to wizard ] in the GUI
        '''
        text = trim(text)
        label1 = PrettyLabel(self.frame, text, self.master.font, height=18)
        label1.pack(fill='both', expand=True, side='top', anchor='nw')
        # create the listbox (note that size is in characters)
        self.titlebox = TitleBox(self.frame, text="Root 'menu link' titles")
        # set next button to page_controller()
        self.master.next_button.configure(command=self.page_controller)

    def save_list(self):
        """Save the current listbox contents
        """
        # get a list of listbox lines
        temp_list = list(self.titlebox.get(0, END))
        return [ l for l in temp_list if l]

    def page_controller(self):
        run_cmds = list(self.titlebox.get(0, END))
        run_cmds = [l for l in run_cmds if l]
        if len(run_cmds) < 2:
            showerror(message=\
              'At least two titlesets (titles) must be defined')
            return
        else:
            # withdraw the wizard and run the GUI, collecting commands
            run_cmds.insert(0,  '-titles')
            index = self.master.index.get()
            get_commands = self.run_gui(run_cmds, index)
            # append to list and go to next page unless GUI was cancelled out of
            if not get_commands:
                status = 1
                self.root.deiconify()
                return
            else:
                status = 0
                self.trim_list_header(get_commands)
                cmds = ['-vmgm']
                cmds.extend(get_commands)
                cmds.append('-end-vmgm')
                self.master.commands.append(cmds)
                print self.master.commands[1]
            self.master.next()
            self.root.deiconify()
            self.master.show_status(status)


    def hide_page(self):
        self.frame.pack_forget()


class Page4(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)

    def make_widgets(self):
        self.frame = Frame(self.master)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')

    def draw(self):
        text1 = '''TITLESET MENUS

        Okay, now you will enter options for each of your titlesets.  
        The only REQUIRED option here is to load one or more video
        files, but of course you should spruce up your menu by
        exploring some of the other options!  The menu title for each
        has been changed to the text you used for the menu links in 
        the root menu - change this to whatever you want.

        Follow the simple instructions that appear in the next and 
        subsequent pages: 

        you will need to press  [Next >>>]  for each titleset.
        '''
        text1 = trim(text1)
        self.label1 = PrettyLabel(self.frame, text1, self.master.font)
        self.label1.pack(fill='both', expand=True, side='top', anchor='nw')
        self.frame2 = Frame(self.frame, borderwidth=2, relief=GROOVE)
        self.label2 = Label(self.frame2, text='', font=self.master.font,
          justify=LEFT, padx=10, pady=10)
        self.label2.pack(fill='both', expand=True, side='top', anchor='nw')
        # set next button to page_controller()
        self.master.next_button.configure(command=self.page_controller)

    def page_controller(self):
        # FIXME this will run the gui for titlesets in a loop
        # for now it just goes to the next page
        self.root.withdraw()
        options_list = self.get_list_args(self.master.commands[1], '-titles')
        numtitles = len(options_list)
        print 'numtitles are: ', numtitles
        # set [Next >>>] button to set waitVar, allowing loop to continue
        self.master.next_button.configure(command=self.master.set_waitvar)

        for i in range(numtitles):
            run_cmds = ['-menu-title']
            run_cmds.append(options_list[i])
            if i < numtitles:
                text2 = 'Now we will work on titleset %s:\n"%s"\n\n'
                text2 += 'Press  [Next >>>]  to continue'
                text2 = text2 % (int(i+1), options_list[i])
                self.label2.configure(text=text2)
                self.frame2.pack()
                self.see_me(self.label2)
            # withdraw the wizard and run the GUI, collecting commands
            self.root.deiconify()
            # pressing 'Next' sets the waitVar and continues
            self.master.wait_variable(self.master.waitVar)
            if self.master.is_running.get() == 1:
                get_commands = self.run_gui(run_cmds, '%s' %(i+3))
            else:
                quit()
            if get_commands:
                status = 0
                get_commands = self.trim_list_header(get_commands)
                # wrap the commands in titleset 'tags', then write out script
                cmds = ['-titleset']
                cmds.extend(get_commands)
                cmds.append('-end-titleset')
                self.master.commands.append(cmds)
            else:
                status = 0
            self.master.show_status(status)
        self.write_script()
        self.master.next_button.configure(command=self.master.next)
        self.root.deiconify()
        self.master.next()

    def hide_page(self):
        self.frame.pack_forget()

class Page5(WizardPage):
    def __init__(self, master):
        WizardPage.__init__(self, master)
        print 'len(argv) is: ', len(argv)
        if len(argv) > 1:
            self.set_project_commands()
            self.draw()
            # draw must be called before load_project
            self.load_project()
 
    def make_widgets(self):
        self.frame = Frame(self.master)
        self.frame.pack(side='right', fill=BOTH, expand=1, anchor='nw')

    def draw(self):
        text = '''
        If you are happy with your saved options, now you can either 
        choose to run the script now in an xterm, or exit and run it 
        later in your favorite terminal.

        You can run it with:
        bash %s

        You may also edit the file with a text editor but do not 
        change the headers (first 3 lines of text) or change the 
        order of the sections:

        1. General opts, 2. Root menu 3. Titleset menus

        You may also load the file back onto this page of the GUI and 
        make any changes you want, using the command:
        tovid titlesets %s

        Press [Run script now] or [Exit].
        ''' % (self.script_file, self.script_file)
        text = trim(text)
        self.heading_label = Label(self.frame, text='Finished',
          font=self.master.lrg_font)
        self.label = PrettyLabel(self.frame, text,
          self.master.font, height=18)
        self.label.pack(fill=BOTH, expand=1, anchor='nw')
        # create the listbox (note that size is in characters)
        frame_text = "Double-click item to edit with GUI, or select " + \
          "and  press [ Edit ] "
        frame2 = LabelFrame(self.frame, text=frame_text)
        self.listbox = Listbox(frame2)
        self.listbox.pack(side='top', fill='both', expand=1)
        frame2.pack(fill='y', expand=False)
        button_frame = Frame(frame2)
        button_frame.pack(fill=X, expand=1)
        button2 = Button(button_frame, text='Add titleset', \
          command=self.add_titleset)
        button2.pack(side=LEFT, anchor='w')
        button1 = Button(button_frame, text='Edit', command=self.rerun_options)
        button1.pack(side=LEFT, fill='x', expand=1)
        button3 = Button(button_frame, text='Remove titleset', \
          command=self.remove_titleset)
        button3.pack(side=RIGHT, anchor='e')
        # the 2nd index contains the titleset titles (VMGM menu)
        self.refill_listbox(self.listbox, self.master.commands[1])
        # set next button to run gui etc before moving forward
        self.master.next_button.configure(command=self.run_in_xterm)

    def add_titleset(self):
        pass

    def remove_titleset(Event=None):
        mess1='You can only remove titlesets'
        mess2='You must have at least 2 titlesets. Please add ' + \
          'a new titleset [ Add titleset ]  before deleting one'
        mess3='Please select a titleset to remove first'
        try:
            ind = int(self.listbox.curselection()[0])
            if ind < 2:
                showerror(message=mess1)
                return
            elif self.listbox.size() < 5:
                showerror(message=mess2)
                return
        except IndexError:
            if self.listbox.size() < 5:
                mess = mess3 + '\n\n' + mess2
            else:
                mess = mess3
            showerror(message=mess)
            return
        # get the index from listbox then delete it
        item = self.listbox.get(ind)
        self.listbox.delete(ind)
        # remove the menu title from vmgm options
        self.master.commands[1].remove(item)
        # delete that index from commands
        self.master.commands.pop(ind)
        # write out the script again
        self.write_script()

    def rerun_options(self, Event=None):
        """Run the gui with the selected options
        """
        # self.master is the WizardPage
        commands = self.master.commands
        try:
            index = int(self.listbox.curselection()[0])
        except IndexError:
            showerror(message='Please select an options line first')
            return
        rerun_opts = []
        os.environ['METAGUI_WIZARD'] = str(index+1)
        # the GUI doesn't understand the titleset type options
        remove = ['-vmgm', '-end-vmgm', '-titleset', '-end-titleset']
        options = [ i for i in commands[index] if not i in remove ]
        rerun_opts = self.run_gui(options, '%s' %(index+1))
        if rerun_opts:
            status = 0
            # trim header from todisc_cmds
            rerun_opts = self.trim_list_header(rerun_opts)
            # fill the listbox again if vmgm opts changed
            # add the 'tags' back around the option list if needed
            if index == 1:
                self.refill_listbox(self.listbox, rerun_opts)
                rerun_opts = ['-vmgm'] + rerun_opts + ['-end-vmgm']
            elif index >= 2:
                rerun_opts = ['-titleset'] + rerun_opts + ['-end-titleset']
            commands[index] = rerun_opts
            # rewrite the saved script file
            self.write_script()
        else:
            status = 1
        self.root.deiconify()
        self.master.show_status(status)

    def run_in_xterm(self):
        """Run the final script in an xterm, completing the project
        """
        if not askyesno(message="Run in xterm now?"):
            self.master.show_status(1)
            return
        script = self.script_file
        cmd = \
         ['xterm', '-fn', '10x20', '-sb', '-title', 'todisc', '-e', 'sh', '-c']
        wait_cmd = ';echo ;echo "Press Enter to exit terminal"; read input'
        tovid_cmd = 'bash %s' % script
        cmd.append(tovid_cmd + wait_cmd)
        self.root.withdraw()
        command = Popen(cmd, stderr=PIPE)
        self.root.deiconify()  

    def hide_page(self):
        self.frame.pack_forget()

    def set_project_commands(self):
        in_contents = self.script_to_list(argv[1])
        in_cmds = in_contents[:]
        all = [self.get_chunk(in_cmds, '-vmgm', '-end-vmgm')]
        while '-titleset' in in_cmds:
            all.append( self.get_chunk(in_cmds, '-titleset', '-end-titleset') )
        all.insert(0, in_cmds)
        self.master.commands = all

    def load_project(self):
        """Load a saved project script for editing with the wizard and GUI
        """
        self.heading_label.configure(text='Editing a saved project')
        error_msg = 'This is not a saved tovid project script\n' + \
          'Do you want to try to load it anyway?'
        if not '# tovid project script\n' in open(argv[1], 'r'):
            if not askyesno(message=error_msg):
                showinfo(message='Cancelled')
                quit()
        #self.set_project_commands()
        numtitles = len(self.master.commands[2:])
        menu_titles = []
        for l in self.master.commands[2:]:
            menu_titles.extend(self.get_list_args(l, '-menu-title'))
        print 'menu_titles are: ', menu_titles
        #self.listbox.pack(side=LEFT, anchor='w', fill=X, expand=1)
        self.refill_listbox(self.listbox, menu_titles)
        # write out todisc_commands.bash in current dir
        # if it exists in current dir, prompt for rename
        if os.path.exists(self.script_file):
            self.rename_script()
        self.write_script()
        return all

class TitleBox(Frame):
    '''A Listbox in a LabelFrame with Entry associated with it
       text: the label for the frame
    '''
    def __init__(self, master=None, text=''):
        Frame.__init__(self, master)
        self.master = master
        self.text = text
        self.draw()

    def draw(self):
        # create the listbox (note that size is in characters)
        frame1 = LabelFrame(self.master, text=self.text)
        frame1.pack(side='top', fill='y', expand=False)
        self.listbox = Listbox(frame1, width=50, height=12)
        self.listbox.pack(side='left', fill='y', expand=False, anchor='nw')
        self.get = self.listbox.get

        # create a vertical scrollbar to the right of the listbox
        yscroll = Scrollbar(frame1, command=self.listbox.yview, \
          orient='vertical')
        yscroll.pack(side='right', fill='y', anchor='ne')
        self.listbox.configure(yscrollcommand=yscroll.set)
        # use entry widget to display/edit selection
        self.enter1 = Entry(self.master, width=50)
        self.enter1.pack(fill='y', expand=False)
        # set focus on entry
        self.enter1.select_range(0, 'end')
        self.enter1.focus_set()
        # pressing the return key will update edited line
        self.enter1.bind('<Return>', self.set_list)
        self.listbox.bind('<ButtonRelease-1>', self.get_list)

    def set_list(self, event):
        """Insert an edited line from the entry widget back into the listbox
        """
        try:
            index = self.listbox.curselection()[0]
            # delete old listbox line
            self.listbox.delete(index)
        except IndexError:
            index = END
        # insert edited item back into self.listbox at index
        self.listbox.insert(index, self.enter1.get())
        self.enter1.delete(0, END)
        # don't add more than one empty index
        next2last = self.listbox.size() -1
        if not self.listbox.get(next2last) and not self.listbox.get(END):
            self.listbox.delete(END)
        # add a new empty index if we are at end of list
        if self.listbox.get(END):
            self.listbox.insert(END, self.enter1.get())
        self.listbox.selection_set(END)

    def get_list(self, event):
        """Read the listbox selection and put the result in an entry widget
        """
        try:
            # get selected line index
            index = self.listbox.curselection()[0]
            # get the line's text
            seltext = self.listbox.get(index)
            # delete previous text in enter1
            self.enter1.delete(0, END)
            # now display the selected text
            self.enter1.insert(0, seltext)
            self.enter1.focus_set()
        except IndexError:
            pass


if __name__ == '__main__':
    # get tovid prefix
    tovid_prefix = commands.getoutput('tovid -prefix')
    tovid_prefix = os.path.join(tovid_prefix, 'lib', 'tovid')
    os.environ['PATH'] = tovid_prefix + os.pathsep + os.environ['PATH']
    img_file = os.path.join(tovid_prefix, 'titleset-wizard.png')
    root = Tk()
    root.minsize(width=800, height=660)
    app = Wizard(root, 'Tovid\nTitleset Wizard', img_file)
    # instantiate pages
    page1 = Page1(app)
    page2 = Page2(app)
    page3 = Page3(app)
    page4 = Page4(app)
    page5 = Page5(app)
    # let main wizard instance know about all the pages
    pages = [page1, page2, page3, page4, page5]
    app.set_pages(pages)
    # run it
    try:
        mainloop()
    except KeyboardInterrupt:
        exit(1)

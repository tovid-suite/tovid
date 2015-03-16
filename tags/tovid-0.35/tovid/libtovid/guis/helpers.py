import time
import shlex
import re
import os
import fnmatch
from libtovid.metagui import *
from libtovid.metagui.control import _SubList
from libtovid.util import filetypes
from subprocess import Popen, PIPE
from tempfile import mkdtemp, mkstemp
from sys import stdout

try:
    from commands import getstatusoutput, getoutput
    import Tkinter as tk
except ImportError:
    # python 3
    from subprocess import getstatusoutput, getoutput
    import tkinter as tk

__all__ = [ 'VideoGui', 'SetChapters', 'Chapters', 'strip_all', 'to_title',
'find_masks', 'nodupes', 'video_filetypes', 'image_filetypes',
'visual_filetypes', 'dvd_video_files', 'av_filetypes', 'sys_dir',
'thumb_masks', 'home_dir', 'tovid_prefix', 'tovid_icon', 'os_path',
'heading_text', '_files_and_titles', '_out', 'CopyableInfo' ]


class VideoGui(tk.Frame):
    """A basic GUI to play video files.  It runs mplayer in slave mode
    so that commands can be sent to it via fifo.

    Without subclassing it only contains a 'play/pause button
    and an 'exit' button.
    """
    def __init__(self, master, args='', title='', callback=None):
        """Initialize GUI

           master
               widget that will conain this GUI
           args
               additional arguments to mplayer command, inserted
               at the end of the command just before the 'FILE' argument.
           title
               the wm title given to the master widget.
           callback
               a function run at program exit, before cleanup of temp files
        """
        tk.Frame.__init__(self, master)

        self.args = args
        self.show_osd = False
        if '-osdlevel 3' in args:
            self.show_osd = True
        self.master = master
        if title:
            try:
                self.master.title(title)
            except AttributeError:
                print("Error: " + \
                  "VideoGui master must be a root window for 'title' option")
        self.callback = callback
        self.v_width = 540
        self.v_height = 405
        self.is_running = tk.BooleanVar()
        self.is_running.set(False)
        self.pauseplay = tk.StringVar()
        self.pauseplay.set('Play')
        # temporary directory for fifo and other mplayer files
        self.make_tmps()
        self.draw()

    def make_tmps(self):
        """Make temporary directory containing fifo for mplayer commmands,
        editlist, and log
        """
        self.tempdir = mkdtemp(prefix='tovid-')
        self.cmd_pipe = os.path.join(self.tempdir, 'slave.fifo')
        self.editlist = os.path.join(self.tempdir, 'editlist')
        os.mkfifo(self.cmd_pipe)
        self.log = os.path.join(self.tempdir, 'mplayer.log')
        
    def draw(self):
        """Draw the GUI in self.master and get X11 identifier for container"""
        self.root_frame = tk.Frame(self)
        self.root_frame.pack(side='top', fill='both', expand=1, pady=20)
        self.container = tk.Frame(self.root_frame, bg='black', container=1, colormap='new')
        self.container.configure(width=self.v_width, height=self.v_height, bg='black')
        self.container.pack()
        # X11 identifier for the container frame
        self.xid = self.tk.call('winfo', 'id', self.container)
        self.add_widgets()

    def add_widgets(self):
        """Add buttons to the VideoGui.  Override this to customize buttons.
        root_frame has 'grab_set()' applied to it so make sure widgets go
        into this frame or they will not be functional!
        This function is called in draw()
        """
        button_frame = tk.Frame(self.root_frame)
        button_frame.pack(side='bottom', fill='x', expand=1)
        self.control_frame = tk.Frame(button_frame, borderwidth=1, relief='groove')
        self.control_frame.pack()
        self.load_button = tk.Button(self.control_frame,
            command=self.load, text='load video')
        self.load_button.pack(side='left')
        exit_button = tk.Button(self.control_frame, command=self.exit_mplayer, text='exit')
        self.pause_button = tk.Button(self.control_frame, command=self.pause,
                          width=12, textvariable=self.pauseplay)
        self.pause_button.pack(side='left')
        exit_button.pack(side='left', padx=5)
        self.mp_ctrls = [self.pause_button]
        self.toggle_controls('disabled', self.mp_ctrls)


    def identify(self, video):
        """Get information about video from mplayer -identify.
        Called by set_container()
        """
        
        cmd = 'mplayer -vo null -ao null -frames 5 -channels 6 -identify'
        cmd = shlex.split(cmd) + [video]
        output = Popen(cmd, stdout=PIPE, stderr=PIPE)
        return output.communicate()[0]

    def load(self, event=None):
        """Load a file to play in the GUI"""
        try:
            from tkFileDialog import askopenfilename
        except ImportError:
            # python 3
            from tkinter.filedialog import askopenfilename
        vid_name = askopenfilename()
        if vid_name:
            self.toggle_controls('normal', self.mp_ctrls)
            if self.pauseplay.get() == 'Pause':
                self.pauseplay.set('Play')
            self.run(vid_name)

    def set_container(self, video=None):
        """Get aspect ratio and set dimensions of video container.
           Called by run().
        """
        media_info = self.identify(video)
        asr = re.findall('ID_VIDEO_ASPECT=.*', str(media_info))
        # get last occurence as the first is 0.0 with mplayer
        if asr:
            asr = sorted(asr, reverse=True)[0].split('=')[1]
            try:
                asr = float(asr)
            except ValueError:
                asr = 0.0
        # get largest value as mplayer prints it out before playing file
        if asr and asr > 0.0:
            v_height = int(self.v_width/asr)
        else:
            # default to 4:3 if identify fails
            v_height = int(self.v_width/1.333)
        self.container.configure(width=self.v_width, height=v_height)

    def run(self, video):
        """Play video in this GUI using mplayer."""
        if video == None:
            self.toggle_controls('disabled', self.mp_ctrls)
            return
        elif not os.path.exists(video):
            try:
                from tkMessageBox import showerror
            except ImportError:
                from tkinter.messagebox import showerror
            showerror('Oops', video + ' does not exist')
            self.toggle_controls('disabled', self.mp_ctrls)
            self.master.master.withdraw()
        else:
            self.toggle_controls('enabled', self.mp_ctrls)
        # a new video has been loaded if no temp files, so make them
        if not os.path.exists(self.tempdir):
            self.make_tmps()
        # set the container size, then run the video
        self.set_container(video)
        command =  'mplayer -wid %s -nomouseinput -slave \
          -input nodefault-bindings:conf=/dev/null:file=%s \
          -edlout %s %s' \
          %(self.xid, self.cmd_pipe, self.editlist, self.args)
        self.command = shlex.split(command) + [video]

    def toggle_controls(self, state, widgets):
        """
        Enable/disable mplayer control widgets
        state is either 'normal' or 'disabled', widgets is an instance list
        """
        for widget in widgets:
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass

    def poll(self):
        """
        Check mplayer log output for 'End of file' and restart the video.
        This is necessary because otherwise Tkinter has no way of knowing
        mplayer is still running.  In this way mplayer must be sent a 'quit'
        explicity before exit. Use 'on_eof()' to run custom command when
        'End of file' is found.
        """
        if not self.is_running.get():
            return
        f = open(self.log, 'r')
        # seek to 50 bytes from end of file
        try:
            f.seek(-50, 2)
            if '(End of file)' in f.read():
                self.on_eof()
                # check for is_running again as on_oef() might set it to false
                if self.is_running.get():
                    cmd = Popen(self.command, stderr=open(os.devnull, 'w'), \
                      stdout=open(self.log, "w"))
                    if self.show_osd:
                        self.send('osd 3')
                    self.pause()
        # if file does not contain 50 bytes, do nothing
        except IOError:
            pass
        self.master.after(100, self.poll)


    def on_eof(self):
        """
        Run when 'End of file' discovered in mplayer output by poll().
        Override to run custom commands.
        Note: change is_running() variable to false to prevent looping of video.
        """
        pass

    def send(self, text):
        """Send command to mplayer's slave fifo"""
        if self.is_running.get():
            getstatusoutput('echo "%s"  > %s' %(text, self.cmd_pipe))

    def pause(self):
        """Send pause to mplayer via slave and set button var to opposite value"""
        # mplayer's 'pause' pauses if playing and plays if paused
        # pauseplay ==Play in pause mode, and ==Pause in play mode (button text)
        if self.is_running.get():
            if self.pauseplay.get() == 'Pause':
                self.pauseplay.set('Play')
            else:
                self.pauseplay.set('Pause')
            self.send('pause')
        else:
            # start the video for the 1st time
            cmd = Popen(self.command, stderr=open(os.devnull, 'w'), stdout=open(self.log, "w"))
            self.is_running.set(True)
            self.poll()
            # show osd time and remaining time
            if self.show_osd:
                self.send('osd 3')
            self.pauseplay.set('Pause')

    def exit_mplayer(self): # called by [done] button
        """
        Close mplayer if it is running, then exit, running callback if it exists
        """
        # unpause so mplayer doesn't hang
        if self.is_running.get():
            if self.pauseplay.get() == 'Play':
                self.send('mute 1')
                self.send('pause')
            self.send('quit')
            self.is_running.set(False)
        time.sleep(0.3)
        self.confirm_exit()

    def confirm_msg(self):
        mess = "osd_show_text 'please exit mplayer first' 4000 3"
        if not self.show_osd:
            self.send('osd 3\n%s' %mess)
            self.after(2500, lambda:self.send('osd 0'))
        else:
            self.send(mess)

    def confirm_exit(self, event=None):
        """On exit, make sure that mplayer is not running before quit"""
        if self.is_running.get():
            self.confirm_msg()
        else:
            # run any custom commands on exit
            if callable(self.callback):
                self.callback()
            # remove temporary files and directory
            for f in self.cmd_pipe, self.log, self.editlist:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(self.tempdir):
                os.rmdir(self.tempdir)
            self.quit()

    def quit(self):
        """Quit the application.  This detroys the root window, exiting Tkinter"""
        self.destroy()


class SetChapters(VideoGui):
    """Elements for a GUI to set video chapter points using Mplayer"""
    def __init__(self, master, args='', title='', callback=None):
        """
        master
            Pack into this widget
        args
            Additional args to pass to mplayer
        title
            Window manager titlebar title (master must be root window for this)
        callback
            Function to run on application exit, run before temp file cleanup
        """
        VideoGui.__init__(self, master, args, title, callback)
        self.chapter_var = tk.StringVar()

    def add_widgets(self):
        """
        Add buttons to the Gui. root_frame has 'grab_set()' applied to it so
        make sure widgets go into this frame or they will not be functional!
        This function is called in draw()
        """
        # button frame and buttons
        button_frame = tk.Frame(self.root_frame)
        button_frame.pack(side='bottom', fill='x', expand=1)
        self.control_frame = tk.Frame(button_frame, borderwidth=1, relief='groove')
        self.control_frame.pack()
        exit_button = tk.Button(self.control_frame, command=self.exit_mplayer, text='done !')
        mark_button = tk.Button(self.control_frame, command=self.set_chapter,text='set chapter')
        pause_button = tk.Button(self.control_frame, command=self.pause,
                          width=12, textvariable=self.pauseplay)
        framestep_button = tk.Button(self.control_frame, text='step>',
                                                command=self.framestep)
        forward_button = tk.Button(self.control_frame, text='>>',
                                                command=self.forward)
        fast_forward_button = tk.Button(self.control_frame, text='>>>',
                                                command=self.fastforward)
        back_button = tk.Button(self.control_frame, text='<<', command=self.back)
        fast_back_button = tk.Button(self.control_frame, text='<<<', command=self.fast_back)
#        self.seek_scale = tk.Scale(seek_frame, from_=0, to=100, tickinterval=10,
#        orient='horizontal', label='Use slider to seek to point in file (%)')
#        self.seek_scale.bind('<ButtonRelease-1>', self.seek)
        # pack the buttons and scale in their frames
        mark_button.pack(side='bottom', fill='both', expand=1)
        #self.seek_scale.pack(side='left', fill='x', expand=1)
        exit_button.pack(side='left')
        fast_back_button.pack(side='left')
        back_button.pack(side='left')
        pause_button.pack(side='left', expand=1)
        framestep_button.pack(side='left')
        forward_button.pack(side='left')
        fast_forward_button.pack(side='left')
        self.mp_ctrls = self.control_frame.winfo_children()

#    def seek(self, event=None):
#        """Seek in video according to value set by slider"""
#        self.send('seek %s 3\n' %self.seek_scale.get())
#        self.after(500, lambda:self.seek_scale.set(0))

    def forward(self):
        """Seek forward 10 seconds and make sure button var is set to 'Pause'"""
        self.send('seek 10')
        self.pauseplay.set('Pause')

    def fastforward(self):
        """Seek forward 5 minutes and make sure button var is set to 'Pause'"""
        self.send('seek 300')
        self.pauseplay.set('Pause')

    def back(self):
        """Seek backward 10 seconds and make sure button var is set to 'Pause'"""
        self.send('seek -10')
        self.pauseplay.set('Pause')

    def fast_back(self):
        """Seek backward 10 seconds and make sure button var is set to 'Pause'"""
        self.send('seek -300')
        self.pauseplay.set('Pause')

    def framestep(self):
        """Step frame by frame forward and set button var to 'Play'"""
        self.send('pausing frame_step')
        self.pauseplay.set('Play')

    def set_chapter(self):
        """Send chapter mark (via slave) twice so mplayer writes the data.
           we only take the 1st mark on each line
        """
        for i in range(2):
            self.send('edl_mark')
        mess = "osd_show_text 'chapter point saved' 2000 3"
        if not self.show_osd:
            self.send('osd 3%s' %mess)
            self.after(2500, lambda:self.send('osd 0'))
        else:
            self.send(mess)


    def get_chapters(self):
        """Read mplayer's editlist to get chapter points and return
        HH:MM:SS.xxx format string, comma separated
        """
        # need a sleep to make sure mplayer gives up its data
        if not os.path.exists(self.editlist):
            return
        time.sleep(0.5)
        f = open(self.editlist)
        c = f.readlines()
        f.close()
        # if chapter_var has value, editlist has been reset.  Append value.
        # only 1st value on each line is taken (the 2nd makes mplayer write out)
        s = [ i.split()[0]  for i  in self.chapter_var.get().splitlines() if i]
        c.extend(s)
        times = [ float(shlex.split(i)[0]) for i in c ]
        chapters = ['00:00:00']
        for t in sorted(times):
            fraction = '.' + str(t).split('.')[1]
            chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)) + fraction)
        if c:
            return '%s' %','.join(chapters)
    
    def on_eof(self):
        """
        Run when 'End of file' discovered in mplayer output by poll().
        """
        f = open(self.editlist)
        self.chapter_var.set(f.read())
        f.close()

class SetChaptersGui(SetChapters):
    """A standalone GUI to set video chapter points using SetChapters class"""
    def __init__(self, master, args='', title='', callback=None):
        """
        master
            Pack into this widget
        args
            Additional args to pass to mplayer
        title
            Window manager titlebar title (master must be root window for this)
        callback
            Function to run on application exit, run before temp file cleanup
        """
        SetChapters.__init__(self, master, args, title, callback)
        self.callback = self.print_chapters
        # bindings for exit
        self._root().protocol("WM_DELETE_WINDOW", self.exit)
        self._root().bind('<Control-q>', self.exit)


    def add_widgets(self):
        """Override add_widgets() from SetChapters, calling it first
        then adding widgets to it
        """
        SetChapters.add_widgets(self)
        self.result_frame = tk.Frame(self)
        self.text_frame = tk.Frame(self.result_frame)
        self.result_frame.pack(side='bottom', fill='x', expand=1)
        self.text_frame.pack(side='bottom', fill='x', expand=1)
        self.load_button = tk.Button(self.text_frame,
            command=self.load, text='Load Video')
        self.load_button.pack(side='left', padx=5)
        self.entry = tk.Entry(self.text_frame)
        self.entry.insert(0, "00:00:00.0")
        self.entry.pack(side='left', fill='x', expand=1)
        self.exit_button = tk.Button(self.text_frame,
            command=self.exit, text='Exit')
        self.exit_button.pack(side='left')
        # keep a list of mplayer controls so we can disable/enable them later
        self.mp_ctrls = self.control_frame.winfo_children()

    def load(self, event=None):
        """Load a file to play in the GUI"""
        try:
            from tkFileDialog import askopenfilename
        except ImportError:
            # python 3
            from tkinter.filedialog import askopenfilename
        vid_name = askopenfilename()
        if vid_name:
            self.toggle_controls('normal', self.mp_ctrls)
            # reset entry to 0 and chapter_var if we have a new video loaded
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "00:00:00.0")
            if self.pauseplay.get() == 'Pause':
                self.pauseplay.set('Play')
            self.run(vid_name)

    def print_chapters(self):
        """
        Run get_chapters(), output result to stdout, entry box, and write
        to tempory file.  Disable mplayer controls.
        This functions as the callback on mplayer exit.
        """
        if self.get_chapters():
            try:
                from tkMessageBox import askyesno, showinfo
            except ImportError:
                # python 3
                from tkinter.messagebox import askyesno, showinfo
            output = self.get_chapters()
            stdout.write(output + '\n')
            self.entry.delete(0, tk.END)
            self.entry.insert(0, output)
            self.toggle_controls('disabled', self.mp_ctrls)
            string1 = "Chapter string will be saved to: "
            string2 = '\nDo you wish to save it ?'
            #string2 += '  Choose "Yes" to save it.'
            # get basename of video, remove extension, add a '_'
            vid = os.path.basename(self.command[-1]) + '_'
            tmpfile = mkstemp(prefix=vid)
            if askyesno(title="Save chapter string",
              message= '%s%s%s' %(string1, tmpfile[1], string2)):
                save_msg = "%s%s\n" %('Saved ', tmpfile[1])
                showinfo(title='Chapters saved', message=save_msg)
                if os.path.exists(tmpfile[1]):
                    f = open(tmpfile[1], 'w')
                    f.write(output)
                    f.close()
            else:
                    os.remove(tmpfile[1])

    def quit(self):
        """Override quit() from base class, as standalone uses exit()"""
        # disable controls, because tempdir has been deleted
        self.toggle_controls('disabled', self.mp_ctrls)
        if self.chapter_var.get():
            self.chapter_var.set('')

    def exit(self, event=None):
        """Exit the GUI after confirming that mplayer is not running."""
        if self.is_running.get():
            self.confirm_msg()
        else:
            self.master.destroy()


# class for control that allow setting chapter points
class Chapters(ListToOne):
    """A popup version of the ListToOne Control, that also
    allows setting chapter points with a mplayer GUI
    (SetChapters).  This Control is specific to the tovid GUI.
    """
    def __init__(self,
                 parent,
                 label="ListToOne",
                 option='',
                 default=None,
                 help='',
                 filter=lambda x: x,
                 side='left',
                 control=Text(),
                 text='',
                 **kwargs):
        """initialize Chapters
        text
           The text for the button that calls mplayer
        For other options see help(control.ListToOne) 
        """
        ListToOne.__init__(self, parent, label, option, default, help,
                          control, filter, side, **kwargs)
        self.text = text
        self.parent = parent
        self.top_width = 540
        self.top_height = 540

    def draw(self, master):
        """Initialize Toplevel popup, video/chapters lists, and mplayer GUI.
        Only pack the video/chapter lists (_SubList).  Withdraw until called.
        """
        chapters_button = tk.Button(master, text='edit', command=self.popup)
        chapters_button.pack()
        # popup to hold lists and mplayer
        self.top = tk.Toplevel(master)
        self.top.withdraw()
        self.top.minsize(540, 540)
        self.top.title('Chapters')
        # text and label for instructions
        txt = 'Auto chapters:\n' + \
        '   1. Enter single value (integer) for all videos on 1st line.\n' + \
        '   2. Or, use a different auto chapter value for each video.\n' + \
        'HH:MM:SS format:\n' + \
        '   1. Enter timecode for each video, eg. 00:00:00,00:05:00 ...\n' + \
        '   2. Or use the "set with mplayer" button to use a GUI.'
        self.top.label = tk.Label(self.top, text=txt, justify=tk.LEFT)
        self.top.label.pack(side=tk.TOP)
        self.top_button = tk.Button(self.top, text='Okay', command=self.top.withdraw)
        # frames to hold the _Sublist and mplayer
        self.sublist_frame = tk.Frame(self.top)
        self.mplayer_frame = tk.Frame(self.top)
        # bindings for initial toplevel window
        self.top.protocol("WM_DELETE_WINDOW", self.top.withdraw)
        self.top.bind('<Escape>', self.withdraw_popup)
        # pack the _SubList frame and draw _SubList
        self.sublist_frame.pack(expand=1, fill=tk.BOTH)
        _SubList.draw(self, self.sublist_frame, allow_add_remove=False)
        self.top_button.pack(side='bottom')

        # a button to allow setting chapters in mplayer GUI
        button = tk.Button(self.control, text=self.text,
        command=self.run_mplayer, state='disabled')
        button.pack(side='left')
        # 1:1, parent listbox is linked to this one
        self.parent_listbox.link(self.listbox)
        # Add callbacks to handle changes in parent
        self.add_callbacks()

    def get_geo(self, widget):
        """Get geometry of a widget.
        Returns List (integers): width, height, Xpos, Ypos
        """
        geo = widget.winfo_geometry()
        return  [ int(x) for x in geo.replace('x', '+').split('+') ]

    def center_popup(self, master, width, height):
        """Get centered screen location of popup, relative to master.
        Returns geometry string in form of 'WxH+Xpos+Ypos'
        """
        root_width, root_height, rootx, rooty = self.get_geo(master)
        xoffset = (root_width - width) / 2
        # subtract 15 pixels for WM titlebar (still looks OK if there is none)
        yoffset = ((root_height - height) / 2 ) - 15
        return '%dx%d+%d+%d' %(width, height, rootx + xoffset, rooty + yoffset)
        
    def popup(self):
            """Popup the list of chapters, with button to run mplayer GUI"""
            videolist = self.parent_listbox
            self.top.transient(self.parent._root())
            w = self.top_width
            h = self.top_height
            self.top.geometry(self.center_popup(self.parent._root(), w, h))
            self.after(100, lambda:self.top.deiconify())
            if videolist.items.count() and not videolist.selected.get():
                self.parent_listbox.select_index(0)
    
    def run_mplayer(self, event=None):
        """Run the mplayer GUI to set chapters"""
        selected = self.parent_listbox.selected.get()
        if selected:
            # initialize mplayer GUI
            self.mpl = SetChapters(self.mplayer_frame, '-osdlevel 3', '', self.on_exit)
            self.mpl.pack()
            # unpack label
            self.sublist_frame.pack_forget()
            self.top.label.pack_forget()
            self.top_button.pack_forget()
            self.mplayer_frame.pack()
            self.mpl.run(selected)
            # disable close button while mplayer running, both top and _root()
            self.top.protocol("WM_DELETE_WINDOW", self.mpl.confirm_exit)
            self.master._root().protocol("WM_DELETE_WINDOW", self.mpl.confirm_exit)
            # disable usage of _root() window while mplayer running
            self.top.grab_set()
            self.top.bind('<Escape>', self.mpl.confirm_exit)

    def on_exit(self):
        """Callback run when mplayer GUI exits. This sets the chapters list
        to the timecodes set by the mplayer gui, repacks the label and the
        list frame, sets/resets bindings, and releases the grab_set().
        """
        if self.mpl.get_chapters():
            self.control.variable.set(self.mpl.get_chapters())
        self.mplayer_frame.pack_forget()
        # repack label
        self.top.label.pack(side=tk.TOP)
        self.sublist_frame.pack(expand=1, fill=tk.BOTH)
        self.top_button.pack(side='bottom')
        self.top.protocol("WM_DELETE_WINDOW", self.top.withdraw)
        self.top.grab_release()
        self.master._root().protocol("WM_DELETE_WINDOW", self.master._root().confirm_exit)
        self.top.bind('<Escape>', self.withdraw_popup)

    def withdraw_popup(self, event=None):
        """Withdraw the chapters popup window"""
        self.top.withdraw()

    def select(self, index, value):
        """Select an item in the list and enable editing.
        List select method overriden in order to clear entry selection.
        """
        List.select(self, index, value)
        # don't make it easy to erase a chapters string with a keypress
        self.control.selection_clear()

# Define a few supporting functions
def to_title(filename):
    basename = os.path.basename(filename)
    firstdot = basename.find('.')
    if firstdot >= 0:
        return basename[0:firstdot]
    else:
        return basename

def strip_all(filename):
    return ''

def find_masks(dir, pattern):
    file_list=[]
    ext = pattern.replace('*', '')
    for path, dirs, files in os.walk(os.path.abspath(dir)):
        for filename in fnmatch.filter(files, pattern):
            file_list+=[ filename.replace(ext, '') ]
    return file_list

def nodupes(seq):
    noDupes = []
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes

def get_loadable_opts(opts):
    good_opts = []
    bad_opts = []
    add_opt = False
    for index, opt in enumerate(opts):
        if opt.startswith('-'):
            if opt in no_load_opts:
                add_opt = False
            else:
                add_opt = True
                # -colour is not loadable, but is a valid todisc option
                if '-colour' in opt:
                    opt = opt.replace('-colour','-color')
        if add_opt:
            good_opts.append(opt)
        else:
            bad_opts.append(opt)

    return [good_opts, bad_opts]

# this is part of the HACK in working around broken load_args
# load_script was lifted from gui.py in metagui, with mods
def load_script(filename):
    #"""Load current script options and arguments from a text file.
    #"""
    # Read lines from the file and reassemble the command
    command = ''
    for line in open(filename, 'r'):
        line = line.strip()
        # Discard comment lines and PATH assignment
        if line and not (line.startswith('#') or line.startswith('PATH=')):
            command += line.rstrip('\\')
    # Split the full command into arguments, according to shell syntax
    args = shlex.split(command)

    # Ensure the expected program is being run
    program = args.pop(0)
    if program != 'todisc':
        raise ValueError("This script runs '%s', expected '%s'" %
              (program, 'todisc'))
    return args


def filter_args(master=None, args=None):
    # HACK
    # we need to sanitize the GUI args as load_args in metagui is broken
    # this function and imports of it can be removed when it is fixed
    a = get_loadable_opts(args)
    args = a[0]
    if a[1]:
        #import Tkinter as tk
        from textwrap import dedent
        heading = '''
        The tovid GUI did not load some of your options.
        This is normal as loading options externally
        is experimental. Sorry for the inconvenience.

        You can copy this for reference as you will need
        to set the following options yourself in the GUI:

        '''

        #u = unloadable_opts[:]
        #data = ['\n' + x + '\n' if x.startswith('-') else x for x in u]
        nonloadable = []
        for i in a[1]:
            if i.startswith('-'):
                nonloadable.append('\n' + i)
            elif ' ' in i:
                nonloadable.append("'" + i + "'")
            else:
                nonloadable.append(i)
        #data = ' '.join(nonloadable)
        master.title('Important!')
        info_msg = CopyableInfo(master, 'Important', dedent(heading),
                                     ' '.join(nonloadable), tovid_icon)
        info_msg.mainloop()
    return args


from libtovid.metagui.support import show_icons
from libtovid.metagui import Style
class CopyableInfo(tk.Frame):
    def __init__(self, master, title='', heading='', data='', icon=None):
        tk.Frame.__init__(self, master)
        self.pack()
        master.minsize(300, 300)
        text_frame = tk.Frame(self)
        text_frame.pack(side='top')
        style = Style()
        inifile = os.path.expanduser('~/.metagui/config')
        if os.path.exists(inifile):
            style.load(inifile)
            font = style.font or None
        else:
            font = None
        text_widget = tk.Text(text_frame, width=50, height=20, wrap='word')
        text_widget["bg"] = self.cget('background')
        text_widget["relief"] = 'flat'
        master["relief"] = 'flat'
        if font:
            text_widget["font"] = font
        text_widget.pack(side='top', fill='both', expand=1)
        text_widget.insert('1.0',heading)
        #text_widget.bind("<1>", self.set_focus(self, text_widget))
        text_widget.insert('end',data)
        text_widget['state'] = 'disabled'
        lines = int(text_widget.index('end-1c').split('.')[0]) 
        text_widget['height'] = lines + 3
        rclick = RightClickMenu(text_widget)
        text_widget.bind("<3>", rclick)
        exit_button = tk.Button(self, text='Close',
                       command=lambda:self._quit())
        #exit_button.focus_set()
        exit_button.pack(side='bottom')
        master.bind('<Control-q>', lambda event=None: self._quit())
        master.bind('<Escape>', lambda event=None: self._quit())
        if icon:
            show_icons(self.master, icon)
        master.update_idletasks() # update geometry
        # center the popup
        m = master
        x = int((m.winfo_screenwidth() / 2) - (m.winfo_width() /2))
        y = int((m.winfo_screenheight() / 2) - int((m.winfo_height() /2)))
        master.geometry('+%s+%s' %(x, y))



    def _quit(self, event=None):
        self.master.destroy()
        #self.master.destroy()


class RightClickMenu(object):
    # thanks to 'paperrobot' at:
    #  http://paperrobot.wordpress.com for this gem
    """
    Simple widget to add basic right click menus to entry widgets.

    usage:

    rclickmenu = RightClickMenu(some_entry_widget)
    some_entry_widget.bind("<3>", rclickmenu)

    Replace all Tix references with Tkinter and this will still work fine.
    """
    def __init__(self, parent):
        self.parent = parent
        # bind Control-A to select_all() to the widget.  Others work ok without
        self.parent.bind("<Control-a>", lambda e: self.select_all(), add='+')
        self.parent.bind("<Control-A>", lambda e: self.select_all(), add='+')
    def __call__(self, event):
        # grab focus of the entry widget.  this way you can see
        # the cursor and any marking selections
        self.parent.focus_force()
        self.build_menu(event)
    def build_menu(self, event):
        self.menu = tk.Menu(self.parent, tearoff=0)
        #self.parent.bind("<Button-1>", self.close_menu)
        #self.parent.bind("<Escape>", self.close_menu)
        if self.parent.tag_ranges("sel"):
            self.menu.add_command(
                label="Copy",
                command=lambda: self.parent.event_generate("<<Copy>>"))
        else:
            self.menu.add_command(label="Copy", state=tk.DISABLED)
        self.menu.add_command(label="Cut", state=tk.DISABLED)
        self.menu.add_command(label="Paste", state=tk.DISABLED)
        # make things pretty with a horizontal separator
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=self.select_all)
        self.menu.tk_popup(event.x_root, event.y_root)
    def select_all(self):
        self.parent.tag_add(tk.SEL, 1.0, tk.END)
        # return 'break' because doesn't work otherwise.
        return 'break'



# List of file-type selections for Filename controls
image_filetypes = [filetypes.image_files]
image_filetypes.append(filetypes.all_files)
#image_filetypes.extend(filetypes.match_types('image'))  # confusing
# video file-types from filetypes needs some additions
v_filetypes = 'm2v vob ts '
v_filetypes += filetypes.get_extensions('video').replace('*.', '')
v_filetypes += ' mp4 mpeg4 mp4v divx mkv ogv ogm ram rm rmvb wmv webm'
vid_filetypes = filetypes.new_filetype('Video files', v_filetypes)
video_filetypes = [vid_filetypes]
video_filetypes += [filetypes.all_files]

# some selectors can use video or audio
av_filetypes = [ filetypes.all_files, filetypes.audio_files, vid_filetypes ]

# some selectors can use image or video
visual_filetypes = [ filetypes.all_files, filetypes.image_files, vid_filetypes ]

# DVD video
dvdext = 'vob mpg mpeg mpeg2'
dvd_video_files = [ filetypes.new_filetype('DVD video files', dvdext) ]

# Users can use their own thumb masks.  Add to thumb mask control drop-down
masks = [ 'none', 'normal', 'oval', 'vignette', 'plectrum', 'arch', 'spiral', \
'blob', 'star', 'flare' ]

# some options can not be loaded by the gui:
# options with multiple choices for args, for example: none, single, multiple
# this is a list of 'unloadable' options for the GUI
no_load_opts = ['-chapter-titles', '-menu-fade', '-loop', '-video-pause', '-group-video-pause', '-slide-blur', '-slide-border', '-slide-frame', '-chain-videos', '-showcase', '-titles-font-deco', '-chapters', '-subtitle-lang', '-audio-channel', '-audio-lang', '-seek', '-showcase-seek', '-bg-video-seek', '-bgvideo-seek', '-bg-audio-seek', '-bgaudio-seek', '-submenu-audio-seek', '-rotate-thumbs', '-tile3x1', '-tile-3x1', '-tile4x1', '-tile-4x1']

# $PREFIX/lib/tovid is already added to end of PATH
os_path = os.environ['PATH'].rsplit(':')
sys_dir = os_path[-1] + '/masks'
home_dir = os.path.expanduser("~") + '/.tovid/masks'
for dir in sys_dir, home_dir:
    masks.extend(find_masks(dir, '*.png'))
thumb_masks =  '|'.join(nodupes(masks))
tovid_prefix = getoutput('tovid -prefix')
tovid_icon = os.path.join(tovid_prefix, 'lib', 'tovid', 'tovid.png')

# default heading text for tovid GUI (opening pane)
heading_text = 'You can author (and burn) a DVD with a simple menu '
heading_text += 'using ONLY this "Basic" pane\n'
heading_text += 'Required: video files (and/or slideshows) and "Output name"'

### configuration for titleset wizard ( 'tovid titlesets' )
wizard = os.getenv('METAGUI_WIZARD') or '0'
if wizard == '1':
    # General options
    heading_text = 'General options applying to all titlesets.\n'
    heading_text += 'Required: "Output name" at bottom of window'
elif wizard == '2':
    # Root menu options
    heading_text = 'Root menu options.  Use any options that do not depend\n'
    heading_text += 'on video files or slideshows being loaded. Required: None'
    heading_text += '\nChange "Menu title" from the default to suit your needs'
elif wizard >= '3':
    # titleset options
    heading_text = 'Options for titleset %s\n' %(int(wizard) - 2)
    heading_text += 'Required: 1 or more videos and/or slideshows'

if wizard == '2':
    # Root menu options
    _files = List('Do not load any files for Root menu !', '-files', None,
        '',
        Filename('', filetypes=video_filetypes))
    _files_and_titles = ListToOne(_files, 'Root menu link titleset titles',
        '-titles', None,
        'The titles for the Root menu link titleset titles',
        Text(),
        filter=to_title)
else:
    _files = List('Video files', '-files', None,
        'List of video files to include on the disc',
        Filename('', filetypes=video_filetypes))
    _files_and_titles = ListToOne(_files, 'Video titles', '-titles', None,
        'Titles to display in the main menu, one for each video file on the disc',
        Text(),
        filter=to_title)

if int(wizard) and wizard != '1':
    # 'Output name' only for General Options ( '1' )
    _out = Label(' ')
else:
    _out = Filename('Output name', '-out', '',
        'Name to use for the output directory where the disc will be created.',
        'save', 'Choose an output name')

import Tkinter as tk
import time
import shlex
import commands
import re
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkdtemp

class VideoGui(tk.Frame):
    """A basic GUI to play video files.  It runs mplayer in slave mode
    so that commands can be sent to it via fifo.

    Without subclassing it only contains a 'play/pause button
    and an 'exit' button.
    """
    def __init__(self, master, args='', title='', callback=None, style='popup'):
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
           style
               may be one of 'popup' (default), 'standalone', or 'embedded'(TBA)
        """
        tk.Frame.__init__(self, master)

        self.args = args
        self.show_osd = False
        if '-menu' in shlex.split(args):
            self.show_osd = True
        self.master = master
        if title:
            try:
                self.master.title(title)
            except AttributeError:
                print "Error: " + \
                  "VideoGui master must be a root window for 'title' option"
        self.callback = callback
        self.style = style
                
        self.is_running = tk.BooleanVar()
        self.is_running.set(False)
        self.pauseplay = tk.StringVar()
        self.pauseplay.set('play')
        # temporary directory for fifo and other mplayer files
        self.tempdir = mkdtemp(prefix='tovid-')
        self.cmd_pipe = os.path.join(self.tempdir, 'slave.fifo')
        self.editlist = os.path.join(self.tempdir, 'editlist')
        os.mkfifo(self.cmd_pipe)
        self.log = os.path.join(self.tempdir, 'mplayer.log')
        self.draw()

    def draw(self):
        """Draw the GUI in self.master and get X11 identifier for container"""
        self.root_frame = tk.Frame(self)
        self.root_frame.pack(side='top', fill='both', expand=1, pady=20)
        self.container = tk.Frame(self.root_frame, bg='black', container=1, colormap='new')
        self.container.pack()
        # X11 identifier for the container frame
        self.xid = self.tk.call('winfo', 'id', self.container)
        # bindings for exit
        if self.style == 'standalone':
            self._root().protocol("WM_DELETE_WINDOW", self.confirm_exit)
            self._root().bind('<Control-q>', self.confirm_exit)
        self.add_widgets()

    def add_widgets(self):
        """
        Add buttons to the VideoGui.  Override this to customize buttons.
        root_frame has 'grab_set()' applied to it so make sure widgets go
        into this frame or they will not be functional!
        This function is called in draw()
        """
        button_frame = tk.Frame(self.root_frame)
        button_frame.pack(side='bottom', fill='x', expand=1)
        control_frame = tk.Frame(button_frame, borderwidth=1, relief='groove')
        control_frame.pack()
        exit_button = tk.Button(control_frame, command=self.exit_mplayer, text='exit')
        pause_button = tk.Button(control_frame, command=self.pause,
                          width=12, textvariable=self.pauseplay)
        exit_button.pack(side='left')
        pause_button.pack(side='left')


    def identify(self, video):
        """
        Get information about video from mplayer -identify.
        Called by set_container()
        """
        
        output = commands.getoutput('mplayer -vo null -ao null -frames 5 \
          -channels 6 -identify %s' %video)
        return output

    def set_container(self, video):
        """Get aspect ratio and set dimensions of video container.
           Called by run().
        """
        if self.style == 'standalone':
            v_width = 600
        else:
            v_width = 540
        media_info = self.identify(video)
        asr = re.findall('ID_VIDEO_ASPECT=.*', media_info)
        # get last occurence as the first is 0.0 with mplayer
        if asr:
            asr = sorted(asr, reverse=True)[0].split('=')[1]
        try:
            asr = float(asr)
        except ValueError:
            asr = 0.0
        # get largest value as mplayer prints it out before playing file
        if asr and asr > 0.0:
            v_height = int(v_width/asr)
        else:
            # default to 4:3 if identify fails
            v_height = int(v_width/1.333)
        self.container.configure(width=v_width, height=v_height)

    def run(self, video):
        """Play video in this GUI using mplayer."""
        self.set_container(video)
        command =  'mplayer -wid %s -nomouseinput -slave \
          -input nodefault-bindings:conf=/dev/null:file=%s \
          -edlout %s %s %s' \
          %(self.xid, self.cmd_pipe, self.editlist, self.args, video)
        self.command = shlex.split(command)

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
        tail = 'tail -n 1 %s' %self.log
        log_output = commands.getoutput(tail)
        # restart mplayer with same commands if it exits without being sent
        # an explict 'quit'.
        if '(End of file)' in log_output:
            self.on_eof()
            # check for is_running again as on_oef() might set it to false
            if self.is_running.get():
                cmd = Popen(self.command, stderr=open(os.devnull, 'w'), \
                  stdout=open(self.log, "w"))
                if self.show_osd:
                    self.send('osd 3\n')
                self.pause()
        self.master.after(200, self.poll)

    def on_eof(self):
        """
        Run when 'End of file' discovered in mplayer output by poll().
        Override to run custom commands.
        Note: change is_running() variable to false to prevent looping of video.
        """
        pass

    def send(self, text):
        """send command to mplayer's slave fifo"""
        if self.is_running.get():
            commands.getstatusoutput('echo -e "%s"  > %s' %(text, self.cmd_pipe))

    def pause(self):
        """send pause to mplayer via slave and set button var to opposite value"""
        # mplayer's 'pause' pauses if playing and plays if paused
        # pauseplay ==play in pause mode, and ==pause in play mode (button text)
        if self.is_running.get():
            if self.pauseplay.get() == 'pause':
                self.pauseplay.set('play')
            else:
                self.pauseplay.set('pause')
            self.send('pause\n')
        else:
            # start the video for the 1st time
            cmd = Popen(self.command, stderr=open(os.devnull, 'w'), stdout=open(self.log, "w"))
            self.is_running.set(True)
            self.poll()
            # show osd time and remaining time
            if self.show_osd:
                self.send('osd 3\n')
            self.pauseplay.set('pause')

    def exit_mplayer(self):
        """
        Close mplayer if it is running, then exit, running callback if it exists
        """
        # unpause so mplayer doesn't hang
        if self.is_running.get():
            if self.pauseplay.get() == 'play':
                self.send('mute 1\n')
                self.send('pause\n')
            self.send('quit\n')
            self.is_running.set(False)
        time.sleep(0.3)
        self.confirm_exit()

    def confirm_exit(self, event=None):
        """on exit, make sure that mplayer is not running before quit"""
        if self.is_running.get():
            mess = "osd_show_text 'please exit mplayer first' 4000 3\n"
            if not self.show_osd:
                self.send('osd 3\n%s' %mess)
                self.after(2500, lambda:self.send('osd 0\n'))
            else:
                self.send(mess)
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
            if self.style == 'standalone':
                self.quit()
            else:
                self.destroy()


class SetChapters(VideoGui):
    """A GUI to set video chapter points using mplayer"""
    def __init__(self, master, args='', title='', callback=None, style='popup'):
        """
        master
            Pack into this widget
        args
            Additional args to pass to mplayer
        title
            Window manager titlebar title (master must be root window for this)
        callback
            Function to run on application exit, run before temp file cleanup
        style
            Can one of: 'popup' (default), 'standalone', or 'embedded'(TBA)
        """
        VideoGui.__init__(self, master, args, title, callback, style)

        self.chapter_var = tk.StringVar()

    def add_widgets(self):
        # button frame and buttons
        button_frame = tk.Frame(self.root_frame)
        button_frame.pack(side='bottom', fill='x', expand=1)
        control_frame = tk.Frame(button_frame, borderwidth=1, relief='groove')
        control_frame.pack()
        exit_button = tk.Button(control_frame, command=self.exit_mplayer, text='done !')
        mark_button = tk.Button(control_frame, command=self.set_chapter,text='set chapter')
        pause_button = tk.Button(control_frame, command=self.pause,
                          width=12, textvariable=self.pauseplay)
        framestep_button = tk.Button(control_frame, text='step >', command=self.framestep)
        forward_button = tk.Button(control_frame, text='seek >', command=self.forward)
        back_button = tk.Button(control_frame, text='< seek', command=self.back)
        # seek frame and scale widget
        seek_frame = tk.Frame(self.root_frame)
        seek_frame.pack(side='left', fill='x', expand=1, padx=30)
        self.seek_scale = tk.Scale(seek_frame, from_=0, to=100, tickinterval=10,
        orient='horizontal', label='Use slider to seek to point in file (%)')
        self.seek_scale.bind('<ButtonRelease-1>', self.seek)
        # pack the buttons and scale in their frames
        mark_button.pack(side='bottom', fill='both', expand=1)
        self.seek_scale.pack(side='left', fill='x', expand=1)
        exit_button.pack(side='left')
        back_button.pack(side='left')
        pause_button.pack(side='left')
        framestep_button.pack(side='left')
        forward_button.pack(side='left')

    def seek(self, event=None):
        """seek in video according to value set by slider"""
        self.send('seek %s 3\n' %self.seek_scale.get())

    def forward(self):
        """seek forward 10 seconds and make sure button var is set to 'pause'"""
        self.send('seek 10\n')
        self.pauseplay.set('pause')

    def back(self):
        """seek backward 10 seconds and make sure button var is set to 'pause'"""
        self.send('seek -10\n')
        self.pauseplay.set('pause')

    def framestep(self):
        """step frame by frame forward and set button var to 'play'"""
        self.send('pausing frame_step\n')
        self.pauseplay.set('play')

    def set_chapter(self):
        """send chapter mark (via slave) twice so mplayer writes the data.
           we only take the 1st mark on each line
        """
        for i in range(2):
            self.send('edl_mark\n')
        mess = "osd_show_text 'chapter point saved' 2000 3\n"
        if not self.show_osd:
            self.send('osd 3\n%s' %mess)
            self.after(2500, lambda:self.send('osd 0\n'))
        else:
            self.send(mess)


    def get_chapters(self):
        # need a sleep to make sure mplayer gives up its data
        if not os.path.exists(self.editlist):
            return '00:00:00'
        time.sleep(0.5)
        f = open(self.editlist)
        c = f.readlines()
        f.close()
        # if chapter_var has value, editlist has been reset.  Append value, if any.
        # only 1st value on each line is taken (2nd is to make mplayer write out)
        s = [ i.split()[0]  for i  in self.chapter_var.get().splitlines() if i]
        c.extend(s)
        times = [ float(shlex.split(i)[0]) for i in c ]
        chapters = ['00:00:00']
        for t in sorted(times):
            fraction = '.' + str(t).split('.')[1]
            chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)) + fraction)
        return '%s' %','.join(chapters)



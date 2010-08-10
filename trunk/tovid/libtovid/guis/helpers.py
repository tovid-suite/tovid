import Tkinter as tk
import time
import shlex
import commands
import re
import os
from subprocess import Popen, PIPE, STDOUT
from sys import argv
from tempfile import mkdtemp

class VideoGui(tk.Frame):
    """A basic GUI to play video files.  It runs mplayer in slave mode
    so that command can be sent to it via fifo.

    Without subclassing it only contains a 'play/pause button
    and an 'exit' button.
    """
    def __init__(self, master, args='', title=''):
        tk.Frame.__init__(self, master)

        self.args = args
        self.master = master
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
        self.root_frame = tk.Frame(self.master)
        self.root_frame.pack(side='top', fill='both', expand=1, pady=40)
        self.container = tk.Frame(self.root_frame, bg='black', container=1, colormap='new')
        self.container.pack()
        # X11 identifier for the container frame
        self.xid = self.tk.call('winfo', 'id', self.container)
        # bindings for exit
        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.bind('<Control-q>', self.confirm_exit)
        self.add_widgets()

    def add_widgets(self):
        """
        Add buttons to the VideoGui.  Override this to customize buttons.
        This is called in draw()
        """
        button_frame = tk.Frame(self.root_frame)
        button_frame.pack(side='bottom', fill='x', expand=1)
        control_frame = tk.Frame(button_frame, borderwidth=1, relief='groove')
        control_frame.pack()
        exit_button = tk.Button(control_frame, command=self.exit_mplayer, text='done !')
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
        v_width = 600
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
          -edlout %s %s' \
          %(self.xid, self.cmd_pipe, self.editlist, video)
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
            self.send('osd 3\n')
            self.pauseplay.set('pause')

    def exit_mplayer(self):
        """
        Close mplayer if it is running, then exit, running any pre_exit commands
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

    def confirm_exit(self):
        """on exit, make sure that mplayer is not running before quit"""
        if self.is_running.get():
            self.send("osd_show_text 'press exit before quitting program' 4000 3\n")
        else:
            # remove temporary files and directory
            for f in self.cmd_pipe, self.log, self.editlist:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(self.tempdir):
                os.rmdir(self.tempdir)
            self.pre_exit()
            quit()

    def pre_exit(self):
        """override this function to run custom commands on exit"""
        pass

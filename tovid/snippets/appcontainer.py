import commands
import shlex
from Tkinter import *
from subprocess import Popen, PIPE
from tkMessageBox import *
from sys import argv

class AppContainer(Frame):
    """A frame container for an external application.
       master: the container frame will be packed into this widget
       height: the height of the application
       width:  the width of the application
       callback: called on application exit (AppContainer is 'destroyed' then)

       After creating a container instance, call container.get_id()
       to find out the X11 id of the container(ie. for xterm -into id)
       Then call container.run(command), where command is the command
       that starts the external app.
       This file can be run standalone, and uses the example at the bottom
    """       
    
    def __init__(self, master, width, height, callback=None):
        Frame.__init__(self, master)
        self.master = master
        self.wth = width 
        self.ht = height
        self.callback = callback
        self.is_running = BooleanVar()
        self.is_running.set(False)
        self.draw()

    def draw(self):
        """Pack self in self.master"""
        self.pack(fill='both', expand=1)

    def get_id(self):
        """Create and pack container frame,
           then get X11 identifier for it (converted to base 10).
           Return the identifier
        """
        self.frame = LabelFrame(self.master, container=1, width=self.wth, height=self.ht,
                                                             text='Xterm', borderwidth=0)
        self.frame.pack(fill='both', expand=1)
        id = self.tk.call('winfo', 'id', self.frame)
        self.frame_id = '%s' %int(id, 16)
        return self.frame_id

    def run(self, command):
        """Execute self.command, call the callback from self.master"""
        self.is_running.set(True)
        cmd = Popen(command, stderr=PIPE, stdout=PIPE)
        self.after(200, self.poll())
        self.callback()

    def poll(self):
        """When the container app stops running, call callback from self.master"""
        # only poll if app still running
        if self.is_running.get() == 1:
            if not self.tk.call('winfo', 'exists', self.frame):
                self.is_running.set(False)
                # call function in master when app exits
                if self.callback:
                    self.callback()
            self.after(200, self.poll)


###############################################################################
#                      demo of AppContainer with xterm                        #
###############################################################################
if __name__ == '__main__':

    def demo_xterm():
        def callback():
            """Called upon creation and exiting of container app,
               Set a BooleanVar() to track whether the app is running.
            """
            if container.is_running.get() == True:
                xterm_is_running.set(True)
                
            else:
                xterm_is_running.set(False)
                root_frame.pack_forget()
                label.pack(side='top', fill='both', expand=1)
                label.configure(text='xterm has exited')
                button.pack(side='bottom')

        def execute():
            label.pack_forget()
            button.pack_forget()
            root_frame.pack(fill='both', expand=1)
            id = container.get_id()
            geometry = '80x40+0+0'
            font = '-misc-fixed-medium-r-normal--13-100-100-100-c-70-iso8859-1'
            command = 'xterm -geometry %s -fn %s  -into %s &' %(geometry, font, id)
            command = shlex.split(command)
            container.run(command)

        def confirm_exit():
            if xterm_is_running.get() == 1:
                showerror(message="Close the xterm by typing 'exit', before exiting this demo")
                return
            quit()


        root = Tk()
        root.minsize(660, 600)
        # bindings for exit
        root.protocol("WM_DELETE_WINDOW", confirm_exit)
        root.bind('<Control-q>', confirm_exit)
        root.title('AppContainer demo')
        # run button
        button = Button(root, text='Run xterm', command=execute)
        button.pack(side='bottom')
        # frame for container
        root_frame = Frame(root)
        # label to show when container app not running
        label = Label(root, text='')
        # BooleanVar that tracks if container app is running through callback()
        xterm_is_running = BooleanVar()
        xterm_is_running.set(False)
        # initialize but don't pack the container class
        container = AppContainer(root_frame, 660, 500, callback)

        root.mainloop()
    if len(argv) < 2:
        demo_xterm()
    """
    # setting chapters with mplayer demo - coming soon
    elif os.exists(argv[1]):
        media_file = argv[1]
    """

import time
import shlex
import commands
import re
from Tkinter import *
from subprocess import Popen, PIPE, STDOUT
from sys import argv
from os import path, mkfifo, devnull
from tempfile import mkdtemp

##############################################################################
#                              functions                                     #
##############################################################################
def send(text):
    commands.getstatusoutput('echo -e "%s"  > %s' %(text, cmd_pipe))

def seek(event=None):
    send('seek %s 3\n' %seek_scale.get())

def pause():
    # this is counter-intuitive, as we set to the opposite for pause/play label
    # pauseplay ==play and we're in pause mode, ==pause and we're in play mode
    if pauseplay.get() == 'pause':
        pauseplay.set('play')
    else:
        pauseplay.set('pause')
    send('pause\n')

def forward():
    send('seek 10\n')
    pauseplay.set('pause')

def back():
    send('seek -10\n')
    pauseplay.set('pause')

def framestep():
    # step frame by frame forward
    send('pausing frame_step\n')
    pauseplay.set('play')

def confirm_exit():
    if is_running.get():
        send("osd_show_text 'press exit before quitting program' 4000 3\n")
    else:
        quit()

def exit_mplayer():
    is_running.set(False)
    # unpause so mplayer doesn't hang
    if pauseplay.get() == 'play':
        send('mute 1\n')
        send('pause\n')
    send('quit\n')
    time.sleep(0.3)
    frame.destroy()
    root_frame.pack_forget()
    output = '-chapters ' + get_chapters()
    info_label.configure(text=output)
    print output

def set_chapter():
    # send chapter mark twice so mplayer writes the data
    # we only take the 1st mark on each line
    for i in range(2):
        send('edl_mark\n')
    send("osd_show_text 'chapter point saved' 2000 3\n")

def get_chapters():
    # need a sleep to make sure mplayer gives up its data
    time.sleep(0.5)
    f = open(editlist)
    c = f.readlines()
    f.close()
    # if chapter_var has value, editlist has been reset.  Append value, if any.
    # only 1st value on each line is taken (2nd is to make mplayer write out)
    s = [ i.split()[0]  for i  in chapter_var.get().splitlines() if i]
    c.extend(s)
    times = [ float(shlex.split(i)[0]) for i in c ]
    # insert mandatory 1st chapter
    times.insert(0, 0.0)
    times.sort()
    chapters = []
    for t in times:
        fraction = '.' + str(t).split('.')[1]
        chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)) + fraction)
        time_codes = "'%s'" %','.join(chapters)
    return time_codes

def poll():
    #cmd = "tail -n 1  %s | sed -r 's/.*([0-9].*\/.*[0-9]+).*/\1/;s/\/.*//g'" %log
    if not is_running.get():
        return
    tail = 'tail -n 1 %s' %log
    output = commands.getoutput(tail)
    # restart mplayer with same commands if it exits without user intervention
    if '(End of file)' in output:
        # save editlist, as mplayer overwrites it on restart
        o = open(editlist, 'r')
        chapter_var.set(chapter_var.get() + o.read())
        o.close()
        cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
        send('osd 3\n')
    root.after(200, poll)

def identify(file):
    output = commands.getoutput('mplayer -vo null -ao null -frames 30 \
      -channels 6 -identify %s' %file)
    return output

##############################################################################
#              start Tk instance and set tk variables
##############################################################################

if len(sys.argv) < 2:
    print("Usage: set_chapters.py video")
    exit()
root = Tk()
root.minsize(660, 600)
seek_var = IntVar()
seek_var.set(0)
chapter_var = StringVar()
is_running = BooleanVar()
is_running.set(True)
pauseplay = StringVar() 
pauseplay.set('pause')
# bindings for exit
root.protocol("WM_DELETE_WINDOW", confirm_exit)
root.bind('<Control-q>', confirm_exit)
root.title('Set chapters')

##############################################################################
#                                   widgets                                  #
##############################################################################

# label to display chapters after mplayer exit
info_label = Label(root, wraplength=500, justify='left')
info_label.pack(side='bottom', fill='both', expand=1)
# frame to hold mplayer container
root_frame = Frame(root)
root_frame.pack(side='top', fill='both', expand=1, pady=40)
frame = Frame(root_frame, container=1)
frame.pack()
# button frame and buttons
button_frame = Frame(root_frame)
button_frame.pack(side='bottom', fill='x', expand=1)
control_frame = Frame(button_frame, borderwidth=1, relief='groove')
control_frame.pack()
apply_frame = Frame(button_frame, borderwidth=1, relief='groove')
#apply_frame.pack()
exit_button = Button(control_frame, command=exit_mplayer, text='exit')
mark_button = Button(control_frame, command=set_chapter,text='set chapter')
pause_button = Button(control_frame, command=pause,
                  width=12, textvariable=pauseplay)
framestep_button = Button(control_frame, text='step >', command=framestep)
forward_button = Button(control_frame, text='seek >', command=forward)
back_button = Button(control_frame, text='< seek', command=back)
# frame and seek scale
seek_frame = Frame(root_frame)
seek_frame.pack(side='left', fill='x', expand=1, padx=30)
seek_scale = Scale(seek_frame, from_=0, to=100, tickinterval=10,
orient='horizontal', label='Use slider to seek to point in file (%)')
seek_scale.bind('<ButtonRelease-1>', seek)
# pack the buttons and scale in their frames
mark_button.pack(side='bottom', fill='both', expand=1)
seek_scale.pack(side='left', fill='x', expand=1)
exit_button.pack(side='left')
back_button.pack(side='left')
pause_button.pack(side='left')
framestep_button.pack(side='left')
forward_button.pack(side='left')
# X11 identifier for the container frame
xid = root.tk.call('winfo', 'id', frame)
# temporary directory for fifo, edit list and log
dir = mkdtemp(prefix='tovid-')
cmd_pipe = path.join(dir, 'slave.fifo')
mkfifo(cmd_pipe)
editlist = path.join(dir, 'editlist')
log = path.join(dir, 'mplayer.log')
media_file = sys.argv[1]

##############################################################################
#           get aspect ratio and set dimensions of video container           #
##############################################################################
v_width = 600
media_info = identify(media_file)
asr = re.findall('ID_VIDEO_ASPECT=.*', media_info)
# get last occurence as the first is 0.0 with mplayer
asr = sorted(asr, reverse=True)[0].split('=')[1]
try:
    asr = float(asr)
except ValueError:
    asr = 0.0
# get largest value as mplayer prints it out before playing file
if asr and asr > 0.0:
    v_height = int(v_width/asr)
else:
    v_height = int(v_width/1.333)
frame.configure(width=v_width, height=v_height)

###############################################################################
#                 start mplayer and poll for end of file                      #
###############################################################################
mplayer_cmd =  'mplayer -wid %s -nomouseinput -slave \
  -input nodefault-bindings:conf=/dev/null:file=%s \
  -edlout %s %s ' %(xid, cmd_pipe, editlist, media_file)
mplayer_cmd = shlex.split(mplayer_cmd)
cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
poll()
# show osd time and remaining time
send('osd 3\n')

##############################################################################
#                                 run it                                     #
##############################################################################
if __name__ == '__main__':
    root.mainloop()

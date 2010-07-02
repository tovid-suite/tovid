import time
import shlex
import commands
import re
from Tkinter import *
from subprocess import Popen, PIPE, STDOUT
from tkMessageBox import *
from sys import argv
from os import path, mkfifo, devnull
from tempfile import mkdtemp


def send_command(text):
    commands.getstatusoutput('echo %s  > %s' %(text, cmd_pipe))
    commands.getstatusoutput('echo > %s' %cmd_pipe)

def seek(event=None):
    send_command('seek %s 3' %seek_scale.get())

def pause():
    send_command('pause')

def confirm_exit():
    # TBA
    pass
    
def exit_mplayer():
    is_running.set(False)
    send_command('quit')
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
        send_command('edl_mark')
    show_status('Chapter set!')

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
        # save editlist and rewrite it, as mplayer overwrites it on restart
        o = open(editlist, 'r')
        chapter_var.set(chapter_var.get() + o.read())
        o.close()
        cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
        send_command('osd 3')
    root.after(200, lambda:poll())

def identify(file):
    output = commands.getoutput('mplayer -vo null -ao null -frames 30 \
      -channels 6 -identify %s' %file)
    return output

def show_status(message):
    """Show status of setting chapter, with timeout
    """
    status_frame.configure(relief='raised', borderwidth=1)
    status_frame.pack(side='top', anchor='n')
    label1.configure(text=message)
    label2.configure(text='ok', relief='groove', borderwidth=1)
    label1.pack(side='top')
    label2.pack(side='top')
    root.after(1000, lambda: label2.configure(relief=SUNKEN))
    root.after(2000, hide_status)

def hide_status():
    status_frame.configure(relief='flat', borderwidth=0)
    label2.configure(text='', relief='flat', borderwidth=0)
    label1.configure(text='')

root = Tk()
root.minsize(660, 600)
seek_var = IntVar()
seek_var.set(0)
chapter_var = StringVar()
is_running = BooleanVar()
is_running.set(True)
# bindings for exit
#root.protocol("WM_DELETE_WINDOW", confirm_exit)
#root.bind('<Control-q>', confirm_exit)
root.title('AppContainer demo')
info_label = Label(root, wraplength=500, justify='left')
info_label.pack(side='bottom', fill='both', expand=1)
status_frame = Frame(root)
label1 = Label(status_frame, text='', fg='blue')
label2 = Label(status_frame)
root_frame = Frame(root)
root_frame.pack(side='top', fill='both', expand=1, pady=40)
frame = Frame(root_frame, container=1)
frame.pack()
button_frame = Frame(root_frame)
button_frame.pack(side='bottom', fill='x', expand=1)
exit_button = Button(button_frame, command=exit_mplayer, text='exit')
mark_button = Button(button_frame, command=set_chapter, text='set chapter')
pause_button = Button(button_frame, command=pause, text='pause/play')
seek_frame = Frame(root_frame)
seek_frame.pack(side='left', fill='x', expand=1, padx=30)
seek_scale = Scale(seek_frame, from_=0, to=100, tickinterval=10,
orient='horizontal', label='Use slider to seek to point in file (%)')
seek_scale.bind('<ButtonRelease-1>', seek)
seek_scale.pack(side='left', fill='x', expand=1)
pause_button.pack(side='left')
mark_button.pack(side='left', fill='both', expand=1)
exit_button.pack(side='right')

xid = root.tk.call('winfo', 'id', frame)
dir = mkdtemp(prefix='tovid-')
cmd_pipe = path.join(dir, 'slave.fifo')
mkfifo(cmd_pipe)
editlist = path.join(dir, 'editlist')
log = path.join(dir, 'mplayer.log')
media_file = sys.argv[1]
# try to get aspect ratio
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
# disable keyboard input with nodefault-bindings...
mplayer_cmd =  'mplayer -wid %s -nomouseinput -slave \
  -input nodefault-bindings:conf=/dev/null:file=%s \
  -edlout %s %s ' %(xid, cmd_pipe, editlist, media_file)
mplayer_cmd = shlex.split(mplayer_cmd)
cmd = Popen(mplayer_cmd, stderr=open(devnull, 'w'), stdout=open(log, "w"))
poll()
# show osd time and remaining time
send_command('osd 3')


if __name__ == '__main__':
    root.mainloop()

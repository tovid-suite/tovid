import time
import shlex
import commands
from Tkinter import *
from subprocess import Popen, PIPE, STDOUT
from tkMessageBox import *
from sys import argv
from os import path, mkfifo, devnull
from tempfile import mkdtemp

def send_command(text):
    commands.getstatusoutput('echo %s  > %s' %(text, cmd_pipe))
    #commands.getstatusoutput('echo > %s' %cmd_pipe)

def seek(event=None):
    if commands.getstatusoutput('kill -0 %s' %cmd.pid)[0]:
        send_command('loadfile %s' %media_file)
    send_command('seek %s 3' %seek_scale.get())

def confirm_exit():
    pass
    
def exit_mplayer():
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

def get_chapters():
    # need a sleep to make sure mplayer gives up its data
    time.sleep(0.5)
    f = open(editlist)
    c = f.readlines()
    f.close()
    times = [ float(shlex.split(i)[0]) for i in c ]
    # insert mandatory 1st chapter
    times.insert(0, 0.0)
    chapters = []
    for t in times:
        fraction = '.' + str(t).split('.')[1]
        chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)) + fraction)
        time_codes = "'%s'" %','.join(chapters)
    return time_codes

def get_asr(file):
    asr = commands.getoutput('mplayer -vo null -ao null -frames 30 \
      -channels 6 -identify %s 2>&1 |grep ID_VIDEO_ASPECT' %file)
    asr = shlex.split(asr)[1].split('=')[1]
    try:
        asr = float(asr)
    except ValueError:
        asr = 0.0
    return asr

root = Tk()
root.minsize(660, 600)
seek_var = IntVar()
seek_var.set(0)
# bindings for exit
#root.protocol("WM_DELETE_WINDOW", confirm_exit)
#root.bind('<Control-q>', confirm_exit)
root.title('AppContainer demo')
info_label = Label(root)
info_label.pack(side='bottom', fill='both', expand=1)
root_frame = Frame(root)
root_frame.pack(side='top', fill='both', expand=1, pady=40)
frame = Frame(root_frame, container=1)
frame.pack()
button_frame = Frame(root_frame)
button_frame.pack(side='bottom', fill='x', expand=1)
exit_button = Button(button_frame, command=exit_mplayer, text='exit')
mark_button = Button(button_frame, command=set_chapter, text='set chapter')
seek_frame = Frame(root_frame)
seek_frame.pack(side='left', fill='x', expand=1, padx=30)
#seek_label1 = Label(seek_frame, text='Seek %')
#seek_label1.pack(side='left')
seek_scale = Scale(seek_frame, from_=0, to=99, orient='horizontal')
seek_scale.bind('<ButtonRelease-1>', seek)
seek_scale.pack(side='left', fill='x', expand=1)
mark_button.pack(side='left', fill='both', expand=1)
exit_button.pack(side='left', fill='both', expand=1)

xid = root.tk.call('winfo', 'id', frame)
dir = mkdtemp(prefix='tovid-')
cmd_pipe = path.join(dir, 'slave.fifo')
mkfifo(cmd_pipe)
editlist = path.join(dir, 'editlist')
media_file = sys.argv[1]
# try to get aspect ratio
v_width = 600
asr = get_asr(media_file)
print 'asr is: ', asr
if asr > 0.0:
    v_height = int(v_width/asr)
else:
    v_height = int(v_width/1.333)
frame.configure(width=v_width, height=v_height)
# disable keyboard input with nodefault-bindings...
mplayer_cmd =  'mplayer -wid %s -nomouseinput -idle -slave \
  -input nodefault-bindings:conf=/dev/null:file=%s \
  -edlout %s %s ' %(xid, cmd_pipe, editlist, media_file)
mplayer_cmd = shlex.split(mplayer_cmd)
cmd = Popen(mplayer_cmd, stderr=STDOUT, stdout=open(devnull, 'w'))
# show osd time and remaining time
send_command('osd 3')


if __name__ == '__main__':
    root.mainloop()

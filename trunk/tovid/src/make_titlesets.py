from Tkinter import *
from tkFileDialog import askopenfilename
from subprocess import Popen, PIPE
import os.path
from libtovid.metagui import Style
from tkMessageBox import *

num_titles = 0
todisc_cmds = []
error_msg = 'This is not a saved GUI script\n' + \
  'Please select the file that you saved'

def move(amt):
    global current
    ind = pages.index(current) + amt
    if not 0 <= ind < len(pages):
        return
    current.pack_forget()
    current = pages[ind]
    current.pack(side=TOP, fill=BOTH, expand=1)

def next():
    # if 1st page (general) then
    # move forward and unless cancelled, append anything added in current
    # page to [todisc_cmds], removing todisc_cmds[current] first
    global num_titles, todisc_cmds
    mv_amt = +1
    if pages.index(current) == 0:
        # withdraw the wizard and run the GUI, collecting commands
        tk.withdraw()
        get_commands = run_gui()
        # append to list and go to next page unless GUI was cancelled out of
        if len(get_commands) == 1 and 'Cancelled' in get_commands:
            mv_amt = 0
        else:
            if len(todisc_cmds) > 0:
                todisc_cmds.pop(0)
            #cmds = [l + ' \\' for l in get_commands if l]
            # get header: shebang, PATH, and 'todisc'
            global header
            header = []
            while not get_commands[0].startswith('-'):
                header.append(get_commands[0] + '\n')
                get_commands.pop(0)
            header[-1] = 'todisc \\\n'
            cmds = [l for l in get_commands if l]
            todisc_cmds.append(cmds)
            print header
        tk.deiconify()
    elif pages.index(current) == 1:
        cmds = list(listbox1.get(0, END))
        cmds = [l for l in cmds if l]
        cmds.insert(0, '-vmgm')
        cmds.insert(1, '-titles')
        # add an backslash and trailing newline char to each line
        #cmds = [l + ' \\' for l in cmds if l]
        # withdraw the wizard and run the GUI, collecting commands
        tk.withdraw()
        get_commands = run_gui()
        # append to list and go to next page unless GUI was cancelled out of
        if len(get_commands) == 1 and 'Cancelled' in get_commands:
            mv_amt = 0
        else:
            if len(todisc_cmds) > 1:
                todisc_cmds.pop(1)
                # get rid of shebang and PATH statements
            while not get_commands[0].startswith('-'):
                get_commands.pop(0)
            cmds.extend(get_commands)
            cmds.append('-end-vmgm')
            todisc_cmds.append(cmds)
        print todisc_cmds
        cmdout = open(script_file, 'w')
        # add the shebang, PATH, and 'todisc \' lines
        cmdout.writelines(header)
        # flatten the list
        #all_lines = [line for line in sublist for sublist in todisc_cmds]
        all_lines = [line for sublist in todisc_cmds for line in sublist]
        #
        # write every line with a '\' at the end, except the last
        for line in all_lines[:-1]:
            cmdout.write(line + ' \\\n')
        # write the last line
        cmdout.write(all_lines[-1])
        cmdout.close()
        tk.deiconify()
        #num_titles = len(list(listbox1.get(0, END)))-1
        #temp_list.pop(-1)
    elif pages.index(current) == 2:
        #save_list()
        # delete titleset listbox contents else it increases with page movement
        listbox2.delete(0, END)
        numtitles = num_titles
        if (numtitles > 10): numtitles = 10
        listbox2.configure(height=numtitles)
        # insert or reinsert VMGM titles into titleset listbox
        for i in xrange(numtitles):
            listbox2.insert(END, temp_list[i])
    move(mv_amt)

def prev():
    move(-1)

def get_list(event):
    """
    function to read the listbox selection
    and put the result in an entry widget
    """
    try:
        # get selected line index
        index = listbox1.curselection()[0]
        # get the line's text
        seltext = listbox1.get(index)
        # delete previous text in enter1
        enter1.delete(0, END)
        # now display the selected text
        enter1.insert(0, seltext)
    except IndexError:
        pass

def set_list(event):
    """
    insert an edited line from the entry widget
    back into the listbox
    """
    try:
        index = listbox1.curselection()[0]
        # delete old listbox line
        listbox1.delete(index)
    except IndexError:
        index = END
    # insert edited item back into listbox1 at index
    listbox1.insert(index, enter1.get())
    enter1.delete(0, END)
    # add a new index if we are at end of list
    if listbox1.get(END):
        listbox1.insert(END, enter1.get())
    listbox1.selection_set(END)

def save_list():
    """
    save the current listbox contents to a file
    """
    global num_titles, temp_list
    # get a list of listbox lines
    temp_list = list(listbox1.get(0, END))
    num_titles = len(list(listbox1.get(0, END)))-1
    #temp_list.pop(-1)
    # add a trailing newline char to each line
    vmgm_titles = [l + ' \\' for l in temp_list if l]
    # give the file a different name
    #fout = open("todisc_commands.bash", "w")
    #fout.writelines(temp_list)
    #fout.close()
    #sys.stdout.write('\n'.join(temp_list))
    #quit()

def run_gui():
    #todiscgui_cmd = tovid_prefix + '/' + 'todiscgui'
    todiscgui_cmd = Popen(['tovid', 'gui'], stdout=PIPE)
    status = todiscgui_cmd.wait()
    if status == 0:
        todisc_cmds = read_script()
    else:
        todisc_cmds = []
    return todisc_cmds

def read_script():
    title = 'load saved script'
    curdir = os.path.abspath('')
    script = 'todisc_commands.bash'

    if os.path.exists(script_file):
        filecontents = get_contents(script_file)
        script_status = check_script(filecontents)
    else:
        while not os.path.exists(script):
            script = askopenfilename(title=title, initialfile=script)
            if script:
                filecontents = get_contents(script)
                script_status = check_script(filecontents)
            else:
                showinfo(message='Operation cancelled, Returning')
                return ['Cancelled']
    if script_status:
        return filecontents
    else:
        return ['Cancelled']

def check_script(contents):
    # not sure what to use now that '\\\n is stripped before running this
    if not 'todisc' in contents:
        showerror(message=error_msg)
        return False 
    else:
        return True
 
 
def get_contents(script_file):
    filecontents = [line.rstrip(' \\\n') for line in open('todisc_commands.bash')]
    #filedata = open(script_file, "r")
    #filecontents = filedata.readlines()
    #filedata.close()
    return filecontents
 


###################### get/set some external variables #######################

# get tovid prefix
path_cmd = ['tovid', '--prefix']
tovid_prefix = Popen(path_cmd, stdout=PIPE)
tovid_prefix = tovid_prefix.communicate()[0].strip()

# get metagui font configuration
inifile = os.path.expanduser('~/.metagui/config')
style = Style()
style.load(inifile)
caption_font = list(style.font)
caption_font[2] = 'bold'
heading_font = []
lrg_font = []
bold_font = []
heading_font.extend(caption_font)
lrg_font.extend(caption_font)
bold_font.extend(caption_font)
heading_font[1] = 20
lrg_font[1] = 16
bold_font[2] = 'bold'

# the script we will be using for options
cur_dir = os.path.abspath('')
script_file = cur_dir + '/todisc_commands.bash'


##############################################################################
##################### GUI initialization and execution #######################
##############################################################################

tk = Tk()
tkframe = Frame(tk)
tkframe.pack(side=LEFT, fill=Y, anchor='w')
tk.title('Tovid titleset wizard')
tk.minsize(width=800, height=660)
button_frame = Frame(tk)
button_frame.pack(expand=1, fill=X, side=BOTTOM, anchor='s')
button2 = Button(button_frame, text='Previous', command=prev)
button2.pack(side=LEFT, fill=X, expand=1, anchor='w')
button1 = Button(button_frame, text='Next', command=next)
button1.pack(side=RIGHT, fill=X, expand=1, anchor='e')

############################ Page 1 of wizard ############################
text0 = '''
iNTRODUCTION

Welcome to the tovid titleset wizard.  We will be making a complete DVD, with
multiple levels of menus including a root menu (VMGM menu) and titleset menus.
menus. We will be using the 'tovid gui', which uses the 'todisc' script.

Any of these menus can be either static or animated, and use thumbnail menu
links or plain text links.  In addition the titleset menus can have chapter
selection menus ("submenus") which by default have only thumbnail menu links.

A great many options of these menus are configurable, including fonts, shapes
shapes and effects for thumbnails, fade-in/fade-out effects, "switched menus",
the addition of a "showcased" image/video, animated or static background image or
video, audio background ... etc.  There are also playback options including the
supplying of chapter points, special navigation features like "quicknav",
and configurable DVD button links.

LET'S BEGIN

When you press the "Next" button at the bottom of the wizard, we will start the
GUI and begin with general options applying to all titlesets.  The only REQUIRED
option here is specifying an Output directory at the bottom of the GUI's main tab.
'''
text1 = '''
After making your selections, it is important that you save the file to
%s

Press 'Next' to begin ...
''' %script_file
#   The GUI will then be called repeated for each titleset you wish to make.
#
#    Each time you will need to press the "Save script" button and save to the same
#    file.  When you have no more titlesets, press the "Done" button and you will
#    be prompted to run your final project.
#
#    Press "Next" to begin...

page1 = Frame(tk)
frame1 = Frame(tkframe)
img_file = tovid_prefix + '/data/tovid.gif'
if os.path.isfile(img_file):
    img = PhotoImage(file=img_file)
    label1 = Label(frame1, text='Tovid', font=heading_font)
    label1.pack(side=TOP, pady=40)
else:
    print img_file, ' does not exist'
label2 = Label(frame1, image=img).pack(side=TOP)
label3 = Label(frame1, text='Titleset Wizard', font=lrg_font)
label3.pack(side=TOP, pady=40)
#label4 = Label(frame1, text='Wizard', font=lrg_font).pack(side=TOP)
frame1.pack(side=LEFT, padx=30, anchor='nw')
page1.pack(fill=BOTH, expand=1)
label5 = Label(page1, text=text0, justify=LEFT, font=style.font)
label5.pack(fill=BOTH, expand=1, side=TOP, anchor='w')
label6 = Label(page1, text=text1, justify=LEFT, font=caption_font)
label6.pack(fill=BOTH, expand=1, side=TOP, anchor='w')
############################ Page 2 of wizard ############################
text2 = \
'''Now we will save options for your root (VMGM) menu.  The only option you
really need is the titleset titles.  Since you can not save titles in the GUI
without loading videos you need to enter them here.  These titleset names will
appear as menu titles for the respective menu in your DVD.

Enter the names of your titlesets, one per line, pressing <ENTER> each time.
Do not use quotes unless you want them to appear literally in the title.

Press "Next" when you are finished.

'''

page2 = Frame(tk)
page2_opts = ['-vmgm \\\n', '-titles \\\n']
page3_opts = ['-titleset \\\n']
label2 = Label(page2, text=text2, justify=LEFT, font=style.font)
label2.pack(fill=BOTH, expand=1)
# create the listbox (note that size is in characters)
list_frame = LabelFrame(page2, text="Root 'menu link' titles")
list_frame.pack(fill=Y, expand=1)
listbox1 = Listbox(list_frame, width=50, height=12)
#listbox1.insert(0, '')
listbox1.pack(side=LEFT, fill=Y, expand=1)

# create a vertical scrollbar to the right of the listbox
yscroll = Scrollbar(list_frame, command=listbox1.yview, orient=VERTICAL)
yscroll.pack(side=LEFT, fill=Y)
listbox1.configure(yscrollcommand=yscroll.set)

# use entry widget to display/edit selection
enter1 = Entry(page2, width=50, text='Enter titles here')
enter1.pack(fill=Y, expand=1)
# set focus on entry
enter1.select_range(0, 'end')
enter1.focus_set()
# pressing the return key will update edited line
enter1.bind('<Return>', set_list)

# button to save the listbox's data lines to a file
#button2 = Button(page2, text='Done', command=save_list)
#button2.pack(fill=X, expand=1, side=LEFT, anchor='sw')


listbox1.bind('<ButtonRelease-1>', get_list)

############################ Page 3 of wizard ############################

page3 = Frame(tk)
text3 = '''
'''
label7 = Label(page2, text=text3, justify=LEFT, font=style.font)
label7.pack(fill=BOTH, expand=1)
# create the listbox (note that size is in characters)
list_frame2 = LabelFrame(page3, text="Your titlesets")
list_frame2.pack(fill=X, expand=1)

listbox2 = Listbox(list_frame2, width=60)

#listbox1.insert(0, '')
listbox2.pack(side=LEFT, fill=X, expand=1)

# create a vertical scrollbar to the right of the listbox
yscroll2 = Scrollbar(list_frame2, command=listbox2.yview, orient=VERTICAL)
yscroll2.pack(side=LEFT, fill=Y)
listbox2.configure(yscrollcommand=yscroll.set)

# button to save the listbox's data lines to a file
#button2 = Button(page2, text='Done', command=save_list)

#    run the gui and collect the options

############################ Page 4 of wizard ############################

page4 = Frame(tk)
page4_frame = Frame(page4)
page4_frame.pack(fill=BOTH, expand=1)
page4label = Label(page4_frame, text='This is page 4')
page4label.pack()

page5 = Frame(tk)
page5_frame = Frame(page5)
page5_frame.pack(fill=BOTH, expand=1)
page5label = Label(page5_frame, text='This is page 5')
page5label.pack()

######################### Run the darn thing already #########################

pages = [page1, page2, page3, page4, page5]
current = page1
mainloop()

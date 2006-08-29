#!/usr/bin/python
# -=- encoding: latin-1 -=-
import unittest
import dvdauthor

class TestDvdauthor(unittest.TestCase):
    """Test the pydvdauthor module"""
    
    def setUp(self):
        """Create a new Disc object, brand new and empty"""
        self.disc = dvdauthor.Disc()

    def tearDown(self):
        pass

    ###################
    ### Begin tests ###
    ###################

    def test_vmgm(self):
        # Create VMGM menu structure
        vmgm = dvdauthor.VMGM('The first top-level menu')
        # Add it to the disc
        self.disc.set_vmgm(vmgm)

        # Create a men
        menu1 = dvdauthor.Menu('Main menu example')
        vmgm.add_menu(menu1)

    def test_ids(self):
        """Make sure everything sets an ID"""
        assert self.disc.id

        menu = dvdauthor.Menu('this is my menu')
        title = dvdauthor.Title('this is my title')
        vmgm = dvdauthor.VMGM('This is my official VMGM')
        titleset = dvdauthor.Titleset('this is my own Titleset')
        self.assert_(menu.id)
        self.assert_(title.id)
        self.assert_(vmgm.id)
        self.assert_(titleset.id)

    def test_add_titleset(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        x = len(self.disc.titlesets)
        self.disc.add_titleset(titleset)
        y = len(self.disc.titlesets)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Disc.add_titleset() should add "\
                     "the Titleset to self.titlesets")

    def test_add_title(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        title = dvdauthor.Title('This is my own Title')

        x = len(titleset.titles)
        titleset.add_title(title)
        y = len(titleset.titles)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_title() should add "\
                     "the Title to self.titles")

    def test_add_menu(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')
        menu = dvdauthor.Menu('This is my own Menu')

        x = len(titleset.menus)
        titleset.add_menu(menu)
        y = len(titleset.menus)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_menu() should add "\
                     "the Menu to self.menus")


    def test_add_audiolang(self):
        titleset = dvdauthor.Titleset('This is my new Titleset')

        x = len(titleset.audio_langs)
        titleset.add_audio_lang('fr')
        y = len(titleset.audio_langs)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Titleset.add_audio_lang() should add "\
                     "the audio_lang to self.audio_langs")


    def test_add_subpictures(self):
        vmgm = dvdauthor.VMGM('This is my new VMGM')

        x = len(vmgm.subpictures)
        vmgm.add_subpicture_lang('fr')
        y = len(vmgm.subpictures)

        # Make sure it's really added.
        self.assert_(y == (x+1), "VMGM.add_subpicture_lang() should add "\
                     "the audio_lang to self.subpictures")

    def test_add_videofile(self):
        title = dvdauthor.Title('This is my Title')

        x = len(title.videofiles)
        title.add_video_file('thisfile.mpg')
        y = len(title.videofiles)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Title.add_video_file() should add "\
                     "the file,chapters,pause to self.videofiles")

    def test_add_cell(self):
        title = dvdauthor.Title('This is my Title')

        x = len(title.cells)
        title.add_cell('0:10', '10:10')
        y = len(title.cells)

        # Make sure it's really added.
        self.assert_(y == (x+1), "Title.add_cell() should add "\
                     "the start,end,chapter,program,pause to self.cells")

    def test_set_prepost_cmds(self):
        """Make sure the pre/post_commands are set properly"""
        menu = dvdauthor.Menu('This is my menu')
        
        cmd = 'jump %s' % menu.id
        menu.set_pre_commands(cmd)
        self.assert_(cmd == menu.pre_cmds)
        
        cmd = 'jump cell 1'
        menu.set_pre_commands(cmd)
        self.assert_(cmd == menu.pre_cmds)
        
    def test_button_set(self):
        """Make sure the commands are set for the good button, even
        if we overwrite it's value"""
        menu = dvdauthor.Menu('this is a Menu')
        cmd1 = 'jump cell 1'
        menu.set_button_commands(cmd1, None)
        cmd2 = 'jump cell 2'
        menu.set_button_commands(cmd2, None)
        cmd3 = 'jump cell 3'
        menu.set_button_commands(cmd3, 'MyButton')
        cmd4 = 'jump cell 4'
        menu.set_button_commands(cmd4, 'MyButton')

        self.assert_(menu.buttons[0][1] == cmd1)
        self.assert_(menu.buttons[1][1] == cmd2)
        # the value was overwritte by cmd4, if everything works
        self.assert_(menu.buttons[2][1] == cmd4)
        

    def test_set_vmgm(self):
        vmgm = dvdauthor.VMGM('This is my VMGM menu')

        self.assert_(self.disc.vmgm == None)
        
        self.disc.set_vmgm(vmgm)

        self.assert_(self.disc.vmgm != None)

if __name__ == '__main__':
    unittest.main()

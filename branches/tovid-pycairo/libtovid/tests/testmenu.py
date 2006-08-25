import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
import menu
import standards


class TestMenu(unittest.TestCase):
    def test_preproc(self):
        """Test if the preproc grabs it's arguments from standards"""
        m = menu.Menu({'format': 'dvd', 'tvsys': 'ntsc'})
        m.preproc()

        w, h = standards.get_resolution('dvd', 'ntsc')
        r = standards.get_samprate('dvd')
        
        self.assertEquals(m.options['samprate'], r)
        self.assertEquals(m.options['expand'], (w, h))


if __name__ == '__main__':
    unittest.main()

#! /usr/bin/env python
# test_menu.py

import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid.layout import menu
from libtovid import standard


class TestMenu(unittest.TestCase):
    def test_preproc(self):
        """Test if the preproc grabs its arguments from standard"""
        m = menu.Menu({'format': 'dvd', 'tvsys': 'ntsc'})
        m.preproc()

        w, h = standard.resolution('dvd', 'ntsc')
        r = standard.samprate('dvd')
        
        self.assertEquals(m.options['samprate'], r)
        self.assertEquals(m.options['expand'], (w, h))


if __name__ == '__main__':
    unittest.main()

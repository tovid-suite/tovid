#! /usr/bin/env python
# test_media.py

import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from libtovid import media


class TestMedia(unittest.TestCase):
    def test_init(self):
        """Blank test"""
        pass


if __name__ == '__main__':
    unittest.main()


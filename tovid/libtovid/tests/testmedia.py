import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
import media


class TestMedia(unittest.TestCase):
    def test_init(self):
        """Blank test"""
        pass


if __name__ == '__main__':
    unittest.main()


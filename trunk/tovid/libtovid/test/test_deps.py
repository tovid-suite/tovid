"""Unit test for deps.py"""

import unittest
from libtovid import deps

class BadInput(unittest.TestCase):

    I = 9
    T = ('hello', 'world')

    def testInt(self):
        """require should not accept integer input"""
        self.assertRaises(ValueError, deps.require, self.I)

    def testTup(self):
        """require should not accept tuple input"""
        self.assertRaises(ValueError, deps.require, self.T)


class MissingDependency(unittest.TestCase):

    D = {"foo": "a fictional utility (foo.org)",
         "bar": "something to duck under (bar.gov)"}
    L = ["foo", "bar"]
    S = "foo bar"

    def testFoobar(self):
        """require should never find foo or bar!"""
        print("Testing a dictionary.\n")
        self.assertRaises(deps.MissingDep, deps.require, self.D)
        print("\n\nTesting a list.\n")
        self.assertRaises(deps.MissingDep, deps.require, self.L)
        print("\n\nTesting a string.\n")
        self.assertRaises(deps.MissingDep, deps.require, self.S)

if __name__ == "__main__":
    unittest.main()

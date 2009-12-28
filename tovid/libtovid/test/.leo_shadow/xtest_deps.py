#@+leo-ver=4-thin
#@+node:eric.20090722212922.3355:@shadow test_deps.py
#@+others
#@+node:eric.20090722212922.3356:test_deps declarations
"""Unit test for deps.py"""

import unittest
from libtovid import deps

#@-node:eric.20090722212922.3356:test_deps declarations
#@+node:eric.20090722212922.3357:class BadInput
class BadInput(unittest.TestCase):

    I = 9
    T = ('hello', 'world')

    #@    @+others
    #@+node:eric.20090722212922.3358:testInt
    def testInt(self):
        """require should not accept integer input"""
        self.assertRaises(deps.InputError, deps.require, self.I)

    #@-node:eric.20090722212922.3358:testInt
    #@+node:eric.20090722212922.3359:testTup
    def testTup(self):
        """require should not accept tuple input"""
        self.assertRaises(deps.InputError, deps.require, self.T)


    #@-node:eric.20090722212922.3359:testTup
    #@-others
#@-node:eric.20090722212922.3357:class BadInput
#@+node:eric.20090722212922.3360:class MissingDependency
class MissingDependency(unittest.TestCase):

    D = {"foo": "a fictional utility (foo.org)",
         "bar": "something to duck under (bar.gov)"}
    L = ["foo", "bar"]
    S = "foo bar"

    #@    @+others
    #@+node:eric.20090722212922.3361:testFoobar
    def testFoobar(self):
        """require should never find foo or bar!"""
        print("Testing a dictionary.\n")
        self.assertRaises(deps.MissingError, deps.require, self.D)
        print("\n\nTesting a list.\n")
        self.assertRaises(deps.MissingError, deps.require, self.L)
        print("\n\nTesting a string.\n")
        self.assertRaises(deps.MissingError, deps.require, self.S)

    #@-node:eric.20090722212922.3361:testFoobar
    #@-others
#@-node:eric.20090722212922.3360:class MissingDependency
#@-others
if __name__ == "__main__":
    unittest.main()
#@-node:eric.20090722212922.3355:@shadow test_deps.py
#@-leo

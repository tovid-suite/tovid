import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
import cli


class TestArg(unittest.TestCase):
    def assertArg(self, output, arg=None):
        if arg is None:
            arg = self.arg
            
        self.assertEquals(output, str(arg))
    
    def test_arg(self):
        a = cli.Arg("foo")
        self.assertEquals(str(a), "foo")
        
        a.add("bar")
        self.assertEquals(str(a), "foo bar")

    def test_special_chars(self):
        a = self.arg = cli.Arg("foo")
        
        a.add("&")
        
        self.assertArg('foo "&"')


        a.add("<")
        
        self.assertArg('foo "&" "<"')

        a.add(">")
        
        self.assertArg('foo "&" "<" ">"')

        a.add("\"")
        
        self.assertArg('foo "&" "<" ">" "\\""')

        a.add(" poop ")
        
        self.assertArg('foo "&" "<" ">" "\\"" " poop "')


        a = self.arg = cli.Arg("foo")
        
        a.add("(Oh Man!")
        
        self.assertArg('foo "(Oh Man!"')

    def test_pipe(self):
        a = cli.Arg("foo")
        
        b = a.pipe(cli.Arg("bar"))

        self.arg = b
        
        self.assertArg("foo | bar")

        self.assertRaises(TypeError, b.read_from, "foo")
        
        a = cli.Arg("foo")
        a.write_to("/dev/null")
        self.assertArg("foo > /dev/null", a)
        # since 'a' is redirecting it's output into a file it can be
        # used in a pipe
        self.assertRaises(TypeError, a.pipe, cli.Arg("bar"))

        a = cli.Arg("bar")
        a.read_from("/dev/zero")
        self.assertArg("bar < /dev/zero", a)
        # the second command is reading from a file, thus it can't
        # be used in a pipe either
        self.assertRaises(TypeError, cli.Arg("foo").pipe, a)
        
        a = cli.Arg("foo")
        b = cli.Arg("bar")
        c = a.pipe(b)
        
        # a pipe object is not the same as 'b' or 'a'
        assert b is not c
        assert a is not c
        
        # changes on a pipe are reflected on the second argument
        c.write_to("/dev/null")
        self.assertEquals("/dev/null", c.stdout)
        self.assertEquals("/dev/null", b.stdout)
        self.assertArg("bar > /dev/null", b)
        self.assertArg("foo | bar > /dev/null", c)

        # changes on the actual object are reflected on the pipe
        b.write_to(None)
        assert c.stdout is None
        assert b.stdout is None
        self.assertArg("bar", b)
        self.assertArg("foo | bar", c)
        
    
    def test_bg(self):
        """Tests programs that run in background"""
        a = cli.Arg("foo")
        b = a.to_bg()
        # the object returned is a new object, not the same
        assert a is not b
        
        self.assertArg("foo", a)
        self.assertArg("foo &", b)

    def test_and(self):
        a = cli.Arg("a")
        b = cli.Arg("b")
        c = a.if_done(b)
        assert c is not a
        assert c is not b
        self.assertArg("a && b", c)

        d = cli.Arg("d")
        e = c.if_done(d)
        
        self.assertArg("(a && b) && c", e)

if __name__ == '__main__':
    unittest.main()

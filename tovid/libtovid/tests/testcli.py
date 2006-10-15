import unittest
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
import cli


class TestCommand(unittest.TestCase):
    def assertCommand(self, output, arg=None):
        if arg is None:
            arg = self.arg
            
        self.assertEquals(output, str(arg))
    
    def test_arg(self):
        a = cli.Command("foo")
        self.assertEquals(str(a), "foo")
        
        a.add("bar")
        self.assertEquals(str(a), "foo bar")

    def test_special_chars(self):
        a = self.arg = cli.Command("foo")
        
        a.add("&")
        
        self.assertCommand('foo "&"')


        a.add("<")
        
        self.assertCommand('foo "&" "<"')

        a.add(">")
        
        self.assertCommand('foo "&" "<" ">"')

        a.add("\"")
        
        self.assertCommand('foo "&" "<" ">" "\\""')

        a.add(" poop ")
        
        self.assertCommand('foo "&" "<" ">" "\\"" " poop "')


        a = self.arg = cli.Command("foo")
        
        a.add("(Oh Man!")
        
        self.assertCommand('foo "(Oh Man!"')

    def test_pipe(self):
        a = cli.Command("foo")
        
        b = a.pipe(cli.Command("bar"))

        self.arg = b
        
        self.assertCommand("foo | bar")

        self.assertRaises(TypeError, b.read_from, "foo")
        
        a = cli.Command("foo")
        a.write_to("/dev/null")
        self.assertCommand("foo > /dev/null", a)
        # since 'a' is redirecting it's output into a file it can be
        # used in a pipe
        self.assertRaises(TypeError, a.pipe, cli.Command("bar"))

        a = cli.Command("bar")
        a.read_from("/dev/zero")
        self.assertCommand("bar < /dev/zero", a)
        # the second command is reading from a file, thus it can't
        # be used in a pipe either
        self.assertRaises(TypeError, cli.Command("foo").pipe, a)
        
        a = cli.Command("foo")
        b = cli.Command("bar")
        c = a.pipe(b)
        
        # a pipe object is not the same as 'b' or 'a'
        assert b is not c
        assert a is not c
        
        # changes on a pipe are reflected on the second argument
        c.write_to("/dev/null")
        self.assertEquals("/dev/null", c.stdout)
        self.assertEquals("/dev/null", b.stdout)
        self.assertCommand("bar > /dev/null", b)
        self.assertCommand("foo | bar > /dev/null", c)

        # changes on the actual object are reflected on the pipe
        b.write_to(None)
        assert c.stdout is None
        assert b.stdout is None
        self.assertCommand("bar", b)
        self.assertCommand("foo | bar", c)
        
    
    def test_bg(self):
        """Tests programs that run in background"""
        a = cli.Command("foo")
        b = a.to_bg()
        # the object returned is a new object, not the same
        assert a is not b
        
        self.assertCommand("foo", a)
        self.assertCommand("foo &", b)

    def test_and(self):
        a = cli.Command("a")
        b = cli.Command("b")
        c = a.if_done(b)
        assert c is not a
        assert c is not b
        self.assertCommand("a && b", c)

        d = cli.Command("d")
        e = c.if_done(d)
        
        self.assertCommand("(a && b) && c", e)

if __name__ == '__main__':
    unittest.main()

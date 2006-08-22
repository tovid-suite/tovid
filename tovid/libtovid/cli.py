#! /usr/bin/env python
# cli.py

"""This module provides an interface for running command-line applications.

Most of tovid's work is done by calling external applications (mplayer,
mpeg2enc, ffmpeg...) with usually lengthy command-lines. The Command class is a
simple interface for building command-lines, spawning subprocesses, and reading
output from them.
"""

__all__ = ['Command', 'Script', 'verify_app']

# From standard library
import os
import sys
import tempfile
from stat import S_IREAD, S_IWRITE, S_IEXEC
from signal import SIGKILL
# From libtovid
from libtovid.log import Log

log = Log('libtovid.cli')

class Command:
    """A command-line app with arguments, and process control."""
    def __init__(self, command, purpose=''):
        """Create a Command with the given command-line string. Optionally
        include a brief description of the command's purpose.

        The command string should begin with the name of the application to
        invoke, followed by that application's arguments. For example:

            >>> cmd = Command('ls -l /usr', "List contents of /usr")

        Then, to execute the command, call:

            >>> cmd.run()
        
        """
        self.command = command
        self.purpose = purpose
        self.childpid = None
        # All lines of output from the command
        self.output = []

    def append(self, args):
        """Append the given string of arguments to the end of the command."""
        if not isinstance(args, str):
            raise TypeError, "Command.append() can only take strings."
        self.command += ' ' + args

    def prepend(self, args):
        """Prepend the given string of arguments."""
        self.command = args + ' ' + self.command

    def run(self, wait=True):
        log.info(self.purpose)
        log.info(self.command)
        try:
            self._run(wait)
        except KeyboardInterrupt:
            print "Process interrupted. Exiting..."
            self.kill()
            sys.exit()

    def _run(self, wait):
        """Execute the command and return its exit status. Optionally wait for
        execution to finish."""
        fd, self.tempfile = tempfile.mkstemp()
        # Fork a child process to run the command and log output
        pid = os.fork()
        if pid == 0: # Child
            log.debug("Writing command output to temporary file %s" %
                      self.tempfile)
            cmd = "%s > %s 2>&1" % (self.command, self.tempfile)
            status = os.system(cmd)
            sys.exit()
        else: # Parent
            self.childpid = pid
            if wait:
                os.waitpid(self.childpid, 0)
                self.get_output()

    def get_output(self):
        """Retrive output from the temp file and store locally."""
        file = open(self.tempfile, 'r')
        for line in file.readlines():
            self.output.append(line.rstrip('\r\n '))
        file.close()
        for line in self.output:
            log.info(line)
        os.remove(self.tempfile)

    def kill(self):
        """Kill all processes spawned by this Command."""
        if self.childpid:
            os.kill(self.childpid, SIGKILL)

class Script:
    """An executable shell script."""
    def __init__(self, name, locals={}):
        """Create a script, with optional local variables and values.
        Any variables named in locals may then be used by script
        commands using the shell $var_name syntax."""
        self.commands = []
        self.name = name
        self.locals = locals

    def append(self, command):
        """Append the given command to the end of the script."""
        self.commands.append(str(command))

    def prepend(self, command):
        """Prepend the given command at the beginning of the script."""
        self.commands.insert(0, str(command))

    def text(self):
        """Return the text of the script."""
        text = '#!/bin/sh\n'
        text += 'cat %s\n' % self.script_file
        # TODO: 
        for var, value in self.locals.iteritems():
            text += '# %s=%s\n' % (var, value)
        for cmd in self.commands:
            text += '%s\n' % cmd
        text += 'exit\n'
        return text

    def run(self):
        """Write the script, execute it, and remove it."""
        log.info("Preparing to execute script...")
        self._prepare()
        # TODO: Stream redirection (to logfile/stdout)
        log.info("Running script: %s" % self.script_file)
        os.system('sh %s' % self.script_file)
        #os.remove(self.script_file)
        log.info("Finished script: %s" % self.script_file)

    def _prepare(self):
        """Write the script to a temporary file and prepare it for execution."""
        fd, self.script_file = tempfile.mkstemp('.sh', self.name)
        # Make script file executable
        os.chmod(self.script_file, S_IREAD|S_IWRITE|S_IEXEC)
        # Write the script to the temporary script file
        script = file(self.script_file, 'w')
        script.write(self.text())
        script.close()

def verify_app(appname):
    """If appname is not in the user's path, print a error and exit."""
    """ - True if app exists, 
        - False if not """
    env_path = os.getenv("PATH")
    found = False
    for dir in env_path.split(":"):
        if (os.path.exists("%s/%s" % (dir, appname))):
            log.info("Found %s/%s" % (dir, appname))
            found =  True
            break
        
    if found == False:
        log.error("%s not found in your PATH. Exiting.." % appname)
        sys.exit()
        
     
def enc_arg(arg):
    """Converts it to a string and encodes an argument making it safe 
    from special bash characters"""
    arg = str(arg)
    for special_char in '# "\'\\&|<>()':
        if special_char in arg:
            return '"%s"' % arg.replace('\\', '\\\\').replace('"', '\\"')
    return arg

class Bg(object):
    """
    This makes sure there is only one 'Arg' in backgrond.
    """
    def __init__(self, arg):
        if not isinstance(arg, Arg):
            raise TypeError("must be an Arg")
            
        self.arg = arg
    
    def __str__(self):
        return str(self.arg) + " &"
    
    def __repr__(self):
        return "Bg(%r)" % self.arg

class Pipe(object):
    """Represents a pipe object, makes sure no extra operations
    are performed to a piped command."""
    
    def __init__(self, first, after):
        self.first = first
        self.after = after
    
    def read_from(self, filename):
        raise TypeError("Piped programs cannot read from other places.")

    def __repr__(self):
        return "Pipe(%r, %r)" % (self.first, self.after)
    
    def __str__(self):
        return "%s | %s" % (self.first, self.after)

    def __getattr__(self, attr):
        return getattr(self.after, attr)

class Arg(object):
    """An object used for creating commands used on shell scripts.
    It encodes the arguments automagically. Examples::

        >>> Arg('echo')
        Arg('echo')
        >>> echo = Arg('echo')
        >>> echo.add('foo', 'bar')
        >>> echo
        Arg('echo foo bar')
        >>> Arg("echo") + 'foo and bar'
        Arg('echo "foo and bar"')
        >>> echo = Arg("echo").add('foo and bar')
        >>> echo
        Arg('echo "foo and bar"')
        >>> echo += "baz"
        Arg('echo "foo and bar" baz')
        >>> str(echo)
        'echo "foo and bar" baz'
        
    """
    def __init__(self, arg="", stdin=None, stdout=None, stderr=None):
        self.arg = arg
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def __add__(self, other):
        return Arg(self.arg + " %s" % enc_arg(other))
    
    def add(self, *others):
        """Adds a number of strings, each argument is a command argument
        and will be encoded as such. This method returns the 'self'"""
        self.arg += " %s" % " ".join(map(enc_arg, others))
        return self

    def add_raw(self, raw):
        """the 'raw' argument must be a string and will be stripped of
        extra whitechars. Returns itself."""
        self.arg += " %s" % raw.strip()
        return self

    def pipe(self, other):
        """Creates a new Arg object which results on the pipe between this
        and the other program."""
        if self.stdout is not None:
            raise TypeError("Cannot pipe if output was redirected to a file.")
        if other.stdin is not None:
            raise TypeError("Cannot pipe if input of other process is redirected to a file.")
        
        return Pipe(self, other)

    def to_bg(self):
        """Makes this command run in background, returns itself."""
        return Bg(self)

    def read_from(self, filename):
        """makes the process read from a file"""
        self.stdin = filename

    def write_to(self, filename):
        """makes the process write to a file"""
        self.stdout = filename

    def errors_to(self, filename):
        """makes the process write error stream to a file"""
        self.stderr = filename

    def __str__(self):
        ret = self.arg
        if self.stdin is not None:
            ret += " < %s" % enc_arg(self.stdin)
        if self.stdout is not None:
            ret += " > %s" % enc_arg(self.stdout)
        if self.stderr is not None:
            ret += " 2> %s" % enc_arg(self.stderr)
            
        return ret

    def __repr__(self):
        return "Arg(%r, %r, %r, %r)" % (self.arg, self.stdin, self.stdout,
                                        self.stderr)
      

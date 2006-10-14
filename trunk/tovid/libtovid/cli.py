#! /usr/bin/env python
# cli.py

"""This module provides an interface for running command-line applications.


"""

"""
Requirements (+: met, -: unmet):

+ Construct command lines by appending/inserting formatted text
+ Pipe commands to other commands
+ Print out commands before they are executed
+ Execute commands in foreground or background
- Capture or log output of commands
- Check exit status of commands

"""
__all__ = [\
    'Script',
    'And',
    'Or',
    'Command',
    'Bg',
    'NoBg',
    'InfixOper',
    'Pipe',
    'verify_app'
    ]

# From standard library
import os
import sys
import tempfile
import doctest
from subprocess import Popen, PIPE
from stat import S_IREAD, S_IWRITE, S_IEXEC
from signal import SIGKILL
# From libtovid
from libtovid.log import Log

log = Log('libtovid.cli')

class Script:
    """An executable shell script."""
    def __init__(self, name, locals=None):
        """Create a script, with optional local variables and values.
        Any variables named in locals may then be used by script
        commands using the shell $var_name syntax.
        
            name:   Name of the script, as a string
            locals: Dictionary of name/value pairs for local variables
            
        """
        self.commands = []
        self.name = name
        self.locals = locals or {}

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
        # Write local variable definitions
        for var, value in self.locals.iteritems():
            text += '%s=%s\n' % (var.replace("-", "_"), enc_arg(value))
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
    """If appname is not found in the user's $PATH, print an error and exit."""
    """ - True if app exists, 
        - False if not """
    path = os.getenv("PATH")
    found = False
    for dir in path.split(":"):
        if os.path.exists("%s/%s" % (dir, appname)):
            log.info("Found %s/%s" % (dir, appname))
            found = True
            break
        
    if not found:
        log.error("%s not found in your PATH. Exiting." % appname)
        sys.exit()


def enc_arg(arg):
    """Convert an argument to a string, and do any necessary quoting so
    that bash will treat the string as a single argument."""
    arg = str(arg)
    # If the argument contains special characters, enclose it in single
    # quotes to preserve the literal meaning of those characters. Any
    # contained single-quotes must be specially escaped, though.
    for char in ' #"\'\\&|<>()[]!?*':
        if char in arg:
            return "'%s'" % arg.replace("'", "'\\''")
    # No special characters found; use literal string
    return arg


class Command(object):
    """An executable command-line statement with support for capturing output
    and piping to other commands.
    """
    def __init__(self, program, *args):
        """Create a Command that will run a given program with the given
        arguments.
        
            program: A string containing the name of a program to execute
            args:    Individual arguments to supply the command with
        
        For example:
        
            >>> cmd = Command('echo', 'Hello world')
            
        """
        self.program = program
        self.args = []
        for arg in args:
            self.args.append(arg)
        self.proc = None
        self.pipe = None
        self.output = ''

    def add(self, *args):
        """Append arguments to the command. The arguments to this function
        directly correspond to individual arguments to append to the command.
        Arguments are converted to string form, and special shell characters
        are handled automatically, so there is no need to escape them.
        """
        for arg in args:
            self.args.append(str(arg))

    def run(self, stdin=None):
        """Execute the command.
            stdin: File object to read input from
        """
        log.info("Running: " + str(self))
        self.output = ''
        self.proc = Popen([self.program] + self.args,
                    stdin=stdin, stdout=PIPE)
        # Run piped-to command if it exists
        if isinstance(self.pipe, Command):
            self.pipe.run(self.proc.stdout)
    
    def get_output(self):
        """Wait for the command to finish executing, and return a string
        containing the command's output. Returns an empty string if the
        command has not been run() yet.
        """
        if self.output is '' and self.proc is not None:
            self.output = self.proc.communicate()[0]
        return self.output
    
    def __str__(self):
        """Return a string representation of the Command.
        """
        ret = self.program
        for arg in self.args:
            ret += " %s" % enc_arg(arg)
        return ret

    def pipe_to(self, command):
        """Pipe the output of this Command into another Command.
            command: A Command to pipe to, or None to disable piping
        """
        if command:
            assert isinstance(command, Command)
        self.pipe = command


    # Deprecated(?) functions

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

    def if_done(self, other):
        """Creates a new object that represents the chained processes"""
        return And(self, other)
    
    def if_failed(self, other):
        return Or(self, other)

# Deprecated(?) classes
class Bg(object):
    """
    This makes sure there is only one Command in backgrond.
    """
    def __init__(self, command):
        assert isinstance(command, Command)
        self.command = command
    
    def __str__(self):
        return str(self.command) + " &"
    
    #def __repr__(self):
    #    return "Bg(%r)" % self.command

class Pipe(object):
    """Represents a pipe object, makes sure no extra operations
    are performed to a piped command."""
    
    def __init__(self, first, after):
        self.first = first
        self.after = after
    
    def read_from(self, filename):
        raise TypeError("Piped programs cannot read from other places.")

    #def __repr__(self):
    #    return "Pipe(%r, %r)" % (self.first, self.after)
    
    def __str__(self):
        return "%s | %s" % (self.first, self.after)

    def __getattr__(self, attr):
        return getattr(self.after, attr)


class InfixOper(object):
    """Represents the bash '&&', which means that the next command
    will only be run if the first one was run successfully."""

    OPER = None

    def __init__(self, first, after):
        self.first = first
        self.after = after

    def if_done(self, other):
        """Creates a new object that represents the chained processes"""
        return And(self, other)
    
    def if_failed(self, other):
        return Or(self, other)

    #def __repr__(self):
    #    return "%s(%r, %r)" % (type(self).__name__, self.first, self.after)
    
    def __str__(self):
        return "%s %s %s" % (group(self.first), self.OPER, group(self.after))

    def __getattr__(self, attr):
        return getattr(self.after, attr)



class NoBg(InfixOper):
    def __init__(self, first, after):
        if isinstance(first, Bg) or isinstance(after, Bg):
            raise TypeError("May not run 'if_done' commands with backgrounded process")

        super(NoBg, self).__init__(first, after)

def group(command):
    if isinstance(command, Command):
        return str(command)
    else:
        return "(%s)" % command

class And(NoBg):
    """Represents the bash '&&' other, which means that the next command
    will only be run if the first one was run successfully."""
    OPER = "&&"

class Or(NoBg):
    """Represents the bash '||' operator, which means that the next command
    will only be run if the first one was not run successfully."""
    OPER = "||"


if __name__ == '__main__':
    doctest.testmod(verbose=True)

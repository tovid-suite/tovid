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
    'Command',
    'Script',
    'verify_app'
    ]

# From standard library
import os
import sys
import doctest
from subprocess import Popen, PIPE
# From libtovid
from libtovid import log

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
        self.bg = False

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
        print "Running: %s" % self
        self.output = ''
        self.proc = Popen([self.program] + self.args,
                    stdin=stdin, stdout=PIPE)
        # Run piped-to command if it exists
        if isinstance(self.pipe, Command):
            self.pipe.run(self.proc.stdout)
        if not self.bg:
            self.proc.wait()
    
    def get_output(self):
        """Wait for the command to finish executing, and return a string
        containing the command's output. If this command is piped into another,
        return that command's output instead. Returns an empty string if the
        command has not been run yet.
        """
        if self.pipe:
            return self.pipe.get_output()
        if self.output is '' and self.proc is not None:
            self.output = self.proc.communicate()[0]
        return self.output
    
    def pipe_to(self, command):
        """Pipe the output of this Command into another Command.
            command: A Command to pipe to, or None to disable piping
        """
        if command:
            assert isinstance(command, Command)
        self.pipe = command

    def __str__(self):
        """Return a string representation of the Command, including any
        piped-to Commands.
        """
        ret = self.program
        for arg in self.args:
            ret += " %s" % enc_arg(arg)
        if self.pipe:
            ret += " | %s" % self.pipe
        return ret


class Script:
    """A sequence of Commands to be executed."""
    def __init__(self, name):
        """Create a script with the given name.
            name:   Name of the script, as a string
        """
        self.name = name
        self.commands = []

    def append(self, command):
        """Append a Command to the end of the script."""
        assert isinstance(command, Command)
        self.commands.append(command)

    def prepend(self, command):
        """Prepend a Command at the beginning of the script."""
        assert isinstance(command, Command)
        self.commands.insert(0, str(command))

    def run(self):
        """Execute all Commands in the script."""
        log.info("Executing script: %s" % self.name)
        for cmd in self.commands:
            log.info("Running command: %s" % cmd)
            cmd.run()


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


if __name__ == '__main__':
    doctest.testmod(verbose=True)

#! /usr/bin/env python
# cli.py

"""This module provides an interface for running command-line applications.
Two primary classes are provided:

    Command:  For constructing and executing command-line commands
    Pipe:     For piping commands together
    
Commands are constructed by specifying a program to run, and each separate
argument to pass to that program. Arguments are used in a platform-independent
way, so there is no need to escape shell-specific characters or do any quoting
of arguments.

Commands may be executed in the foreground or background; they can print their
output on standard output, or capture it in a string variable.

For example:

    >>> echo = Command('echo', "Hello world")
    >>> echo.run()
    Hello world

Commands may be connected together with pipes:

    >>> sed = Command('sed', 's/world/nurse/')
    >>> pipe = Pipe(echo, sed)
    >>> pipe.run()
    Hello nurse

Command output may be captured and retrieved later with get_output():

    >>> echo.run(capture=True)
    >>> echo.get_output()
    'Hello world\\n'

"""
# Note: Some of the run() tests above will fail doctest.testmod(), since output
# from Command subprocesses is not seen as real output by doctest. Fix this?

__all__ = [\
    'Command',
    'Pipe',
    'Script',
    'verify_app'
    ]

# From standard library
import os
import sys
import doctest
import signal
from subprocess import Popen, PIPE
# From libtovid
from libtovid import log

class Command(object):
    """A command-line statement, consisting of a program and its arguments,
    with support for various modes of execution.
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
            self.add(arg)
        self.proc = None
        self.output = ''

    def add(self, *args):
        """Append one or more arguments to the command. Each argument passed
        to this function is converted to string form, and treated as a single
        argument in the command. No special quoting or escaping of argument
        contents is necessary.
        """
        for arg in args:
            self.args.append(str(arg))
    
    def run(self, capture=False, background=False):
        """Run the command and capture or display output.
        
            capture:    False to show command output on stdout,
                        True to capture output for retrieval by get_output()
            background: False to wait for command to finish running,
                        True to run process in the background
        """
        if capture:
            self._run_redir(None, PIPE)
        else:
            self._run_redir(None, None)
        if not background:
            self.wait()
    
    def wait(self):
        """Wait for the command to finish running; handle keyboard interrupts.
        """
        if not isinstance(self.proc, Popen):
            return
        try:
            self.proc.wait()
        except KeyboardInterrupt:
            os.kill(self.proc.pid, signal.SIGTERM)
            raise KeyboardInterrupt

    def get_output(self):
        """Wait for the command to finish running, and return a string
        containing the command's output. If this command is piped into another,
        return that command's output instead. Returns an empty string if the
        command has not been run yet.
        """
        if self.output is '' and isinstance(self.proc, Popen):
            self.output = self.proc.communicate()[0]
        return self.output

    def _run_redir(self, stdin=None, stdout=None):
        """Internal function; execute the command using the given stream
        redirections.
        
            stdin:  File object to read input from (None for regular stdin)
            stdout: File object to write output to (None for regular stdout)
        """
        self.output = ''
        self.proc = Popen([self.program] + self.args,
                          stdin=stdin, stdout=stdout)

    def __str__(self):
        """Return a string representation of the Command, as it would look if
        run in a command-line shell.
        """
        ret = self.program
        for arg in self.args:
            ret += " %s" % enc_arg(arg)
        return ret


class Pipe(object):
    """A series of Commands, each having its output piped into the next.
    """
    def __init__(self, *commands):
        """Create a new Pipe containing all the given Commands."""
        self.commands = []
        for cmd in commands:
            self.add(cmd)
        self.proc = None
    
    def add(self, *commands):
        """Append the given commands to the end of the pipeline."""
        for cmd in commands:
            self.commands.append(cmd)

    def run(self, capture=False):
        """Run all Commands in the pipeline, doing appropriate stream
        redirection for piping.
        
            capture:    False to show pipeline output on stdout,
                        True to capture output for retrieval by get_output()
        
        """
        self.output = ''
        prev_stdout = None
        # Run each command, piping to the next
        for cmd in self.commands:
            # If this is not the last command, pipe into the next one
            if cmd != self.commands[-1]:
                cmd._run_redir(prev_stdout, PIPE)
                prev_stdout = cmd.proc.stdout
            # Last command in pipeline; direct output appropriately
            else:
                if capture:
                    cmd._run_redir(prev_stdout, PIPE)
                else:
                    cmd._run_redir(prev_stdout, None)

    def get_output(self):
        """Wait for the pipeline to finish executing, and return a string
        containing the output from the last command in the pipeline.
        """
        return self.commands[-1].get_output()

    def __str__(self):
        """Return a string representation of the Pipe.
        """
        commands = [str(cmd) for cmd in self.commands]
        return ' | '.join(commands)


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

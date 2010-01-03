"""This module provides an interface for running command-line applications.
Two primary classes are provided:

    Command
        For constructing and executing command-line commands
    Pipe
        For piping commands together

Commands are constructed by specifying a program to run, and each separate
argument to pass to that program. Arguments are used in a platform-independent
way, so there is no need to escape shell-specific characters or do any quoting
of arguments.

Commands may be executed in the foreground or background; they can print their
output on standard output, or capture it in a string variable.

For example::

    >>> echo = Command('echo', "Hello world")
    >>> echo.run()                                # doctest: +SKIP
    Hello world

Commands may be connected together with pipes::

    >>> sed = Command('sed', 's/world/nurse/')
    >>> pipe = Pipe(echo, sed)
    >>> pipe.run()                                # doctest: +SKIP
    Hello nurse

Command output may be captured and retrieved later with get_output()::

    >>> echo.run(capture=True)
    >>> echo.get_output()
    'Hello world\\n'

"""
# Note: Some of the run() tests above will fail doctest.testmod(), since output
# from Command subprocesses is not seen as real output by doctest. The current
# workaround is to use the "doctest: +SKIP" directive (new in python 2.5).
# For other directives see http://www.python.org/doc/lib/doctest-options.html

__all__ = [
    'Command',
    'Pipe',
]

import os
import doctest
import signal
from subprocess import Popen, PIPE

class Command:
    """A command-line statement, consisting of a program and its arguments,
    with support for various modes of execution.
    """
    def __init__(self, program, *args):
        """Create a Command to run a program with the given arguments.

            program
                A string containing the name of a program to execute
            args
                Individual arguments to supply the command with

        For example::

            >>> cmd = Command('echo', 'Hello world')

        """
        self.program = program
        self.args = []
        for arg in args:
            self.add(arg)
        self.proc = None
        self.output = ''
        self.error = ''


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

            capture
                False to show command output/errors on stdout,
                True to capture output/errors for retrieval
                by get_output() and get_error()
            background
                False to wait for command to finish running,
                True to run process in the background

        By default, this function displays all command output, and waits
        for the program to finish running, which is usually what you'd want.
        Capture output if you don't want it printed immediately (and call
        get_output() later to retrieve it).

        This function does not allow special stream redirection. For that,
        use run_redir().
        """
        if capture:
            self.run_redir(None, PIPE, stderr=PIPE)
        else:
            self.run_redir(None, None, stderr=None)
        if not background:
            self.wait()


    def run_redir(self, stdin=None, stdout=None, stderr=None):
        """Execute the command using the given stream redirections.

            stdin
                Filename or File object to read input from
            stdout
                Filename or File object to write output to
            stderr
                Filename or File object to write errors to

        Use None for regular system stdin/stdout/stderr (default behavior).
        That is, if stdout=None, the command's standard output is printed.

        This function is used internally by run(); if you need to do stream
        redirection (ex. ``spumux < menu.mpg > menu_subs.mpg``), use this
        function instead of run(), and call wait() afterwards if needed.
        """
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Running command:")
        print(self)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        self.output = ''
        # Open files if string filenames were provided
        if type(stdin) in (str, unicode):
            stdin = open(stdin, 'r')
        if type(stdout) in (str, unicode):
            stdout = open(stdout, 'w')
        if type(stderr) in (str, unicode):
            stderr = open(stderr, 'w')
        # Run the subprocess
        self.proc = Popen([self.program] + self.args,
                          stdin=stdin, stdout=stdout, stderr=stderr)


    def wait(self):
        """Wait for the command to finish running, and return the result
        (``self.proc.returncode`` attribute).

        If a ``KeyboardInterrupt`` occurs (user pressed Ctrl-C), the
        subprocess is killed (and ``KeyboardInterrupt`` re-raised).
        """
        if not isinstance(self.proc, Popen):
            print("**** Can't wait(): Command is not running")
            return
        try:
            result = self.proc.wait()
        except KeyboardInterrupt:
            self.kill()
            raise KeyboardInterrupt
        return result


    def kill(self):
        """Abort!
        """
        #os.kill(self.proc.pid, signal.SIGTERM)
        self.proc.kill()



    def done(self):
        """Return True if the command is finished running; False otherwise.
        Only useful if the command is run in the background.
        """
        return self.proc.poll() != None


    def get_output(self):
        """Wait for the command to finish running, and return a string
        containing the command's output. If this command is piped into another,
        return that command's output instead. Returns an empty string if the
        command has not been run yet.
        """
        if self.output == '' and isinstance(self.proc, Popen):
            self.output = self.proc.communicate()[0]
        return self.output


    def get_error(self):
        """Wait for the command to finish running, and return a string
        containing the command's standard error output. Returns an empty
        string if the command has not been run yet.
        """
        if self.error == '' and isinstance(self.proc, Popen):
            self.error = self.proc.communicate()[1]
        return self.error

    get_errors = get_error
    def __str__(self):
        """Return a string representation of the Command, as it would look if
        run in a command-line shell.
        """
        ret = self.program
        for arg in self.args:
            ret += " %s" % _enc_arg(arg)
        return ret


    def to_script(self):
        """Return a bash script for running the given command.
        """
        script = '#!/usr/bin/env bash' + '\n\n'
        # Write arguments, one per line with backslash-continuation
        words = [_enc_arg(arg) for arg in [self.program] + self.args]
        script += ' \\\n'.join(words)
        return script


class Pipe:
    """A series of Commands, each having its output piped into the next.
    """
    def __init__(self, *commands):
        """Create a new Pipe containing all the given Commands."""
        self.commands = []
        for cmd in commands:
            self.add(cmd)
        self.proc = None
        self.output = ''


    def add(self, *commands):
        """Append the given commands to the end of the pipeline."""
        for cmd in commands:
            self.commands.append(cmd)


    def run(self, capture=False, background=False):
        """Run all Commands in the pipeline, doing appropriate stream
        redirection for piping.

            capture
                False to show pipeline output on stdout,
                True to capture output for retrieval by get_output()

        """
        self.output = ''
        prev_stdout = None
        # Run each command, piping to the next
        for cmd in self.commands:
            # If this is not the last command, pipe into the next one
            if cmd != self.commands[-1]:
                cmd.run_redir(prev_stdout, PIPE, None)
                prev_stdout = cmd.proc.stdout
            # Last command in pipeline; direct output appropriately
            else:
                if capture:
                    cmd.run_redir(prev_stdout, PIPE, None)
                else:
                    cmd.run_redir(prev_stdout, None, None)
                # Wait for last command to finish
                if not background:
                    cmd.wait()


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


def _enc_arg(arg):
    """Quote an argument for proper handling of special shell characters.
    Don't quote unless necessary. For example:

        >>> print(_enc_arg("spam"))
        spam
        >>> print(_enc_arg("spam & eggs"))
        'spam & eggs'
        >>> print(_enc_arg("['&&']"))
        '['\\''&&'\\'']'

    This is used internally by Command; you'd only need this if you're running
    shell programs without using the Command class.
    """
    arg = str(arg)
    # At the first sign of any special character in the argument,
    # single-quote the whole thing and return it (escaping ' itself)
    for char in ' #"\'\\&|<>()[]!?*':
        if char in arg:
            return "'%s'" % arg.replace("'", "'\\''")
    # No special characters found; use literal string
    return arg




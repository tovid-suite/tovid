"""This module provides an interface for running command-line applications.
Two primary classes are provided:

    `Command`
        For constructing and executing command-line commands
    `Pipe`
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

The above can be easily accomplished using Python standard library functions
like ``os.Popen`` or ``commands.getoutput``. This module was designed to
simplify the task of executing long-running commands or command-line pipes in
the background, and getting their output later. This behavior is controlled by
the arguments to the `~Command.run` method.

Normally, `~Command.run` prints all output on standard output. If instead you
need to capture the output, pass ``capture=True``, then retrieve it later with
`~Command.get_output`::

    >>> echo.run(capture=True)                    # doctest: +SKIP
    >>> echo.get_output()
    'Hello world\\n'

If the command you're running will take a long time to run, and you don't want
your program to be blocked while it's running, pass ``background=True``. If the
command may produce a lot of output during execution, you'll probably want to
capture it instead of printing it::

    >>> find = Command('find', '/')               # doctest: +SKIP
    >>> find.run(capture=True, background=True)

In this way, your application can keep doing other things while the long-running
command is executing; you can check whether it's done like so::

    >>> find.done()
    False
    >>> find.done()
    False
    >>> find.done()
    True

Then, as before, use `~Command.get_output` to get the output, if you need it. If
you need to get the standard error output, use `~Command.get_errors`.

"""
# Note: Some of the run() tests above will fail doctest.testmod(), since output
# from Command subprocesses is not seen as real output by doctest. The current
# workaround is to use the "doctest: +SKIP" directive (new in python 2.5).
# For other directives see http://www.python.org/doc/lib/doctest-options.html

# TODO: Make the 'capture/get_output' mechanisms able to handle large amounts
# of output, perhaps by logging to a temporary file and/or returning an iterator
# for lines of output, instead of a flat string.

__all__ = [
    'Command',
    'Pipe',
]

import subprocess
import signal
from os import environ

# Small workaround for Python 3.x
try:
    _temp = unicode
except NameError:
    unicode = str

class ProgramNotFound (ValueError):
    """Raised when the program given to a command is not available.
    """
    pass

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
            self.args.append(unicode(arg))


    def run(self, capture=False, background=False, silent=False):
        """Run the command and capture or display output.

            capture
                ``False`` to show command output/errors on stdout,
                ``True`` to capture output/errors for retrieval
                by `get_output` and `get_errors`
            background
                ``False`` to wait for command to finish running,
                ``True`` to run process in the background
            silent
                ``False`` to print each command as it runs,
                ``True`` to run silently

        By default, this function displays all command output, and waits
        for the program to finish running, which is usually what you'd want.
        Capture output if you don't want it printed immediately (and call
        `get_output` later to retrieve it).

        This function does not allow special stream redirection. For that,
        use `run_redir`.
        """
        if not silent:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Running command:")
            print(unicode(self))
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        if capture:
            self.run_redir(None, subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.run_redir(None, None, stderr=None)
        if not background:
            self.wait()


    def run_redir(self, stdin=None, stdout=None, stderr=None):
        """Execute the command using the given stream redirections.

            stdin
                Filename or `file` object to read input from
            stdout
                Filename or `file` object to write output to
            stderr
                Filename or `file` object to write errors to

        Use ``None`` for regular system stdin/stdout/stderr (default behavior).
        That is, if ``stdout=None``, the command's standard output is printed.

        This function is used internally by `run`; if you need to do
        stream redirection (ex. ``spumux < menu.mpg > menu_subs.mpg``), use
        this function instead of `run`, and call `wait` afterwards
        if needed.
        """
        self.output = ''
        # Open files if string filenames were provided
        if isinstance(stdin, basestring):
            stdin = open(stdin, 'r')
        if isinstance(stdout, basestring):
            stdout = open(stdout, 'w')
        if isinstance(stderr, basestring):
            stderr = open(stderr, 'w')
        # Run the subprocess
        try:
            self.proc = subprocess.Popen([self.program] + self.args,
                              stdin=stdin, stdout=stdout, stderr=stderr)
        except OSError:
            raise ProgramNotFound("Program '%s' not found." % self.program)


    def wait(self):
        """Wait for the command to finish running, and return the result
        (`self.proc.returncode`).

        If a :exc:`KeyboardInterrupt` occurs (user pressed Ctrl-C), the
        subprocess is killed (and :exc:`KeyboardInterrupt` re-raised).
        """
        if not isinstance(self.proc, subprocess.Popen):
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
        os.kill(self.proc.pid, signal.SIGTERM)
        #self.proc.kill()



    def done(self):
        """Return ``True`` if the command is finished running; ``False``
        otherwise. Only useful if the command is run in the background.
        """
        return self.proc.poll() != None


    def get_output(self):
        """Wait for the command to finish running, and return a string
        containing the command's output. If this command is piped into another,
        return that command's output instead. Returns an empty string if the
        command has not been run yet.
        """
        if self.output == '' and isinstance(self.proc, subprocess.Popen):
            self.output = self.proc.communicate()[0]
        return self.output


    def get_errors(self):
        """Wait for the command to finish running, and return a string
        containing the command's standard error output. Returns an empty
        string if the command has not been run yet.
        """
        if self.error == '' and isinstance(self.proc, subprocess.Popen):
            self.error = self.proc.communicate()[1]
        return self.error


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
        script_path = environ['PATH'].rsplit(':')
        script += 'PATH=' + script_path[0] + ':$PATH'  + '\n\n'
        # Write arguments, one per line with backslash-continuation
        words = [_enc_arg(arg) for arg in [self.program] + self.args]
        script += ' \\\n'.join(words)
        return script


class Pipe:
    """Several `Command` objects, each having its output piped into the next.
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
                ``False`` to show pipeline output on stdout,
                ``True`` to capture output for retrieval by `get_output`

        """
        self.output = ''
        prev_stdout = None
        # Run each command, piping to the next
        for cmd in self.commands:
            # If this is not the last command, pipe into the next one
            if cmd != self.commands[-1]:
                cmd.run_redir(prev_stdout, subprocess.PIPE, None)
                prev_stdout = cmd.proc.stdout
            # Last command in pipeline; direct output appropriately
            else:
                if capture:
                    cmd.run_redir(prev_stdout, subprocess.PIPE, None)
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
        commands = [unicode(cmd) for cmd in self.commands]
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
    arg = unicode(arg)
    # At the first sign of any special character in the argument,
    # single-quote the whole thing and return it (escaping ' itself)
    for char in ' #"\'\\&|<>()[]!?*':
        if char in arg:
            return "'%s'" % arg.replace("'", "'\\''")
    # No special characters found; use literal string
    return arg




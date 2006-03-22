#! /usr/bin/env python2.4
# cli.py

"""This module provides an interface for running command-line applications.

Most of tovid's work is done by calling external applications (mplayer,
mpeg2enc, ffmpeg...) with usually lengthy command-lines. The Command class is a
simple interface for building command-lines, spawning subprocesses, and reading
output from them.
"""

__all__ = ['Command', 'subst']

# From standard library
import os
from subprocess import Popen, PIPE
# From libtovid
from libtovid.log import Log

log = Log('cli.py')

class Command:
    """A command-line app with arguments, and process control."""
    def __init__(self, command, purpose=''):
        """Create a Command with the given command-line string. Optionally
        include a brief description of the purpose of the command-line.

        The command string should begin with the name of the application to
        invoke, followed by that application's arguments. For example:

            >>> cmd = Command('ls -l /usr', "List contents of /usr")

        Then, to execute the command, call:

            >>> cmd.run()
        
        To see the output from the command (after calling run()):

            >>> for line in cmd.output:
            ...     print line

        """
        self.command = command
        self.purpose = purpose
        # Verify application availability
        appname = command.split()[0]
        verify_app(appname)
        # All lines of output from the command
        self.output = []

    def append(self, args):
        """Append the given string of arguments."""
        self.command += ' ' + args

    def prepend(self, args):
        """Prepend the given string of arguments.

        Note: Arguments are inserted before the existing command; this is
        useful mainly for setting up piped input to the current command (by
        calling prepend('cat infile | ') or similar)."""
        self.command = args + ' ' + self.command

    def version(self):
        """Return the version number of the application."""
        # TODO: Call upon the user's package manager to determine installed
        # version of self.appname
        pass

    def run(self, wait=True):
        """Execute the given command, with proper stream redirection and
        verbosity. Wait for execution to finish if desired. Return the
        exit status of the process."""
        log.info(self.purpose)
        log.info(self.command)
        proc = Popen(self.command, shell=True, bufsize=1, \
                stdout=PIPE, stderr=PIPE, close_fds=True)
        stdout = proc.stdout
        stderr = proc.stderr

        if wait:
            for line in stdout.readlines():
                self.output.append(line.rstrip('\n'))
            for line in stderr.readlines():
                self.output.append(line.rstrip('\n'))
            log.info("Waiting for process to terminate...")
            return proc.wait()
        else:
            return proc.returncode


def verify_app(appname):
    """If appname is not in the user's path, print a error and exit."""
    app = subst('which %s' % appname)
    if not app:
        log.error("Application: %s does not appear to be in your path.")
        sys.exit()


def subst(command, include_stderr=False):
    """Do shell-style command substitution and return the output of command
    as a string (equivalent to bash `CMD` or $(CMD)). Optionally include
    standard error output."""
    if include_stderr:
        cin, cout = os.popen4(command, 'r')
        cin.close()
        output = cout.readlines()
    else:
        output = os.popen(command, 'r').readlines()
    return ''.join(output).rstrip('\n')


#! /usr/bin/env python2.4
# cli.py

"""This module provides an interface for running command-line applications.

Most of tovid's work is done by calling external applications (mplayer,
mpeg2enc, ffmpeg...) with usually lengthy command-lines. The Command class is a
simple interface for building command-lines, spawning subprocesses, and reading
output from them.
"""

__all__ = ['Command', 'verify_app', 'subst']

# From standard library
import os
import sys
from subprocess import Popen, PIPE
from signal import SIGKILL
# From libtovid
from libtovid.log import Log

log = Log('cli.py')

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
        
        To see the output from the command (after calling run()):

            >>> for line in cmd.output:
            ...     print line

        """
        self.command = command
        self.purpose = purpose
        self.proc = None
        self.childpid = None
        # All lines of output from the command
        self.output = []

    def append(self, args):
        """Append the given string of arguments."""
        if not isinstance(args, str):
            raise TypeError, "Command.append() can only take strings."
        self.command += ' ' + args

    def prepend(self, args):
        """Prepend the given string of arguments."""
        self.command = args + ' ' + self.command

    def version(self):
        """Return the version number of the application."""
        # TODO: Call upon the user's package manager to determine installed
        # version of self.appname
        pass

    def run(self, wait=True):
        try:
            self._run(wait)
        except KeyboardInterrupt:
            log.info("Process interrupted. Exiting...")
            self.kill()
            sys.exit()

    def _run(self, wait):
        """Execute the command and return its exit status. Optionally wait for
        execution to finish."""
        log.info(self.purpose)
        log.info(self.command)
        self.proc = Popen(self.command, bufsize=1, shell=True,
                     stdout=PIPE, stderr=PIPE, close_fds=True)
        # Fork a child process to log output
        pid = os.fork()
        if pid > 0: # Parent
            self.childpid = pid
            if wait:
                os.waitpid(pid, 0)
        
        else: # Child
            for line in self.proc.stdout:
                self.output.append(line)
            for line in self.proc.stderr:
                self.output.append(line)
            sys.exit()

    def is_done(self):
        """Return True if the command is finished executing; False otherwise."""
        if self.proc.poll():
            return True
        else:
            return False

    def kill(self):
        """Kill all processes spawned by this Command."""
        if self.childpid:
            os.kill(self.childpid, SIGKILL)
        os.kill(self.proc.pid, SIGKILL)

    
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


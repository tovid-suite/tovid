#! /usr/bin/env python
# cli.py

"""This module provides an interface for running command-line applications.

Most of tovid's work is done by calling external applications (mplayer,
mpeg2enc, ffmpeg...) with usually lengthy command-lines. The Command class is a
simple interface for building command-lines, spawning subprocesses, and reading
output from them.
"""

__all__ = ['Command', 'verify_app']

# From standard library
import os
import sys
import logging
import tempfile
import commands
from stat import S_IREAD, S_IWRITE, S_IEXEC
from signal import SIGKILL
# From libtovid
#from libtovid.log import Log

log = logging.getLogger('libtovid.cli')

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
    def __init__(self, name):
        self.name = name
        self.lines = []
        # Set up logging
        self.log = logging.getLogger('Script.%s' % self.name)
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.StreamHandler(sys.stdout))

    def append(self, command):
        """Append the given command to the end of the script."""
        assert isinstance(command, str)
        self.lines.append(command)

    def prepend(self, command):
        """Prepend the given command at the beginning of the script."""
        assert isinstance(command, str)
        self.lines.insert(0, command)

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
        #fd, self.log_file = tempfile.mkstemp('.log', self.name)
        # Make script file executable
        os.chmod(self.script_file, S_IREAD|S_IWRITE|S_IEXEC)
        # Write the script to the temporary script file
        script = file(self.script_file, 'w')
        script.write('#!/bin/sh\n')
        script.write('# %s\n' % self.name)
        script.write('cat %s\n' % self.script_file)
        for line in self.lines:
            script.write('%s\n' % line)
        script.write('\n')
        script.close()

class Backend:
    """"""

def verify_app(appname):
    """If appname is not in the user's path, print a error and exit."""
    app = commands.getoutput('which %s' % appname)
    if not app:
        log.error("Application: %s does not appear to be in your path.")
        sys.exit()
    

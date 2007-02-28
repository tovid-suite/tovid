#! /usr/bin/env python
# grep.py
# metagui for grep

from metagui import *

panel1 = Panel("Page 1",
    HPanel('',
        FlagGroup("Match settings", 'normal',
            Flag('-i',
                'Ignore case', False,
                "Ignore case distinctions in both the PATTERN and"\
                " the input files."),
            Flag('-v',
                'Invert match', False,
                "Invert the sense of matching, to select non-matching lines."),
            Flag('-w',
                'Match whole words', False,
                "Select only those lines containing matches that form whole"\
                " words. The test is that the matching substring must either"\
                " be at the beginning of the line, or preceded by a non-word"\
                " constituent character. Similarly, it must be either at the"\
                " end of the line or followed by a non-word constituent"\
                " character. Word-constituent characters are letters, digits,"\
                " and the underscore."),
            Flag('-x',
                'Match whole lines', False,
                "Select only those matches that exactly match the whole line.")
            ),
    
        FlagGroup("Regular expressions", 'normal',
            Flag('-G',
                'Basic regular expression', True,
                "Interpret PATTERN as a basic regular expression."),
            Flag('-E',
                'Extended regular expression', False,
                "Interpret PATTERN as an extended regular expression."),
            Flag('-F',
                'Fixed strings', False,
                "Interpret PATTERN as a list of fixed strings, separated"\
                " by newlines, any of which is to be matched."),
            Flag('-P',
                'Perl regular expression', False,
                "Interpret PATTERN as a Perl regular expression.")
            )
        ),

    Panel("Context",
        Number('-A',
            'Trailing context', 0,
            "Print NUM lines of trailing context after matching lines."\
            " Places a line containing -- between contiguous groups of"\
            " matches.",
            0, 20),
        Number('-B',
            'Leading context', 0,
            "Print NUM lines of leading context before matching lines."\
            " Places a line containing -- between contiguous groups of"\
            " matches.",
            0, 20),
        Number('-C',
            'Output context', 0,
            "Print NUM lines of output context. Places a line containing --"\
            " between contiguous groups of matches.",
            0, 20)
        ),

    FlagGroup('Output', 'normal',
        Flag('-l',
            'Print matching lines', False,
            "Suppress  normal output; instead print the name of each"\
            " input file from which output would normally have been"\
            " printed. The scanning will stop on the first match."),
        Flag('-L',
            'Print non-matching lines', False,
            "Suppress  normal output; instead print the name of each"\
            " input file from which no output would normally have been"\
            " printed. The scanning will stop on the first match."),
        Flag('-c',
            'Count matching lines', False,
            "Suppress normal output; instead print a count of matching"\
            " lines for each input file. With the -v, --invert-match"\
            " option (see below), count non-matching lines."),
        Flag('-n',
            'Show matching part only', False,
            "Show only the part of a matching line that matches PATTERN."),
        Flag('-b',
            'Print byte offset',
            "Print the byte offset within the input file before each"\
            " line of output."),
        Flag('-n',
            'Print line number', False,
            "Prefix each line of output with the line number within"\
            " its input file.")
        ),

    FlagGroup('Print filename', 'exclusive',
        Flag('-H', 'Print', True),
        Flag('-h', 'Suppress')
        ),

    Panel("Recursive search",
          Flag('-R',
              'Recursive', False,
              "Read  all files under each directory, recursively; this is"\
              "equivalent to the -d recurse option."),
          Text('--include',
              'Recursive include pattern', '',
              "Recurse in directories only searching file matching PATTERN."),
          Text('--exclude',
              'Recursive exclude pattern', '',
              "Recurse in directories skip file matching PATTERN.")
          ),

    Flag('-a',
        'Treat as text', False,
        "Process  a  binary  file as if it were text; this is equivalent to"\
        " the --binary-files=text option."),
    
    Choice('--color',
        'Colored output', 'never',
        "Surround  the  matching  string with the marker find in GREP_COLOR"\
        " environment variable.",
        'never|always|auto'),

    Text('-e',
        'Pattern', '',
        "Use PATTERN as the pattern; useful to protect patterns beginning"\
        " with -."),

)

panel2 = Panel("Page 2",

    Text('--binary-files',
        'Assume type for binary files', '',
        "If  the  first few bytes of a file indicate that the file contains"\
        " binary data, assume that the file is of type  TYPE.   By  default,"\
        " TYPE  is  binary, and grep normally outputs either a one-line mes-"\
        " sage saying that a binary file matches, or no message if there  is"\
        " no  match.   If  TYPE is without-match, grep assumes that a binary"\
        " file does not match; this is equivalent to the -I option.  If TYPE"\
        " is  text, grep processes a binary file as if it were text; this is"\
        " equivalent to the -a option.   Warning:  grep  --binary-files=text"\
        " might  output binary garbage, which can have nasty side effects if"\
        " the output is a terminal and if  the  terminal  driver  interprets"\
        " some of it as commands."),
    Choice('-D',
        'Device/FIFO/socket action', 'read',
        "If an input file is a device, FIFO or socket, use ACTION to"\
        " process it. By default, ACTION is read, which means that devices"\
        " are read just as if they were ordinary files. If ACTION is  skip,"\
        " devices are silently skipped.",
        'read|skip'),
    Choice('-d',
        'Directory action', 'read',
        " If  an  input  file  is a directory, use ACTION to process it.  By"\
        " default, ACTION is read, which means  that  directories  are  read"\
        " just  as if they were ordinary files.  If ACTION is skip,"\
        " directories are silently skipped.  If ACTION is recurse, grep reads"\
        " all files under each directory, recursively; this is equivalent"\
        " to the -r option.",
        'read|skip|recurse'),
    Filename('-f',
        'Get patterns from file', '',
        "Obtain patterns from FILE, one per line.  The empty file  contains"\
        " zero patterns, and therefore matches nothing."),
    Flag('-I',
        '?', False,
        "Process a binary file as if it did not contain matching data; this"\
        " is equivalent to the --binary-files=without-match option."),
    Number('-m',
        'Stop after this many matches', 0,
        "Stop  reading  a  file  after NUM matching lines.  If the input is"\
        " standard input from a regular file, and  NUM  matching  lines  are"\
        " output, grep ensures that the standard input is positioned to just"\
        " after the last matching line before  exiting,  regardless  of  the"\
        " presence  of  trailing  context  lines.   This  enables  a calling"\
        " process to resume a search.  When grep stops  after  NUM  matching"\
        " lines,  it  outputs  any  trailing  context lines.  When the -c or"\
        " --count option is also used, grep does not output a count  greater"\
        " than NUM.  When the -v or --invert-match option is also used, grep"\
        " stops after outputting NUM non-matching lines."),
    Flag('--mmap',
        'Use mmap instead of read', False,
        "If possible, use the mmap(2) system call to read input, instead of"\
        " the  default  read(2)  system  call.   In  some situations, --mmap"\
        " yields better performance.  However, --mmap  can  cause  undefined"\
        " behavior  (including  core  dumps)  if an input file shrinks while"\
        " grep is operating, or if an I/O error occurs."),
    Text('--label',
        'Label for stdin', '',
        "Displays input actually coming from standard input as input coming"\
        " from file LABEL.  This is especially useful for tools like  zgrep,"\
        " e.g.  gzip -cd foo.gz |grep --label=foo something"),
    Flag('--line-buffered',
        'Use line buffering', False,
        "Use line buffering, it can be a performance penality."),
    Flag('-q',
        'Quiet', False,
        "Quiet; do not write anything to standard output.  Exit immediately"\
        " with zero status if any match is found, even if an error was"\
        " detected.  Also see the -s or --no-messages option."),
    Flag('-s',
        'Suppress errors', False,
        "Suppress error messages about  nonexistent  or  unreadable  files."\
        " Portability  note:  unlike GNU grep, traditional grep did not con-"\
        " form to POSIX.2, because traditional grep lacked a -q  option  and"\
        " its  -s  option  behaved like GNU grep's -q option.  Shell scripts"\
        " intended to be portable to traditional grep should avoid  both  -q"\
        " and -s and should redirect output to /dev/null instead."),
    Flag('-U',
        'Treat all files as binary', False,
        "Treat the file(s) as binary.  By default, under MS-DOS and MS-Win-"\
        " dows, grep guesses the file type by looking at the contents of the"\
        " first 32KB read from the file.  If grep decides the file is a text"\
        " file, it strips the CR characters from the original file  contents"\
        " (to make regular expressions with ^ and $ work correctly).  Speci-"\
        " fying -U overrules this guesswork, causing all files  to  be  read"\
        " and  passed  to  the matching mechanism verbatim; if the file is a"\
        " text file with CR/LF pairs at the end  of  each  line,  this  will"\
        " cause some regular expressions to fail.  This option has no effect"\
        " on platforms other than MS-DOS and MS-Windows."),
    Flag('-u',
        'Unix byte offsets', False,
        "Report Unix-style byte offsets.  This switch causes grep to report"\
        " byte  offsets  as if the file were Unix-style text file, i.e. with"\
        " CR characters stripped off.  This will produce  results  identical"\
        " to  running  grep  on  a  Unix machine.  This option has no effect"\
        " unless -b option is also used; it has no effect on platforms other"\
        " than MS-DOS and MS-Windows."),
    Flag('-V',
        'Print version number', False,
        "Print  the version number of grep to standard error.  This version"\
        " number should be included in all bug reports (see below)."),
    Flag('-Z',
        'Output zero byte after each filename', False,
        "Output  a zero byte (the ASCII NUL character) instead of the char-"\
        " acter that normally follows a file name.  For  example,  grep  -lZ"\
        " outputs a zero byte after each file name instead of the usual new-"\
        " line.  This option makes the output unambiguous, even in the pres-"\
        " ence  of  file  names containing unusual characters like newlines."\
        " This option can be used with commands like find -print0, perl  -0,"\
        " sort  -z, and xargs -0 to process arbitrary file names, even those"\
        " that contain newline characters.")
)

app = Application('grep', [panel1, panel2])
gui = GUI('gUIrep', [app])
gui.run()


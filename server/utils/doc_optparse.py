#!/usr/bin/python
# Filename: doc_optparse.py

# Extracted from the bx-python project with minor modifications; originally
# known as optionparse from <http://code.activestate.com/recipes/278844/>

"""
:Author: M. Simionato
:Date: April 2004
:Title: A much simplified interface to optparse.

You should use doc_optparse in your scripts as follows.
First, write a module level docstring containing something like this
(this is just an example)::

    '''usage: %prog files [options]
       -d, --delete: delete all files
       -e, --erase = ERASE: erase the given file'''
   
Then write a main program of this kind:

# sketch of a script to delete files::

    if __name__=='__main__':
        import doc_optparse
        option,args = doc_optparse.parse(__doc__)
        if not args and not option: doc_optparse.exit()
        elif option.delete: print "Delete all files"
        elif option.erase: print "Delete the given file"

Notice that ``doc_optparse`` parses the docstring by looking at the
characters ",", ":", "=", "\\n", so be careful in using them. If
the docstring is not correctly formatted you will get a SyntaxError
or worse, the script will not work as expected.
"""

import optparse, re, sys, traceback

USAGE = re.compile(r'(?s)\s*usage: (.*?)(\n[ \t]*\n|$)')

def nonzero(self): # will become the nonzero method of optparse.Values         
    "True if options were given"
    for v in self.__dict__.itervalues():
        if v is not None: return True
    return False

optparse.Values.__nonzero__ = nonzero # dynamically fix optparse.Values

class ParsingError(Exception): pass

optionstring = ""

def exception(msg=""):
    print >> sys.stderr, "Exception while parsing command line:"
    print >> sys.stderr, traceback.format_exc()
    exit(msg)

def exit(msg=""):
    raise SystemExit(msg or optionstring.replace("%prog", sys.argv[0]))

def parse(docstring, arglist=None):
    global optionstring
    optionstring = docstring
    match = USAGE.search(optionstring)
    if not match: raise ParsingError("cannot find the option string")
    optlines = match.group(1).splitlines()
    try:
        p = optparse.OptionParser(optlines[0], conflict_handler="resolve")
        for line in optlines[1:]:
            opt, help = line.split(":")[:2]
            if "=" in opt:
                action = "store"
                opt = opt.split("=")[0]
            else:
                action = "store_true"
            optstrings = [k.strip() for k in opt.split(",")[:2]]
            p.add_option(*optstrings, **dict(action=action, help=help.strip()))
    except (IndexError, ValueError):
        raise ParsingError("cannot parse the option string correctly")
    return p.parse_args(arglist)

def help_callback(option, opt, value, parser, help):
    print >> sys.stderr, help
    sys.exit(1)

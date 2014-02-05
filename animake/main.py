# animake -- The Ani-Nouto Make
# Copyright (c) 2014 Pete Zaitcev <zaitcev@yahoo.com>

from __future__ import print_function

import codecs
import os
import sys

from animake import AppError

TAG="animake"

# Param

class ParamError(Exception):
    pass

class Param:
    def __init__(self, argv):
        skip = 0;  # Do skip=1 for full argv.
        #: Repo path, no default
        self.repo = None
        #: The output directory, no default
        self.root = None
        #: For debugging
        # XXX verify if -d & -v are actually used
        self.debug = False
        self.verbose = False
        for i in range(len(argv)):
            if skip:
                skip = 0
                continue
            arg = argv[i]
            if len(arg) != 0 and arg[0] == '-':
                if arg == "-d":
                    self.debug = True
                elif arg == "-o":
                    if i+1 == len(argv):
                        raise ParamError("Parameter -o needs an argument")
                    self.root = argv[i+1]
                    skip = 1;
                elif arg == "-v":
                    self.verbose = True
                else:
                    raise ParamError("Unknown parameter " + arg)
            else:
                if self.repo:
                    raise ParamError("Redundant repository parameter")
                self.repo = arg
        if self.repo == None:
            raise ParamError("No mandatory repository parameter")
        if self.root == None:
            raise ParamError("No mandatory output directory parameter")

#

class Index(object):
    def __init__(self, outname):
        """
        raises: AppError in case we cannot create the output # XXX not yet
        """
        self.oname = outname
        self.ofp = open(outname, 'w')
    def close(self):
        self.ofp.close()
        self.ofp = None

class Entry(object):
    def __init__(self, dirpath, name):
        self.path = os.path.join(dirpath, name)
        self.unpublished = False
        self.author = "Author" #: This may confuse some, but yes, it's "Author"
        self.subject = None
        self.tags = []
        self.url = None

        efp = codecs.open(self.path, 'r', encoding='utf-8', errors='replace')

        while 1:
            s = efp.readline()
            if not s:
                break
            if s[-1] == '\n':
                s = s[:-1]
            if len(s) == 0:
                break
            hv = s.split(':', 1)
            if len(hv) == 1:
                if hv[0] == 'UNPUBLISHED':
                    self.unpublished = True
                elif hv[0] == 'DELETED':
                    self.unpublished = True
                else:
                    raise AppError("%s: Bad header `%s'" % (self.path, hv[0]))
            else:
                if hv[0] == 'Subject':
                    self.subject = hv[1]
                elif hv[0] == 'Tags':
                    self.tags = map(lambda s: s.strip(), hv[1].split(','))
                elif hv[0] == 'URL':
                    self.url = hv[1]
                elif hv[0] == 'Edit':
                    # Edit: has no sense in the static website, skipping
                    pass
                elif hv[0] == 'Trackback':
                    # Skipping trackbacks
                    pass
                elif hv[0] == 'Author':
                    self.author = hv[1]
                else:
                    # XXX
                    print("%s: Unknown header `%s'" % (self.path, hv[0]))

        self.body = ''
        while 1:
            b = efp.read()
            if not b:
                break
            self.body += b
        # If would be nice to verify that tags are balanced.

        efp.close()

def listerror(e):
    raise AppError("Cannot list: "+str(e))

def do(par):
    # Unfortunately, we have to walk twice. First, we generate all the
    # straight indexes such as archives and categories. We pick up pages
    # and prepare feed list on that step as well. Second, we generate the
    # reverse index for the ticker.

    try:
        os.mkdir(par.root)
    except OSError as e:
        raise AppError("Cannot make output directory: " + str(e))

    all_tags = dict()

    for dirpath, dirnames, filenames in os.walk(par.repo, onerror=listerror):
        dirnames.sort()

        if par.verbose:
            print('%s' % dirpath)

        if dirpath[-1] == '/':
            dirname = dirpath.rsplit('/', 2)[-2]
        else:
            dirname = dirpath.rsplit('/', 2)[-1]
        try:
            year = int(dirname)
        except ValueError:
            year = 0
        if 2000 < year <= 2100:
            filenames.sort()
            for name in filenames:
                if name[-4:] == '.txt':
                    ent = Entry(dirpath, name)

                    for tag in ent.tags:
                        if tag not in all_tags:
                            all_tags[tag] = ""

    for dirpath, dirnames, filenames in os.walk(par.repo, onerror=listerror):
        dirnames.sort(reverse=True)
        if par.verbose:
            print('%s' % dirpath)

    # P3
    # XXX output not sorted
    print("Tags:")
    for tag in all_tags:
        print(" %s" % tag)

def main(args):
    try:
        par = Param(args)
    except ParamError as e:
        print(TAG+": Error in arguments:", e, file=sys.stderr)
        print("Usage:", TAG+" [-d] [-v] -o /out/dir /path/to/repo",
              file=sys.stderr)
        return 1

    try:
        do(par)
    except AppError as e:
        print(TAG+":", e, file=sys.stderr)
        return 1
    # except AppTraceback as e:  -- NO
    except KeyboardInterrupt:
        # The stock exit code is also 1 in case of signal, so we are not
        # making it any worse. Just stubbing the traceback.
        return 1

    return 0

# http://utcc.utoronto.ca/~cks/space/blog/python/ImportableMain
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# animake -- The Ani-Nouto Make
# coding=utf-8
# Copyright (c) 2014 Pete Zaitcev <zaitcev@yahoo.com>

from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import sys

from animake import AppError

TAG="animake"

# We forgot to encode this relationship in the repo, so now we have to
# hardcode the known anime series.
anime_known = [
'abenobashi',
'accel world',
'AIURA',
'AKB0048',
'angel beats',
'ano natsu',
'arashi',
'aria',
'asoiku',
'azumanga',
'bakemonogatari',
'bamboob',
'bamboo blade',
'banner',
'black lagoon',
'campanella',
'chihayafuru',
'chuu2koi',
'dai-guard',
'dennou coil',
'dog days',
'druaga',
'dual',
'ef',
'fairy_tail',
'figure17',
'fractale',
'FSN',
'fullmoon',
'ga_gadc',
'gargantia',
'garupan',
'gatakei',
'golden_time',
'gundam',
'gurren-lagann',
'Haganai',
'haibane',
'hanamaru',
'haruhi',
'hidamari',
'hyakko',
'ichizon',
'infinite stratos',
'Initial D',
'j2',
'Joshiraku',
'kamichu',
'kampfer',
'kannagi',
'katanagatari',
'kimikiss',
'kobato',
'K-ON',
'kuragehime',
'lagrange',
'lucky star',
'macademi',
'macross',
'madoka',
'magikano',
'mahoraba',
'manabi',
'marimite',
'midori days',
'mitsudomoe',
'moribito',
'morita-san',
'mouretsu',
'muromi-san',
'mushishi',
'muv-luv',
'nanoha',
'naruto',
'natsuiro kiseki',
'nazo no kanojo x',
'nichijou',
'nodame',
'non_non_biyori',
'Oba Nobuna',
'oh_edo_rocket',
'ookami-san',
'oreimo',
'polar bear cafe',
'precure',
'rahxephon',
'railgun',
'rocket girls',
'seiyuu',
'sekirei',
'shingu',
'shining hearts',
'silver_spoon',
'sops',
'sorakake',
'stella',
'stellvia',
'strike witches',
'sunred',
'SYD',
'tamako_market',
'tari tari',
'to heart',
'tokikake',
'toradora',
'true tears',
'TWGOK',
'uchouten_kazoku',
'upotte',
'vandread',
'vividred',
'watamote',
'xenoglossia',
'yakuindomo',
'yama no susume',
'yowapeda',
'yuyushiki',
'zakuro',
'ZKC',
'君に届け',
'無敵看板娘']

# We also hardcode all categories, so warnings may be issued.
cat_known = [
'anime',
'bost',
'ecchi',
'game',
'hentai',
'manga',
'meta',
'micro-nouto',
'music',
'netflix',
'nihongo',
'nipponism',
'other',
'ren-ai',
'retrospective',
'space',
'taf',
'triptych',
'石田燿子']

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
        self.verbose = False
        for i in range(len(argv)):
            if skip:
                skip = 0
                continue
            arg = argv[i]
            if len(arg) != 0 and arg[0] == '-':
                if arg == "-o":
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
                    print("Warning: Unknown header `%s' in %s" %
                              (hv[0], self.path),
                          file=sys.stderr)

        self.body = ''
        while 1:
            b = efp.read()
            if not b:
                break
            self.body += b
        # If would be nice to verify that tags are balanced.

        efp.close()

class Index(object):
    def __init__(self, par, parent, name):
        """
        raises: AppError in case we cannot create the output
        """
        self.parent = parent
        self.name = name

        outname = os.path.join(par.root, 'category')
        if parent:
            outname = os.path.join(outname, parent)
        outname = os.path.join(outname, name)
        try:
            os.mkdir(outname)
        except OSError as e:
            pass  # likely already-existing
        outname = os.path.join(outname, 'index.html')
        try:
            self.ofp = open(outname, 'w')
        except OSError as e:
            raise AppError("Cannot create index: "+str(e))

        self.oname = outname
        self.count = 0

    def inc(self):
        self.count += 1

    def close(self):
        self.ofp.close()

class Categories(object):
    def __init__(self, par):
        self.par = par
        self.all_tags = dict()

    def update(self, ent):

        """
        Merge ent.tags into all_tags.
        """
        if len(ent.tags) == 0:
            print("Warning: No tags in %s" % ent.path, file=sys.stderr)
        for tag in ent.tags:
            if tag not in self.all_tags:
                if tag in anime_known:
                    parent = 'anime'
                else:
                    parent = None
                    if not tag in cat_known:
                        print("Warning: Unknown tag `%s' in %s" % (
                               tag, ent.path), file=sys.stderr)
                index = Index(self.par, parent, tag)
                index.inc()
                self.all_tags[tag] = index
            else:
                index = self.all_tags[tag]
                index.inc()

    # XXX This prints parented tags mixed with freestanding ones.
    # XXX suddenly when moved into class these are sorted in C locale, why?
    def printout(self):
        print("Tags:")
        for tag in sorted(self.all_tags.iterkeys()):
            index = self.all_tags[tag]
            s = "%s%s: %d" % (
                 ' ' if index.parent else '', index.name, index.count)
            print(s.encode('utf-8'))

    def close(self):
        for tag in self.all_tags:
            index = self.all_tags[tag]
            index.close()

#def write_post(ent):
#    .......

#def write_index_updates(ent, all_tags):
#    .......

#def write_extras(par):
#    .......

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
    try:
        os.mkdir(os.path.join(par.root, 'category'))
    except OSError as e:
        raise AppError("Cannot make output directory: " + str(e))
    try:
        os.mkdir(os.path.join(par.root, 'category', 'anime'))
    except OSError as e:
        raise AppError("Cannot make output directory: " + str(e))

    cats = Categories(par)

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
            for name in sorted(filenames):
                if name[-4:] == '.txt':
                    ent = Entry(dirpath, name)
                    cats.update(ent)
                    #write_post(ent)
                    #write_index_updates(ent, all_tags)

    if par.verbose:
        cats.printout()

    for dirpath, dirnames, filenames in os.walk(par.repo, onerror=listerror):
        dirnames.sort(reverse=True)
        if par.verbose:
            print('%s' % dirpath)

    # write_extras(par)  # pages and category list

    cats.close()

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

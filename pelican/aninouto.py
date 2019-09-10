#
# Read the Ani-nouto format blog
#

from __future__ import print_function

import os
import sys

from six.moves.urllib.parse import urlparse

from pelican import signals
from pelican.readers import BaseReader

# Make a default slug that sort of resembles how WordPress does it.
def make_slug(title):
    out = []
    state = 0
    for c in title:
        if c.isalpha():
            out.append(c.lower())
            state = 0
        elif c.isdigit():
            out.append(c)
            state = 0
        else:
            if state == 0:
                out.append('-')
            state = 1
    return ''.join(out)

class AninoutoReader(BaseReader):
    enabled = True

    file_extensions = ['txt']

    # You need to have a read method, which takes a filename and returns
    # some content and the associated metadata.
    def read(self, filename):

        metadata = {}

        fname = os.path.basename(filename)
        # 20070130-01.txt but also 20071217-05-d1.txt 20110406a.txt etc.
        if len(fname) < 13 or fname[-4:] != '.txt':
            print("Bad file name format: %s" % (fname,), file=sys.stderr)
            # How to abort reading properly?
            return '', {}
        year_s = fname[0:4]
        month_s = fname[4:6]
        day_s = fname[6:8]
        # We have a few files with idents that do not match the rigid format.
        #ident_s = fname[9:11]

        # Special-case some historic zeroes to make the date valid
        if int(day_s) == 0:
            day_s = "01"

        metadata['date'] = '%s-%s-%s' % (year_s, month_s, day_s)

        with open(filename, 'r') as fp:

            url = None

            for line in fp:
                line = line.rstrip('\n')
                if len(line) == 0:
                    break
                kv = line.split(':', 1)
                # Bad syntax, just ignore for now
                if len(kv) != 2:
                    continue
                k = kv[0].strip()
                if k == 'Subject':
                    metadata['title'] = kv[1].strip()
                elif k == 'Tags':
                    # XXX we don't know how to pass multiply categories
                    tags = [tag.strip() for tag in kv[1].split(',')]
                    if len(tags) != 0:
                        metadata['category'] = tags[0]
                elif k == 'URL':
                    url = kv[1].strip()
                else:
                    # Unknown tag, maybe add some statistics later
                    continue

            if metadata.get('title') is None:
                metadata['title'] = fname[:-4]

            if url:
                path = urlparse(url).path.lstrip('/')
            else:
                # It is very common for URLs to be missing.
                slug = make_slug(metadata['title'])
                path = '%s/%s/%s/%s/' % (year_s, month_s, day_s, slug)
            metadata['url'] = path
            metadata['save_as'] = path + 'index.html'

            content = []
            for line in fp:
                line = line.rstrip('\n')
                content.append(line)

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return '\n'.join(content), parsed

def add_reader(readers):
    readers.reader_classes['txt'] = AninoutoReader

# This is how pelican works.
def register():
    signals.readers_init.connect(add_reader)

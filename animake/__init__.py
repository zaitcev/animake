# animake -- The Ani-Nouto Make
# coding=utf-8
# Copyright (c) 2014 Pete Zaitcev <zaitcev@yahoo.com>

import urllib


# The caught exception
class AppError(Exception):
    pass

# The uncaught exception
class AppTraceback(Exception):
    pass


html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    "\\": "&#92;",
    }

def escapeURLComponent(s):
    # Turn s into a bytes first, quote_plus blows up otherwise
    return unicode(urllib.quote_plus(s.encode("utf-8")))

def escapeURL(s):
    # quote_plus() doesn't work as it clobbers the :// portion of the URL
    # Make sure the resulting string is safe to use within HTML attributes.
    # N.B. Mooneyspace.com hates when we reaplace '&' with %26, so don't.
    # On output, the remaining & will be turned into &quot; by the templating
    # engine. No unescaped-entity problems should result here.
    s = s.replace('"', '%22')
    s = s.replace("'", '%27')
    # s = s.replace('&', '%26')
    s = s.replace('<', '%3C')
    s = s.replace('>', '%3E')
    return s

def escapeHTML(text):
    """Escape strings to be safe for use anywhere in HTML

    Should be used for escaping any user-supplied strings values before
    outputting them in HTML. The output is safe to use HTML running text and
    within HTML attributes (e.g. value="%s").

    Escaped chars:
      < and >   HTML tags
      &         HTML entities
      " and '   Allow use within HTML tag attributes
      \\        Shouldn't actually be necessary, but better safe than sorry
    """
    # performance idea: compare with cgi.escape-like implementation
    return "".join(html_escape_table.get(c,c) for c in text)

def safestr(u):
    try:
        if isinstance(u, unicode):
            return u.encode('utf-8')
    except NameError:
        # Python 3
        if isinstance(u, str):
            return u.encode('utf-8')
    return u

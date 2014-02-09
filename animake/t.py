# animake -- The Ani-Nouto Make
# coding=utf-8
# Copyright (c) 2014 Pete Zaitcev <zaitcev@yahoo.com>

from __future__ import unicode_literals
from animake.template import Template, TemplateElemLoop, TemplateElemCond


t_header = Template("""
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body>
""")

t_tag = Template(
'      <a href="${tag.href_tag}">${tag.name_tag}</a>\r\n'
)

t_top = Template("""
<table width="100%" style="background: #ebf7eb"
 border=0 cellpadding=1 cellspacing=0>
<tr valign="top">
    <td align="left">
        <h2 style="margin-bottom:0"> Title </h2>
    </td>
    <td align="right">
        [<b><a href="$href_root">root</a></b>]
    </td>
</tr></table>
""")

# XXX Add prev/next navigation
#   [$_page_prev][$_page_this][$_page_next]<br />
t_bottom = Template("""
<hr />
</body></html>
""")

# A standalone entry
t_entry = Template(
    t_header,
    t_top,
    # XXX title may be None, fix up with TemplateElemCond
    # XXX URL too
"""
    <p>${date}<br />
          <a href="${entry_url}">${title}</a> <br />
""",
          #TemplateElemCond('mark.note', '      ${mark.note}<br />\r\n', None),
          TemplateElemLoop('tag', 'entry_tags', t_tag),
"""
    </p>
    ${body}
""",
    #TemplateElemCond('flogin',
    #    '    <p>[<a href="$href_edit">edit</a>]</p>\r\n', None),
    t_bottom)

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/12/14'

"""
    georest.geo.jsonhelper
    ~~~~~~~~~~~~~~~~~~~~~~
    Wraps ujson
"""

import ujson

# ujson doesn't support most kwargs in standard json library
def dumps(obj, ensure_ascii=False, encode_html_chars=False,
          double_precision=9, **kw):
    return ujson.dumps(obj, ensure_ascii=ensure_ascii,
                       encode_html_chars=encode_html_chars,
                       double_precision=double_precision)


def loads(s, precise_float=False, **kw):
    return ujson.loads(s, precise_float=precise_float)


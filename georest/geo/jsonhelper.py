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
def dumps(obj, ensure_ascii=True, **kw):
    return ujson.dumps(obj, ensure_ascii=ensure_ascii)


def loads(s, **kw):
    return ujson.loads(s)

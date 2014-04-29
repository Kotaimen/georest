# -*- encoding: utf-8 -*-

"""
    georest.geo.jsonhelper
    ~~~~~~~~~~~~~~~~~~~~~~
    Hide differences of json implementations

"""

__author__ = 'kotaimen'
__date__ = '4/21/14'

try:
    # Prefer ujson because its faster
    import ujson

    # ujson doesn't support most kwargs in standard json library
    def dumps(obj, ensure_ascii=True, **kw):
        return ujson.dumps(obj, ensure_ascii=ensure_ascii)

    def loads(s, **kw):
        return ujson.loads(s)

    JSON_LIB_NAME = 'ujson'

except ImportError:

    from json import dumps, loads

    JSON_LIB_NAME = 'json'


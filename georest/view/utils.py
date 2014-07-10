# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/25/14'

"""
    georest.view.utils
    ~~~~~~~~~~~~~~~~~
    helper/mixin things for views
"""

import sys
from functools import wraps

from flask import request

from .exceptions import InvalidRequest
from ..geo import GeoException


def get_json_content():
    """check content type and return raw text instrad of json data"""
    if request.mimetype != 'application/json':
        raise InvalidRequest('Only "application/json" supported')
    try:
        data = request.data.decode('utf-8')
        # data = request.get_data().decode('utf-8')
    except UnicodeError:
        raise InvalidRequest('Cannot decode content with utf-8')
    return data


def get_if_match():
    """get if_match etag from request"""
    etag = None
    if request.if_match and not request.if_match.star_tag:
        try:
            etag, = request.if_match.as_set()  # only 1 allowed
        except ValueError:
            raise InvalidRequest('Cannot process if_match %s' % \
                                 request.if_match)
    return etag


def catcher(f):
    """catching uncatched errors, and filling the traceback"""
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GeoException as e:
            if not e.traceback:
                e.traceback = sys.exc_info()[2]
            raise

    return decorator

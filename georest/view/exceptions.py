# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/23/14'


"""
    georest.view.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~

    View exceptions.
"""

from ..geo import GeoException


class InvalidRequest(GeoException):  # XXX: is this appropriate?
    HTTP_STATUS_CODE = 400

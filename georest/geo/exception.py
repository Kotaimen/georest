# -*- encoding: utf-8 -*-

"""
    GeoExceptions
    ~~~~~~~~~~~~~
"""
__author__ = 'kotaimen'
__date__ = '3/19/14'

import sys


class GeoException(Exception):
    """
        Try to emulate python3 exception chain
    """

    def __init__(self, other_or_message=None):
        self.exc_info = sys.exc_info()
        if isinstance(other_or_message, basestring):
            super(GeoException, self).__init__(other_or_message)
        elif isinstance(other_or_message, BaseException):
            super(GeoException, self).__init__(other_or_message.message)
        else:
            super(GeoException, self).__init__()


class InvalidGeometry(GeoException):
    pass


class InvalidCRS(GeoException):
    pass

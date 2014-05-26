# -*- encoding: utf-8 -*-

"""
    georest.geo.exception
    ~~~~~~~~~~~~~~~~~~~~~
"""
__author__ = 'kotaimen'
__date__ = '3/19/14'

import sys
import six


class GeoException(Exception):
    """Try to emulate python3 exception chain"""

    HTTP_STATUS_CODE = 500

    def __init__(self, message=None, e=None):

        assert message is None or isinstance(message, six.string_types)

        self.tb = sys.exc_info()[2]
        if message is None and e is not None:
            super(GeoException, self).__init__(e.message)
        elif message is not None and e is None:
            super(GeoException, self).__init__(message)
        elif message is not None and e is not None:
            super(GeoException, self).__init__('%s: %s' % (message, e.message))
        else:
            super(GeoException, self).__init__()


class InvalidGeometry(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidCRS(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidFeature(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidProperty(GeoException):
    HTTP_STATUS_CODE = 400


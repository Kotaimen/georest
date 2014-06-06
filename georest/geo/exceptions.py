# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/29/14'

"""
    georest.geo.exception
    ~~~~~~~~~~~~~~~~~~~~~
    Geo exceptions, mimics py3k exception chain.
"""

import sys


class GeoException(Exception):
    # HTTP status code to simplify REST API error processing
    HTTP_STATUS_CODE = 500

    def __init__(self, message=None, e=None):
        assert message is None or isinstance(message, basestring)
        assert e is None or isinstance(e, BaseException)

        if e is not None:
            # Assemble additional message from exception
            if message is None:
                message = e.message
            else:
                message = '%s: %s' % (message, e.message)

        super(GeoException, self).__init__(message)

        self.traceback = sys.exc_info()[2]


class InvalidGeometry(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidFeature(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidProperties(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidProperty(GeoException):
    HTTP_STATUS_CODE = 400


class InvalidGeoJsonInput(InvalidGeometry):
    HTTP_STATUS_CODE = 400


class InvalidSpatialReference(GeoException):
    HTTP_STATUS_CODE = 400


# -*- encoding: utf-8 -*-

"""
    georest.view.exception
    ~~~~~~~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/26/14'

from ..geo.exception import GeoException


class InvalidGeometryOperator(GeoException):
    HTTP_STATUS_CODE = 400


class BadGeometryOperation(GeoException):
    HTTP_STATUS_CODE = 400


class IdentialGeometryError(GeoException):
    HTTP_STATUS_CODE = 409

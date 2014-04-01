# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/26/14'

from ..geo.exception import GeoException


class InvalidGeometryOperator(GeoException):
    pass


class BadGeometryOperation(GeoException):
    pass


class IdentialGeometryError(GeoException):
    pass
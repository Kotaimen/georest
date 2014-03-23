# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/23/14'

from ..geo.exception import GeoException


class GeoStoreError(GeoException):
    pass


class GeometryAlreadyExists(GeoStoreError):
    pass


class GeometryDoesNotExist(GeoStoreError):
    pass


class InvalidKey(GeoStoreError):
    pass


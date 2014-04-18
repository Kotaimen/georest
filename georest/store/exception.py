# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/23/14'

from ..geo.exception import GeoException


class GeoStoreError(GeoException):
    pass


class FeatureAlreadyExists(GeoStoreError):
    pass


class FeatureDoesNotExist(GeoStoreError):
    pass


class InvalidKey(GeoStoreError):
    pass


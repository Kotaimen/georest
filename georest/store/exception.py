# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/23/14'

from ..geo.exception import GeoException


class GeoStoreError(GeoException):
    pass


class FeatureAlreadyExists(GeoStoreError):
    HTTP_STATUS_CODE = 409


class FeatureDoesNotExist(GeoStoreError):
    HTTP_STATUS_CODE = 404


class InvalidKey(GeoStoreError):
    HTTP_STATUS_CODE = 400

class PropertyDoesNotExist(GeoStoreError):
    HTTP_STATUS_CODE = 404
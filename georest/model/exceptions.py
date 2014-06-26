# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/18/14'

"""
    georest.model.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Model exceptions.
"""

from ..geo.exceptions import GeoException


class ModelException(GeoException):
    pass


class FeatureModelException(ModelException):
    pass


class KeyExists(FeatureModelException):
    HTTP_STATUS_CODE = 409


class BucketNotAccessable(FeatureModelException):
    HTTP_STATUS_CODE = 403


class OperationsModelException(ModelException):
    pass


class NoSuchOperation(OperationsModelException):
    HTTP_STATUS_CODE = 404

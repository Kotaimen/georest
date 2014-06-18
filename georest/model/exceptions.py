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


class KeyExists(ModelException):
    HTTP_STATUS_CODE = 409

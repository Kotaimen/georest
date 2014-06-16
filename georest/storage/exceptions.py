# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

"""
    georest.storage.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Exceptions.
"""

from ..geo.exceptions import *


class StorageError(GeoException):
    pass


class FeatureNotFound(StorageError):
    pass


class ConflictVersion(StorageError):
    pass

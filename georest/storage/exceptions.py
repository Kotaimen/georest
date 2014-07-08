# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

"""
    georest.storage.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Exceptions.
"""

from ..geo.exceptions import *


class StorageError(GeoException):
    pass


class StorageInternalError(StorageError):
    HTTP_STATUS_CODE = 500


class UnknownStoragePrototype(StorageError):
    HTTP_STATUS_CODE = 400


class DuplicatedBucket(StorageError):
    HTTP_STATUS_CODE = 409


class BucketNotFound(StorageError):
    HTTP_STATUS_CODE = 404


class FeatureNotFound(StorageError):
    HTTP_STATUS_CODE = 404


class ParentRevisionNotFound(StorageError):
    HTTP_STATUS_CODE = 409


class NotHeadRevision(StorageError):
    HTTP_STATUS_CODE = 409

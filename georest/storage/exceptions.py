# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

"""
    georest.storage.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Exceptions.
"""

class StorageError(Exception):
    pass


class FeatureNotFound(StorageError):
    pass


class InvalidFeature(StorageError):
    pass


class InvalidProperties(StorageError):
    pass


class InvalidGeometry(StorageError):
    pass


class VersionConflicted(StorageError):
    pass


class ModificationConflicted(StorageError):
    pass

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
    def __init__(self, message=None, e=None):
        GeoException.__init__(self, message, e)


class UnknownStoragePrototype(StorageError):
    def __init__(self, prototype='', e=None):
        message = 'prototype: "%s"' % prototype
        StorageError.__init__(self, message, e)


class DuplicatedBucket(StorageError):
    def __init__(self, bucket_name='', e=None):
        message = 'bucket_name: "%s"' % bucket_name
        StorageError.__init__(self, message, e)


class BucketNotFound(StorageError):
    def __init__(self, bucket_name='', e=None):
        message = 'name: "%s"' % bucket_name
        StorageError.__init__(self, message, e)


class FeatureNotFound(StorageError):
    def __init__(self, key='', revision='', e=None):
        message = 'key: "%s", rev: %s' % (key, revision)
        StorageError.__init__(self, message, e)


class ParentRevisionNotFound(StorageError):
    def __init__(self, key='', parent_rev='', e=None):
        message = 'key: "%s", parent_rev: "%s"' % (key, parent_rev)
        StorageError.__init__(self, message, e)


class NotHeadRevision(StorageError):
    def __init__(self, key='', parent_rev=''):
        message = 'key: "%s", parent_rev: "%s"' % (key, parent_rev)
        StorageError.__init__(self, message, None)

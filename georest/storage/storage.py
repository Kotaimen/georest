# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/16/14'

"""
    georest.storage.storage
    ~~~~~~~~~~~~~~~~~~~~~~~
    A Geo Feature Storage.

"""

import six
from .exceptions import BucketNotFound, DuplicatedBucket


class FeatureStorage(object):
    """Geo Feature Storage

    The storage manages feature buckets.
    """

    def __init__(self, bucket_factory):
        self._factory = bucket_factory
        self._collection = dict()

    def create_bucket(self, name, **kwargs):
        """Create a feature bucket.

        :param basestring name: bucket name
        :param dict kwargs: parameters of the creation
        :rtype `FeatureBucket`
        """
        assert isinstance(name, six.string_types)

        if name in self._collection:
            raise DuplicatedBucket(name)

        bucket = self._factory(name, **kwargs)

        self._collection[name] = bucket
        return bucket

    def get_bucket(self, name):
        """Get a created feature bucket.

        :param basestring name: bucket name
        :rtype `FeatureBucket`
        """
        assert isinstance(name, six.string_types)
        try:
            return self._collection[name]
        except KeyError:
            raise BucketNotFound(name)

    def delete_bucket(self, name):
        """Delete a created feature bucket. Do not raise if bucket not found.

        :param basestring name: bucket name
        :rtype `FeatureBucket`
        """
        assert isinstance(name, six.string_types)
        try:
            del self._collection[name]
        except KeyError:
            pass

    def list_buckets(self):
        """List all the buckets in the storage.

        :rtype list
        """
        return self._collection.keys()

    def close(self):
        pass


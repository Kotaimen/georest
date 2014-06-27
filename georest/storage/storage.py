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

    def describe(self):
        """Get Storage Description.
        """
        return self._factory.describe()

    def create_bucket(self, name, **kwargs):
        """Create a feature bucket.

        :param basestring name: bucket name
        :param dict kwargs: parameters of the creation
        :rtype :class:`FeatureBucket`
        """
        assert isinstance(name, six.string_types)

        bucket = self._factory.create(name, **kwargs)

        return bucket

    def get_bucket(self, name):
        """Get a created feature bucket.

        :param basestring name: bucket name
        :rtype :class:`FeatureBucket`
        """
        assert isinstance(name, six.string_types)

        bucket = self._factory.get(name)

        return bucket

    def delete_bucket(self, name):
        """Delete a created feature bucket. Do not raise if bucket not found.

        :param basestring name: bucket name
        """
        assert isinstance(name, six.string_types)

        self._factory.delete(name)

        return True

    def close(self):
        pass


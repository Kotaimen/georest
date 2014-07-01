# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/16/14'

"""
    georest.storage.storage
    ~~~~~~~~~~~~~~~~~~~~~~~
    A Geo Feature Storage.

"""


class FeatureStorage(object):
    """Geo Feature Storage

    The storage manages feature buckets.
    """

    support_version = False

    def describe(self):
        return dict(support_version=self.support_version)

    def create_bucket(self, name, overwrite=False, **kwargs):
        """Create a feature bucket.

        :param basestring name: bucket name
        :param bool overwrite: whether overwrite the bucket with same name.
        :param dict kwargs: parameters of the creation
        :rtype :class:`FeatureBucket`
        """
        raise NotImplementedError

    def get_bucket(self, name):
        """Get a created feature bucket.

        :param basestring name: bucket name
        :rtype :class:`FeatureBucket`
        """
        raise NotImplementedError

    def delete_bucket(self, name):
        """Delete a created feature bucket. Do not raise if bucket not found.

        :param basestring name: bucket name
        """
        raise NotImplementedError

    def has_bucket(self, name):
        """Check existence of the bucket.

        :param basestring name: bucket name
        """
        raise NotImplementedError

    def close(self):
        """Shutdown the storage
        """
        pass


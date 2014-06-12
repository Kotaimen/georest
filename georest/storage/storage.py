# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/3/14'

"""
    georest.storage.storage
    ~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Interface.
"""

from collections import namedtuple


class FeatureStorageResult(namedtuple('Foo', 'success feature version')):
    pass


class FeatureStorage(object):
    """Interface for Geo Feature Storage

    A `FeatureStorage` is a versioned, persistent storage for geo features,
    which supports atomic and concurrent operations.
    """

    def put_feature(self, feature, version=None):
        """Put the feature.

        Return the feature for the "key".
        If version is not provided, a new version of the feature will be added.
        Otherwise, the operation will success only if the version matches
        the latest version for the "key", which means the feature has not been
        modified since last get.

        :param `Feature` feature: the feature
        :param str version: version of the feature
        :rtype `FeatureStorageResult`
        """
        raise NotImplementedError

    def get_feature(self, key, version=None):
        """Get the feature.

        Return the feature for the "key". Raise `FeatureNotFound` if not found.
        If version is provided, the feature of the specified version will
        be returned. Otherwise, it will be the top version of the feature.

        :param str key: key of the feature
        :param str version: version of the feature
        :rtype `FeatureStorageResult`
        """
        raise NotImplementedError

    def delete_feature(self, key, version=None):
        """Remove the feature.

        Return True on success. It is not an error if "key" is not found.

        :param str key: key of the feature
        :param str version: version of the feature
        :rtype FeatureStorageResult
        """
        raise NotImplementedError

    def update_properties(self, key, properties, version=None):
        """Put the properties into the feature.

        Return the feature with new properties. Raise `FeatureNotFound` if not
        found.

        :param str key: key of the feature
        :param dict properties: properties of the feature
        :param str version: version of the feature
        :rtype `FeatureStorageResult`
        """
        raise NotImplementedError

    def get_properties(self, key, version=None):
        """Get the properties of the feature.

        Return the properties of the feature.

        :param str key: key of the feature
        :param str version: version of the feature
        :rtype dict
        """
        raise NotImplementedError

    def update_geometry(self, key, geometry, version=None):
        """Put the geometry into the feature.

        :param str key: key of the feature
        :param `Geometry` geometry: geometry of the feature
        :param str version: version of the feature
        :rtype `FeatureStorageResult`
        """
        raise NotImplementedError

    def get_geometry(self, key, version=None):
        """Get the geometry of the feature.

        :param str key: key of the feature
        :param str version: version of the feature
        :rtype `Geometry`
        """
        raise NotImplementedError

    def close(self):
        """Close the data source
        """
        pass

    def __enter__(self):
        yield self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/3/14'

"""
    georest.storage.storage
    ~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Interface.
"""

from collections import namedtuple


class StorageResponse(namedtuple('Foo', 'key revision feature')):
    pass


class FeatureStorage(object):
    """Interface for Geo Feature Storage

    A `FeatureStorage` is a versioned, persistent storage for geo features,
    which supports atomic and concurrent operations.
    """

    def put_feature(self, key, feature, revision=None, fetch=False):
        """Put the feature.

        Return the key and revision of the feature
        If revision is None, a new revision of the feature will be added.
        Otherwise, a new feature will be added only if the feature has not
        been modified since the revision. (the revision matches the latest one)

        :param `Key` key: key of the feature
        :param `Feature` feature: the feature
        :param str revision: revision of the feature
        :param bool fetch: output the feature in the result
        :raise `ConflictVersion`
        :rtype `StorageResponse`
        """
        raise NotImplementedError

    def get_feature(self, key, revision=None):
        """Get the feature.

        Return the feature for the "key". Raise `FeatureNotFound` if not found.
        If revision is None, top version of the feature will be returned.
        Otherwise, the feature of the specified revision will be returned.

        :param `Key` key: key of the feature
        :param str revision: revision of the feature
        :raise `FeatureNotFound`
        :rtype `StorageResponse`
        """
        raise NotImplementedError

    def delete_feature(self, key, revision=None, fetch=False):
        """Remove the feature.

        Return True on success. It is not an error if "key" is not found.
        If revision is None, top revision will be deleted. Otherwise, the
        feature will be deleted only if the revision is the top revision

        :param `Key` key: key of the feature
        :param str revision: revision of the feature
        :param bool fetch: output the deleted feature in the result
        :raise `ConflictVersion`
        :rtype `StorageResponse`
        """
        raise NotImplementedError

    def update_properties(self, key, properties, revision=None, fetch=False):
        """Update the properties of the feature.

        Return the new feature. Raise `FeatureNotFound` if not found.

        :param `Key` key: key of the feature
        :param dict properties: properties of the feature
        :param str revision: revision of the feature
        :param bool fetch: output the feature in the result
        :raise `FeatureNotFound`
        :raise `ConflictVersion`
        :rtype `StorageResponse`
        """
        raise NotImplementedError


    def update_geometry(self, key, geometry, revision=None, fetch=False):
        """Update the geometry of the feature.

        Return the new feature. Raise `FeatureNotFound` if not found.

        :param `Key` key: key of the feature
        :param `Geometry` geometry: geometry of the feature
        :param str revision: revision of the feature
        :raise `FeatureNotFound`
        :raise `ConflictVersion`
        :rtype `StorageResponse`
        """
        raise NotImplementedError


    def close(self):
        """Close the data source
        """
        pass

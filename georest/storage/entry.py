# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/20/14'

"""
    georest.storage.entry
    ~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Accessor.
"""

from collections import namedtuple

from ..geo import Key, Feature, SpatialReference, Metadata, Geometry
from .bucket import FeatureBucket, FeatureMapper


def make_mapper_from_feature(feature):
    assert isinstance(feature, Feature)
    properties = dict(feature.properties)
    metadata = dict(feature.metadata._asdict())
    wkt = feature.geometry.wkt
    srid = feature.crs.srid
    return FeatureMapper(properties, metadata, wkt, srid)


def make_feature_from_mapper(key, mapper):
    assert isinstance(mapper, FeatureMapper)
    crs = SpatialReference(srid=mapper.srid)
    metadata = Metadata(**mapper.metadata)
    properties = dict(mapper.properties)
    geometry = Geometry.build_geometry(mapper.wkt, srid=mapper.srid)

    feature = Feature(key, geometry, crs, properties, metadata)
    return feature


class Response(namedtuple('Bar', 'key, revision, parent_revision, timestamp')):
    """Response for Feature Entry
    """

    @classmethod
    def from_commit(cls, commit):
        key = Key.build_from_qualified_name(commit.name)
        return Response(
            key, commit.revision, commit.parent_revision, commit.timestamp)


class FeatureEntry(object):
    """ A Feature Accessor.

    Access feature in the bucket.
    """

    def __init__(self, bucket):
        assert isinstance(bucket, FeatureBucket)
        self._bucket = bucket

    def put_feature(self, key, feature, revision=None):
        """ Put a feature in the bucket

        Conditions:
            key exists, parent None:
                parent = head
                add a new record based on head
            key exists, parent not None:
                parent = parent
                raise NotHeadRevision if parent is not head revision
                add a new record based on parent
            key not exists, parent None:
                parent = None
                add a new record based on parent
            key not exists, parent not None:
                parent = None
                raise ParentRevisionNotFound

        :param :class:`Key` key: feature key
        :param :class:`Feature` feature: feature instance
        :param str revision: feature revision
        :rtype :class:`Response`
        """
        # make a random name if name is None
        bucket, name = key
        if not name:
            name = self._bucket.make_random_name()
        key = Key.make_key(bucket=bucket, name=name)

        full_name = key.qualified_name
        mapper = make_mapper_from_feature(feature)

        commit = self._bucket.commit(full_name, mapper, parent=revision)
        return Response.from_commit(commit)

    def get_feature(self, key, revision=None):
        """ Get a feature in the bucket

        Conditions:
            key exists, parent None:
                parent = head
                get a feature with head revision
            key exists, parent not None:
                parent = parent
                raise FeatureNotFound if parent is not found
                get a feature with parent revision
            key not exists, parent None:
                raise FeatureNotFound
            key not exists, parent not None:
                raise FeatureNotFound

        :param :class:`Key` key: feature key
        :param str revision: feature revision
        :rtype tuple(:class:`Response`, :class:`Feature`)
        """
        full_name = key.qualified_name

        commit, mapper = self._bucket.checkout(full_name, revision=revision)
        feature = make_feature_from_mapper(key, mapper)
        return Response.from_commit(commit), feature

    def delete_feature(self, key, revision=None):
        """ Delete a feature in the bucket

        Conditions:
            key exists, parent None:
                parent = head
                delete a feature with head revision
            key exists, parent not None:
                parent = parent
                raise NotHeadRevision if parent is not head revision
                delete a feature with parent revision
            key not exists, parent None:
                parent = None
                raise FeatureNotFound
            key not exists, parent not None:
                parent = None
                raise FeatureNotFound

        :param :class:`Key` key: feature key
        :param str revision: feature revision
        :rtype :class:`Response`
        """
        name = key.qualified_name

        commit = self._bucket.remove(name, parent=revision)
        return Response.from_commit(commit)


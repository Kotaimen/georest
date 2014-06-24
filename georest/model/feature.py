# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.model.feature
    ~~~~~~~~~~~~~~~~~~~~~

    feature persistent/representation interface
"""


from datetime import datetime

from .. import geo
from ..geo import jsonhelper as json
from .. import storage
from . import exceptions


class BaseFeatureModel(object):
    """The way to persist, (de)serialize objects

    For now, this model is meant to be a thin-wrapper. All Exceptions are
    simply forwarded from georest.geo.exception and georest.store.exception
    """
    def __init__(self, feature_storage,
                 bucket_table=None,
                 allow_unknown_buckets=True,
                 default_bucket_config=None):
        """initialize the feature model

        :param feature_storage: the storage object this model handles
        :param bucket_table: bucket_name -> bucket_config mapping
        :param allow_unknown_buckets: whether allow unknown bucket names
                                      (not found in bucket_table)
        :param default_bucket_config: when bucket config not specified in
                                      bucket_table, use this config as default
        """
        self.feature_storage = feature_storage
        self.bucket_table = bucket_table or dict()
        self.allow_unknown_buckets = allow_unknown_buckets
        self.default_bucket_config = default_bucket_config or dict()

    def from_json(self, s, **kwargs):
        """load obj from json representation

        :param s: serialized obj
        :returns: obj
        :raises ModelInvalidData: invalid serialized
        """
        raise NotImplementedError

    def as_json(self, obj, **kwargs):
        """to string representation

        :returns: string-serialized obj
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def create(self, obj, bucket=None):
        """create an obj in storage without giving the key

        :param bucket: storage bucket
        :returns: key, metadata
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def put(self, obj, key, etag=None):
        """upadte an storage object

        :param key: storage key
        :param etag: check etag consistency if provided
        :returns: metadata
        :raises ModelInvalidData: invalid obj
        :raises ModelKeyExists: etag error
        """
        raise NotImplementedError

    def get(self, key):
        """get the object by key and bucket from storage

        :param key: storage key
        :returns: obj, metadata
        :raises ModelNotFound: no such obj
        """
        raise NotImplementedError

    def _get_visitor(self, key):
        try:
            storage_bucket = self.feature_storage.get_bucket(key.bucket)
        except storage.BucketNotFound:
            try:
                bucket_config = self.bucket_table[key.bucket]
            except KeyError:
                if self.allow_unknown_buckets:
                    bucket_config = self.default_bucket_config
                else:
                    raise exceptions.BucketNotAccessable(
                        'bucket %s is not allowed' % key.bucket)
            storage_bucket = self.feature_storage.create_bucket(key.bucket,
                                                                **bucket_config)
        visitor = storage.FeatureEntry(storage_bucket)
        return visitor


def _result2metadata(r):
    metadata = {'last_modified': r.timestamp}
    if not r.revision is None:
        metadata['etag'] = r.revision
    return metadata


class FeatureModel(BaseFeatureModel):
    def from_json(self, s):
        return geo.Feature.build_from_geojson(s)

    def as_json(self, obj):  # XXX: flat precision
        return obj.geojson

    def create(self, obj, bucket=None):
        key = geo.Key.make_key(bucket=bucket)
        visitor = self._get_visitor(key)
        r = visitor.put_feature(key, obj)
        metadata = _result2metadata(r)
        return r.key.qualified_name, metadata

    def get(self, key, srid=None):
        assert not srid, 'srid modification not implemented!'
        key = geo.Key.build_from_qualified_name(key)
        visitor = self._get_visitor(key)
        r, feature = visitor.get_feature(key)
        metadata = _result2metadata(r)
        return feature, metadata

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)
        visitor = self._get_visitor(key)
        r = visitor.put_feature(key, obj, revision=etag)
        metadata = _result2metadata(r)
        return metadata


class GeometryModel(BaseFeatureModel):
    def from_json(self, s, **kwargs):
        return geo.Geometry.build_geometry(s)

    def as_json(self, obj, **kwargs):
        return obj.geojson

    def create(self, obj, bucket=None):
        key = geo.Key.make_key(bucket=bucket)

        # new object
        feature = geo.Feature.build_from_geometry(obj)

        # store
        visitor = self._get_visitor(key)
        r = visitor.put_feature(key, feature)
        metadata = _result2metadata(r)
        return r.key.qualified_name, metadata

    def get(self, key, srid=None):

        key = geo.Key.build_from_qualified_name(key)
        visitor = self._get_visitor(key)
        r, feature = visitor.get_feature(key)
        geometry = feature.geometry
        if srid:
            # geometry srid conversion
            # XXX: maybe add a function for this.
            geometry = geo.UnaryOperation(srid=srid)(geometry)
        metadata = _result2metadata(r)
        return geometry, metadata

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)
        visitor = self._get_visitor(key)
        # get feature
        try:
            r1 = visitor.get_feature(key)
        except storage.FeatureNotFound:

            # create new feature from scratch
            feature = geo.Feature.build_from_geometry(obj)
        else:
            if etag and r1.revision != etag:
                raise exceptions.KeyExists('given etag %s is stale' % etag)

            # replace geometry
            feature = r1.feature
            feature.geometry = obj

        # save
        r2 = visitor.put_feature(key, feature, revision=etag)
        metadata = _result2metadata(r2)
        return metadata


class FeaturePropertiesModel(BaseFeatureModel):
    def from_json(self, s, **kwargs):
        return json.loads(s)

    def as_json(self, obj, **kwargs):
        return json.dumps(obj, double_precision=7)

    # No direct create for properties
    # def create(self, obj, bucket=None):

    def get(self, key):
        key = geo.Key.build_from_qualified_name(key)
        visitor = self._get_visitor(key)
        r, feature = visitor.get_feature(key)
        metadata = _result2metadata(r)
        return feature.properties, metadata

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)

        # get feature
        visitor = self._get_visitor(key)
        r1, feature = visitor.get_feature(key)
        if etag and r1.revision != etag:
            raise exceptions.KeyExists('given etag %s is stale' % etag)

        # replace properties
        feature.properties.clear()
        feature.properties.update(obj)

        # save
        r2 = visitor.put_feature(key, feature, revision=etag)
        metadata = _result2metadata(r2)
        return metadata

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
    def __init__(self, feature_storage):
        self.feature_storage = feature_storage

    def from_json(self, s):
        """load obj from json representation

        :param s: serialized obj
        :returns: obj
        :raises ModelInvalidData: invalid serialized
        """
        raise NotImplementedError

    def as_json(self, obj):
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


def _result2metadata(r):
    return {'etag': r.version,
            'last_modified': datetime.utcfromtimestamp(r.timestamp)}


class FeatureModel(BaseFeatureModel):
    def from_json(self, s):
        return geo.Feature.build_from_geojson(s)

    def as_json(self, obj):  # XXX: flat precision
        return obj.geojson

    def create(self, obj, bucket=None):
        key = geo.Key(bucket=bucket)
        r = self.feature_storage.put_feature(key, obj)
        metadata = _result2metadata(r)
        return r.key, metadata

    def get(self, key):
        key = geo.Key.build_from_qualified_name(key)
        r = self.feature_storage.get_feature(key)
        metadata = _result2metadata(r)
        return r.feature, metadata

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)
        r = self.feature_storage.put_feature(key, obj, revision=etag)
        metadata = _result2metadata(r)
        return metadata


class GeometryModel(BaseFeatureModel):
    def from_json(self, s):
        return geo.Geometry.build_geometry(s)

    def as_json(self, obj):
        return geo.Geometry.export_geojson(obj)

    def create(self, obj, bucket=None):
        key = geo.Key(bucket=bucket)

        # new object
        feature = geo.Feature.build_from_geometry(obj)

        # store
        r = self.feature_storage.put_feature(key, feature)
        metadata = _result2metadata(r)
        return r.key, metadata

    def get(self, key):
        key = geo.Key.build_from_qualified_name(key)
        r = self.feature_storage.get_feature(key)
        metadata = _result2metadata(r)
        return r.feature.geometry, metadata

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)

        # get feature
        try:
            r1 = self.feature_storage.get_feature(key)
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
        r2 = self.feature_storage.put_feature(key, feature, revision=etag)
        metadata = _result2metadata(r2)
        return metadata


class FeaturePropModel(BaseFeatureModel):
    def from_json(self, s):
        return json.loads(s)

    def as_json(self, obj):
        return json.dumps(obj)

    # No direct create for properties
    # def create(self, obj, bucket=None):

    def get(self, key):
        key = geo.Key.build_from_qualified_name(key)
        r = self.feature_storage.get_feature(key)
        metadata = _result2metadata(r)
        return r.feature.properties

    def put(self, obj, key, etag=None):
        key = geo.Key.build_from_qualified_name(key)

        # get feature
        r1 = self.feature_storage.get_feature(key)
        if etag and r1.revision != etag:
            raise exceptions.KeyExists('given etag %s is stale' % etag)

        # replace properties
        feature = r1.feature
        feature.properties = obj

        # save
        r2 = self.feature_storage.put_feature(key, feature, revision=etag)
        metadata = _result2metadata(r2)
        return metadata

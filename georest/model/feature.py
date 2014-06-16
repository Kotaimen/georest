# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.model.feature
    ~~~~~~~~~~~~~~~~~~~~~

    feature persistent/representation interface
"""


from .. import geo
from ..geo import jsonhelper as json


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


class FeatureModel(BaseFeatureModel):
    def from_json(self, s):
        return geo.Feature.build_from_geojson(s)

    def as_json(self, obj):  # XXX: flat precision
        return obj.geojson

    def create(self, obj, bucket=None):
        key = geo.Key(bucket=bucket)
        obj.key = key
        r = self.feature_storage.put_feature(obj)
        # XXX: assert r.success
        etag = str(r.version)

        return super(FeatureModel, self).create(obj, bucket)

    def get(self, key):
        return super(FeatureModel, self).get(key)

    def put(self, obj, key, etag=None):
        return super(FeatureModel, self).put(obj, key, etag)


class GeometryModel(BaseFeatureModel):
    def from_json(self, s):
        return geo.Geometry.build_geometry(s)

    def as_json(self, obj):
        return geo.Geometry.export_geojson(obj)

    def create(self, obj, bucket=None):
        return super(GeometryModel, self).create(obj, bucket)

    def get(self, key):
        return super(GeometryModel, self).get(key)

    def put(self, obj, key, etag=None):
        return super(GeometryModel, self).put(obj, key, etag)


class FeaturePropModel(BaseFeatureModel):
    def from_json(self, s):
        return json.loads(s)

    def as_json(self, obj):
        return json.dumps(obj)

    def create(self, obj, bucket=None):
        return super(FeaturePropModel, self).create(obj, bucket)

    def get(self, key):
        return super(FeaturePropModel, self).get(key)

    def put(self, obj, key, etag=None):
        return super(FeaturePropModel, self).put(obj, key, etag)

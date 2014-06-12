__author__ = 'pp'

from georest import geo
from .base import Model, FeatureStorageMixin


class FeatureModel(Model, FeatureStorageMixin):
    def from_json(self, s):
        return geo.Feature.build_from_geojson(s)

    def as_json(self, obj):
        return obj.geojson

    def create(self, obj, bucket=None):
        return super(FeatureModel, self).create(obj, bucket)

    def put(self, obj, key, bucket=None, etag=None):
        return super(FeatureModel, self).put(obj, key, bucket, etag)

    def get(self, key, bucket=None):
        return super(FeatureModel, self).get(key, bucket)

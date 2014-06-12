__author__ = 'pp'

from georest.geo import jsonhelper as json
from .base import Model, FeatureStorageMixin


class FeaturePropModel(Model, FeatureStorageMixin):
    def from_json(self, s):
        return json.loads(s)

    def as_json(self, obj):
        return json.dumps(obj)

    def create(self, obj, bucket=None):
        return super(FeaturePropModel, self).create(obj, bucket)

    def get(self, key, bucket=None):
        return super(FeaturePropModel, self).get(key, bucket)

    def put(self, obj, key, bucket=None, etag=None):
        return super(FeaturePropModel, self).put(obj, key, bucket, etag)

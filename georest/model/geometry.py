__author__ = 'pp'

from georest import geo
from .base import Model, FeatureStorageMixin


class GeometryModel(Model, FeatureStorageMixin):
    def from_json(self, s):
        return geo.Geometry.build_geometry(s)

    def as_json(self, obj):
        return geo.Geometry.export_geojson(obj)

    def create(self, obj, bucket=None):
        return super(GeometryModel, self).create(obj, bucket)

    def get(self, key, bucket=None):
        return super(GeometryModel, self).get(key, bucket)

    def put(self, obj, key, bucket=None, etag=None):
        return super(GeometryModel, self).put(obj, key, bucket, etag)
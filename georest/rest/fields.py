# -*- encoding: utf-8 -*-

"""
    georest.rest.fields
    ~~~~~~~~~~~~~~~~~~~

    Custom flask.restful.fields for marshaling
"""
__author__ = 'kotaimen'
__date__ = '3/21/14'

try:
    import ujson as json
except ImportError:
    import json

from flask.ext.restful import fields, marshal_with
from flask.ext.restful.fields import Raw, String, Integer, DateTime, List


class UUID(Raw):
    def format(self, value):
        return value.hex


class Geometry(Raw):
    def format(self, value):
        return json.loads(value.geojson)


class CRS(Raw):
    def format(self, value):
        if value is None:
            return None
        elif value.srid:
            return {'type': 'name',
                    'properties': {'name': 'EPSG:%d' % value.srid}}
        else:
            return {'type': 'name',
                    'properties': {'proj': value.proj}}


FEATURE_FIELDS = {
    '_id': UUID(attribute='id'),
    # '_etag': String(attribute='etag'),
    '_created': DateTime(attribute='created'),
    # '_modified': DateTime(attribute='modified'),
    '_geohash': String(attribute='geohash', default=''),
    'bbox': Raw(),
    'geometry': Geometry(),
    'type': String(),
    'crs': CRS(),
    'properties': Raw(default={})
}

GEOMETRY_FIELDS = {
    'geometry': Geometry(),
    'type': String(),
}

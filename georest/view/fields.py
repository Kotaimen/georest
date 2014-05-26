# -*- encoding: utf-8 -*-

"""
    georest.view.fields
    ~~~~~~~~~~~~~~~~~~~

    Custom flask.restful.fields for marshaling
"""
__author__ = 'kotaimen'
__date__ = '3/21/14'

from ..geo import jsonhelper as json
from werkzeug.http import http_date

from flask import current_app
from flask.ext.restful import fields, marshal_with
from flask.ext.restful.fields import Raw, String, Integer, List

#
# Formatters
#


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


class DateTime(Raw):
    def format(self, value):
        return http_date(value)

#
# Fields
#

FEATURE_FIELDS = {
    '_key': String(attribute='key'),
    '_etag': String(attribute='etag'),
    '_created': DateTime(attribute='created'),
    '_modified': DateTime(attribute='modified'),
    '_geohash': String(attribute='geohash', default=''),
    'bbox': Raw(),
    'geometry': Geometry(),
    'type': String(),
    'crs': CRS(),
    'properties': Raw(default={})
}

METADATA_FIELDS = {
    'key': String(),
    'id': UUID(),
    'etag': String(),
    'created': DateTime(),
    'modified': DateTime(),
}

GEOMETRY_FIELDS = {
    'geometry': Geometry(),
    'type': String(),
}

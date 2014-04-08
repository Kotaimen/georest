# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/21/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser
from .fields import FEATURE_FIELDS

from ..geo.exception import GeoException

__all__ = ['GeometriesResource', 'GeometryResource', 'FeatureResource',
           'FeatureResourceGeoHash', 'FeatureResourceBBox']

#
# Object get/set/delete
#

class GeometriesResource(BaseResource):
    def post(self):
        data = request.data
        feature = self.model.put_feature(None, data, overwrite=False)
        return {'key': feature.id, 'code': 201}, \
               201, make_header_from_feature(feature)


class GeometryResource(BaseResource):
    """ Interact with geometry in a feature """
    parser = GeometryRequestParser()

    def get(self, key):
        args = self.parser.parse_args()
        feature = self.model.get_feature(key)
        headers = make_header_from_feature(feature)
        return make_response_from_geometry(feature.geometry,
                                           args.format,
                                           args.srid,
                                           headers)

    def post(self, key):
        data = request.data
        feature = self.model.put_feature(key, data, overwrite=True)
        return {'key': feature.id, 'code': 201}, \
               201, make_header_from_feature(feature)

    def put(self, key):
        data = request.data
        feature = self.model.put_feature(key, data)
        return {'key': feature.id, 'code': 201}, \
               201, make_header_from_feature(feature)

    def delete(self, key):
        self.model.delete_feature(key)
        return None, 200


class FeatureResource(BaseResource):
    """ Feature
    """
    # TODO: Not finished yet, only need geometry api above
    @marshal_with(FEATURE_FIELDS)
    def get(self, key):
        feature = self.model.get_feature(key)
        return feature, 200, make_header_from_feature(feature)


class FeatureResourceGeoHash(BaseResource):
    def get(self, key):
        feature = self.model.get_feature(key)

        return {'result': feature.geohash}


class FeatureResourceBBox(BaseResource):
    def get(self, key):
        feature = self.model.get_feature(key)

        return {'result': feature.bbox}
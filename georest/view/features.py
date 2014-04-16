# -*- encoding: utf-8 -*-

"""
    georest.view.features
    ~~~~~~~~~~~~~~~~~~~~~

    Spatial resources
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser
from .fields import FEATURE_FIELDS

__all__ = ['FeaturesResource', 'FeatureResource',
           'FeatureResourceGeoHash', 'FeatureResourceBBox']


class FeaturesResource(BaseResource):
    """Post a new feature"""

    def post(self):
        data = request.data
        feature = self.model.put_feature(data, key=None)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)


class FeatureResource(BaseResource):
    """ Get&put&delete a feature"""
    @marshal_with(FEATURE_FIELDS)
    def get(self, key):
        feature = self.model.get_feature(key)
        return feature, 200, make_header_from_feature(feature)

    def put(self, key):
        data = request.data
        feature = self.model.put_feature(data, key=key)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)

    def delete(self, key):
        self.model.delete_feature(key)
        return None, 204


class FeatureResourceGeoHash(BaseResource):
    def get(self, key):
        feature = self.model.get_feature(key)

        return {'result': feature.geohash}


class FeatureResourceBBox(BaseResource):
    def get(self, key):
        feature = self.model.get_feature(key)

        return {'result': feature.bbox}
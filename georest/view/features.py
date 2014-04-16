# -*- encoding: utf-8 -*-

"""
    georest.view.features
    ~~~~~~~~~~~~~~~~~~~~~

    Spatial resources
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

from flask import request
from flask.ext.restful import marshal_with, abort

from .base import BaseResource, make_header_from_feature, \
    PrefixParser
from .fields import FEATURE_FIELDS

__all__ = ['FeaturesResource', 'FeatureResource',
           'FeatureResourceGeoHash', 'FeatureResourceBBox']


class FeaturesResource(BaseResource):
    """Post a new feature"""

    parser = PrefixParser()

    def post(self):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.put_feature(data, key=None, prefix=args.prefix)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)


class FeatureResource(BaseResource):
    """ Get&put&delete a feature"""

    parser = PrefixParser()

    @marshal_with(FEATURE_FIELDS)
    def get(self, key):
        feature = self.model.get_feature(key)
        return feature, 200, make_header_from_feature(feature)

    def put(self, key):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.put_feature(data, key=key, prefix=args.prefix)
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
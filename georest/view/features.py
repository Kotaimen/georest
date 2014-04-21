# -*- encoding: utf-8 -*-

"""
    georest.view.features
    ~~~~~~~~~~~~~~~~~~~~~

    Spatial resources
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

import json

from flask import request
from flask.ext.restful import marshal_with, abort

from .base import BaseResource, make_header_from_feature, \
    PrefixParser
from .fields import FEATURE_FIELDS

__all__ = ['FeaturesResource', 'FeatureResource',
           'FeatureResourceGeoHash', 'FeatureResourceBBox',
           'PropertiesResource', 'PropertyByNameResource']


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
        args = self.parser.parse_args()
        feature = self.model.get_feature(key, prefix=args.prefix)
        return feature, 200, make_header_from_feature(feature)

    def put(self, key):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.put_feature(data, key=key, prefix=args.prefix)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)

    def delete(self, key):
        args = self.parser.parse_args()
        data = request.data
        self.model.delete_feature(key, prefix=args.prefix)
        return None, 204


class FeatureResourceGeoHash(BaseResource):
    parser = PrefixParser()

    def get(self, key):
        args = self.parser.parse_args()
        feature = self.model.get_feature(key, args.prefix)
        return {'result': feature.geohash}, 200, \
               make_header_from_feature(feature)


class FeatureResourceBBox(BaseResource):
    parser = PrefixParser()

    def get(self, key):
        args = self.parser.parse_args()
        feature = self.model.get_feature(key, args.prefix)
        return {'result': feature.bbox}, 200, \
               make_header_from_feature(feature)


class PropertiesResource(BaseResource):
    parser = PrefixParser()

    def get(self, key):
        args = self.parser.parse_args()
        feature = self.model.get_feature(key, args.prefix)
        return feature.properties, 200, \
               make_header_from_feature(feature)

    def post(self, key):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.update_properties(data, key, args.prefix)
        return feature.properties, 201, \
               make_header_from_feature(feature)

    def delete(self, key):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.delete_properties(None, key, args.prefix)
        return None, 204


class PropertyByNameResource(BaseResource):
    parser = PrefixParser()

    def get(self, key, name):
        raise NotImplementedError


    def post(self, key, name):
        raise NotImplementedError


    def delete(self, key, name):
        raise NotImplementedError


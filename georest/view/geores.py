# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/21/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort
from flask.ext.restful.reqparse import RequestParser

from .base import BaseResource
from .fields import FEATURE_FIELDS

from ..geo.exception import GeoException

__all__ = ['Stat', 'GeometryResource', 'FeatureResource',
           'UnaryGeometryOperation']


class Stat(BaseResource):
    def get(self):
        return self.model.describe_capabilities()


class GeometryResource(BaseResource):
    parser = RequestParser()
    parser.add_argument('format',
                        dest='format',
                        action='store',
                        location='args',
                        type=str,
                        choices=['json', 'ewkt', 'ewkb'],
                        default='json',
                        required=False)
    parser.add_argument('srid',
                        dest='srid',
                        action='store',
                        location='args',
                        type=str,
                        default=0,
                        required=False)

    def get(self, key):
        args = self.parser.parse_args()
        try:
            feature = self.model.get_feature(key)
        except GeoException as e:
            self.abort(e)

        headers = self.make_header_from_feature(feature)

        return self.make_response_from_geometry(feature.geometry,
                                                args.format,
                                                args.srid,
                                                headers)

    def post(self, key):
        data = request.data
        try:
            feature = self.model.put_feature(key, data)
        except GeoException as e:
            self.abort(e)

        return None, 201, self.make_header_from_feature(feature)

    def delete(self, key):
        try:
            self.model.delete_feature(key)
        except GeoException as e:
            self.abort(e)
        return None, 200


class FeatureResource(BaseResource):
    @marshal_with(FEATURE_FIELDS)
    def get(self, key):
        try:
            feature = self.model.get_feature(key)
        except GeoException as e:
            self.abort(e)
        return feature, 200, self.make_header_from_feature(feature)




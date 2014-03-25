# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/21/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort
from flask.ext.restful.reqparse import RequestParser

from .base import BaseResource
from .fields import FEATURE_FIELDS, METADATA_FIELDS

from ..geo.exception import GeoException

__all__ = ['Stat', 'GeometryResource', 'FeatureResource']


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
                        choices=['json', 'geojson', 'ewkt', 'ewkb'],
                        default='json',
                        required=False)

    def get(self, key):
        args = self.parser.parse_args()
        try:
            feature = self.model.get_feature(key)
        except GeoException as e:
            self.abort(e)

        headers = self.header(feature)

        if args.format in ('json', 'geojson'):
            return json.loads(feature.geometry.json), 200, headers

        if args.format == 'ewkt':
            response_data = feature.geometry.ewkt
            response = make_response(response_data, 200)
            response.headers['Content-Type'] = 'text/plain'
        elif args.format == 'ewkb':
            response_data = str(feature.geometry.ewkb)
            response = make_response(response_data, 200)
            response.headers['Content-Type'] = 'application/binary'

        for k, v in headers.iteritems():
            response.headers[k] = v
        return response

    def post(self, key):
        data = request.data
        try:
            feature = self.model.put_feature(key, data)
        except GeoException as e:
            self.abort(e)

        return None, 201, self.header(feature)

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
        return feature, 200, self.header(feature)


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
                        choices=['json', 'wkt', 'ewkt', 'ewkb'],
                        default='json',
                        required=False)

    def get(self, key):
        try:
            feature = self.model.get_feature(key)
        except GeoException as e:
            self.abort(e)
        return json.loads(feature.geometry.json), 200, self.header(feature)

    def post(self, key):
        data = request.data
        try:
            feature = self.model.put_feature(key, data)
        except GeoException as e:
            self.abort(e)

        return None, 201, self.header(feature)


class FeatureResource(BaseResource):
    @marshal_with(FEATURE_FIELDS)
    def get(self, key):
        try:
            feature = self.model.get_feature(key)
        except GeoException as e:
            self.abort(e)
        return feature, 200, self.header(feature)


    def delete(self, key):
        self.model.delete_feature(key)
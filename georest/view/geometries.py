# -*- encoding: utf-8 -*-

"""
    georest.view.geometries
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

from flask import request

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser, PrefixParser

__all__ = ['GeometriesResource', 'GeometryResource']


class GeometriesResource(BaseResource):
    """Post a geometry"""
    parser = PrefixParser()

    def post(self):
        args = self.parser.parse_args()
        data = request.data
        feature = self.model.put_geometry(data, key=None, prefix=args.prefix)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)


class GeometryResource(BaseResource):
    """Get&put a geometry"""

    get_parser = GeometryRequestParser()
    put_parser = PrefixParser()

    def get(self, key):
        args = self.get_parser.parse_args()
        feature = self.model.get_feature(key)
        headers = make_header_from_feature(feature)
        return make_response_from_geometry(feature.geometry,
                                           args.format,
                                           args.srid,
                                           headers)

    def put(self, key):
        args = self.put_parser.parse_args()
        data = request.data
        feature = self.model.put_geometry(data, key=key, prefix=args.prefix)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)

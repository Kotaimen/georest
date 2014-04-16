# -*- encoding: utf-8 -*-

"""
    georest.view.geometries
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

from flask import make_response, request

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser

__all__ = ['GeometriesResource', 'GeometryResource']


class GeometriesResource(BaseResource):
    """Post a geometry"""

    def post(self):
        data = request.data
        feature = self.model.put_geometry(data, key=None)
        return {'key': feature.key, 'code': 201}, \
               201, make_header_from_feature(feature)


class GeometryResource(BaseResource):
    """Get&put a geometry"""

    parser = GeometryRequestParser()

    def get(self, key):
        args = self.parser.parse_args()
        feature = self.model.get_feature(key)
        headers = make_header_from_feature(feature)
        return make_response_from_geometry(feature.geometry,
                                           args.format,
                                           args.srid,
                                           headers)

    def put(self, key):
        data = request.data
        feature = self.model.put_geometry(data, key=key)
        return {'key': feature.id, 'code': 201}, \
               201, make_header_from_feature(feature)

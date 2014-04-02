# -*- encoding: utf-8 -*-

"""
    restapi
    ~~~~~~~

    Flask-restful API
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from flask.ext import restful

from .view import *


class GeoRestApi(restful.Api):
    """
        Add all georest api resources
    """

    def __init__(self, app, **args):
        assert app is not None
        super(GeoRestApi, self).__init__(app, **args)

        self.model = app.model
        self.add_resources()

    def add_resources(self):
        self.add_resource(Describe, '/describe')

        # Geometry resource
        self.add_resource(GeometriesResource,
                          '/geometries', methods=['POST'])
        self.add_resource(GeometryResource,
                          '/geometries/<key>', methods=['GET', 'PUT', 'DELETE'])
        # Feature resource
        self.add_resource(FeatureResource,
                          '/features/<key>')

        # Geometry operation
        self.add_resource(MixedGeometryOperation,
                          '/geometries/<key>/<operation>',
                          methods=['GET', 'POST'])
        self.add_resource(BinaryGeometryOperation,
                          '/geometries/<this>/<operation>/<other>',
                          methods=['GET'])
        self.add_resource(MixedPostGeometryOperation,
                          '/operation/<operation>',
                          methods=['POST'])

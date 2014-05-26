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
                          '/features/geometry', methods=['POST'])
        self.add_resource(GeometryResource,
                          '/features/<key>/geometry', methods=['GET', 'PUT'])

        # Feature resource
        self.add_resource(FeaturesResource,
                          '/features', methods=['POST'])
        self.add_resource(FeatureResource,
                          '/features/<key>', methods=['GET', 'PUT', 'DELETE'])
        self.add_resource(FeatureResourceGeoHash,
                          '/features/<key>/geohash', methods=['GET'])
        self.add_resource(FeatureResourceBBox,
                          '/features/<key>/bbox', methods=['GET'])

        # Feature Properties
        self.add_resource(PropertiesResource,
                          '/features/<key>/properties',
                          methods=['GET', 'POST', 'DELETE'])
        self.add_resource(PropertyByNameResource,
                          '/features/<key>/properties/<name>',
                          methods=['GET', 'DELETE'])

        # Geometry operation
        self.add_resource(MixedGeometryOperation,
                          '/operations/<operation>/<key>',
                          methods=['GET', 'POST'])
        self.add_resource(BinaryGeometryOperation,
                          '/operations/<operation>/<this>/<other>',
                          methods=['GET'])
        self.add_resource(MixedPostGeometryOperation,
                          '/operations/<operation>',
                          methods=['POST'])

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
        self.add_resource(GeometryResource, '/geometry/<key>')
        self.add_resource(FeatureResource, '/feature/<key>')
        self.add_resource(UnaryGeometryOperation, '/geometry/<key>/<operation>')
        self.add_resource(BinaryGeometryOperation,
                          '/geometry/<this>/<operation>/<other>')


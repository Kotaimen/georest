# -*- encoding: utf-8 -*-

"""
    restapi
    ~~~~~~~

    Flask-restful API
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from flask import current_app
from flask.ext import restful

from .rest import EngineStatus


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
        self.add_resource(EngineStatus, '/stat')


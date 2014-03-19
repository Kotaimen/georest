# -*- encoding: utf-8 -*-

"""
    georest.rest
    ~~~~~~~~~~~~~

    Restful resources
"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

from flask import current_app
from flask.ext import restful


class EngineStatus(restful.Resource):
    def __init__(self):
        self.model = current_app.model

    def get(self):
        return self.model.describe_engine()


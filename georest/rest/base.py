# -*- encoding: utf-8 -*-

"""
    georest.rest.base
    ~~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

from flask import current_app
from flask.ext.restful import Resource


class BaseResource(Resource):
    """
        Injects current application model into resource
    """

    def __init__(self):
        self.model = current_app.model

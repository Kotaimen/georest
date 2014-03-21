# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/21/14'


from flask import make_response
from flask.ext.restful import marshal_with

from .base import BaseResource
from .fields import FEATURE_FIELDS,GEOMETRY_FIELDS


__all__ = ['Stat', 'TestFeature', 'TestGeometry']


class Stat(BaseResource):
    def get(self):
        return self.model.describe_capabilities()


class TestFeature(BaseResource):
    @marshal_with(FEATURE_FIELDS)
    def get(self):
        return self.model.get_feature('blah')


class TestGeometry(BaseResource):
    @marshal_with(GEOMETRY_FIELDS)
    def get(self):

        return self.model.get_feature('blah')
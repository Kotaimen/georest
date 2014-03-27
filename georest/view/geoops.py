# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/25/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser
from .fields import FEATURE_FIELDS

from .exception import InvalidGeometryOperator, IdentialGeometryError

__all__ = ['UnaryGeometryOperation', 'BinaryGeometryOperation']


def make_predicate_result(op, ret):
    return dict(operation=op, result=ret)


default_parser = GeometryRequestParser()

UNARY_GEOM_PROPERTIES = {
    'area': 'area',
    'type': 'geom_type',
    'num_coords': 'num_coords',
    'coords': 'coords',
    'num_geom': 'num_geom',
    'has_z': 'hasz',
    'is_empty': 'empty',
    'is_ring': 'ring',
    'is_simple': 'simple',
}

BINARY_GEOM_PREDICATES = {
    'contains': 'contains',
    'crosses': 'crosses',
    'disjoint': 'disjoint',
    'equals': 'equals',
    'intersects': 'intersects',
    'overlaps': 'overlaps',
    'touches': 'touches',
    'within': 'within',

}


class UnaryGeometryOperation(BaseResource):
    def get(self, key, operation):
        feature = self.model.get_feature(key)
        if operation in UNARY_GEOM_PROPERTIES:
            result = getattr(feature.geometry, UNARY_GEOM_PROPERTIES[operation])
            return make_predicate_result('%s(%s)' % (operation, key), result)
        else:
            raise InvalidGeometryOperator(operation)


class BinaryGeometryOperation(BaseResource):
    def get(self, this, operation, other):
        if this == other:
            raise IdentialGeometryError
        this_feature = self.model.get_feature(this)
        other_feature = self.model.get_feature(other)
        if operation in BINARY_GEOM_PREDICATES:
            method = getattr(this_feature.geometry,
                             BINARY_GEOM_PREDICATES[operation])
            result = method(other_feature.geometry)

            return make_predicate_result('%s.%s(%s)' % (this, operation, other),
                                         result)
        else:
            raise InvalidGeometryOperator(operation)

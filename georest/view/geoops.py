# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/25/14'

import json

from flask import make_response, request
from flask.ext.restful import marshal_with, abort

from ..geo import build_geometry

from .base import BaseResource, make_header_from_feature, \
    make_response_from_geometry, GeometryRequestParser

from .exception import InvalidGeometryOperator, IdentialGeometryError


__all__ = ['UnaryGeometryOperation', 'BinaryGeometryOperation']

#
# Result
#
def make_predicate_result(ret):
    return dict(result=ret)

#
# Default geometry parser
#
default_parser = GeometryRequestParser()

# operation name: method name
UNARY_GEOMETRY_PROPERTIES = {
    'type': 'geom_type',
    'coords': 'coords',
    'geoms': 'num_geom',
    'area': 'area',
    'length': 'length',
    'is_empty': 'empty',
    'is_ring': 'ring',
    'is_simple': 'simple',
}

# operation name: method name
UNARY_TOPOLOGICAL_PROPERTIES = {
    'boundary': 'boundary',
    'centroid': 'centroid',
    'convex_hull': 'convex_hull',
    'envelope': 'envelope',
    'point_on_surface': 'point_on_surface',
}

buffer_parser = GeometryRequestParser()
buffer_parser.add_argument('width',
                           dest='width',
                           action='store',
                           location='args',
                           type=float,
                           required=True)
buffer_parser.add_argument('quadsegs',
                           dest='quadsegs',
                           action='store',
                           location='args',
                           type=int,
                           default=8,
                           required=False)

simplify_parser = GeometryRequestParser()
simplify_parser.add_argument('tolerance',
                             dest='tolerance',
                             action='store',
                             location='args',
                             type=float,
                             required=True)
simplify_parser.add_argument('topo',
                             dest='preserve_topology',
                             action='store',
                             location='args',
                             type=bool,
                             default=False,
                             required=False)

# operation name: (method name, parser)
UNARY_TOPOLOGICAL_METHODS = {
    'buffer': ('buffer', buffer_parser),
    'simplify': ('simplify', simplify_parser)
}

# operation name: (method name, parser)
BINARY_GEOMETRY_PREDICATES = {
    'contains': 'contains',
    'crosses': 'crosses',
    'disjoint': 'disjoint',
    'equals': 'equals',
    'intersects': 'intersects',
    'overlaps': 'overlaps',
    'touches': 'touches',
    'within': 'within',
}

# operation name: (method name, parser)
BINARY_GEOMETRY_METHODS = {
    'distance': 'distance',
}

BINARY_TOPOLOGICAL_METHODS = {
    'intersection': 'intersection',
    'difference': 'difference',
    'union': 'union',
}


class UnaryGeometryOperation(BaseResource):
    OPERATIONS = set()
    OPERATIONS.update(UNARY_GEOMETRY_PROPERTIES.keys())
    OPERATIONS.update(UNARY_TOPOLOGICAL_METHODS.keys())
    OPERATIONS.update(UNARY_TOPOLOGICAL_PROPERTIES.keys())

    def _parse_args(self, operation):
        if operation in UNARY_TOPOLOGICAL_METHODS:
            method, parser = UNARY_TOPOLOGICAL_METHODS[operation]
            return parser.parse_args()
        else:
            return default_parser.parse_args()

    def _process(self, geometry, operation):

        args = self._parse_args(operation)

        if args.srid:
            geometry.transform(args.srid)

        # TODO: Ugly, refactor later ...
        if operation in UNARY_GEOMETRY_PROPERTIES:
            result = getattr(geometry, UNARY_GEOMETRY_PROPERTIES[operation])
            return make_predicate_result(result)
        elif operation in UNARY_TOPOLOGICAL_PROPERTIES:
            result = getattr(geometry, UNARY_TOPOLOGICAL_PROPERTIES[operation])
            return make_response_from_geometry(result, args.format)
        elif operation in UNARY_TOPOLOGICAL_METHODS:
            method_args = dict(args)
            del method_args['srid']
            del method_args['format']
            method_name, parser = UNARY_TOPOLOGICAL_METHODS[operation]
            method = getattr(geometry, method_name)
            result = method(**method_args)

            return make_response_from_geometry(result, args.format)
        else:
            assert False

    def get(self, key, operation):
        if operation not in self.OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid geometry operation :"%s"' % operation)
        feature = self.model.get_feature(key)
        geometry = feature.geometry

        return self._process(geometry, operation)


    def post(self, operation):
        if operation not in self.OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid geometry operation :"%s"' % operation)
        geometry = build_geometry(request.data, srid=4326)

        return self._process(geometry, operation)



class BinaryGeometryOperation(BaseResource):
    OPERATIONS = set()
    OPERATIONS.update(BINARY_GEOMETRY_PREDICATES)

    def _parse_args(self, operation):
        return default_parser.parse_args()

    def get(self, this, operation, other):

        if operation not in self.OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid geometry operation :"%s"' % operation)

        if this == other:
            raise IdentialGeometryError('Given geometries are identical')

        args = self._parse_args(operation)

        this_geom = self.model.get_feature(this).geometry
        other_geom = self.model.get_feature(other).geometry

        if operation in BINARY_GEOMETRY_PREDICATES \
                or operation in BINARY_GEOMETRY_METHODS:
            method = getattr(this_geom,
                             BINARY_GEOMETRY_PREDICATES[operation])
            result = method(other_geom)
            return make_predicate_result(result)
        elif operation in BINARY_TOPOLOGICAL_METHODS:
            method = getattr(this_geom,
                             BINARY_GEOMETRY_PREDICATES[operation])
            result = method(other_geom)
            return make_response_from_geometry(result, args.format)
        else:
            assert False


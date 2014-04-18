# -*- encoding: utf-8 -*-

"""
    georest.view.operations
    ~~~~~~~~~~~~~~~~~~~~~~~

"""


__author__ = 'kotaimen'
__date__ = '3/25/14'

from flask import request

from ..geo import build_geometry
from ..geo.exception import InvalidGeometry

from .base import BaseResource, make_response_from_geometry, \
    OperationRequestParser

from .exception import InvalidGeometryOperator, IdentialGeometryError


__all__ = ['UNARY_OPERATIONS', 'BINARY_OPERATIONS',
           'MixedGeometryOperation', 'BinaryGeometryOperation',
           'MixedPostGeometryOperation']


def make_predicate_result(ret):
    return dict(result=ret)

#
# Parsers
#
default_parser = OperationRequestParser()

buffer_parser = OperationRequestParser()
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

simplify_parser = OperationRequestParser()
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

#
# Operations
#

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

UNARY_OPERATIONS = set()
UNARY_OPERATIONS.update(UNARY_GEOMETRY_PROPERTIES.keys())
UNARY_OPERATIONS.update(UNARY_TOPOLOGICAL_METHODS.keys())
UNARY_OPERATIONS.update(UNARY_TOPOLOGICAL_PROPERTIES.keys())

BINARY_OPERATIONS = set()
BINARY_OPERATIONS.update(BINARY_GEOMETRY_METHODS.keys())
BINARY_OPERATIONS.update(BINARY_GEOMETRY_PREDICATES.keys())
BINARY_OPERATIONS.update(BINARY_TOPOLOGICAL_METHODS.keys())


#
# Unary operations
#

class GeometryOperationBase(object):
    def _parse_args(self, operation):
        if operation in UNARY_TOPOLOGICAL_METHODS:
            _method, parser = UNARY_TOPOLOGICAL_METHODS[operation]
        else:
            parser = default_parser

        return parser.parse_args()

    def _process(self, operation, this, other=None):
        args = self._parse_args(operation)

        if args.srid:
            this.transform(args.srid)
            if other is not None:
                other.transform(args.srid)

        # XXX: This is so so ugly...
        # NOTE: Select a geometry attribute or bounded method call from given
        # operation string.  Argument list, arg parsing, result are all
        # different and depends on the operation selected.  Maybe Command
        # patten fits here?
        if operation in UNARY_GEOMETRY_PROPERTIES:
            attribute_name = UNARY_GEOMETRY_PROPERTIES[operation]
            return make_predicate_result(getattr(this, attribute_name))

        elif operation in UNARY_TOPOLOGICAL_PROPERTIES:
            attribute_name = UNARY_TOPOLOGICAL_PROPERTIES[operation]
            attribute = getattr(this, attribute_name)
            return make_response_from_geometry(attribute, args.format)

        elif operation in UNARY_TOPOLOGICAL_METHODS:
            method_args = dict(args)
            del method_args['srid']
            del method_args['format']
            method_name, parser = UNARY_TOPOLOGICAL_METHODS[operation]
            bounded_method = getattr(this, method_name)
            result = bounded_method(**method_args)
            return make_response_from_geometry(result, args.format)

        elif operation in BINARY_GEOMETRY_PREDICATES:
            method_name = BINARY_GEOMETRY_PREDICATES[operation]
            bounded_method = getattr(this, method_name)
            result = bounded_method(other)
            return make_predicate_result(result)

        elif operation in BINARY_GEOMETRY_METHODS:
            method_name = BINARY_GEOMETRY_METHODS[operation]
            bounded_method = getattr(this, method_name)
            result = bounded_method(other)
            return make_predicate_result(result)

        elif operation in BINARY_TOPOLOGICAL_METHODS:
            method_name = BINARY_TOPOLOGICAL_METHODS[operation]
            bounded_method = getattr(this, method_name)
            result = bounded_method(other)
            return make_response_from_geometry(result, args.format)

        else:
            raise InvalidGeometryOperator(operation)


class MixedGeometryOperation(GeometryOperationBase, BaseResource):
    def get(self, key, operation):
        """ Unary operation on stored geometry

            GET /geometries/<key>/operation
        """
        if operation not in UNARY_OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid unary operation :"%s"' % operation)

        feature = self.model.get_feature(key)
        return self._process(operation, feature.geometry)

    def post(self, key, operation):
        """ Binary operation on stored geometry and posted geometry
            POST /geometries/<this>/operation
            DATA <other>
        """
        if operation not in BINARY_OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid binary operation :"%s"' % operation)

        this_geometry = self.model.get_feature(key).geometry
        other_geometry = build_geometry(request.data, srid=4326)

        return self._process(operation, this_geometry, other_geometry)


class BinaryGeometryOperation(GeometryOperationBase, BaseResource):
    def get(self, this, operation, other):
        """ Binary operation on stored geometries
            GET /geometries/<this>/operation/<other>
        """
        if operation not in BINARY_OPERATIONS:
            raise InvalidGeometryOperator(
                'Invalid binary operation :"%s"' % operation)

        if this == other:
            raise IdentialGeometryError('Given geometries are identical')

        this_geometry = self.model.get_feature(this).geometry
        other_geometry = self.model.get_feature(other).geometry

        return self._process(operation, this_geometry, other_geometry)


class MixedPostGeometryOperation(GeometryOperationBase, BaseResource):
    def post(self, operation):
        if operation in UNARY_OPERATIONS:
            geometry = build_geometry(request.data)
            return self._process(operation, geometry)

        elif operation in BINARY_OPERATIONS:
            geometry_collection = build_geometry(request.data)
            if geometry_collection.geom_typeid < 7:
                raise InvalidGeometry(
                    'Requires a GeometryCollection, got "%s" instead' % geometry_collection.geo_type)

            if geometry_collection.num_geom != 2:
                raise InvalidGeometry(
                    'GeometryCollection, should contain 2 geometries, got %d',
                    geometry_collection.num_geom)
            this_geometry = geometry_collection[0]
            other_geometry = geometry_collection[1]
            return self._process(operation, this_geometry, other_geometry)

        else:
            raise InvalidGeometryOperator(
                'Invalid geometry operation :"%s"' % operation)




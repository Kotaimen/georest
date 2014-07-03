# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/19/14'

"""
    georest.model.operations
    ~~~~~~~~~~~~~~~~~~~~~~~~
    thin operation wrapper/mapper for georest.geo.operations
"""

from collections import namedtuple
from .. import geo
from ..geo import operations as ops
from ..geo import jsonhelper as json
from .exceptions import NoSuchOperation, BadInvoke


OPERATION_MAPPING = dict(
    area=ops.Area,
    length=ops.Length,
    is_simple=ops.IsSimple,
    buffer=ops.Buffer,
    convex_hull=ops.ConvexHull,
    envelope=ops.Envelope,
    parallel_offset=ops.ParallelOffset,
    simplify=ops.Simplify,
    boundary=ops.Boundary,
    centroid=ops.Centroid,
    point_on_surface=ops.PointOnSurface,
    distance=ops.Distance,
    equals=ops.Equals,
    contains=ops.Contains,
    crosses=ops.Crosses,
    disjoint=ops.Disjoint,
    intersects=ops.Intersects,
    touches=ops.Touches,
    within=ops.Within,
    intersection=ops.Intersection,
    difference=ops.Difference,
    symmetric_difference=ops.SymmetricDifference,
    union=ops.Union,
)

ATTRIBUTE_MAPPING = dict((k, v) for k, v in OPERATION_MAPPING.items() if
                         (issubclass(v, ops.UnaryOperation) and
                          not v.RESULT_TYPE is geo.Geometry))

GEOM_TYPE_ATTRIBUTES_MAPPING = {
    'Point': [],
    'LineString': ['length'],
    'Polygon': ['area'],
    'MultiPoint': [],
    'MultiLineString': ['length'],
    'MultiPolygon': ['area'],
    'GeometryCollection': [],
}


class OperationResult(namedtuple('OperationResult', ['value', 'is_pod'])):
    """operation result capsulation"""
    __slots__ = ()

    def json(self):
        """json representation of the result"""
        if self.is_pod:
            return json.dumps({'result': self.value})
        else:
            return self.value.geojson


class OperationsModel(object):
    """high-level operation model

    This model wraps georest.geo.operations, provide ways to invoke, inspect
    operations for view.
    """
    def __init__(self):
        self.operations = OPERATION_MAPPING

    def describe(self):
        """list useful informations for this model here"""
        return {
            'operations': list(self.operations)
        }

    def describe_operation(self, op_name):
        op = self.operations.get(op_name, None)
        if not op:
            raise NoSuchOperation('Cannot find op %s' % op_name)

        return {'name': op_name, 'doc': getattr(op, '__doc__', None)}

    def invoke(self, op_name, *args, **kwargs):
        """invoke an operation

        :param op_name: name of the operation
        :param args: list of geometry objects
        :param kwargs: operation arguments
        :raises NoSuchOperation: when operation is not found
        :rtype: OperationResult
        """
        op = self.operations.get(op_name, None)
        if not op:
            raise NoSuchOperation('Cannot find op %s' % op_name)

        l_args = len(args)
        if l_args <= 0:
            raise BadInvoke('invoking %s with zero args' % op_name)

        if issubclass(op, ops.UnaryOperation) and l_args != 1:
            raise BadInvoke('invoking unary operation %s with %d args'
                            % (op_name, l_args))

        if issubclass(op, ops.BinaryOperation) and l_args != 2:
            raise BadInvoke('invoking binary operation %s with %d args'
                            % (op_name, l_args))

        value = op(**kwargs)(*args)
        is_pod = not op.RESULT_TYPE is geo.Geometry
        return OperationResult(value, is_pod)


class AttributesModel(object):
    """high level abstraction of geometry attributes"""
    def __init__(self):
        self.operations = ATTRIBUTE_MAPPING

    def attributes(self, geometry, includes=None, excludes=None, **kwargs):
        """Expose interesting attributes of the geometry"""
        includes = set(includes) if includes else set()
        excludes = set(excludes) if excludes else set()
        default_keys = set(GEOM_TYPE_ATTRIBUTES_MAPPING[geometry.geom_type])
        keys = (default_keys | includes) - excludes

        result = {}

        for key in keys:
            try:
                result[key] = self._get_attribute(geometry, key, **kwargs)
            except NoSuchOperation:
                pass
        return json.dumps(result)

    def _get_attribute(self, geometry, key, **kwargs):
        op = self.operations.get(key, None)
        if not op:
            raise NoSuchOperation('Cannot find attribute %s' % op)

        value = op(**kwargs)(geometry)
        return value

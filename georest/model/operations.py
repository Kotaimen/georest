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
from .exceptions import NoSuchOperation


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
    def __init__(self):
        self.operations = OPERATION_MAPPING

    def describe(self):
        """list useful informations for this model here"""
        return {
            'operations': list(self.operations)
        }

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

        value = op(**kwargs)(*args)
        return OperationResult(value, not isinstance(value, geo.Geometry))

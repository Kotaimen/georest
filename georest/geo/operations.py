# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/12/14'

"""
    georest.geo.operations
    ~~~~~~~~~~~~~~~~~~~~~~
    Wraps every geometry operation in its own functor class, thus being very
    naive and stupid.

    All operator parameters are set in the CTOR and only accept geometries
    in the `__call__` operator.  Basic type conversion and validation is
    also done in the CTOR, so we can simply pass `request.args` into the
    operator.

    Geometry parameters are never modified but may returned as result if
    no computation is required.

    Design note:

    We can implement this using pythonic method like dynamic bounded method
    lookup, but chose not to since this is more friendly to unit testing.
    However, operation parameter handling is still implemented in a clever,
    twisted, cruel, wild, pythonic metaprogrammingish way to save typing :)
"""

import six
import shapely.geometry.base

from .geometry import Geometry
from .exceptions import GeoException, OperationError, InvalidParameter
from .spatialref import CoordinateTransform, SpatialReference

__all__ = ['UnaryOperation', 'Attribute', 'UnaryPredicate',
           'UnaryConstructor',
           'Area', 'Length', 'IsSimple', 'Buffer',
           'ConvexHull', 'Envelope', 'ParallelOffset',
           'Simplify', 'Boundary', 'PointOnSurface', 'Centroid',
           'BinaryOperation',
           'Equals', 'Contains', 'Crosses', 'Disjoint', 'Intersects',
           'Touches', 'Within',
           'Intersection', 'SymmetricDifference', 'Difference', 'Union',
]

#
# Base classes
#

class BaseOperation(object):
    """Base geometry operation, being a multi geometry operation"""

    DEBUG = True

    def __init__(self, **kwargs):
        """Create the operator, if `srid` is provided, geometry will be
        transformed to given CRS before the actual operation is called.

        Note if given `srid` is identical the geometry, `CoordinateTransform`
        will not return a new copied geometry object to save time.
        """
        try:
            self._srid = kwargs.pop('srid')
        except KeyError:
            self._srid = None
        # any left args is assumed to be used by actual operator
        self._kwargs = kwargs

    def __call__(self, *geometries):
        assert all(Geometry.is_geometry(g) for g in geometries)

        if self._srid:
            # need do crs transform before performing operation
            geometries = tuple(self._transform_crs(geometries))
            result_crs = SpatialReference(self._srid)
        else:
            result_crs = self._check_crs(geometries)

        # call implementation, catch all exception and raise as 500 error
        try:
            result = self._impl(*geometries)
        except GeoException as e:
            raise
        except Exception as e:
            if self.DEBUG:
                raise
            else:
                raise OperationError(e=e)

        if isinstance(result, shapely.geometry.base.BaseGeometry):
            # update spatial reference
            result = Geometry.build_geometry(result,
                                             srid=result_crs.srid,
                                             empty_check=False)

        return result

    def _transform_crs(self, geometries):
        for geometry in geometries:
            geom_crs = geometry.crs
            if not geom_crs:
                raise InvalidParameter(
                    'Requires all geometries have CRS defined')
            result_crs = SpatialReference(self._srid)
            transform = CoordinateTransform.build_transform(geom_crs,
                                                            result_crs)
            yield transform(geometry)

    def _check_crs(self, geometries):
        if not any(bool(g.crs) for g in geometries):
            # if all geometries have undefined CRS or unassigned CRS
            # we assume you know what you are doing
            return SpatialReference(srid=0)
        elif len(set(g.crs.srid for g in geometries)) > 1:
            # but in any case you can't mix different CRS
            raise InvalidParameter('Cannot operate on mixed CRS')
        else:
            return SpatialReference(geometries[0].crs.srid)


class UnaryOperation(BaseOperation):
    """Base unary geometry operation"""

    def __call__(self, this):
        """Accepts a single geometry, and call underlying implement"""
        return BaseOperation.__call__(self, this)

    def _impl(self, this):
        """By default, be a good coordinate transformer"""
        return this


class Attribute(UnaryOperation):
    """Geometry attributes returns a float/int/string"""
    pass


class UnaryPredicate(UnaryOperation):
    """Accepts a geometry and returns bool"""
    pass


class UnaryConstructor(UnaryOperation):
    """Accepts a geometry and optional parameters,
    returns a new geometry"""
    pass


class UnarySetTheoreticMethod(UnaryOperation):
    pass


class AffineTransform(UnaryOperation):
    pass


class BinaryOperation(BaseOperation):
    """Base binary geometry operation"""

    def __call__(self, this, other):
        """Accepts two geometries, and call underlying implement """
        return BaseOperation.__call__(self, this, other)

    def _impl(self, this, other):
        raise NotImplementedError


class BinaryPredicate(BinaryOperation):
    """Accepts two geometries and returns bool"""
    pass


class BinarySetTheoreticMethod(BinaryOperation):
    """Binary set-theoretic methods"""
    pass


class LineReference(BinaryOperation):
    pass


class MultiGeometryOperation(BaseOperation):
    pass


class ParameterHelper(object):
    """Very simple parameter validator"""

    def __init__(self, args):
        self._args = args

    def update_kwargs(self, kwargs, local):
        """Merge kwargs from given locals using valid args"""
        kwargs = kwargs.copy()
        for name in self._args:
            kwargs[name] = local[name]
        return kwargs

    def extract_kwargs(self, kwargs):
        """Extract valid args from kwargs, so we can ignore any extra
        arguments before call actual geometry operators"""
        args = dict()
        for name in self._args:
            args[name] = kwargs[name]
        return args

    def check_float(self, **kwargs):
        assert len(kwargs) == 1
        name, value = kwargs.popitem()

        if isinstance(value, six.string_types):
            try:
                return float(value)
            except ValueError as e:
                raise InvalidParameter('%s is not a float: "%r"' % \
                                       (name, value), e=e)
        elif isinstance(value, float):
            return value
        else:
            raise InvalidParameter('%s must be a float, got "%r"' % \
                                   (name, value))

    def check_integer(self, **kwargs):
        assert len(kwargs) == 1
        name, value = kwargs.popitem()
        if isinstance(value, six.string_types):
            try:
                return int(value)
            except ValueError as e:
                raise InvalidParameter(
                    '%s is not an integer: "%r"' % (name, value), e=e)
        elif isinstance(value, int):
            return value
        else:
            raise InvalidParameter(
                '%s must be an integer, got "%r"' % (name, value))

    def check_boolean(self, **kwargs):
        assert len(kwargs) == 1
        name, value = kwargs.popitem()
        if isinstance(value, six.string_types):
            if value.lower() in ['1', 'true']:
                return True
            elif value.lower() in ['0', 'false']:
                return False
            else:
                raise InvalidParameter(
                    '%s must be a boolean value, got "%s"' % (name, value))
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)

    def check_range(self, low=0., high=65535., **kwargs):
        assert len(kwargs) == 1
        name, value = kwargs.popitem()
        if value < low or value > high:
            raise InvalidParameter('%s must between %r, %r' % \
                                   (name, low, high))

    def check_open_range(self, low=0., high=65535., **kwargs):
        assert len(kwargs) == 1
        name, value = kwargs.popitem()
        if value <= low or value >= high:
            raise InvalidParameter('%s must between %r, %r' % \
                                   (name, low, high))


    def check_choices(self, choices=None, **kwargs):
        assert len(kwargs) == 1
        assert choices is not None
        name, value = kwargs.popitem()
        if value not in choices:
            raise InvalidParameter('%s must be one of %r, got "%r"' % \
                                   (name, choices, value))

    def check_geometry_type_is(self, geometry, *choices):
        if geometry.geom_type not in choices:
            raise InvalidParameter('Expecting one of %r instead of a %r' % (
                choices, geometry.geom_type))

    def check_geometry_type_is_not(self, geometry, *choices):
        if geometry.geom_type in choices:
            raise InvalidParameter('None of %r is allowed but got a %r' % (
                choices, geometry.geom_type))


class Area(Attribute):
    def _impl(self, this):
        return this.area


class Length(Attribute):
    def _impl(self, this):
        return this.length


class IsSimple(UnaryPredicate):
    def _impl(self, this):
        return this.is_simple


class Buffer(UnaryConstructor, ParameterHelper):
    def __init__(self, distance, resolution=16,
                 cap_style='round', join_style='round',
                 mitre_limit=1.0, **kwargs):
        ParameterHelper.__init__(self, ['distance', 'resolution', 'cap_style',
                                        'join_style', 'mitre_limit'])

        distance = self.check_float(distance=distance)
        resolution = self.check_integer(resolution=resolution)
        mitre_limit = self.check_float(mitre_limit=mitre_limit)

        self.check_range(resolution=resolution, low=1, high=100)
        self.check_range(mitre_limit=mitre_limit, low=0., high=100.0)

        self.check_choices(cap_style=cap_style,
                           choices=['round', 'flat', 'square'])
        self.check_choices(join_style=join_style,
                           choices=['round', 'mitre', 'bevel'])

        cap_style = getattr(shapely.geometry.CAP_STYLE, cap_style)
        join_style = getattr(shapely.geometry.JOIN_STYLE, join_style)

        kwargs = self.update_kwargs(kwargs, locals())
        super(Buffer, self).__init__(**kwargs)

    def _impl(self, this):
        kwargs = self.extract_kwargs(self._kwargs)
        return this.buffer(**kwargs)


class ConvexHull(UnaryConstructor):
    def _impl(self, this):
        return this.convex_hull


class Envelope(UnaryConstructor):
    def _impl(self, this):
        return this.envelope


class ParallelOffset(UnaryConstructor, ParameterHelper):
    def __init__(self, distance, side='left', resolution=16, join_style='round',
                 mitre_limit=1.0, **kwargs):
        ParameterHelper.__init__(self, ['distance', 'side', 'resolution',
                                        'join_style', 'mitre_limit'])
        distance = self.check_float(distance=distance)
        resolution = self.check_integer(resolution=resolution)
        mitre_limit = self.check_float(mitre_limit=mitre_limit)

        self.check_range(resolution=resolution, low=1, high=100)
        self.check_range(mitre_limit=mitre_limit, low=0., high=100.0)
        self.check_choices(side=side,
                           choices=['left', 'right'])
        self.check_choices(join_style=join_style,
                           choices=['round', 'mitre', 'bevel'])

        join_style = getattr(shapely.geometry.JOIN_STYLE, join_style)

        kwargs = self.update_kwargs(kwargs, locals())
        super(ParallelOffset, self).__init__(**kwargs)

    def _impl(self, this):
        self.check_geometry_type_is(this, 'LineString', 'MultiLineString')
        kwargs = self.extract_kwargs(self._kwargs)
        return this.parallel_offset(**kwargs)


class Simplify(UnaryConstructor, ParameterHelper):
    def __init__(self, tolerance, preserve_topology=False, **kwargs):
        ParameterHelper.__init__(self, ['tolerance', 'preserve_topology'])

        tolerance = self.check_float(tolerance=tolerance)
        self.check_open_range(tolerance=tolerance, low=0., high=1.)
        preserve_topology = self.check_boolean(
            preserve_topology=preserve_topology)

        kwargs = self.update_kwargs(kwargs, locals())
        super(Simplify, self).__init__(**kwargs)

    def _impl(self, this):
        kwargs = self.extract_kwargs(self._kwargs)
        return this.simplify(**kwargs)


class Boundary(UnarySetTheoreticMethod, ParameterHelper):
    def _impl(self, this):
        return this.boundary


class Centroid(UnarySetTheoreticMethod):
    def _impl(self, this):
        return this.centroid


class PointOnSurface(UnarySetTheoreticMethod):
    def _impl(self, this):
        return this.representative_point()


class Equals(BinaryPredicate, ParameterHelper):
    def __init__(self, decimal=6, **kwargs):
        ParameterHelper.__init__(self, ['decimal'])
        decimal = self.check_integer(decimal=decimal)
        self.check_range(decimal=decimal, low=0, high=16)

        kwargs = self.update_kwargs(kwargs, locals())
        super(Equals, self).__init__(**kwargs)

    def _impl(self, this, other):
        kwargs = self.extract_kwargs(self._kwargs)
        return this.almost_equals(other, **kwargs)


class Contains(BinaryPredicate):
    def _impl(self, this, other):
        return this.contains(other)


class Crosses(BinaryPredicate):
    def _impl(self, this, other):
        return this.crosses(other)


class Disjoint(BinaryPredicate):
    def _impl(self, this, other):
        return this.disjoint(other)


class Intersects(BinaryPredicate):
    def _impl(self, this, other):
        return this.intersects(other)


class Touches(BinaryPredicate):
    def _impl(self, this, other):
        return this.touches(other)


class Within(BinaryPredicate):
    def _impl(self, this, other):
        return this.within(other)


class Intersection(BinarySetTheoreticMethod):
    def _impl(self, this, other):
        return this.intersection(other)


class Difference(BinarySetTheoreticMethod):
    def _impl(self, this, other):
        return this.difference(other)


class SymmetricDifference(BinarySetTheoreticMethod):
    def _impl(self, this, other):
        return this.symmetric_difference(other)


class Union(BinarySetTheoreticMethod):
    def _impl(self, this, other):
        return this.union(other)


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

    Geometry parameters are never modified but may be returned as result if
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


class BaseOperation(object):
    """Base geometry operation"""

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


class UnaryOperation(BaseOperation):
    """Base unary geometry operation"""

    def __call__(self, this):
        """Accepts a single geometry, being a good functor and call underlying
        implement"""
        assert Geometry.is_geometry(this)

        # coordinate transform
        this_crs = this._crs
        if self._srid and this_crs:
            result_crs = SpatialReference(self._srid)
            transform = CoordinateTransform.build_transform(this_crs,
                                                            result_crs)
            this = transform(this)
        else:
            result_crs = None

        # call implementation, catch all exception and raise as 500 error
        try:
            result = self._impl(this)
        except GeoException as e:
            raise
        except Exception as e:
            if self.DEBUG:
                raise
            else:
                raise OperationError(e=e)

        if Geometry.is_geometry(result):
            # update spatial reference
            result_crs = result_crs if result_crs else this_crs

        return result

    def _impl(self, this):
        """By default, be a good coordinate transformer"""
        return this


class BinaryOperation(BaseOperation):
    """Base binary geometry operation"""

    def __call__(self, this, other):
        """Accepts two geometries, and call underlying implement """
        assert Geometry.is_geometry(this)
        assert Geometry.is_geometry(other)

        # coordinate transform
        if self._srid:
            transform1 = CoordinateTransform.build_transform(this._crs,
                                                             self._srid)
            transform2 = CoordinateTransform.build_transform(other._crs,
                                                             self._srid)

            this = transform1(this)
            other = transform2(other)

        # call implementation
        try:
            result = self._impl(this, other)
        except GeoException as e:
            raise
        except Exception as e:
            if self.DEBUG:
                raise
            else:
                raise OperationError(e=e)

        if Geometry.is_geometry(result):
            # update spatial reference
            result._crs = SpatialReference(srid=self._srid)

        return result


    def _impl(self, this, other):

        raise NotImplementedError


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

    def check_geometry_type(self, geometry, choices=None):
        if geometry.geom_type not in choices:
            raise InvalidParameter(
                'Got "%s" instead of a %r' % (geometry.geom_type, choices))


class Attributes(UnaryOperation):
    """Geometry attributes returns a float/int/string"""
    pass


class Area(Attributes):
    def _impl(self, this):
        return this.area


class Length(Attributes):
    def _impl(self, this):
        return this.length


class UnaryPredicate(UnaryOperation):
    """Accepts a geometry and returns bool"""
    pass


class IsSimple(UnaryPredicate):
    def _impl(self, this):
        return this.is_simple


class UnaryConstructor(UnaryOperation):
    """Accepts a geometry and optional parameters,
    returns a new geometry"""
    pass


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
        kwargs = self.extract_kwargs(self._kwargs)
        return this.paraell_offset(**kwargs)


class Simplify(UnaryConstructor, ParameterHelper):
    def __init__(self, tolerance, preserve_topology=True, **kwargs):
        ParameterHelper.__init__(self, ['tolerance', 'preserve_topology'])

        tolerance = self.check_float(tolerance=tolerance)
        self.check_open_range(tolerance=tolerance, low=0., high=1.)
        preserve_topology = self.check_boolean(
            preserve_topology=preserve_topology)

        kwargs = self.update_kwargs(kwargs, locals())
        super(Buffer, self).__init__(**kwargs)

    def _impl(self, this):
        kwargs = self.extract_kwargs(self._kwargs)
        return this.simplify(**kwargs)

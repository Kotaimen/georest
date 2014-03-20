# -*- encoding: utf-8 -*-

"""
    Geometry object
    ~~~~~~~~~~~~~~~
"""
__author__ = 'kotaimen'
__date__ = '3/19/14'

from .engine import geos, gdal
from .exception import GeoException, InvalidGeometry, \
    InvalidCoordinateReferenceSystem

import six

#
# Geometry
#

class Geometry(object):
    """ Geometry object

        Contains geometry coordinate data and coordinate reference system
    """

    def __init__(self, the_geom):
        assert (isinstance(the_geom, geos.GEOSGeometry))
        self._the_geom = the_geom


    def __getattr__(self, name):
        """
            Pretend to be a geos.Geometry instance without much coding
        """
        # XXX: Violates DIP but much less coding
        # XXX: I like dynamic languages
        try:
            ret = getattr(self._the_geom, name)
        except Delegation.ENGINE_EXCEPTIONS as e:
            raise GeoException(e)

        if six.callable(ret):
            return Delegation(ret)
        else:
            return Delegation.type_guard(ret)

    def __repr__(self):
        return 'Geometry( %s )' % self._the_geom.wkt


class Delegation(object):
    """
        Delegate the callable and swap result GEOSGeometry back to Geometry
        when necessary
    """
    ENGINE_EXCEPTIONS = (geos.GEOSException,
                         gdal.OGRException, gdal.SRSException)

    @staticmethod
    def type_guard(ret):
        if isinstance(ret, geos.GEOSGeometry):
            return Geometry(ret)
        elif isinstance(ret, gdal.SpatialReference):
            # XXX: Also warps SpatialReference?
            raise NotImplementedError
        else:
            return ret

    def __init__(self, target):
        self._target = target

    def __call__(self, *args, **kwargs):
        try:
            ret = self._target(*args, **kwargs)
        except self.ENGINE_EXCEPTIONS as e:
            raise GeoException(e)

        return self.type_guard(ret)

#
# Factory method
#

ALLOWED_GEOMETRY_TYPES = frozenset(['Point',
                                    'LineString',
                                    'Polygon',
                                    'MultiPoint',
                                    'MultiLineString',
                                    'MultiPolygon'])


def build_geometry(geo_input, srid=None):
    try:
        geom = geos.GEOSGeometry(geo_input, srid)
    except (TypeError, ValueError, geos.GEOSException) as e:
        raise InvalidGeometry(e)

    if not geom.valid:
        raise InvalidGeometry(geom.valid_reason)

    if geom.srid is not None and geom.crs is None:
        raise InvalidCoordinateReferenceSystem('Invalid srid "%s"' % geom.srid)

    if geom.geom_type not in ALLOWED_GEOMETRY_TYPES:
        raise InvalidGeometry('Invalid geometry type "%s"' % geom.geom_type)

    return Geometry(geom)


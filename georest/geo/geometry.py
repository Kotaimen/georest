# -*- encoding: utf-8 -*-

"""
    georest.geo.geometry
    ~~~~~~~~~~~~~~~~~~~~

"""
__author__ = 'kotaimen'
__date__ = '3/19/14'

import six

from .engine import geos, gdal
from .exception import GeoException, InvalidGeometry, \
    InvalidCRS


#
# Geometry
#

class Geometry(object):
    """ Wrapper for Geometry object

    Contains geometry coordinate? data and coordinate reference system
    """

    def __init__(self, the_geom):
        assert (isinstance(the_geom, geos.GEOSGeometry))
        self._the_geom = the_geom

    @property
    def the_geom(self):
        return self._the_geom

    def __len__(self):
        return len(self._the_geom)

    def __getitem__(self, key):
        return Delegation.type_guard(self._the_geom[key])

    def __getattr__(self, name):
        """Pretend to be a geos.Geometry instance without much coding"""
        # Violates DIP but much less typing (I like dynamic languages)
        try:
            ret = getattr(self._the_geom, name)
        except Delegation.ENGINE_EXCEPTIONS as e:
            raise GeoException(e=e)

        if six.callable(ret):
            return Delegation(ret)
        else:
            return Delegation.type_guard(ret)

    def __repr__(self):
        return 'Geometry(%s)' % self._the_geom.ewkt

    def __getstate__(self):
        return bytes(self._the_geom.ewkb)

    def __setstate__(self, state):
        self._the_geom = geos.GEOSGeometry(buffer(state))


class SpatialReference(object):
    """
        Wrapper for spatial reference system object
    """

    def __init__(self, srs):
        assert isinstance(srs, gdal.SpatialReference)
        self._the_srs = srs

    @property
    def srs(self):
        return self._the_srs

    @property
    def crs(self):
        return self._the_srs

    def __getattr__(self, name):
        try:
            ret = getattr(self._the_srs, name)
        except Delegation.ENGINE_EXCEPTIONS as e:
            raise GeoException(e=e)

        if six.callable(ret):
            return Delegation(ret)
        else:
            return Delegation.type_guard(ret)

    def __repr__(self):
        return 'SpatialReference(%s)' % self._the_srs.name

    def __getstate__(self):
        return self._the_srs.wkt

    def __setstate__(self, state):
        self._the_srs = gdal.SpatialReference(state)


class Delegation(object):
    """
        Delegate the callable and swap result GEOSGeometry back to Geometry
        when necessary
    """
    ENGINE_EXCEPTIONS = (geos.GEOSException,
                         gdal.OGRException,
                         gdal.SRSException)

    @staticmethod
    def type_guard(ret):
        if isinstance(ret, geos.GEOSGeometry):
            return Geometry(ret)
        elif isinstance(ret, gdal.OGRGeometry):
            return Geometry(ret.ewkb)
        elif isinstance(ret, gdal.SpatialReference):
            return SpatialReference(ret)
        else:
            return ret

    def __init__(self, target):
        self._target = target

    def __call__(self, *args, **kwargs):
        try:
            ret = self._target(*args, **kwargs)
        except self.ENGINE_EXCEPTIONS as e:
            raise GeoException(e=e)

        return self.type_guard(ret)


#
# Factory method
#

def build_srs(srsinput):
    """
        Build a spatial reference system
    """
    try:
        srs = gdal.SpatialReference(srs_input=srsinput)
    except (ValueError, gdal.SRSException, gdal.OGRException) as e:
        raise InvalidCRS(e=e)

    return SpatialReference(srs)


ALLOWED_GEOMETRY_TYPES = frozenset(['Point',
                                    'LineString',
                                    'Polygon',
                                    'MultiPoint',
                                    'MultiLineString',
                                    'MultiPolygon',
                                    'GeometryCollection'])


def build_geometry(geoinput, srid=4326):
    """

    :param geoinput: geometry data, can be one of:
         * strings:
            - WKT
            - HEXEWKB (a PostGIS-specific canonical form)
            - GeoJSON (requires GDAL)
         * buffer:
            - WKB
    :param srid: SRID of the geometry
    :return: created geometry
    """

    # NOTE: Wrapping GEOS Geometry here, which does not support CRS, just SRID
    if srid is not None and not isinstance(srid, int):
        raise InvalidCRS('CRS Must be SRID integer')

    try:
        geom = geos.GEOSGeometry(geoinput, srid=srid)
    except (TypeError, ValueError, geos.GEOSException, gdal.OGRException) as e:
        raise InvalidGeometry(e=e)

    if not geom.valid:
        raise InvalidGeometry('Invalid geometry: %s' % geom.valid_reason)

    if geom.empty:
        raise InvalidGeometry('Empty geometry')

    if geom.srid is not None and geom.crs is None:
        raise InvalidCRS('Invalid srid "%s"' % geom.srid)

    if geom.geom_type not in ALLOWED_GEOMETRY_TYPES:
        raise InvalidGeometry('Invalid geometry type "%s"' % geom.geom_type)

    return Geometry(geom)




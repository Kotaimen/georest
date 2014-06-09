# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/5/14'

"""
    georest.geo.spatialref
    ~~~~~~~~~~~~~~~~~~~~~~
    Spatial Reference

"""

import functools

import pyproj
import shapely.ops

from .exceptions import InvalidSpatialReference, CoordinateTransformationError


class SpatialReference(object):
    """Spatial reference wrapper

    In case we replace pyproj to use osgeo.osr.SpatialReference, but not
    simulating osgeo.osr.SpatialReference's mighty interface here....

    Pyproj sucks... but apparently it doesn't require GDAL, and directly
    supports shapely's transform interface without convert to geometry to
    osgro.ogr.OGRGeometry.
    """

    def __init__(self, srid=0):
        assert isinstance(srid, int)
        self._srid = srid
        try:
            self._proj = pyproj.Proj(init='EPSG:%d' % self._srid)
        except RuntimeError as e:
            raise InvalidSpatialReference(e=e)

    @property
    def proj(self):
        return self._proj

    @property
    def srid(self):
        return self._srid

    @property
    def geojson(self):
        if self._srid == 0:
            return None
        else:
            return {'type': 'name',
                    'properties': {
                        'name': 'EPSG:%d' % self._srid
                    }}

    def equals(self, other):
        return self._srid == other._srid


class CoordinateTransform(object):
    def __init__(self, crs1, crs2):
        assert isinstance(crs1, SpatialReference)
        assert isinstance(crs2, SpatialReference)
        self._crs1 = crs1
        self._crs2 = crs2
        self._projection = functools.partial(pyproj.transform,
                                             crs1.proj, crs2.proj)

    def __call__(self, geometry):
        if geometry.geom_type == 'GeometryCollection':
            # XXX shapely don't support transform GeometryCollection"
            raise CoordinateTransformationError(
                message='GeometryCollection is not supported')
        try:
            return shapely.ops.transform(self._projection, geometry)
        except RuntimeError as e:
            raise CoordinateTransformationError(e=e)

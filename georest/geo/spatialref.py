# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/5/14'

"""
    georest.geo.spatialref
    ~~~~~~~~~~~~~~~~~~~~~~
    Spatial Reference

"""

import functools
import re

import pyproj
import shapely.ops

from .exceptions import InvalidSpatialReference, CoordinateTransformationError


class SpatialReference(object):
    """Spatial reference wrapper

    In case we replace pyproj to use osgeo.osr.SpatialReference, but not
    simulating osgeo.osr.SpatialReference's mighty interface here....
    """

    def __init__(self, srid=0):
        assert isinstance(srid, int)
        self._srid = srid
        self._proj = self._make_proj(srid)

    @staticmethod
    def _make_proj(srid):
        try:
            return pyproj.Proj(init='EPSG:%d' % srid)
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

    @staticmethod
    def build_from_geojson_crs(crs):
        if crs is None:
            return None

        if not isinstance(crs, dict):
            raise InvalidSpatialReference('Not a valid GeoJSON CRS')

        try:
            if crs['type'] != 'name':
                raise InvalidSpatialReference(
                    message='Only supports named CRS')
            match = re.match(r'^EPSG:(?P<srid>\d+)$',
                             crs['properties']['name'],
                             re.I)
        except KeyError:
            raise InvalidSpatialReference('Not a valid GeoJSON CRS')

        if match:
            return SpatialReference(srid=int(match.group('srid')))
        else:
            raise InvalidSpatialReference('Only supports EPSG:SRID')

    def equals(self, other):
        return self._srid == other._srid

    def __str__(self):
        return 'SpatialReference(srid=%d)' % self._srid

    def __getstate__(self):
        return self._srid

    def __setstate__(self, state):
        srid = state
        self._srid = srid
        self._proj = self._make_proj(srid)


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
            # XXX shapely don't support transform GeometryCollection
            raise CoordinateTransformationError(
                message='GeometryCollection is not supported')
        try:
            return shapely.ops.transform(self._projection, geometry)
        except RuntimeError as e:
            raise CoordinateTransformationError(e=e)

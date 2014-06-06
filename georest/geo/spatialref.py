# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/5/14'

"""
    georest.geo.spatialref
    ~~~~~~~~~~~~~~~~~~~~~~
    Spatial Reference

"""

import pyproj

from .exceptions import InvalidSpatialReference


class SpatialReference(object):
    """Spatial reference wrapper

    In case we replace pyproj to use osgeo.osr.SpatialReference, but not
    simulating osgeo.osr.SpatialReference's mighty interface here....

    Pyproj sucks... but apparently it doesn't require GDAL, and directly
    supports shapely's transform interface without convert to geometry to
    osgro.ogr.OGRGeometry.
    """

    def __init__(self, srid=0, lazy_init=False):
        assert isinstance(srid, int)
        self._srid = srid
        self._proj = None
        self.proj

    @property
    def proj(self):
        if self._srid != 0 and self._proj is None:
            try:
                self._proj = pyproj.Proj(init='EPSG:%d' % self._srid)
            except RuntimeError as e:
                raise InvalidSpatialReference(e=e)
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

# XXX: transform?

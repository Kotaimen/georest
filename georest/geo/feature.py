# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/29/14'

"""
    georest.geo.feature
    ~~~~~~~~~~~~~~~~~~~
    Geo Feature object

"""

import collections
import pyproj
import shapely.geometry.base
import geojson
import ujson

from .key import Key
from .geometry import SpatialReference, Geometry
from .metadata import Metadata


class Feature(object):
    """ A Geometry with optional properties and SRS."""

    def __init__(self, key, geometry, crs, properties, metadata):
        assert isinstance(key, Key)
        assert isinstance(geometry, shapely.geometry.base.BaseGeometry)
        assert isinstance(crs, SpatialReference)
        assert isinstance(metadata, Metadata)

        self._geometry = geometry
        self._properties = properties
        self._key = key
        self._crs = crs
        self._metadata = metadata

    @property
    def geometry(self):
        return self._geometry

    @property
    def properties(self):
        return self._properties

    @property
    def key(self):
        return self._key

    @property
    def crs(self):
        return self._crs

    @property
    def metadata(self):
        return self._metadata

    @property
    def __geo_interface__(self):
        obj = dict(type='Feature',
                   geometry=self._geometry,
                   properties=self._properties,
                   crs=self._crs.geojson,
                   id=self._key)
        obj.update(self._metadata)
        return obj

    @property
    def geojson(self):
        return ujson.dumps(self.__geo_interface__)


    @staticmethod
    def build_from_geometry(geoinput, key=None, srid=4326):
        raise NotImplementedError

    @staticmethod
    def build_from_geojson(geoinput, key=None, srid=4326):
        raise NotImplementedError



# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/29/14'

"""
    georest.geo.feature
    ~~~~~~~~~~~~~~~~~~~
    Geo Feature object

"""

import shapely.geometry.base
import geojson.base
import ujson as json

from .key import Key
from .geometry import Geometry
from .spatialref import SpatialReference
from .metadata import Metadata
from .exceptions import InvalidFeature, InvalidProperties, InvalidGeoJsonInput


class Feature(object):
    """ A Geo Feature with optional properties and SRS."""

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
        return dict(type='Feature',
                    geometry=shapely.geometry.mapping(self._geometry),
                    properties=self._properties,
                    crs=self._crs.geojson,
                    id=self._key)

    @property
    def geojson(self):
        return json.dumps(self.__geo_interface__)

    @staticmethod
    def make_from_geometry(geo_input, key=None, srid=4326, properties=None):
        geometry = Geometry.make_geometry(geo_input, srid=srid)
        metadata = Metadata.make_metadata(geometry=geometry)

        if key is None:
            key = Key.make_key()

        if properties is None:
            properties = dict()

        crs = geometry._crs
        assert crs is not None

        return Feature(key, geometry, crs, properties, metadata)

    @staticmethod
    def make_from_geojson(geo_input, key=None, srid=4326):
        if isinstance(geo_input, (str, unicode)):
            try:
                literal = json.loads(geo_input)
            except (KeyError, ValueError) as e:
                raise InvalidGeoJsonInput(e)
        elif isinstance(geo_input, dict):
            literal = geo_input

        try:
            geojson_feature = geojson.base.GeoJSON.to_instance(literal)
        except (TypeError, ValueError) as e:
            raise InvalidFeature(message="Invalid feature", e=e)

        geometry = Geometry.make_geometry(geojson_feature['geometry'],
                                          srid=srid)
        metadata = Metadata.make_metadata(geometry=geometry)

        if key is None:
            key = Key.make_key()

        crs = geometry._crs
        assert crs is not None

        return Feature(key, geometry, crs,
                       geojson_feature['properties'], metadata)

    def __repr__(self):
        feature = self.__geo_interface__
        feature.update(self.metadata)
        return json.dumps(feature)

    def __hash__(self):
        return hash(self._key)


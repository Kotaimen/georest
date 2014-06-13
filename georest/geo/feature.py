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
import copy

from . import jsonhelper as json

from .key import Key
from .geometry import Geometry
from .spatialref import SpatialReference
from .metadata import Metadata
from .exceptions import InvalidFeature, InvalidGeometry, InvalidGeoJsonInput, \
    InvalidProperties


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

    @key.setter
    def key(self, key):
        assert isinstance(key, Key)
        self._key = key

    @property
    def crs(self):
        return self._crs

    @property
    def metadata(self):
        return self._metadata

    def refresh_metadata(self):
        self._metadata = self._metadata.respawn(self._geometry)

    @property
    def __geo_interface__(self):
        return dict(type='Feature',
                    geometry=shapely.geometry.mapping(self._geometry),
                    properties=self._properties,
                    crs=self._crs.geojson,
                    id=self._key)

    @property
    def geojson(self):
        return json.dumps(self.__geo_interface__, double_precision=9)

    def equals(self, other):
        assert isinstance(other, Feature)
        return self._geometry.equals(other._geometry) and \
               self._crs.equals(other._crs) and \
               self._properties == other._properties

    def almost_equals(self, other):
        return self._geometry.almost_equals(other._geometry) and \
               self._crs.equals(other._crs) and \
               self._properties == other._properties

    def duplicate(self):
        srid = self._crs.srid
        geometry = Geometry.build_geometry(self._geometry,
                                           srid=srid,
                                           copy=True)
        properties = copy.deepcopy(self._properties)

        return Feature.build_from_geometry(geometry,
                                           key=self._key,
                                           properties=properties)

    @staticmethod
    def build_from_geometry(geo_input, key=None, srid=4326, properties=None):
        geometry = Geometry.build_geometry(geo_input, srid=srid)
        metadata = Metadata.make_metadata(geometry=geometry)

        if key is None:
            key = Key.make_key()

        if properties is None:
            properties = dict()

        crs = geometry._crs
        assert crs is not None

        return Feature(key, geometry, crs, properties, metadata)

    @staticmethod
    def build_from_geojson(geo_input, key=None, srid=4326, precise_float=True):
        # load json as python literal if necessary
        if isinstance(geo_input, (str, unicode)):
            try:
                literal = json.loads(geo_input, precise_float=precise_float)
            except (KeyError, ValueError) as e:
                raise InvalidGeoJsonInput(e=e)
        elif isinstance(geo_input, dict):
            literal = geo_input
        else:
            raise InvalidGeoJsonInput('Not a GeoJson or a literal object')

        # basic feature structural check
        try:
            if literal['type'] != 'Feature':
                raise InvalidGeoJsonInput('Not a GeoFeature object')
        except KeyError as e:
            raise InvalidGeoJsonInput(e=e)
        if 'geometry' not in literal:
            raise InvalidGeoJsonInput('No geometry in the feature')

        # load crs from geojson first
        if 'crs' in literal and literal['crs']:
            crs = SpatialReference.build_from_geojson_crs(literal['crs'])
            srid = crs.srid
        else:
            crs = SpatialReference(srid)

        # build geojson feature object
        try:
            geojson_feature = geojson.base.GeoJSON.to_instance(literal)
        except (TypeError, ValueError) as e:
            raise InvalidFeature(e=e)

        if geojson_feature['geometry'] is None:
            raise InvalidGeometry('Invalid geometry')

        if geojson_feature['properties'] is None:
            properties = dict()
        else:
            properties = geojson_feature['properties']

        # assemble the Feature
        geometry = Geometry.build_geometry(geojson_feature['geometry'],
                                           srid=srid)
        metadata = Metadata.make_metadata(geometry=geometry)

        if key is None:
            key = Key.make_key()

        return Feature(key, geometry, crs,
                       properties, metadata)

    def __repr__(self):
        feature = self.__geo_interface__
        feature.update(self.metadata)
        return 'Feature(%s)' % json.dumps(feature)

    def __hash__(self):
        return hash(self._key)

    def __getstate__(self):
        return (self._key, self._geometry.wkb, self._crs,
                self._properties, self._metadata)

    def __setstate__(self, state):
        key, wkb, crs, properties, metadata = state
        geometry = Geometry.build_geometry(wkb, srid=crs.srid)
        self._key = key
        self._geometry = geometry
        self._crs = crs
        self._properties = properties
        self._metadata = metadata

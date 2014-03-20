# -*- encoding: utf-8 -*-

"""
    Feature Object
    ~~~~~~~~~~~~~~

"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

import hashlib
import itertools
import datetime
import collections
import uuid
import geohash

from .engine import geos
from .geometry import build_geometry


class Feature(collections.OrderedDict):
    """
        GeoFeature

        A more GeoJson friendly data layout
    """

    # Fields starts with "_" are not part of the geojson standard
    FIELDS = ('_id', '_etag', '_created', '_modified',
              '_geotype', '_geoformat', '_geohash',
              'type', 'geometry', 'crs', 'bbox', 'properties')

    def __init__(self, geometry, properties,
                 id_, created, modified, geoformat):
        super(Feature, self).__init__(itertools.izip_longest(self.FIELDS, []))

        self['_id'] = id_
        self['_created'] = created
        self['_modified'] = modified
        self['_geoformat'] = geoformat
        # XXX: Consider FeatureCollection...
        self['type'] = 'Feature'
        self['geometry'] = geometry

        self['properties'] = properties
        self.recalculate()

    def recalculate(self):
        # XXX: Add a hooker to recalculate these after __setitem__
        self['_geotype'] = self['geometry'].geom_type
        self['_etag'] = calc_etag(self['geometry'].the_geom, self['properties'])
        self['_modified'] = datetime.datetime.utcnow()
        self['_geohash'] = calc_geohash(self['geometry'].the_geom)
        self['bbox'] = calc_bbox(self['geometry'].the_geom)
        self['crs'] = self['geometry'].crs

    def __setitem__(self, key, value):
        if key not in self.FIELDS:
            raise KeyError(key)
        super(Feature, self).__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return self.__getattribute__(item)


#
# Feature factory
#

def calc_etag(geom, props):
    """ Calculate etag of a feature using geometry and properties """
    assert isinstance(geom, geos.GEOSGeometry)
    h = hashlib.sha1()
    h.update(geom.ewkb)
    h.update(repr(props))
    return h.hexdigest()


GEOHASH_PRECISION = 12


def calc_geohash(geom):
    """
        Calculate geohash of th geometry

        Mimics behaviour of postgis st_geohash
    """
    assert isinstance(geom, geos.GEOSGeometry)
    if geom.crs is not None and geom.crs.angular_name != 'degree':
        # Geohash only supports geographic crs with degree unit
        return None

    if geom.geom_type == 'Point':
        lon, lat = geom.tuple
        return geohash.encode(lat, lon, GEOHASH_PRECISION)
    else:
        envelope = geom.envelope.tuple
        assert len(envelope[0]) == 5
        left, bottom = envelope[0][0]
        right, top = envelope[0][2]

        # Calculate the bounding box precision
        hash1 = geohash.encode(bottom, left, GEOHASH_PRECISION)
        hash2 = geohash.encode(top, right, GEOHASH_PRECISION)

        precision = list(x == y for x, y in zip(hash1, hash2)).index(False)
        if precision <= 0:
            precision = GEOHASH_PRECISION

        # Calculate geohash using center point and precision
        return geohash.encode((top + bottom) / 2.,
                              (right + left) / 2.,
                              precision)


def calc_bbox(geom):
    """ Calculate bounding box of the geometry """
    assert isinstance(geom, geos.GEOSGeometry)

    if geom.geom_type == 'Point':
        point = list(geom.coords)
        point.extend(geom.coords)
        return point
    else:
        bbox = []
        envelope = geom.envelope[0]
        assert len(envelope) == 5
        bbox.extend(envelope[0])
        bbox.extend(envelope[2])
        return bbox


def build_feature(geoinput,
                  srid=4326,
                  properties=None,
                  id_=None,
                  created=None,
                  modified=None,
                  geoformat='geojson'):
    """
        Build a geometry feature
    """

    if created is None:
        created = datetime.datetime.utcnow()

    if modified is None:
        modified = created

    if properties is None:
        properties = dict()

    if id_ is None:
        id_ = uuid.uuid4()

    geometry = build_geometry(geoinput, srid)

    feature = Feature(geometry, properties,
                      id_, created, modified,
                      geoformat)
    return feature


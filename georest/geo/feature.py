# -*- encoding: utf-8 -*-

"""
    georest.geo.feature
    ~~~~~~~~~~~~~~~~~~~

    Spatial feature object and creation

"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

import hashlib
import datetime
import uuid
import json

import geohash

from .engine import geos
from .geometry import build_geometry
from .exception import InvalidFeature


class Feature(object):
    """GeoFeature with more GeoJson friendly properties.

    Unlike OGRFeature, does not require property have a field definition.
    """

    def __init__(self,
                 key, etag,
                 created, modified,
                 geometry, properties,
                 bbox, geohash):
        self._key = key
        self._etag = etag

        self._created = created
        self._modified = modified

        self._geometry = geometry
        self._properties = properties

        self._bbox = bbox
        self._geohash = geohash

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def etag(self):
        return self._etag

    @property
    def created(self):
        return self._created

    @property
    def modified(self):
        return self._modified

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, new_geometry):
        self._geometry = new_geometry
        self.recalculate()

    @property
    def properties(self):
        return self._properties

    @property
    def bbox(self):
        return self._bbox

    @property
    def type(self):
        return 'Feature'

    @property
    def geotype(self):
        return self._geometry.geom_type

    @property
    def geohash(self):
        return self._geohash

    @property
    def crs(self):
        return self._geometry.crs

    def recalculate(self):
        # XXX: Add a hooker to recalculate these after changed major properties

        self._modified = datetime.datetime.utcnow()
        self._etag = calc_etag(self._geometry.the_geom, self._properties)
        self._geohash = calc_geohash(self._geometry.the_geom)
        self._bbox = calc_bbox(self._geometry.the_geom)

    def __repr__(self):
        return 'Feature(%r,%s)' % (self._geometry, self._properties)


#
# Feature factory
#

def calc_etag(geom, props):
    """Calculate etag of a feature using geometry and properties"""
    assert isinstance(geom, geos.GEOSGeometry)
    h = hashlib.sha1()
    h.update(geom.ewkb)
    h.update(repr(props))
    return h.hexdigest()


GEOHASH_PRECISION = 12


def calc_geohash(geom):
    """Calculate geohash of th geometry, mimics behaviour of postgis st_geohash
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
    """Calculate bounding box of the geometry"""
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
                  properties=None,
                  srid=4326,
                  key=None,
                  created=None,
                  modified=None):
    """Build a feature from geometry and properties."""

    if created is None:
        created = datetime.datetime.utcnow()

    if modified is None:
        modified = created

    if properties is None:
        properties = dict()

    if key is None:
        key = uuid.uuid4().hex

    geometry = build_geometry(geoinput, srid)

    feature = Feature(key=key, etag=None,
                      created=created, modified=modified,
                      geometry=geometry, properties=properties,
                      bbox=None, geohash=None)

    feature.recalculate()

    return feature


def build_feature_from_geojson(geojsoninput,
                               key=None,
                               created=None,
                               modified=None):
    input = json.loads(geojsoninput)

    if 'type' not in input or input['type'] != 'Feature' \
            or 'geometry' not in input:
        raise InvalidFeature('Must be a GeoJson Feature object')

    geoinput = json.dumps(input['geometry'])

    if 'properties' not in input:
        props = {}
    else:
        props = input['properties']

    return build_feature(geoinput,
                         props,
                         key=key,
                         created=created,
                         modified=modified)
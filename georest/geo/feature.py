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

import six
import geohash

import jsonhelper as json

from .engine import geos
from .geometry import build_geometry, Geometry
from .exception import InvalidFeature, InvalidProperty

#
# Feature
#
class Feature(object):
    """GeoFeature with more GeoJson friendly properties.

    Unlike OGRFeature, does not require property have a field definition.
    """

    def __init__(self,
                 key, etag,
                 created, modified,
                 geometry, properties,
                 bbox, geohash):
        """ To create a new feature, use factory methods below.

        :param string key: key of the feature
        :param string etag: etag of the feature
        :param datetime.datetime created: timestamp when feature is created
        :param datetime.datetime modified: timestamp when feature is last modified
        :param Geometry geometry: geometry object
        :param dict properties: feature properties
        :param list bbox: bounding box of the geometry
        :param string geohash: geohash of the geometry
        """
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

    def update_geometry(self, geom):
        self._geometry = geom
        self.recalculate()

    def update_properties(self, props):
        self._properties.update(props)
        self.recalculate()

    def delete_properties(self, names=None):
        if names is None:
            self._properties.clear()
        else:
            for name in names:
                del self._properties[name]
        self.recalculate()

    def recalculate(self):
        # XXX: Add a hooker to recalculate after setter call?
        self._modified = datetime.datetime.utcnow()
        self._etag = calc_etag(self._geometry.the_geom, self._properties)
        self._geohash = calc_geohash(self._geometry.the_geom)
        self._bbox = calc_bbox(self._geometry.the_geom)

    def __repr__(self):
        return 'Feature(%r,%s)' % (self._geometry, self._properties)

    def __eq__(self, other):
        if not isinstance(other, Feature):
            return False
        return self._geometry.ewkt == other._geometry.ewkt \
                   and self._properties == other._properties \
                   and self._key == other._key \
                   and self._etag == other._etag \
                   and self._created == other._created \
                   and self._modified == other._modified \
                   and self._bbox == other._bbox \
            and self._geohash == other._geohash


#
# JSON Serialization
#

def make_crs(crs):
    if not crs.srid:
        return None
    else:
        return {'type': 'name',
                'properties': {
                    'name': 'EPSG:%d' % crs.srid
                }}


def load_iso_datetime(utc_datetime):
    return datetime.datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%S.%f')


def dump_iso_datetime(datetime):
    if datetime.microsecond == 0:
        # isoformat() drops .mmmmmm when microsecond is 0
        return datetime.isoformat() + '.000000'
    else:
        return datetime.isoformat()


def feature2literal(feature, binary=False):
    """ Dump a Feature object to a literal dict
    :param Feature feature: Feature
    :param bool binary: Whether dump geometry into HEXEWKB format
    :return: literal dict
    """
    return dict(
        type="Feature",
        geometry=json.loads(
            feature.geometry.geojson) if not binary else feature.geometry.hexewkb,
        properties=feature.properties,
        bbox=feature.bbox,
        crs=make_crs(feature.crs.crs),
        _srid=feature.crs.srid,
        _format='geojson' if not binary else 'hexewkb',
        _key=feature.key,
        _etag=feature.etag,
        _geohash=feature.geohash,
        _created=dump_iso_datetime(feature.created),
        _modified=dump_iso_datetime(feature.modified),
    )


def literial2feature(data):
    """ Build a Feature object from python dict"""
    assert isinstance(data, dict)
    assert data['type'] == 'Feature'
    if data['_format'] == 'geojson':
        geometry = build_geometry(json.dumps(data['geometry']),
                                  srid=data['_srid'])
    else:
        geometry = build_geometry(data['geometry'],
                                  srid=data['_srid'])
    return Feature(data['_key'], data['_etag'],
                   load_iso_datetime(data['_created']),
                   load_iso_datetime(data['_modified']),
                   geometry, data['properties'],
                   data['bbox'], data['_geohash'])


def feature2json(feature, binary=False):
    """ Dump a Feature object as geojson """

    return json.dumps(feature2literal(feature, binary))


def json2feature(json_input):
    """ Load a Feature object form geojson string.

    This function does not validate the input!
    """
    return literial2feature(json.loads(json_input))


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

    if isinstance(geoinput, Geometry):
        geometry = geoinput
    elif isinstance(geoinput, geos.GEOSGeometry):
        geometry = Geometry(geoinput)
    else:
        geometry = build_geometry(geoinput, srid)

    feature = Feature(key=key, etag=None,
                      created=created, modified=modified,
                      geometry=geometry, properties=properties,
                      bbox=None, geohash=None)

    feature.recalculate()

    return feature


def check_properties(props):
    """ Check whether given properties is valid
    """
    if not isinstance(props, dict):
        raise InvalidProperty('Properties must be a dictionary')

    for name, value in props.iteritems():
        if not isinstance(name, six.string_types):
            raise InvalidProperty(
                'Property name must be a string, got "%s"' % type(
                    name).__name__)

        try:
            json.dumps(value)
        except TypeError:
            raise InvalidProperty(
                'Property value must be json serializable')


def build_feature_from_geojson(geojsoninput,
                               key=None,
                               srid=4326,
                               created=None,
                               modified=None):
    """ Build a feature from geojson input. """
    try:
        input_ = json.loads(geojsoninput)
    except (TypeError, ValueError) as e:
        raise InvalidFeature('Invalid Feature geojson input', e)

    if 'type' not in input_ or input_['type'] != 'Feature' \
            or 'geometry' not in input_:
        raise InvalidFeature('Must be a GeoJson Feature object')

    geo_input = json.dumps(input_['geometry'])

    if 'properties' not in input_:
        props = {}
    else:
        props = input_['properties']
        check_properties(props)

    return build_feature(geo_input,
                         props,
                         key=key,
                         srid=srid,
                         created=created,
                         modified=modified)


def build_properties_from_json(jsoninput):
    """ Build a properties from json input and do validation
    :param string jsoninput: json input
    :return: properties
    """
    try:
        props = json.loads(jsoninput)
    except (TypeError, ValueError) as e:
        raise InvalidProperty(e)

    check_properties(props)

    return props
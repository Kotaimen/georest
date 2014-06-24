# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/4/14'

"""
    georest.geo.geometry
    ~~~~~~~~~~~~~~~~~~~~
    Geometry IO stuff

"""

import re
import io

import six

import shapely.speedups
import shapely.geometry
import shapely.geometry.base
import shapely.geometry.collection
import shapely.validation
import shapely.wkt
import shapely.wkb

import geojson
import geojson.base
import geojson.mapping

from .exceptions import InvalidGeometry, InvalidGeoJsonInput
from .spatialref import SpatialReference
from . import jsonhelper as json


class Geometry(object):
    """ Being a mixin class, provide extra attributes for shapely's geometry"""

    # def __init__(self):
    #     """This class is not intended to be created explicitly """
    #     raise NotImplementedError

    @staticmethod
    def is_geometry(obj):
        # only accepts our Geometry
        return isinstance(obj, Geometry) and \
               isinstance(obj, shapely.geometry.base.BaseGeometry)

    @classmethod
    def build_geometry(cls, geo_input, srid=4326, copy=False, empty_check=True):
        """Make a shapely Geometry object from given geometry input and srid

        `geo_input` can be one of the following format:
        - str/unicode
            - GeoJson geometry
            - WKT/EWKT
            - HEXWKB
        - byte, buffer
            - WKB
        - A subclass of shapely.geometry.base.BaseGeometry
        - A dict satisfies python geo interface

        `srid` specifies spatial reference in EPSG, a `SpatialReference` object
        will be created and assign to `_crs` member of the created geometry
        object.  Available srid is determined by underlying projection library
        (currently pyproj, note pyproj don't use same projection data files as
        gdal, see documents).

        If `geo_input` already contains a bundled SRID (eg: EWKT) then `srid`
        parameter is ignored.

        `copy` means coordinates are copied from GeoJson input to the created
        geometry instead of using a coordinates value proxy.  Don't copy
        coordinates means fast creation but can cause problems when doing
        geometry operations.

        Returns a shapely.base.geometry.BaseGeometry object.

        NOTE: This is not really python3 compatible...
        """
        assert isinstance(srid, int)

        # factory methods, ordered by attempt priority
        factories = [create_geometry_from_geometry,
                     create_geometry_from_literal,
                     create_geometry_from_geojson,
                     create_geometry_from_wkt,
                     create_geometry_from_wkb, ]

        for factory in factories:
            # find a suitable factory for given input
            try:
                geometry, bundled_srid = factory(geo_input, copy=copy)
            except NotMyType:
                continue
            try:
                if not geometry.is_valid:
                    reason = shapely.validation.explain_validity(geometry)
                    raise InvalidGeometry(
                        'Invalid geometry is not allowed: %s' % reason)
            except Exception as e:
                # delayed asShape geometry build causes error only surfaces
                # when we read the geometry
                raise InvalidGeometry('Invalid coordinates', e=e)

            if empty_check and geometry.is_empty:
                raise InvalidGeometry('Empty geometry is not allowed')

            # bundled srid always overwrites provided one
            if bundled_srid is not None and bundled_srid != 4326:
                srid = bundled_srid

            # hack the geometry
            hack_geometry(geometry)

            # assign new crs only if geometry don't already have one
            if not geometry.crs:
                geometry._the_crs = SpatialReference(srid=srid)
            return geometry

        else:
            raise InvalidGeometry('Unrecognized geometry input')

    @property
    def geojson(self, double_precision=7):
        geo_obj = geojson.mapping.to_mapping(self)
        if not self._the_crs or self._the_crs.srid != 4326:
            geo_obj['crs'] = self._the_crs.geojson
        return json.dumps(geo_obj,
                          double_precision=double_precision)

    @property
    def ewkt(self):
        return 'SRID=%d;%s' % (self.crs.srid, self.wkt)

    # don't use shapely's _crs
    _the_crs = None

    @property
    def crs(self):
        return self._the_crs


# TODO: populate the cache instead relying on lazy logic below
HACK_GEOMETRY_TYPES = {}

KNOWN_TYPE_NAMES = frozenset(['MultiPoint', 'LineString', 'Polygon', 'Point',
                              'MultiPointAdapter',
                              'LineStringAdapter', 'GeometryCollection',
                              'MultiLineString',
                              'PolygonAdapter',
                              'MultiPolygonAdapter', 'PointAdapter',
                              'MultiLineStringAdapter',
                              'MultiPolygon', 'GeometryCollection'])


def hack_geometry(geometry):
    """ Inject out attributes by make our Geometry a shapely geometry's parent
    See `shapely.geometry.base.geom_factory()` for why we are doing this.
    """
    if issubclass(geometry.__class__, Geometry):
        # already a hacked geometry object, exiting
        return

    # get name of the geometry class
    type_name = geometry.__class__.__name__
    assert type_name in KNOWN_TYPE_NAMES

    try:
        new_type = HACK_GEOMETRY_TYPES[type_name]
    except KeyError:
        # generate a new hack geometry type of given class
        original_type = geometry.__class__
        # equivalent to
        # class MyHackGeometryType(OriginalGeometry, Geometry): pass
        new_type = type(geometry.__class__.__name__,
                        (original_type, Geometry),
                        dict(geometry.__class__.__dict__))
        # update the cache
        HACK_GEOMETRY_TYPES[type_name] = new_type

    # replace the type object
    geometry.__class__ = new_type


#
# Magic regular expression
#

# NOTE: Not really secure, are we allowing only GeoJSON input from API?
HEX_REGEX = re.compile(r'^[0-9A-F]+$', re.I)

WKT_REGEX = re.compile(r'^(SRID=(?P<SRID>\-?\d+);)?'
                       r'(?P<WKT>'
                       r'(?P<TYPE>POINT|LINESTRING|LINEARRING|POLYGON|'
                       r'MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|'
                       r'GEOMETRYCOLLECTION)'
                       r'[ACEGIMLONPSRUTYZ\d,\.\-\(\) ]+)$',
                       re.I)
JSON_REGEX = re.compile(r'^(\s+)?\{[\s\w,\[\]\{\}\-\."\':]+\}(\s+)?$')


#
# Geometry factory methods for each format, returns a (geometry, srid) tuple
#
class NotMyType(RuntimeError):
    """Exception thrown when factory methods don't recognize the input"""
    pass


def create_geometry_from_geojson(geo_input, copy=False):
    if not isinstance(geo_input, six.string_types) or \
            not JSON_REGEX.match(geo_input):
        raise NotMyType('GeoJson')

    try:
        # load json first
        literal = json.loads(geo_input, precise_float=True)
    except (TypeError, ValueError) as e:
        raise InvalidGeoJsonInput("Can't decode json input", e=e)

    return create_geometry_from_literal(literal, copy=copy)


def create_geometry_from_literal(geo_input, copy=False):
    if not isinstance(geo_input, dict):
        raise NotMyType
    if 'type' not in geo_input:
        raise NotMyType

    try:
        # geojson validation
        geojson_geometry = geojson.base.GeoJSON.to_instance(geo_input)
    except (TypeError, ValueError) as e:
        raise InvalidGeometry("Invalid GeoJson geometry", e=e)

    if 'crs' in geo_input and geo_input['crs']:
        crs = SpatialReference.build_from_geojson_crs(geo_input['crs'])
        srid = crs.srid
    else:
        # geojson default crs is wgs84
        srid = 4326

    try:
        if geojson_geometry['type'] != 'GeometryCollection':
            # whether to copy geometry coordinates from geojson geometry,
            # which is slightly slower
            builder = shapely.geometry.shape if copy else shapely.geometry.asShape

            # create shapely geometry
            geometry = builder(geojson_geometry)

        else:
            # painfully create GeometryCollection from geojson object
            geometry = create_geometrycollection_from_geojson(geojson_geometry)

    except ValueError as e:
        raise InvalidGeometry(e=e)

    # for GeoJson, SRID is always undefined
    return geometry, srid


def create_geometrycollection_from_geojson(geometry, buf=None):
    """shapley don't support create GeometryCollection from python geo
    interface, only from a GEOS Geometry is available, so we convert the
    collection object to WKT and load into shapely again.
    """
    # XXX: https://github.com/Toblerity/Shapely/issues/115
    if buf is None:
        is_top = True
        buf = io.BytesIO()
    else:
        is_top = False

    length = len(geometry.geometries)
    if length == 0:
        buf.write('GEOMETRYCOLLECTION EMPTY')
    else:
        buf.write('GEOMETRYCOLLECTION (')
        for n, geom in enumerate(geometry.geometries):
            if geom['type'] == 'GeometryCollection':
                create_geometrycollection_from_geojson(geom, buf=buf)
            else:
                buf.write(shapely.geometry.asShape(geom).wkt)
                if n < length - 1:
                    buf.write(',')
        buf.write(')')
    if is_top:
        wkt = buf.getvalue()
        return shapely.wkt.loads(wkt)


def create_geometry_from_wkt(geo_input, copy):
    if not isinstance(geo_input, six.string_types):
        raise NotMyType('WKT')
    wkt_m = WKT_REGEX.match(geo_input)
    if not wkt_m:
        raise NotMyType('WKT')

    # try decode bundled geometry srid
    if wkt_m.group('SRID'):
        srid = int(wkt_m.group('SRID'))
    else:
        srid = None

    # get wkt
    wkt = wkt_m.group('WKT')

    try:
        geometry = shapely.wkt.loads(wkt)
    except shapely.wkt.geos.ReadingError as e:
        raise InvalidGeometry(e=e)

    return geometry, srid


def create_geometry_from_wkb(geo_input, copy):
    if isinstance(geo_input, six.string_types):
        if HEX_REGEX.match(geo_input):
            # HEX WKB
            hex = True
        else:
            hex = False
    elif isinstance(geo_input, buffer):
        hex = False
        geo_input = str(geo_input)
    else:
        raise NotMyType('WKB')

    try:
        geometry = shapely.wkb.loads(geo_input, hex=hex)
    except shapely.wkt.geos.ReadingError as e:
        raise InvalidGeometry(e=e)

    return geometry, None


def create_geometry_from_geometry(geo_input, copy=False):
    if Geometry.is_geometry(geo_input):
        bundled_srid = geo_input.crs.srid
        if not copy:
            return geo_input, bundled_srid
        else:
            return shapely.geometry.shape(geo_input), bundled_srid
    elif isinstance(geo_input, shapely.geometry.base.BaseGeometry):
        if not copy:
            return geo_input, None
        else:
            return shapely.geometry.shape(geo_input), None
    else:
        raise NotMyType('Shapely Geometry')


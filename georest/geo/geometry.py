# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/4/14'

"""
    georest.geo.geometry
    ~~~~~~~~~~~~~~~~~~~~
    Geometry IO

"""

import re
import io

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
import ujson

from .exceptions import InvalidGeometry, InvalidGeoJsonInput
from .spatialref import SpatialReference

shapely.speedups.enable()


class Geometry(object):
    """Just a namespace containing static methods"""

    @staticmethod
    def make_geometry(geo_input, srid=4326):
        """Make a shapely Geometry object from given geometry input and srid

        `geo_input` can be one of the following format:
        - str/unicode
            - GeoJson geometry
            - WKT/EWKT
            - HEXWKB
        - byte, buffer
            - WKB
        - A subclass of shapely.geometry.base.BaseGeometry

        A `SpatialReference` object will be created and assign to `_crs` member
        of the created geometry object.

        If `geo_input` already contains a bundled SRID (eg: EWKT) then `srid`
        parameter is always ignored.

        Idea copied from `django.contrib.geo.geos.geometry.__init__()`

        NOTE: This is not really python3 compatible...
        """
        assert isinstance(srid, int)
        assert srid != 0  # we don't support undefined coordinate system
        factories = [create_geometry_from_geometry,
                     create_geometry_from_geojson,
                     create_geometry_from_wkt,
                     create_geometry_from_wkb, ]

        for factory in factories:
            # find a suitable factory for given input
            try:
                geometry, bundled_srid = factory(geo_input)
            except NotMyType:
                continue

            if geometry.is_empty:
                raise InvalidGeometry('Empty geometry is not allowed')

            if not geometry.is_valid:
                reason = shapely.validation.explain_validity(geometry)
                raise InvalidGeometry(
                    'Invalid geometry is not allowed: %s' % reason)

            # bundled srid always overwrites provided one
            if bundled_srid is not None:
                srid = bundled_srid

            # assign new
            if geometry._crs is None:
                geometry._crs = SpatialReference(srid=srid)

            return geometry

        else:
            raise InvalidGeometry('Unrecognized geometry input')

    @staticmethod
    def export_geojson(geometry):
        return ujson.dumps(geojson.mapping.to_mapping(geometry))


#
# Magic regular expression
#

# XXX: Not really secure, are we allowing only GeoJSON input from API?
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
    pass


def create_geometry_from_geojson(geo_input, copy=False):
    if not JSON_REGEX.match(geo_input):
        raise NotMyType('GeoJson')

    try:
        # load json first
        literal = ujson.loads(geo_input)
    except (TypeError, ValueError) as e:
        raise InvalidGeoJsonInput(message="Can't decode json input", e=e)
    try:
        # geojson validation
        geojson_geometry = geojson.base.GeoJSON.to_instance(literal)
    except (TypeError, ValueError) as e:
        raise InvalidGeoJsonInput(message="Invalid GeoJson geometry", e=e)

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
    return geometry, None


def create_geometrycollection_from_geojson(geometry, buf=None):
    """ shapley don't support create GeometryCollection from python geo
    interface, only from a GEOS Geometry is available, so we convert the
    collection object to WKT and load into shapely again.
    """
    # TODO: Check whether this is fixed in shapely (current version is 1.4.0)

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


def create_geometry_from_wkt(geo_input):
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


def create_geometry_from_wkb(geo_input):
    if isinstance(geo_input, (str, unicode)):
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


def create_geometry_from_geometry(geo_input):
    if isinstance(geo_input, shapely.geometry.base.BaseGeometry):
        return geo_input, None
    else:
        raise NotMyType('Shapely Geometry')


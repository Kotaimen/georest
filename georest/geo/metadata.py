# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

"""
    georest.geo.metadata
    ~~~~~~~~~~~~~~~~~~~~
    Metadata of a feature
"""

import time

import geohash
import shapely.geometry.base

from .spatialref import SpatialReference


class Metadata(dict):
    """ Metadata of a geometry feature """

    def __init__(self, created, modified, etag, geohash, bbox):
        super(Metadata, self).__init__(_created=created,
                                       _modified=modified,
                                       _etag=etag,
                                       _geohash=geohash,
                                       bbox=bbox)

    @property
    def created(self):
        return self['_created']

    @property
    def modified(self):
        return self['_modified']

    @modified.setter
    def modified(self, modified):
        self['_modified'] = modified

    @property
    def etag(self):
        return self['_etag']

    @etag.setter
    def etag(self, etag):
        self['_etag'] = etag

    @property
    def geohash(self):
        return self['_geohash']

    @geohash.setter
    def geohash(self, geohash):
        self['_geohash'] = geohash

    @property
    def bbox(self):
        return self['bbox']

    @bbox.setter
    def bbox(self, bbox):
        self['bbox'] = bbox

    # Precision geohash preserves
    GEOHASH_PRECISION = 12

    @staticmethod
    def build_metadata(created=None, modified=None, etag=None,
                      geohash=None, bbox=None, geometry=None):
        if created is None:
            created = time.time()

        if modified is None:
            modified = time.time()

        if geometry is not None:
            assert bbox is None

            bbox = calc_bbox(geometry)

            crs = geometry._crs
            if crs is not None:
                assert geohash is None
                assert isinstance(crs, SpatialReference)
                if crs.proj.is_latlong():
                    # Geohash only supports lonlat coordinates
                    geohash = calc_geohash(geometry, Metadata.GEOHASH_PRECISION)

        return Metadata(created, modified, etag, geohash, bbox)


def calc_bbox(geom):
    """Calculate bounding box of the geometry"""
    assert isinstance(geom, shapely.geometry.base.BaseGeometry)
    return geom.bounds


def calc_geohash(geom, precision=7):
    """Calculate geohash of th geometry, mimics behaviour of postgis st_geohash

    `geom` must be a geometry with lonlat coordinates and `precision` is
    length of returned hash string for Point geometry.
    """
    assert isinstance(geom, shapely.geometry.base.BaseGeometry)
    if geom.is_empty:
        return ''
    assert isinstance(precision, int)
    assert precision > 1  # useless if precision is too short

    if geom.geom_type == 'Point':
        assert isinstance(geom, shapely.geometry.Point)
        return geohash.encode(geom.y, geom.x, precision)

    else:
        (left, bottom, right, top) = geom.bounds

        # Calculate the bounding box precision
        hash1 = geohash.encode(bottom, left, precision)
        hash2 = geohash.encode(top, right, precision)

        try:
            bounds_precision = \
                list(x == y for x, y in zip(hash1, hash2)).index(False)
        except ValueError:
            # list.index throws ValueError if value is not found
            bounds_precision = precision

        # Calculate geohash using center point and bounds precision
        return geohash.encode((top + bottom) / 2.,
                              (right + left) / 2.,
                              bounds_precision)

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

"""
    georest.geo.metadata
    ~~~~~~~~~~~~~~~~~~~~
    Metadata of a feature
"""

import collections
import time

import geohash
import shapely.geometry.base

from .spatialref import SpatialReference


class Metadata(collections.namedtuple('Metadata',
                                      '''created modified bbox geohash
                                      cells''')):
    """ Metadata of a geometry

    - `created` `modified` float timestamp, time since epoch returned
       by `time.time()`
    - `geohash` geohash of the geometry used to do quick adhoc spatial search.
      For point geometry, max precision is 12 chars, for other geometry, defined
      by its bounding box.  Note geohash only works on geometry with lonlat
      based coordinate reference systems.
    - `bbox` bounding box of the geometry as a list [minx, miny, maxx, maxy]
    - `cells` a list of integers describes S2CellID of the geometry, currently
      not implemented.
    """

    GEOHASH_PRECISION = 12

    @staticmethod
    def make_metadata(created=None, modified=None,
                      geometry=None):

        if created is None:
            created = time.time()

        if modified is None:
            modified = time.time()

        bbox = calc_bbox(geometry)

        geohash = calc_geohash(geometry, Metadata.GEOHASH_PRECISION)

        return Metadata(created, modified, bbox, geohash, [])

    def spawn(self, geometry=None):
        modified = time.time()
        bbox = calc_bbox(geometry)

        geohash = calc_geohash(geometry, Metadata.GEOHASH_PRECISION)

        return self._replace(modified=modified,
                             bbox=bbox,
                             geohash=geohash)


def calc_bbox(geom):
    """Calculate bounding box of the geometry"""
    assert isinstance(geom, shapely.geometry.base.BaseGeometry)
    return list(geom.bounds)

# TODO: rename precision to length
def calc_geohash(geom, precision=7, ignore_crs=False):
    """Calculate geohash of th geometry, mimics behaviour of postgis st_geohash

    `geom` must be a geometry with lonlat coordinates and `precision` is
    length of returned hash string for Point geometry.
    """
    assert isinstance(geom, shapely.geometry.base.BaseGeometry)
    if geom.is_empty:
        return ''

    # only supports lonlat coordinates
    if not ignore_crs:
        crs = geom._crs
        if crs is None or not crs.proj.is_latlong():
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


def calc_cell_union(geom):
    # not until we have implemented google.s2 extension
    raise NotImplementedError

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

"""
    georest.geo.metadata
    ~~~~~~~~~~~~~~~~~~~~
    Metadata of a geometry, aka geoindex helpers
"""

import collections

import geohash
import shapely.geometry.base


class Metadata(collections.namedtuple('Metadata',
                                      '''bbox geohash cells''')):
    """ Metadata of a geometry

    - `geohash` geohash of the geometry used to do quick adhoc spatial search.
      For point geometry, max precision is 12 chars, for other geometry, defined
      by its bounding box.  Note geohash only works on geometry with lonlat
      based coordinate reference systems.
    - `bbox` bounding box of the geometry as a list [minx, miny, maxx, maxy]
    - `cells` a list of integers describes S2CellID of the geometry, currently
      not implemented.
    """

    GEOHASH_LENGTH = 12

    @classmethod
    def make_metadata(cls, geometry=None):
        bbox = calc_bbox(geometry)

        geohash = calc_geohash(geometry, Metadata.GEOHASH_LENGTH)

        return cls(bbox, geohash, [])

    def spawn(self, geometry):
        assert geometry is not None
        bbox = calc_bbox(geometry)
        geohash = calc_geohash(geometry, Metadata.GEOHASH_LENGTH)
        return self._replace(bbox=bbox, geohash=geohash)


def calc_bbox(geom):
    """Calculate bounding box of the geometry"""
    assert isinstance(geom, shapely.geometry.base.BaseGeometry)
    return list(geom.bounds)


def calc_geohash(geom, length=7, ignore_crs=False):
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

    assert isinstance(length, int)
    assert length > 1  # useless if precision is too short

    if geom.geom_type == 'Point':
        assert isinstance(geom, shapely.geometry.Point)
        return geohash.encode(geom.y, geom.x, length)

    else:
        (left, bottom, right, top) = geom.bounds

        # Calculate the bounding box precision
        hash1 = geohash.encode(bottom, left, length)
        hash2 = geohash.encode(top, right, length)

        try:
            bounds_precision = \
                list(x == y for x, y in zip(hash1, hash2)).index(False)
        except ValueError:
            # list.index throws ValueError if value is not found
            bounds_precision = length

        # Calculate geohash using center point and bounds precision
        return geohash.encode((top + bottom) / 2.,
                              (right + left) / 2.,
                              bounds_precision)


def calc_cell_union(geom):
    # not until we have implemented google.s2 extension
    raise NotImplementedError

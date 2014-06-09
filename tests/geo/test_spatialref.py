# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/7/14'

import unittest
import geojson

import shapely.geometry

from georest.geo.spatialref import SpatialReference, CoordinateTransform
from georest.geo.exceptions import InvalidSpatialReference, \
    CoordinateTransformationError
from georest.geo.geometry import Geometry

from tests.geo.data import jsondata


class TestSpatialReference(unittest.TestCase):
    def test_create_spatialref(self):
        crs1 = SpatialReference(4326)
        self.assertEqual(crs1.srid, 4326)
        self.assertTrue(crs1.proj.is_latlong())
        crs2 = SpatialReference(3857)
        self.assertEqual(crs2.srid, 3857)
        self.assertFalse(crs2.proj.is_latlong())

    def test_create_fail(self):
        self.assertRaises(InvalidSpatialReference, SpatialReference, 12345)

    def test_tojson(self):
        crs1 = SpatialReference(4326)
        self.assertDictEqual(crs1.geojson,
                             {'type': 'name',
                              'properties': {
                                  'name': 'EPSG:4326'
                              }})


class TestCoordianteTransform(unittest.TestCase):
    def test_transform(self):
        geom1 = shapely.geometry.Point(1, 1)
        crs1 = SpatialReference(4326)
        crs2 = SpatialReference(3857)

        forward = CoordinateTransform(crs1, crs2)
        backward = CoordinateTransform(crs2, crs1)

        geom2 = forward(geom1)
        geom3 = backward(geom2)

        self.assertTrue(geom1.almost_equals(geom3))

    def test_transform_multi(self):
        crs1 = SpatialReference(4326)
        crs2 = SpatialReference(3857)

        forward = CoordinateTransform(crs1, crs2)
        backward = CoordinateTransform(crs2, crs1)

        for k, v in jsondata.iteritems():
            geom1 = Geometry.make_geometry(v, copy=True)
            if k == 'geometrycollection':
                self.assertRaises(CoordinateTransformationError, forward, geom1)
            else:

                geom2 = forward(geom1)
                geom3 = backward(geom2)
                self.assertTrue(geom1.almost_equals(geom3))


if __name__ == '__main__':
    unittest.main()

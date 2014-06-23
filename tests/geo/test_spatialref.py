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
    def test_build_spatialref(self):
        crs1 = SpatialReference(4326)
        self.assertEqual(crs1.srid, 4326)
        self.assertTrue(crs1.proj.is_latlong())
        crs2 = SpatialReference(3857)
        self.assertEqual(crs2.srid, 3857)
        self.assertFalse(crs2.proj.is_latlong())

    def test_build_failure(self):
        self.assertRaises(InvalidSpatialReference, SpatialReference, 12345)

    def test_to_json(self):
        crs1 = SpatialReference(4326)
        self.assertDictEqual(crs1.geojson,
                             {'type': 'name',
                              'properties': {
                                  'name': 'EPSG:4326'
                              }})

    def test_from_json(self):
        self.assertEqual(
            SpatialReference.build_from_geojson_crs({
                'type': 'name',
                'properties': {
                    'name': 'EPSG:3857'
                }}).srid,
            3857)
        self.assertRaises(InvalidSpatialReference,
                          SpatialReference.build_from_geojson_crs,
                          {
                              'type': 'blah',
                              'properties': {
                                  'name': 'EPSG:3857'
                              }
                          })
        self.assertRaises(InvalidSpatialReference,
                          SpatialReference.build_from_geojson_crs,
                          {
                              'type': 'blah',
                              'properties': {
                                  'name': 'EPSG:123XXX'
                              }
                          })


class TestCoordinateTransform(unittest.TestCase):
    def test_transform(self):
        geom1 = shapely.geometry.Point(1, 1)
        crs1 = SpatialReference(4326)
        crs2 = SpatialReference(3857)

        forward = CoordinateTransform(crs1, crs2)
        backward = CoordinateTransform.build_transform(crs2, crs1.srid)

        geom2 = forward(geom1)
        geom3 = backward(geom2)

        self.assertTrue(geom1.almost_equals(geom3))

    def test_transform_multi(self):
        crs1 = SpatialReference(4326)
        crs2 = SpatialReference(3857)

        forward = CoordinateTransform(crs1, crs2)
        backward = CoordinateTransform(crs2, crs1)

        for k, v in jsondata.iteritems():
            geom1 = Geometry.build_geometry(v, copy=True)
            if k == 'geometrycollection':
                self.assertRaises(CoordinateTransformationError, forward, geom1)
            else:
                geom2 = forward(geom1)
                geom3 = backward(geom2)
                self.assertTrue(geom1.almost_equals(geom3))


if __name__ == '__main__':
    unittest.main()

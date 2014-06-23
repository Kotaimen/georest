# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

import unittest
from pprint import pprint

import shapely.geometry
from georest.geo.metadata import Metadata, calc_bbox, calc_geohash
from georest.geo.spatialref import SpatialReference
from georest.geo.geometry import Geometry


class TestMetadata(unittest.TestCase):
    def test_make_metadata(self):
        geometry = Geometry.build_geometry('POINT (1 1)')
        metadata = Metadata.make_metadata(geometry=geometry)

        self.assertIsInstance(metadata, Metadata)
        self.assertIsNotNone(metadata.geohash)
        self.assertIsNotNone(metadata.bbox)

        metadata2 = metadata.spawn(
            geometry=Geometry.build_geometry('POINT (1 2)'))
        self.assertNotEqual(metadata, metadata2)


class TestHelpers(unittest.TestCase):
    def test_calc_bbox(self):
        geom1 = Geometry.build_geometry('POINT (5 10)')
        bbox1 = calc_bbox(geom1)
        self.assertListEqual(list(bbox1), [5, 10, 5, 10])

        geom2 = shapely.geometry.LineString([(5, 10), (10, 5)])
        bbox2 = calc_bbox(geom2)
        self.assertListEqual(list(bbox2), [5, 5, 10, 10])

    def test_calc_geohash(self):
        geom1 = Geometry.build_geometry('POINT (126 48)', srid=3857)
        hash0 = calc_geohash(geom1, length=12)
        self.assertEqual(hash0, '')
        hash1 = calc_geohash(geom1, length=12, ignore_crs=True)
        self.assertEqual('yb9954nkkb99', hash1)

        geom2 = shapely.geometry.LineString([(12, 34), (12.0001, 34.0001)])
        hash2 = calc_geohash(geom2, length=12, ignore_crs=True)
        self.assertEqual('sq093jd0', hash2)

        hash2 = calc_geohash(geom2, length=3, ignore_crs=True)
        self.assertEqual('sq0', hash2)


if __name__ == '__main__':
    unittest.main()

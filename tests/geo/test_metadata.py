# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

import unittest
from pprint import pprint
import shapely.geometry
from georest.geo.metadata import Metadata, calc_bbox, calc_geohash
from georest.geo.spatialref import SpatialReference


class TestMetadata(unittest.TestCase):
    def test_make_metadata(self):
        geometry = shapely.geometry.Point(1, 1)
        geometry._crs = SpatialReference(srid=4326)
        metadata = Metadata.build_metadata(geometry=geometry)
        # pprint(metadata)
        self.assertIsInstance(metadata, Metadata)
        self.assertIsNotNone(metadata.created)
        self.assertIsNotNone(metadata.modified)
        self.assertIsNotNone(metadata.geohash)
        self.assertIsNone(metadata.etag)
        self.assertIsNotNone(metadata.bbox)


class TestHelpers(unittest.TestCase):
    def test_calc_bbox(self):
        geom1 = shapely.geometry.Point(5, 10)
        bbox1 = calc_bbox(geom1)
        self.assertListEqual(list(bbox1), [5, 10, 5, 10])

        geom2 = shapely.geometry.LineString([(5, 10), (10, 5)])
        bbox2 = calc_bbox(geom2)
        self.assertListEqual(list(bbox2), [5, 5, 10, 10])


    def test_calc_geohash(self):
        geom1 = shapely.geometry.Point(126, 48)
        hash1 = calc_geohash(geom1, precision=12)
        self.assertEqual('yb9954nkkb99', hash1)

        geom2 = shapely.geometry.LineString([(12, 34), (12.0001, 34.0001)])
        hash2 = calc_geohash(geom2, precision=12)
        self.assertEqual('sq093jd0', hash2)

        hash2 = calc_geohash(geom2, precision=3)
        self.assertEqual('sq0', hash2)


if __name__ == '__main__':
    unittest.main()

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/20/14'

import unittest
import uuid
from pprint import pprint

from georest.geo.engine import geos

from georest.geo import build_feature, build_feature_from_geojson
from georest.geo.feature import calc_etag, calc_bbox, calc_geohash


class TestFeatureHelpers(unittest.TestCase):
    def test_calc_etag(self):
        geom = geos.fromstr('POINT(10 10)')

        etag1 = calc_etag(geom, None)
        self.assertEqual(len(etag1), 40)

        etag2 = calc_etag(geom, {'foo': 'bar'})
        self.assertNotEqual(etag1, etag2)

        geom.set_srid(4326)
        etag3 = calc_etag(geom, None)
        self.assertNotEqual(etag1, etag3)

    def test_calc_bbox(self):
        geom1 = geos.fromstr('POINT(5 10)')
        bbox1 = calc_bbox(geom1)
        self.assertListEqual(bbox1, [5, 10, 5, 10])

        geom2 = geos.fromstr('LINESTRING(5 10, 10 5)')
        bbox2 = calc_bbox(geom2)
        self.assertListEqual(bbox2, [5, 5, 10, 10])

    def test_calc_geohash(self):
        geom1 = geos.fromstr('POINT(126 48)')
        hash1 = calc_geohash(geom1)
        self.assertEqual('yb9954nkkb99', hash1)

        geom2 = geos.fromstr('LINESTRING(12 34, 12.0001 34.0001)')
        hash2 = calc_geohash(geom2)
        self.assertEqual('sq093jd0', hash2)


class TestFeature(unittest.TestCase):
    def test_build(self):
        feat1 = build_feature('LINESTRING(0.03 0.04, 0.04 0.05, 0.06 0.07)',
                              properties={'hello': 'world'}, )
        self.assertEqual(feat1.geometry.srid, 4326)
        self.assertEqual(feat1.properties['hello'], 'world')


    def test_build_from_geojson(self):
        feat1 = build_feature_from_geojson('''
{ "type": "Feature",
    "geometry":  { "type": "Polygon",
        "coordinates": [
          [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],
          [ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]
          ]
    },
    "properties": {
      "hello": "world",
      "life": 42
    }
}
        ''')
        self.assertEqual(feat1.geometry.srid, 4326)
        self.assertEqual(feat1.properties['hello'], 'world')


if __name__ == '__main__':
    unittest.main()

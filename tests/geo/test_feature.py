# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/7/14'

import unittest
import json
import pickle

from georest.geo.feature import Feature
from georest.geo.geometry import Geometry
from georest.geo.exceptions import InvalidFeature, InvalidGeoJsonInput, \
    InvalidGeometry, InvalidProperties

from tests.geo.data import jsondata, pydata


class TestFeature(unittest.TestCase):
    def test_make_feature(self):
        feature1 = Feature.build_from_geometry('POINT (1 2)',
                                               properties=dict(x=1, y=2))
        self.assertEqual(feature1.crs.srid, 4326)
        self.assertEqual(feature1.properties['x'], 1)
        self.assertEqual(feature1.properties['y'], 2)
        self.assertIsNotNone(feature1.metadata.modified)

        feature2 = Feature.build_from_geojson(feature1.__geo_interface__)
        feature3 = Feature.build_from_geojson(feature1.geojson)
        self.assertTrue(feature2.equals(feature3))

    def test_create_from_geojson(self):
        for k, v in pydata.iteritems():
            data = {'type': 'Feature',
                    'geometry': v,
                    'properties':
                        {'type': 'snow'},
                    'crs':
                        {'type': 'name',
                         'properties': {
                             'name': 'EPSG:4326'
                         }}}
            feature = Feature.build_from_geojson(json.dumps(data))
            self.assertTrue(feature.geometry.equals(Geometry.build_geometry(v)))

    def test_create_fail(self):
        self.assertRaises(InvalidGeoJsonInput, Feature.build_from_geojson,
                          '{}')
        self.assertRaises(InvalidGeoJsonInput, Feature.build_from_geojson,
                          '{"type":"snow"}')

        self.assertRaises(InvalidGeoJsonInput, Feature.build_from_geojson,
                          '{"type":"Feature"}')

        self.assertRaises(InvalidGeometry, Feature.build_from_geojson,
                          '{"type":"Feature", "geometry": {} }')
        self.assertRaises(InvalidGeometry, Feature.build_from_geojson,
                          '''{"type":"Feature", "geometry": {"type": "Point",
                          "coordinates": [1] },
                          }''')
        self.assertRaises(InvalidFeature, Feature.build_from_geojson,
                          '''{"type":"Feature", "geometry": {"type": "Point",
                          "coordinates": "blah" },
                          }''')
        # self.assertRaises(InvalidProperties, Feature.build_from_geojson,
        # '''{"type":"Feature", "geometry": {"type": "Point",
        # "coordinates": [1, 2], "properties": "x" },
        #
        # }''')

    def test_duplicate(self):
        feature = Feature.build_from_geometry('POINT(1 1)', srid=4326)
        feature2 = feature.duplicate()
        self.assertTrue(feature2.equals(feature))

    def test_pickle(self):
        for k, v in pydata.iteritems():
            data = {'type': 'Feature',
                    'geometry': v,
                    'properties':
                        {'type': 'snow'},
                    'crs':
                        {'type': 'name',
                         'properties': {
                             'name': 'EPSG:4326'
                         }}}
            feature = Feature.build_from_geojson(json.dumps(data))
            buf = pickle.dumps(feature)
            feature2 = pickle.loads(buf)

            self.assertEqual(feature2.metadata, feature.metadata)
            self.assertTrue(feature2.equals(feature))


if __name__ == '__main__':
    unittest.main()

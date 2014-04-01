# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest
import json
import pickle

from georest.geo import Geometry, build_geometry, build_srs
from georest.geo.exception import GeoException


class TestGeometryBuilding(unittest.TestCase):
    def test_build_failure(self):
        self.assertRaises(GeoException, build_geometry, 'bad')
        self.assertRaises(GeoException, build_geometry, 'POINT(1 2, x)')
        self.assertRaises(GeoException, build_geometry, 'POINT(1 2)',
                          srid=123456)
        self.assertRaises(GeoException, build_geometry, 'POINT(1 2)',
                          srid='blah')
        self.assertRaises(GeoException, build_geometry,
                          'POLYGON((0 0, 1 0, 0 1, 1 1, 0 0))', )


    def test_build_geometry(self):
        geom = build_geometry(
            '{ "type": "Point", "coordinates": [ 1.0, 2.0 ] }', srid=4326)
        self.assertEqual(
            'POINT (1.0000000000000000 2.0000000000000000)',
            geom.wkt)
        self.assertEqual(
            'SRID=4326;POINT (1.0000000000000000 2.0000000000000000)',
            geom.ewkt)

    def test_geometry_methods(self):
        geom1 = build_geometry('POINT(1 2)', srid=4326)
        geom2 = build_geometry('POINT(3 4)', srid=4326)
        self.assertIsInstance(geom1.buffer(3), Geometry)
        self.assertIsInstance(geom1.union(geom2), Geometry)
        self.assertEqual(2, len(geom1))

    def test_geometry_methods_failure(self):
        geom1 = build_geometry('POINT(1 2)', srid=4326)
        self.assertIsInstance(geom1.buffer(0), Geometry)


class TestGeoJsonGeometryBuilding(unittest.TestCase):
    def setUp(self):
        # Sample geometry taken from
        #   http://geojson.org/geojson-spec.html#appendix-a-geometry-examples
        self.geoms = dict(
            point={'type': 'Point', 'coordinates': [100.0, 0.0]},
            linestring={'type': 'LineString',
                        'coordinates': [[100.0, 0.0], [101.0, 1.0]]},
            polygon={'type': 'Polygon',
                     'coordinates': [
                         [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                          [100.0, 1.0], [100.0, 0.0]],
                         [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8],
                          [100.2, 0.8], [100.2, 0.2]]
                     ]},
            multipoint=
            {'type': 'MultiPoint',
             'coordinates': [[100.0, 0.0], [101.0, 1.0]]},
            multilinestring={'type': 'MultiLineString',
                             'coordinates': [
                                 [[100.0, 0.0], [101.0, 1.0]],
                                 [[102.0, 2.0], [103.0, 3.0]]
                             ]},
            multipolygon={'type': 'MultiPolygon',
                          'coordinates': [
                              [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0],
                                [102.0, 3.0], [102.0, 2.0]]],
                              [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                                [100.0, 1.0], [100.0, 0.0]],
                               [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8],
                                [100.2, 0.8], [100.2, 0.2]]]
                          ]},
            geomcollection={'type': 'GeometryCollection',
                            'geometries': [
                                {'type': 'Point',
                                 'coordinates': [100.0, 0.0]
                                },
                                {'type': 'LineString',
                                 'coordinates': [[101.0, 0.0], [102.0, 1.0]]
                                }
                            ]},
        )

    def test_point(self):
        geom = build_geometry(json.dumps(self.geoms['point']), srid=4326)
        self.assertEqual(geom.geom_type, 'Point')
        self.assertEqual(self.geoms['point'], json.loads(geom.json))

    def test_linestring(self):
        geom = build_geometry(json.dumps(self.geoms['linestring']), srid=4326)
        self.assertEqual(geom.geom_type, 'LineString')
        self.assertEqual(self.geoms['linestring'], json.loads(geom.json))

    def test_polygon(self):
        geom = build_geometry(json.dumps(self.geoms['polygon']), srid=4326)
        self.assertEqual(geom.geom_type, 'Polygon')
        self.assertEqual(self.geoms['polygon'], json.loads(geom.json))

    def test_multipoint(self):
        geom = build_geometry(json.dumps(self.geoms['multipoint']), srid=4326)
        self.assertEqual(geom.geom_type, 'MultiPoint')

    def test_multilinestring(self):
        geom = build_geometry(json.dumps(self.geoms['multilinestring']),
                              srid=4326)
        self.assertEqual(geom.geom_type, 'MultiLineString')

    def test_multipolygon(self):
        geom = build_geometry(json.dumps(self.geoms['multipolygon']), srid=4326)
        self.assertEqual(geom.geom_type, 'MultiPolygon')

    def test_geomcollection(self):
        geom = build_geometry(json.dumps(self.geoms['geomcollection']),
                              srid=4326)
        self.assertEqual(geom.geom_type, 'GeometryCollection')
        self.assertEqual(2, geom.num_geom)

    def test_geomcollection(self):
        geom = build_geometry(json.dumps(self.geoms['geomcollection']),
                              srid=4326)
        self.assertEqual(geom.geom_type, 'GeometryCollection')
        self.assertEqual(2, geom.num_geom)

        print geom.the_geom[1]

    def test_feature(self):
        feat = {'type': 'Feature', 'geometry': self.geoms['point']}
        self.assertRaises(GeoException, build_geometry, json.dumps(feat),
                          srid=4326)


class TestGeometryPickle(unittest.TestCase):
    def test_pickle(self):
        geom1 = build_geometry('POINT(1 2)', 4326)
        pk = pickle.dumps(geom1)
        geom2 = pickle.loads(pk)

        self.assertEqual(geom1.ewkt, geom2.ewkt)
        self.assertEqual(geom1.srid, geom2.srid)


class TestSpatialReference(unittest.TestCase):
    def test_build_failure(self):
        self.assertRaises(GeoException, build_srs, 123445)
        self.assertRaises(GeoException, build_srs, 'wgs blah')

    def test_build_srs(self):
        self.assertRaises(GeoException, build_srs, 12345678)
        self.assertEqual(build_srs(4326).srid, 4326)
        self.assertEqual(build_srs('wgs84').srid, 4326)


class TestSpatialReferencePickling(unittest.TestCase):
    def test_pickle(self):
        srs = build_srs(3857)
        pk = pickle.dumps(srs)
        srs2 = pickle.loads(pk)

        self.assertEqual(srs.proj, srs2.proj)


if __name__ == '__main__':
    unittest.main()

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest
import pickle
from georest.geo import Geometry, GeoException, build_geometry, build_srs


class TestGeometryBuilding(unittest.TestCase):
    def test_build_failure(self):
        self.assertRaises(GeoException, build_geometry, 'bad')
        self.assertRaises(GeoException, build_geometry, 'POINT(1 2, x)')
        self.assertRaises(GeoException, build_geometry, 'POINT(1 2)',
                          srid=123456)

    def test_build_geojson(self):
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
        srs0 = build_srs(3857)
        srs1 = build_srs(4326)
        srs2 = build_srs('EPSG:4326')


if __name__ == '__main__':
    unittest.main()

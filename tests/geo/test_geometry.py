# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest
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

    def test_geometry_methods_failure(self):
        geom1 = build_geometry('POINT(1 2)', srid=4326)
        self.assertIsInstance(geom1.buffer(0), Geometry)


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

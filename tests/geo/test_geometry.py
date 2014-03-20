# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest

from georest.geo import Geometry, build_geometry, GeoException


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
        geom1 = build_geometry('POINT(1 2)', 4326)
        geom2 = build_geometry('POINT(3 4)', 4326)
        self.assertIsInstance(geom1.buffer(3), Geometry)
        self.assertIsInstance(geom1.union(geom2), Geometry)


if __name__ == '__main__':
    unittest.main()

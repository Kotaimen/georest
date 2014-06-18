# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/16/14'

import unittest

from georest.geo.operations import *
from georest.geo.geometry import Geometry


class TestUnaryOperation(unittest.TestCase):
    def test_unary(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = UnaryOperation(srid=3857)
        result = operation(this)
        reference = Geometry.build_geometry(
            'POINT (111319.4907932723 111325.1428663849)')
        reference.almost_equals(result, 9)


class TestAttributes(unittest.TestCase):
    def test_area_empty(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = Area()
        result = operation(this)
        self.assertAlmostEqual(result, 0.0)

    def test_area(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))')
        operation = Area()
        result = operation(this)
        self.assertAlmostEqual(result, 1.0)

    def test_length_zero(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = Length()
        result = operation(this)
        self.assertAlmostEqual(result, 0.0)

    def test_area(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 0, 1 1, 0 1)')
        operation = Length()
        result = operation(this)
        self.assertAlmostEqual(result, 3.0)


class TestUnaryPredicates(unittest.TestCase):
    def test_is_simple(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1, 1 -1, 0 1)')
        operation = IsSimple()
        result = operation(this)
        self.assertFalse(result)


class TestUnaryConstructors(unittest.TestCase):

    def test_buffer(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = Buffer(distance=1., resolution=50)
        result = operation(this)
        self.assertAlmostEqual(result.area, 3.1415927, delta=0.001)

    def test_covex_hull_of_point(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = ConvexHull()
        result = operation(this)
        self.assertTrue(result.equals(this))

    def test_convex_hull_of_points(self):
        this = Geometry.build_geometry(
            'MULTIPOINT (0 0, 1 1, 0 2, 2 2, 3 1, 1 0)')
        operation = ConvexHull()
        result = operation(this)
        reference = Geometry.build_geometry(
            'POLYGON ((0 0, 0 2, 2 2, 3 1, 1 0, 0 0))')
        self.assertTrue(result.equals(reference))

    def test_envelope(self):
        this = Geometry.build_geometry(
            'MULTIPOINT (0 0, 1 1, 0 2, 2 2, 3 1, 1 0)')
        operation = Envelope()
        result = operation(this)
        reference = Geometry.build_geometry(
            'POLYGON ((0 0, 3 0, 3 2, 0 2, 0 0))')
        self.assertTrue(result.equals(reference))

if __name__ == '__main__':
    unittest.main()

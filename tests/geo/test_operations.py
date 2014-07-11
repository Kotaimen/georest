# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/16/14'

import unittest

import shapely.geometry

from georest.geo.operations import *
from georest.geo.operations import ParameterHelper
from georest.geo.geometry import Geometry

from georest.geo.exceptions import InvalidParameter


class TestUnaryOperation(unittest.TestCase):
    def test_unary(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = UnaryOperation(srid=3857)
        result = operation(this)
        reference = Geometry.build_geometry(
            'POINT (111319.4907932723 111325.1428663849)')
        self.assertTrue(reference.almost_equals(result, 7))
        self.assertEqual(result.crs.srid, 3857)


    def test_crs(self):
        this = Geometry.build_geometry('POINT (1 1)')
        operation = UnaryOperation()

        result = operation(this)
        self.assertIsNotNone(result.crs)


class TestParameterHelper(unittest.TestCase):
    def setUp(self):
        self.helper = ParameterHelper(args=[])

    def test_check_float(self):
        self.assertRaises(InvalidParameter, self.helper.check_float, f=1)
        self.assertRaises(InvalidParameter, self.helper.check_float, f='a')
        self.assertEqual(1.0, self.helper.check_float(f=1.0))
        self.assertEqual(1.0, self.helper.check_float(f='1'))
        self.assertEqual(1.0, self.helper.check_float(f='1.0'))

    def test_check_integer(self):
        self.assertRaises(InvalidParameter, self.helper.check_integer, f=1.2)
        self.assertRaises(InvalidParameter, self.helper.check_integer, f='1.0')
        self.assertEqual(1, self.helper.check_integer(f=1))
        self.assertEqual(1, self.helper.check_integer(f='1'))

    def test_check_boolean(self):
        self.assertRaises(InvalidParameter, self.helper.check_boolean, f=2)
        self.assertRaises(InvalidParameter, self.helper.check_boolean, f='2')
        self.assertRaises(InvalidParameter, self.helper.check_boolean, f='yes')
        self.assertFalse(self.helper.check_boolean(f=False))
        self.assertFalse(self.helper.check_boolean(f='false'))
        self.assertFalse(self.helper.check_boolean(f='0'))
        self.assertTrue(self.helper.check_boolean(f=True))
        self.assertTrue(self.helper.check_boolean(f='true'))
        self.assertTrue(self.helper.check_boolean(f='1'))


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

    def test_parallel_offset(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        operation = ParallelOffset(distance=1., side='left')
        result = operation(this)
        self.assertEqual(result.geom_type, 'LineString')

    def test_simplify(self):
        this = Geometry.build_geometry(shapely.geometry.Point(1, 1).buffer(1.5))
        operation = Simplify(tolerance=0.05, preserve_topology=True)
        result = operation(this)
        self.assertTrue(result.area < this.area)


class TestUnarySetTheoreticMethods(unittest.TestCase):
    def test_boundary(self):
        this = Geometry.build_geometry(
            'POINT (0 0)')
        operation = Boundary()
        result = operation(this)
        self.assertTrue(result.is_empty)

    def test_centroid(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        operation = Centroid()
        result = operation(this)
        reference = Geometry.build_geometry('POINT (0.5 0.5)')
        self.assertTrue(result.almost_equals(reference))

    def test_pointonsurface(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        operation = PointOnSurface()
        result = operation(this)
        reference = Geometry.build_geometry('POINT (0.5 0.5)')
        self.assertFalse(result.almost_equals(reference))


class TestBinaryOperation(unittest.TestCase):
    def test_equals_yes(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('LINESTRING (0 0, 1 1.0001)')
        operation = Equals(decimal=3)
        result = operation(this, other)
        self.assertTrue(result)

    def test_equals_no(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('LINESTRING (0 0, 1 1.0001)')
        operation = Equals()
        result = operation(this, other)
        self.assertFalse(result)

    def test_contains_yes(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('POINT (0.5 0.5)')
        operation = Contains()
        result = operation(this, other)
        self.assertTrue(result)

    def test_contains_no(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('POINT (1 1)')
        operation = Contains()
        result = operation(this, other)
        self.assertFalse(result)

    def test_crosses_yes(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('LINESTRING (0 1, 1 0)')
        operation = Crosses()
        result = operation(this, other)
        self.assertTrue(result)

    def test_disjoint_no(self):
        this = Geometry.build_geometry('LINESTRING (0 0, 1 1)')
        other = Geometry.build_geometry('LINESTRING (0 1, 1 0)')
        operation = Crosses()
        result = operation(this, other)
        self.assertTrue(result)

    def test_intersects_yes(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        other = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1.5 0, 1.5 1, 0.5 0))')
        operation = Intersects()
        result = operation(this, other)
        self.assertTrue(result)

    def test_touches_no(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        other = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1.5 0, 1.5 1, 0.5 0))')
        operation = Touches()
        result = operation(this, other)
        self.assertFalse(result)

    def test_within_no(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        other = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1.5 0, 1.5 1, 0.5 0))')
        operation = Within()
        result = operation(this, other)
        self.assertFalse(result)


class TestBinarySetTheoreticMethods(unittest.TestCase):
    def test_intersection(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        other = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1.5 0, 1.5 1, 0.5 0))')
        operation = Intersection()
        result = operation(this, other)
        reference = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1 0, 1 0.5, 0.5 0))')
        self.assertTrue(result.equals(reference))

    def test_difference(self):
        this = Geometry.build_geometry('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        other = Geometry.build_geometry(
            'POLYGON ((0.5 0, 1.5 0, 1.5 1, 0.5 0))')
        operation = SymmetricDifference()
        result = operation(this, other)

        reference = Geometry.build_geometry(
            'MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0.5, 0.5 0, 0 0)), ((1 0, 1 0.5, 1.5 1, 1.5 0, 1 0)))')
        self.assertTrue(result.equals(reference))


class TestMultiOperations(unittest.TestCase):
    def test_cascade_union(self):
        pass


if __name__ == '__main__':
    unittest.main()


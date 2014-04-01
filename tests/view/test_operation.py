# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/25/14'

import unittest
import datetime
import json
from pprint import pprint

from georest import GeoRestApp
from georest.geo import build_feature

from tests.view import ResourceTestBase


class TestUnaryOperation(ResourceTestBase, unittest.TestCase):
    def test_get_type(self):
        response = self.client.get(
            path='/geometries/point1/type',
        )
        result = self.checkResponse(response, 200)

        self.assertEqual(result['result'], 'Point')


    def test_geometry_not_found(self):
        response = self.client.get(
            path='/geometries/what_ever/type',
        )
        result = self.checkResponse(response, 404)


    def test_operation_not_found(self):
        response = self.client.get(
            path='/geometries/point1/what_ever',
        )
        result = self.checkResponse(response, 400)


class TestBinaryOperation(ResourceTestBase, unittest.TestCase):
    def test_intersects(self):
        response = self.client.get(
            path='/geometries/point1/intersects/linestring1',
        )
        result = self.checkResponse(response, 200)
        self.assertEqual(result['result'], False)


    def test_geometry_not_found(self):
        response = self.client.get(
            path='/geometries/point1/intersects/what_ever',
        )
        result = self.checkResponse(response, 404)

    def test_geometry_identical(self):
        response = self.client.get(
            path='/geometries/point1/intersects/point1',
        )
        result = self.checkResponse(response, 400)


    def test_operation_not_found(self):
        response = self.client.get(
            path='/geometries/point1/what_ever/linestring1',
        )
        result = self.checkResponse(response, 400)


class TestUnaryGeometryProperties(ResourceTestBase, unittest.TestCase):
    def checkOp(self, key, operation, query={}):
        response = self.client.get(
            path='/geometries/%s/%s' % (key, operation),
            query_string=query
        )
        result = self.checkResponse(response)
        self.assertIn('result', result)
        return result['result']


    def test_get_type(self):
        self.assertEqual('Point', self.checkOp('point1', 'type'))
        self.assertEqual('LineString', self.checkOp('linestring1', 'type'))
        self.assertEqual('Polygon', self.checkOp('polygon1', 'type'))

    def test_coords(self):
        self.assertListEqual([0.0001, 0.0001], self.checkOp('point1', 'coords'))
        self.assertListEqual([[0.00015, -0.00015], [0.00016, -0.00017]],
                             self.checkOp('linestring1', 'coords'))

        self.assertNotEqual([0.0001, 0.0001],
                            self.checkOp('point1', 'coords', {'srid': 3857}))

    def test_area(self):
        self.assertAlmostEqual(0.0, self.checkOp('point1', 'area'))
        self.assertAlmostEqual(0.75, self.checkOp('polygon1', 'area'))
        self.assertAlmostEqual(9294375688,
                               self.checkOp('polygon1', 'area', {'srid': 3857}),
                               0)

    def test_length(self):
        self.assertAlmostEqual(0.0, self.checkOp('point1', 'length'))
        self.assertAlmostEqual(2.49, self.checkOp('linestring1', 'length',
                                                  {'srid': 3857}),
                               2)

    def test_is_empty(self):
        self.assertEqual(False, self.checkOp('point1', 'is_empty'))


class TestUnaryTopologicalProperties(ResourceTestBase, unittest.TestCase):
    def checkOp(self, key, operation, query={}):
        assert 'format' not in query
        response = self.client.get(
            path='/geometries/%s/%s' % (key, operation),
            query_string=query
        )
        result = self.checkResponse(response)
        return result

    def test_boundary(self):
        result = self.checkOp('polygon1', 'boundary')
        self.assertListEqual(result['coordinates'],
                             [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.5, 1.0],
                              [0.5, 0.5], [0.0, 0.5], [0.0, 0.0]])

    def test_centroid(self):
        result = self.checkOp('polygon1', 'centroid')
        # XXX: No idea why centroid is this...
        self.assertListEqual(result['coordinates'],
                             [0.583333333333333, 0.416666666666667])

    def test_convex_hull(self):
        result = self.checkOp('polygon1', 'convex_hull')
        self.assertListEqual(result['coordinates'],
                             [[[0.0, 0.0], [0.0, 0.5], [0.5, 1.0], [1.0, 1.0],
                               [1.0, 0.0], [0.0, 0.0]]])

    def test_envelope(self):
        result = self.checkOp('polygon1', 'envelope')
        self.assertListEqual(result['coordinates'],
                             [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0],
                               [0.0, 1.0], [0.0, 0.0]]])

    def test_point_on_surface(self):
        result = self.checkOp('polygon1', 'point_on_surface')
        self.assertListEqual(result['coordinates'],
                             [0.75, 0.75])


class TestUnaryTopologicalMethods(ResourceTestBase, unittest.TestCase):
    def checkOp(self, key, operation, query={}):
        assert 'format' not in query
        response = self.client.get(
            path='/geometries/%s/%s' % (key, operation),
            query_string=query
        )
        result = self.checkResponse(response)
        return result

    def test_buffer(self):
        result = self.checkOp('point1', 'buffer',
                              {
                                  'width': 0.001,
                                  'quadsec': 8,
                              })
        # XXX: make a proper check
        self.assertEqual(result['type'], 'Polygon')

    def test_simplify(self):
        result = self.checkOp('polygon1', 'simplify',
                              {
                                  'tolerance': 1,
                                  'topo': True,
                              })
        # XXX: make a proper check
        self.assertEqual(result['type'], 'Polygon')


class TestBinaryGeometryPredicates(ResourceTestBase, unittest.TestCase):
    def checkOp(self, this, operation, other, query={}):
        assert 'format' not in query
        response = self.client.get(
            path='/geometries/%s/%s/%s' % (this, operation, other),
            query_string=query
        )
        result = self.checkResponse(response)
        return result['result']

    def test_contains(self):
        self.assertTrue(self.checkOp('polygon1', 'contains', 'point1'))
        self.assertFalse(self.checkOp('point1', 'contains', 'polygon1'))

    def test_crosses(self):
        self.assertFalse(self.checkOp('polygon1', 'crosses', 'point1'))

    def test_disjoint(self):
        self.assertFalse(self.checkOp('polygon1', 'disjoint', 'point1'))

    def test_equals(self):
        self.assertFalse(self.checkOp('polygon1', 'equals', 'point1'))

    def test_intersects(self):
        self.assertFalse(self.checkOp('point1', 'intersects', 'linestring1'))

    def test_overlaps(self):
        self.assertFalse(self.checkOp('polygon1', 'overlaps', 'linestring1'))

    def test_within(self):
        self.assertTrue(self.checkOp('point1', 'within', 'polygon1'))


class TestUnaryTopologicalMethodsPost(ResourceTestBase, unittest.TestCase):
    def test_buffer(self):
        response = self.client.post(
            path='/operation/buffer' ,
            query_string={
                'width': 0.001,
                'quadsec': 8,
            },
            data='POINT(1 1)'
        )

        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()

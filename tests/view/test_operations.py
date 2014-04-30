# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/25/14'

import unittest
import json

from tests.view import ResourceTestBase


class TestUnaryGeometryProperties(ResourceTestBase, unittest.TestCase):
    def checkOp(self, key, operation, query=None):
        response = self.client.get(
            path='/operations/%s/%s' % (operation, key),
            query_string=query
        )
        result = self.checkResponse(response)
        self.assertIn('result', result)
        return result['result']

    def test_invalid_operation(self):
        response = self.client.get(
            path='/operations/invalid/blah'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_type(self):
        self.assertEqual('Point', self.checkOp('point1', 'type'))
        self.assertEqual('LineString', self.checkOp('linestring1', 'type'))
        self.assertEqual('Polygon', self.checkOp('polygon1', 'type'))

    def test_get_geoms(self):
        self.assertEqual(1, self.checkOp('point1', 'geoms'))

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
    def checkOp(self, key, operation, query=None):
        response = self.client.get(
            path='/operations/%s/%s' % (operation, key),
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
    def checkOp(self, key, operation, query=None):
        assert 'format' not in query
        response = self.client.get(
            path='/operations/%s/%s' % (operation, key),
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
    def checkOp(self, this, operation, other, query=None):
        response = self.client.get(
            path='/operations/%s/%s/%s' % (operation, this, other),
            query_string=query
        )
        result = self.checkResponse(response)
        return result['result']

    def test_invalid_operation(self):
        response = self.client.get(
            path='/operations/invalid/foo/bar'
        )
        self.assertEqual(response.status_code, 400)

    def test_contains(self):
        self.assertTrue(self.checkOp('polygon1', 'contains', 'point1'))
        self.assertFalse(self.checkOp('point1', 'contains', 'polygon1'))
        self.assertTrue(self.checkOp('polygon1', 'contains', 'point1',
                                     query={'srid': 3857}))
        self.assertFalse(self.checkOp('point1', 'contains', 'polygon1',
                                      query={'srid': 3857}))

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


class TestBinaryTopologicalMethods(ResourceTestBase, unittest.TestCase):
    def checkOp(self, this, operation, other, query=None):
        response = self.client.get(
            path='/operations/%s/%s/%s' % (operation, this, other),
            query_string=query
        )
        result = self.checkResponse(response)
        return result

    def test_union(self):
        result = self.checkOp('point1', 'union', 'linestring1')
        self.assertEqual(result['type'], 'GeometryCollection')

    def test_intersection(self):
        result = self.checkOp('point1', 'intersection', 'linestring1')

    def test_difference(self):
        result = self.checkOp('point1', 'difference', 'linestring1')

    def test_distance(self):
        result = self.checkOp('point1', 'distance', 'linestring1')


#
# Only check endpoints here, full api check is done above
#

class TestGetUnaryOperation(ResourceTestBase, unittest.TestCase):
    def test_get_type(self):
        response = self.client.get(
            path='/operations/type/point1',
        )
        result = self.checkResponse(response, 200)

        self.assertEqual(result['result'], 'Point')

    def test_geometry_not_found(self):
        response = self.client.get(
            path='/operations/type/what_ever',
        )
        result = self.checkResponse(response, 404)

    def test_operation_not_found(self):
        response = self.client.get(
            path='/operations/what_ever/point1',
        )
        result = self.checkResponse(response, 400)


class TestGetBinaryOperation(ResourceTestBase, unittest.TestCase):
    def test_intersects(self):
        response = self.client.get(
            path='/operations/intersects/point1/linestring1',
        )
        result = self.checkResponse(response, 200)
        self.assertEqual(result['result'], False)

    def test_geometry_not_found(self):
        response = self.client.get(
            path='/operations/intersects/point1/what_ever',
        )
        result = self.checkResponse(response, 404)

    def test_geometry_identical(self):
        response = self.client.get(
            path='/operations/point1/intersects/point1',
        )
        result = self.checkResponse(response, 400)

    def test_operation_not_found(self):
        response = self.client.get(
            path='/operations/what_ever/point1/linestring1',
        )
        result = self.checkResponse(response, 400)


class TestPostOperation(ResourceTestBase, unittest.TestCase):
    def test_type(self):
        response = self.client.post(
            path='/operations/type',
            query_string={
                'width': 0.001,
                'quadsec': 8,
            },
            data='POINT(1 1)'
        )

        result = self.checkResponse(response)

        self.assertEqual(result['result'], 'Point')


    def test_buffer(self):
        response = self.client.post(
            path='/operations/buffer',
            query_string={
                'width': 0.001,
                'quadsec': 8,
                'format': 'json',
            },
            data='POINT(1 1)'
        )

        result = self.checkResponse(response)
        self.assertEqual(result['type'], 'Polygon')

    def test_union(self):
        response = self.client.post(
            path='/operations/union',
            data=json.dumps({"type": "GeometryCollection",
                             "geometries": [
                                 {"type": "Point",
                                  "coordinates": [100.0, 0.0]
                                 },
                                 {"type": "LineString",
                                  "coordinates": [[101.0, 0.0], [102.0, 1.0]]
                                 }
                             ]
            })
        )
        result = self.checkResponse(response)
        self.assertEqual(result['type'], 'GeometryCollection')

    def test_intersects(self):
        response = self.client.post(
            path='/operations/intersects/polygon1',
            data=json.dumps({"type": "LineString",
                             "coordinates": [[101.0, 0.0], [102.0, 1.0]]})
        )
        result = self.checkResponse(response)
        self.assertFalse(result['result'])


if __name__ == '__main__':
    unittest.main()

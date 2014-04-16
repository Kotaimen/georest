# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest
import datetime
import json
from pprint import pprint

from tests.view import ResourceTestBase


class TestGeometryGet(ResourceTestBase, unittest.TestCase):
    def test_get_geometry(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s/geometry' % key,
            query_string={'format': 'json'},
        )

        result = self.checkResponse(response, 200)

        self.assertEqual(response.headers['Etag'], self.feature1.etag)
        self.assertEqual(response.date, self.feature1.created)
        self.assertEqual(response.last_modified, self.feature1.modified)
        expires = self.feature1.created + datetime.timedelta(
            seconds=self.app.config['EXPIRES'])
        self.assertEqual(response.expires, expires)
        self.assertEqual(result,
                         json.loads(self.feature1.geometry.json))

    def test_get_geometry_not_found(self):
        key = 'never_found'

        response = self.client.get(
            path='/features/%s/geometry' % key,
            query_string={},
        )

        self.checkResponse(response, 404)

    def test_get_geometry_ewkt(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s/geometry' % key,
            query_string={'format': 'ewkt', 'srid': 3857},
        )
        self.assertEqual('text/plain', response.content_type)
        self.assertNotEqual(response.data,
                            self.feature1.geometry.ewkt)

    def test_get_geometry_ewkb(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s/geometry' % key,
            query_string={'format': 'ewkb'},
        )
        self.assertEqual('application/oct-stream', response.content_type)
        self.assertEqual(response.data, str(self.feature1.geometry.ewkb))


class TestGeometryPut(ResourceTestBase, unittest.TestCase):
    def test_put_geometry(self):
        key = 'geometry'
        data = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.put(
            path='/features/%s/geometry' % key,
            data=data,
            query_string={'prefix': 'a_'},
            content_type='application/json',
        )

        result = self.checkResponse(response, 201)

        self.assertEqual(result['key'], 'a_geometry')

        self.assertEqual(201, result['code'])
        self.assertIn('Etag', response.headers)
        self.assertIsInstance(response.date, datetime.datetime)
        self.assertIsInstance(response.last_modified, datetime.datetime)
        self.assertIsInstance(response.expires, datetime.datetime)

    def test_put_geometry_bad_key(self):
        key = 'very bad key'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.put(
            path='/features/%s/geometry' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 400)

        self.assertIn('message', result)
        self.assertEqual(result['exception'], 'InvalidKey')

    def test_put_geometry_bad_geometry(self):
        key = 'bad_geometry'
        payload = json.dumps(
            {'type': 'what ever', 'coordinates': 'where am i?'})

        response = self.client.put(
            path='/features/%s/geometry' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 400)

        self.assertIn('message', result)
        self.assertEqual(result['exception'], 'InvalidGeometry')

    def test_put_geometry_key_duplicate(self):
        key = 'point1'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.put(
            path='/features/%s/geometry' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 409)

        self.assertIn('message', result)
        self.assertEqual(result['exception'], 'GeometryAlreadyExists')


class TestGeometryPost(ResourceTestBase, unittest.TestCase):
    def test_post_geometry_invalid(self):
        key = 'point1'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.post(
            path='/features/%s/geometry' % key,
            data=payload,
            content_type='application/json',
        )

        self.checkResponse(response, 405)

    def test_post_geometry_without_key(self):
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.post(
            path='/features/geometry',
            data=payload,
            query_string={'prefix': 'blah-'},
            content_type='application/json',
        )

        result = self.checkResponse(response, 201)
        self.assertIn('key', result)
        self.assertIsNotNone(result['key'])
        self.assert_(result['key'].startswith('blah-'))
        self.assertEqual(result['code'], 201)


if __name__ == '__main__':
    unittest.main()

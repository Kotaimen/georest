# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/25/14'

import unittest
import datetime
import json

from tests.view import ResourceTestBase


class TestFeatureGet(ResourceTestBase, unittest.TestCase):
    def test_get_feature(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s' % key,
        )

        result = self.checkResponse(response, 200)

        self.assertEqual(response.headers['Etag'], self.feature1.etag)
        self.assertEqual(response.date, self.feature1.created)
        self.assertEqual(response.last_modified, self.feature1.modified)
        expires = self.feature1.created + datetime.timedelta(
            seconds=self.app.config['EXPIRES'])
        self.assertEqual(response.expires, expires)

        self.assertEqual(result['geometry'],
                         json.loads(self.feature1.geometry.json))
        self.assertEqual(result['type'], 'Feature')
        self.assertIn('_key', result)
        self.assertIn('_geohash', result)
        self.assertIn('bbox', result)
        self.assertIn('crs', result)

    def test_get_feature_with_prefix(self):
        key = '1'

        response = self.client.get(
            path='/features/%s' % key,
            query_string={'prefix': 'point'},
        )

        result = self.checkResponse(response, 200)

    def test_get_feature_geohash(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s/geohash' % key,
        )
        result = self.checkResponse(response, 200)
        self.assertEqual(result['result'], 's0000000d6ds')

    def test_get_feature_bbox(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s/bbox' % key,
        )
        result = self.checkResponse(response, 200)
        self.assertListEqual(result['result'], [0.0001, 0.0001, 0.0001, 0.0001])


class TestFeaturePut(ResourceTestBase, unittest.TestCase):
    def setUp(self):
        ResourceTestBase.setUp(self)

        self.payload = json.dumps(
            {"type": "Feature",
             "geometry": {"type": "Polygon",
                          "coordinates": [
                              [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                               [100.0, 1.0], [100.0, 0.0]],
                              [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8],
                               [100.2, 0.8], [100.2, 0.2]]
                          ]
             },
             "properties": {
                 "hello": "world",
                 "life": 42
             }
            })

    def test_post_feature(self):
        payload = self.payload

        response = self.client.post(
            path='/features',
            data=payload
        )
        self.checkResponse(response, 201)

    def test_post_feature_with_prefix(self):
        payload = self.payload

        response = self.client.post(
            path='/features',
            data=payload,
            query_string={'prefix': 'point'},
        )

        self.checkResponse(response, 201)

    def test_put_feature(self):
        payload = self.payload

        response = self.client.put(
            path='/features/blah',
            data=payload
        )
        self.checkResponse(response, 201)

    def test_put_feature_with_prefix(self):
        payload = self.payload

        response = self.client.put(
            path='/features/blah',
            data=payload,
            query_string={'prefix': 'foo.'},
        )

        self.checkResponse(response, 201)


class TestFeatureDelete(ResourceTestBase, unittest.TestCase):
    def test_delete_feature(self):
        key = 'linestring1'
        path = '/features/%s' % key
        self.checkResponse(self.client.get(path=path), 200)
        self.checkResponse(self.client.delete(path=path), 204)
        self.checkResponse(self.client.get(path=path), 404)
        self.checkResponse(self.client.delete(path=path), 404)


if __name__ == '__main__':
    unittest.main()

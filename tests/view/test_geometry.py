# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import unittest
import datetime
import json
from pprint import pprint

from georest import GeoRestApp
from georest.geo import build_feature


class ResourceTestBase(object):
    def setUp(self):
        # Build test features

        # Round timestamp since http header timestamp has 1 second resolution
        timestamp = datetime.datetime.utcnow().replace(microsecond=0)

        self.feature1 = build_feature('POINT (0.0001 0.0001)',
                                      {'name': 'feature1'},
                                      srid=4326,
                                      id_=1,
                                      created=timestamp)

        # Reset modified timestamp since build_feature recalculates it
        self.feature1._modified = timestamp

        self.feature2 = build_feature(
            'LINESTRING (0.00015 -0.00015, 0.00016 -0.00017)',
            {'name': 'feature2'})

        # Load test settings
        settings = {
            'GEOREST_GEOSTORE_CONFIG': {'type': 'simple'},
            'GEOREST_GEOMODEL_CONFIG': {'type': 'simple'},
        }

        # Create test app
        self.app = GeoRestApp(settings=settings)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Preload test features into store
        self.app.model.store.put_feature(self.feature1, 'point1')
        self.app.model.store.put_feature(self.feature2, 'point2')

    def tearDown(self):
        pass

    def checkResponse(self, response, status_code=200):
        self.assertEqual(status_code, response.status_code)
        self.assertEqual('application/json', response.content_type)
        data = json.loads(response.data)
        return data


class TestGeometryGet(ResourceTestBase, unittest.TestCase):
    def test_get_geometry(self):
        key = 'point1'

        response = self.client.get(
            path='/geometry/%s' % key,
            query_string={'format': 'json'},
        )

        result = self.checkResponse(response, 200)

        self.assertEqual(response.headers['Etag'], self.feature1.etag)
        self.assertEqual(response.date, self.feature1.created)
        self.assertEqual(response.last_modified, self.feature1.modified)
        expires = self.feature1.created + \
                  datetime.timedelta(seconds=self.app.config['EXPIRES'])
        self.assertEqual(response.expires, expires)

    def test_get_geometry_not_found(self):
        key = 'never_found'

        response = self.client.get(
            path='/geometry/%s' % key,
            query_string={},
        )

        self.checkResponse(response, 404)


class TestGeometryPut(ResourceTestBase, unittest.TestCase):
    def test_put_geometry(self):
        key = 'geometry1'
        data = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.post(
            path='/geometry/%s' % key,
            data=data,
            content_type='application/json',
        )

        self.checkResponse(response, 201)

        self.assertIn('Etag', response.headers)
        self.assertIsInstance(response.date, datetime.datetime)
        self.assertIsInstance(response.last_modified, datetime.datetime)
        self.assertIsInstance(response.expires, datetime.datetime)

    def test_put_geometry_bad_key(self):
        key = 'very bad key'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.post(
            path='/geometry/%s' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 400)

        self.assertIn('message', result)
        self.assertRegexpMatches(result['message'], r'^Invalid key.*')

    def test_put_geometry_bad_geometry(self):
        key = 'bad_geometry'
        payload = json.dumps(
            {'type': 'what ever', 'coordinates': 'where am i?'})

        response = self.client.post(
            path='/geometry/%s' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 400)

        self.assertIn('message', result)
        self.assertRegexpMatches(result['message'], r'^Invalid geometry.*')

    def test_put_geometry_key_duplicate(self):
        key = 'point1'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.client.post(
            path='/geometry/%s' % key,
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 409)

        self.assertIn('message', result)
        self.assertRegexpMatches(result['message'], r'^Geometry exists.*')


class TestGeometryDelete(ResourceTestBase, unittest.TestCase):
    def test_delete_geometry(self):
        key = 'point2'
        path = '/geometry/%s' % key
        self.checkResponse(self.client.get(path=path), 200)
        self.checkResponse(self.client.delete(path=path), 200)
        self.checkResponse(self.client.get(path=path), 404)
        self.checkResponse(self.client.delete(path=path), 404)


if __name__ == '__main__':
    unittest.main()

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
        self.timestamp = datetime.datetime.utcnow()
        feature1 = build_feature('POINT (0.0001 0.0001)',
                                 {'name': 'feature1'},
                                 srid=4326,
                                 id_=1,
                                 created=self.timestamp)
        feature2 = build_feature('POINT (0.00015 -0.00015)',
                                 {'name': 'feature2'})

        # Load test settings
        settings = {
            'GEOREST_GEOSTORE_CONFIG': {'type': 'simple'},
            'GEOREST_GEOMODEL_CONFIG': {'type': 'simple'},
            'LOGGER_NAME': 'blah'
        }

        # Create test app
        app = GeoRestApp(settings=settings)
        app.config['TESTING'] = True
        self.app = app.test_client()

        # Preload test features into store
        app.model.store.put_feature(feature1, 'point1')
        app.model.store.put_feature(feature2, 'point2')

    def tearDown(self):
        pass

    def checkResponse(self, response, status_code=200):
        self.assertEqual(status_code, response.status_code)
        self.assertEqual('application/json', response.content_type)
        data = json.loads(response.data)
        return data


class TestGeometryGet(ResourceTestBase, unittest.TestCase):
    pass


class TestGeometryPut(ResourceTestBase, unittest.TestCase):
    def test_put_geometry(self):
        key = 'geometry1'
        data = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.app.post(
            path='/geometry/%s' % key,
            query_string={},
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

        response = self.app.post(
            path='/geometry/%s' % key,
            query_string={},
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

        response = self.app.post(
            path='/geometry/%s' % key,
            query_string={},
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 400)

        self.assertIn('message', result)
        self.assertRegexpMatches(result['message'], r'^Invalid geometry.*')

    def test_put_geometry_key_duplicate(self):
        key = 'point1'
        payload = json.dumps({'type': 'Point', 'coordinates': [1, 2]})

        response = self.app.post(
            path='/geometry/%s' % key,
            query_string={},
            data=payload,
            content_type='application/json',
        )

        result = self.checkResponse(response, 409)

        self.assertIn('message', result)
        self.assertRegexpMatches(result['message'], r'^Geometry exists.*')


if __name__ == '__main__':
    unittest.main()

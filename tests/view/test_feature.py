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


class TestFeatureGet(ResourceTestBase, unittest.TestCase):
    def test_get_feature(self):
        key = 'point1'

        response = self.client.get(
            path='/features/%s' % key,
            query_string={'format': 'json'},
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
        self.assertIn('_id', result)
        self.assertIn('_geohash', result)
        self.assertIn('bbox', result)
        self.assertIn('crs', result)

if __name__ == '__main__':
    unittest.main()

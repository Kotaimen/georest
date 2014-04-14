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



class TestFeaturePut():
    pass



# class TestGeometryDelete(ResourceTestBase, unittest.TestCase):
#     def test_delete_geometry(self):
#         key = 'linestring1'
#         path = '/features/%s/geometry' % key
#         self.checkResponse(self.client.get(path=path), 200)
#         self.checkResponse(self.client.delete(path=path), 200)
#         self.checkResponse(self.client.get(path=path), 404)
#         self.checkResponse(self.client.delete(path=path), 404)




if __name__ == '__main__':
    unittest.main()

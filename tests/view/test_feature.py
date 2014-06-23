# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/11/14'

import json
from datetime import datetime
import unittest
from tests.view.base import ViewTestMixin


class StorageViewBase(ViewTestMixin):
    def test_get_ok(self):
        self.model.get.return_value = self.data, {'last_modified': datetime(2014, 6, 20, 1, 0, 0), 'etag': 'foooo'}
        self.model.as_json.return_value = self.jdata
        r = self.client.get(self.get_url)
        self.assertEqual(r.status_code, 200)
        self.model.get.assert_called_once_with(self.key)
        self.model.as_json.assert_called_once_with(self.data)

    def test_get_not_modified(self):
        # in this case, foo.bar is not modified since '2014-06-20-01:00:00 GMT'
        self.model.get.return_value = self.data, {'last_modified': datetime(2014, 6, 20, 1, 0, 0)}
        self.model.as_json.return_value = self.jdata
        d = datetime(2014, 6, 20, 2, 0, 0)
        r = self.client.get(self.get_url, headers={'If-Modified-Since': d.strftime('%a, %d %b %Y %H:%M:%S GMT')})
        self.assertEqual(r.status_code, 304)
        self.model.get.assert_called_once_with(self.key)

    def test_get_non_match(self):
        # in this case, foo.bar is already has etag 'hodorhodorhodor'
        self.model.get.return_value = self.data, {'etag': 'hodorhodorhodor'}
        self.model.as_json.return_value = self.jdata
        r = self.client.get(self.get_url,
                            headers={'If-None-Match': '"hodorhodorhodor"'})
        self.assertEqual(r.status_code, 304)
        self.model.get.assert_called_once_with(self.key)

    def test_put_ok(self):
        r = self.client.put(self.put_url, data=self.jdata,
                            content_type='application/json')
        self.assertEqual(r.status_code, 201)
        rv = json.loads(r.data)
        self.assertEqual(rv['key'], self.key)

    @unittest.skip('Not in thin wrapper')
    def test_put_conflict(self):
        pass

    def test_post_ok(self):
        self.model.create.return_value = 'foo.shoot', {'etag': 'hodorx2'}
        self.model.from_json.return_value = self.data
        r = self.client.post(self.post_url, data=self.jdata,
                             content_type='application/json')

        self.model.create.assert_called_once_with(self.data, bucket=self.bucket)
        self.model.from_json.assert_called_once_with(self.jdata)
        self.assertEqual(r.status_code, 201)
        rv = json.loads(r.data)
        self.assertEqual(rv['key'], 'foo.shoot')
        self.assertEqual(rv['etag'], 'hodorx2')
        self.assertEqual(r.headers['ETag'], '"hodorx2"')


class TestFeatures(StorageViewBase, unittest.TestCase):
    def setUp(self):
        super(TestFeatures, self).setUp()
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [1, 2]
            }
        }
        self.jdata = json.dumps(self.data)
        self.model = self.mock_feature_model
        self.get_url = '/features/foo.bar'
        self.put_url = '/features/foo.bar'
        self.post_url = '/features?bucket=foo'
        self.bucket = 'foo'
        self.key = 'foo.bar'


class TestGeometry(StorageViewBase, unittest.TestCase):
    def setUp(self):
        super(TestGeometry, self).setUp()
        self.data = {
            "type": "Point",
            "coordinates": [1, 2]
        }
        self.jdata = json.dumps(self.data)
        self.model = self.mock_geometry_model
        self.get_url = '/features/foo.bar/geometry'
        self.put_url = '/features/foo.bar/geometry'
        self.post_url = '/geometries?bucket=foo'
        self.bucket = 'foo'
        self.key = 'foo.bar'


class TestProperties(StorageViewBase, unittest.TestCase):
    def setUp(self):
        super(TestProperties, self).setUp()
        self.data = {
            "hodor": "hodor",
            "foo": "kung"
        }
        self.jdata = json.dumps(self.data)
        self.model = self.mock_feature_prop_model
        self.get_url = '/features/foo.bar/properties'
        self.put_url = '/features/foo.bar/properties'
        # self.post_url = '/geometries?bucket=foo'
        self.bucket = 'foo'
        self.key = 'foo.bar'

    @unittest.skip('No post for properties')
    def test_post_ok(self):
        pass

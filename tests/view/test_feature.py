# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/11/14'

import json
from datetime import datetime
import unittest
from tests.view.base import ViewTestMixin


class TestFeature(ViewTestMixin, unittest.TestCase):

    def setUp(self):
        super(TestFeature, self).setUp()
        self.data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [[1, 2], [3, 4]]
            }
        }
        self.jdata = json.dumps(self.data)
        self.model = self.mock_feature_model

    def test_get_ok(self):
        self.model.get.return_value = self.data, {'last_modified': datetime(2014, 6, 20, 1, 0, 0), 'etag': 'foooo'}
        self.model.as_json.return_value = self.jdata
        r = self.client.get('/features/foo.bar')
        self.assertEqual(r.status_code, 200)
        self.model.get.assert_called_once_with('foo.bar')
        self.model.as_json.assert_called_once_with(self.data)

    def test_get_not_modified(self):
        # in this case, foo.bar is not modified since '2014-06-20-01:00:00 GMT'
        self.model.get.return_value = self.data, {'last_modified': datetime(2014, 6, 20, 1, 0, 0)}
        self.model.as_json.return_value = self.jdata
        d = datetime(2014, 6, 20, 2, 0, 0)
        r = self.client.get('/features/foo.bar', headers={'If-Modified-Since': d.strftime('%a, %d %b %Y %H:%M:%S GMT')})
        self.assertEqual(r.status_code, 304)
        self.model.get.assert_called_once_with('foo.bar')

    def test_get_non_match(self):
        # in this case, foo.bar is already has etag 'hodorhodorhodor'
        self.model.get.return_value = self.data, {'etag': 'hodorhodorhodor'}
        self.model.as_json.return_value = self.jdata
        r = self.client.get('/features/foo.bar',
                            headers={'If-None-Match': '"hodorhodorhodor"'})
        self.assertEqual(r.status_code, 304)
        self.model.get.assert_called_once_with('foo.bar')

    def test_put_ok(self):
        r = self.client.put('/features/foo.bar', data=self.jdata,
                            content_type='application/json')
        self.assertEqual(r.status_code, 201)
        rv = json.loads(r.data)
        self.assertEqual(rv['key'], 'foo.bar')

    @unittest.skip('Not in thin wrapper')
    def test_put_conflict(self):
        pass

    def test_post_ok(self):
        self.model.create.return_value = 'foo.shoot', {'etag': 'hodorx2'}
        self.model.from_json.return_value = self.data
        r = self.client.post('/features?bucket=foo', data=self.jdata,
                             content_type='application/json')

        self.model.create.assert_called_once_with(self.data, bucket='foo')
        self.model.from_json.assert_called_once_with(self.jdata)
        self.assertEqual(r.status_code, 201)
        rv = json.loads(r.data)
        self.assertEqual(rv['key'], 'foo.shoot')
        self.assertEqual(rv['etag'], 'hodorx2')
        self.assertEqual(r.headers['ETag'], '"hodorx2"')

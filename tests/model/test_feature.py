# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/24/14'


import json
import unittest
from tests.view.base import ViewTestMixin
from georest.storage import build_feature_storage
from georest.model import *
from georest import geo


class FeatureModelMixin(object):
    """injects the test storage, etc"""
    def setUp(self):
        self.storage = build_feature_storage(prototype='dummy')

    def test_from_json(self):
        """
        used attachments:
          - self.model
          - self.jsonobj
          - self.obj
        """
        self.assertEqual(self.model.from_json(self.jsonobj), self.obj)

    def test_as_json(self):
        """
        used attachments:
          - self.model
          - self.jsonobj
          - self.obj
        """
        self.assertEqual(json.loads(self.model.as_json(self.obj)), json.loads(self.jsonobj))


class TestFeatureModel(FeatureModelMixin, unittest.TestCase):
    def setUp(self):
        super(TestFeatureModel, self).setUp()
        self.model = FeatureModel(self.storage)
        self.jsonobj = '{"type":"Feature","id":"foo.?","geometry":{"type":"LineString","coordinates":[[102.0,0.0],[103.0,1.0]]},"properties":{"prop1":0.0,"prop0":"value0"}}'
        self.obj = geo.Feature.build_from_geojson(self.jsonobj, key=geo.Key.make_key(bucket='foo'))
        self.bucket = 'foo'
        self.key = 'foo.bar'

    def test_from_json(self):
        self.assert_(self.model.from_json(self.jsonobj).equals(self.obj))

    def test_create_get(self):
        key, metadata = self.model.create(self.obj, bucket=self.bucket)
        r_obj, r_metadata = self.model.get(key)
        self.assertEqual(metadata, r_metadata)
        self.assert_(self.obj.equals(r_obj))

    def test_put_get(self):
        metadata = self.model.put(self.obj, key=self.key)
        r_obj, r_metadata = self.model.get(self.key)
        self.assertEqual(metadata, r_metadata)
        self.assert_(self.obj.equals(r_obj))


class TestGeometryModel(FeatureModelMixin, unittest.TestCase):
    def setUp(self):
        super(TestGeometryModel, self).setUp()
        self.model = GeometryModel(self.storage)
        self.jsonobj = '{"type":"LineString","coordinates":[[102.0,0.0],[103.0,1.0]]}'
        self.obj = geo.Geometry.build_geometry(self.jsonobj)
        self.bucket = 'foo'
        self.key = 'foo.bar'

    def test_from_json(self):
        self.assert_(self.model.from_json(self.jsonobj).equals(self.obj))

    def test_create_get(self):
        key, metadata = self.model.create(self.obj, bucket=self.bucket)
        r_obj, r_metadata = self.model.get(key)
        self.assertEqual(metadata, r_metadata)
        self.assert_(self.obj.equals(r_obj))

    def test_put_get(self):
        metadata = self.model.put(self.obj, key=self.key)
        r_obj, r_metadata = self.model.get(self.key)
        self.assertEqual(metadata, r_metadata)
        self.assert_(self.obj.equals(r_obj))


class TestPropertiesModel(FeatureModelMixin, unittest.TestCase):
    def setUp(self):
        super(TestPropertiesModel, self).setUp()
        self.model = FeaturePropertiesModel(self.storage)
        self.jsonobj = '{"hodor":"hodor","leaf":"scorch"}'
        self.obj = json.loads(self.jsonobj)
        self.bucket = 'foo'
        self.key = 'foo.bar'
        # store a feature first to test put
        feature_model = FeatureModel(self.storage)
        feature_key = geo.Key.build_from_qualified_name('foo.bar')
        feature_json = '{"type":"Feature","geometry":{"type":"Point","coordinates":[30,10]},"properties":{}}'
        feature = geo.Feature.build_from_geojson(feature_json,
                                                 key=feature_key)
        feature_model.put(feature, self.key)

    def test_from_json(self):
        self.assertEqual(self.model.from_json(self.jsonobj), self.obj)

    def test_put_get(self):
        metadata = self.model.put(self.obj, key=self.key)
        r_obj, r_metadata = self.model.get(self.key)
        self.assertEqual(metadata, r_metadata)
        self.assertEqual(self.obj, r_obj)

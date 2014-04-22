# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/21/14'

import unittest

from georest.geo import build_feature, build_geometry, Feature
from georest.store import build_store
from georest.store.simple import SimpleGeoStore
from georest.store.exception import *


class SimpleStoreTestBase(object):
    def setUp(self):
        self.store = build_store('simple')
        assert isinstance(self.store, SimpleGeoStore)
        self.feature = build_feature('POINT(1 1)', {'foo': 'bar', 'answer': 42})


class TestSimpleStoreFeature(unittest.TestCase, SimpleStoreTestBase):
    def setUp(self):
        self.store = build_store('simple')
        assert isinstance(self.store, SimpleGeoStore)
        self.feature = build_feature('POINT(1 1)', {'foo': 'bar', 'answer': 42})
        self.geomerty = build_geometry('LINESTRING(0 0, 1 1)')

    def tearDown(self):
        del self.store

    def test_describe(self):
        self.assert_(self.store.describe())

    def test_feature_get(self):
        self.assertRaises(FeatureDoesNotExist, self.store.get_feature, 'none')

    def test_feature_put_no_prefix(self):
        ret = self.store.put_feature(self.feature, key='1', prefix='blah')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'blah1')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

    def test_feature_put_with_prefix(self):
        ret = self.store.put_feature(self.feature, key='blah2')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'blah2')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

    def test_feature_put_duplicate(self):
        ret = self.store.put_feature(self.feature, key='blah')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'blah')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

        self.assertRaises(FeatureAlreadyExists, self.store.put_feature,
                          self.feature, key='blah')

        ret = self.store.delete_feature('blah')
        self.assertIsNone(ret)

        self.assertRaises(FeatureDoesNotExist, self.store.delete_feature,
                          'blah')

    def test_feature_put_randomkey(self):
        ret = self.store.put_feature(self.feature, prefix='blah')
        self.assertIsInstance(ret, Feature)
        self.assertNotEqual(ret.key, 'blah')
        self.assert_(ret.key.startswith('blah'))


class TestSimpleStoreGeometry(unittest.TestCase, SimpleStoreTestBase):
    def setUp(self):
        self.store = build_store('simple')
        assert isinstance(self.store, SimpleGeoStore)
        self.feature = build_feature('POINT(1 1)', {'foo': 'bar', 'answer': 42})
        self.geomerty = build_geometry('LINESTRING(0 0, 1 1)')


    def test_update_geometry(self):
        self.store.put_feature(self.feature, key='blah')
        ret1 = self.store.get_feature('blah')
        ret2 = self.store.update_geometry(self.geomerty, 'blah')
        self.assertNotEqual(ret1.geometry.geom_type, ret2.geometry.geom_type)
        self.assertNotEqual(ret1.geohash, ret2.geohash)
        self.assertNotEqual(ret1.etag, ret2.etag)


class TestSimpleStoreProperty(unittest.TestCase, SimpleStoreTestBase):
    def setUp(self):
        self.store = build_store('simple')
        assert isinstance(self.store, SimpleGeoStore)
        self.feature = build_feature('POINT(1 1)', {'foo': 'bar', 'answer': 42})
        self.store.put_feature(self.feature, 'blah')

    def test_get_property(self):
        self.assertRaises(FeatureDoesNotExist, self.store.get_property, 'nope',
                          'nope')
        self.assertRaises(PropertyDoesNotExist, self.store.get_property, 'nope',
                          'blah')

        self.assertEqual(self.feature.properties['answer'],
                         self.store.get_property('answer', 'blah'))

    def test_delete_property(self):
        self.assertRaises(FeatureDoesNotExist,
                          self.store.delete_property,
                          'nope', 'nope')
        self.assertRaises(PropertyDoesNotExist,
                          self.store.delete_property,
                          'nope', 'blah')

        self.store.delete_property('foo', 'blah')

        self.assertRaises(PropertyDoesNotExist, self.store.get_property, 'foo',
                          'blah')

    def test_update_property(self):
        self.store.update_property('pee', 'poo', 'blah')
        self.assertEqual('poo',
                         self.store.get_property('pee', 'blah'))


if __name__ == '__main__':
    unittest.main()


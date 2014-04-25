# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/21/14'

from georest.geo import build_feature, build_geometry, Feature
from georest.store.exception import *


#
# Mixin classes
#
class SimpleStoreTestBase(object):
    def setUp(self):
        self.feature = build_feature('POINT(1 1)', {'foo': 'bar', 'answer': 42})
        self.geometry = build_geometry('LINESTRING(0 0, 1 1)')
        self.store = self._build_store()

    def _build_store(self):
        raise NotImplementedError


class TestSimpleStoreFeatureMixin(SimpleStoreTestBase):
    def test_feature_get(self):
        self.assertRaises(FeatureDoesNotExist, self.store.get_feature, 'none')

    def test_feature_put_no_prefix(self):
        ret = self.store.put_feature(self.feature, key='1', prefix='test-')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'test-1')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

        self.store.delete_feature('test-1')

    def test_feature_put_with_prefix(self):
        ret = self.store.put_feature(self.feature, key='test-2')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'test-2')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

        self.store.delete_feature('test-2')

    def test_feature_put_duplicate(self):
        ret = self.store.put_feature(self.feature, key='test-3')
        self.assertIsInstance(ret, Feature)
        self.assertEqual(ret.key, 'test-3')
        self.assertEqual(ret.geometry.wkt, self.feature.geometry.wkt)

        self.assertRaises(FeatureAlreadyExists, self.store.put_feature,
                          self.feature, key='test-3')

        ret = self.store.delete_feature('test-3')
        self.assertIsNone(ret)

        self.assertRaises(FeatureDoesNotExist, self.store.delete_feature,
                          'test-3')

    def test_feature_put_random_key(self):
        ret = self.store.put_feature(self.feature, prefix='prefix-')
        self.assertIsInstance(ret, Feature)
        self.assertNotEqual(ret.key, 'prefix-')
        self.assert_(ret.key.startswith('prefix-'))

        self.store.delete_feature(ret.key)


class TestSimpleStoreGeometryMixin(SimpleStoreTestBase):
    def test_update_geometry(self):
        self.store.put_feature(self.feature, key='test-1')
        ret1 = self.store.get_feature('test-1')
        ret2 = self.store.update_geometry(self.geometry, 'test-1')
        self.assertNotEqual(ret1.geometry.geom_type, ret2.geometry.geom_type)
        self.assertNotEqual(ret1.geohash, ret2.geohash)
        self.assertNotEqual(ret1.etag, ret2.etag)

        self.store.delete_feature('test-1')


class TestSimpleStorePropertyMixin(SimpleStoreTestBase):
    def setUp(self):
        super(TestSimpleStorePropertyMixin, self).setUp()
        self.store.put_feature(self.feature, 'test-4')
        self.store.put_feature(self.feature, 'test-5')

    def tearDown(self):
        self.store.delete_feature('test-4')
        self.store.delete_feature('test-5')
        super(TestSimpleStorePropertyMixin, self).tearDown()

    def test_get_property(self):
        self.assertRaises(FeatureDoesNotExist, self.store.get_property, 'nope',
                          'nope')
        self.assertRaises(PropertyDoesNotExist, self.store.get_property, 'nope',
                          'test-4')

        self.assertEqual(self.feature.properties['answer'],
                         self.store.get_property('answer', 'test-4'))

    def test_delete_property(self):
        self.assertRaises(FeatureDoesNotExist,
                          self.store.delete_property,
                          'nope', 'nope')
        self.assertRaises(PropertyDoesNotExist,
                          self.store.delete_property,
                          'nope', 'test-4')

        self.store.delete_property('foo', 'test-5')

        self.assertRaises(PropertyDoesNotExist, self.store.get_property, 'foo',
                          'test-5')

    def test_update_property(self):
        self.store.update_property('pee', 'poo', 'test-4')
        self.assertEqual('poo',
                         self.store.get_property('pee', 'test-4'))

# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/24/14'

import unittest

from georest.store import build_store
from georest.store.couch import SimpleCouchbaseGeoStore

from tests.store.simplebasetest import SimpleStoreTestBase, \
    TestSimpleStoreFeatureMixin, TestSimpleStoreGeometryMixin, \
    TestSimpleStorePropertyMixin

from tests.store.couchbase_settings import ENABLED, ARGS

if ENABLED:
    class MemoryStoreMixin(object):
        def _build_store(self):
            return build_store('couchbase',
                               **ARGS)

    class TestDescribe(MemoryStoreMixin, SimpleStoreTestBase,
                       unittest.TestCase):
        def test_describe(self):
            desc = self.store.describe()
            self.assert_(desc)
            self.assertEqual(desc['backend'], 'couchbase')

        def test_store_obj(self):
            self.assertIsNotNone(self.store)
            self.assertIsInstance(self.store, SimpleCouchbaseGeoStore)


    class TestFeature(MemoryStoreMixin,
                      TestSimpleStoreFeatureMixin,
                      unittest.TestCase):
        pass


    class TestGeometry(MemoryStoreMixin,
                       TestSimpleStoreGeometryMixin,
                       unittest.TestCase):
        pass


    class TestProperty(MemoryStoreMixin,
                       TestSimpleStorePropertyMixin,
                       unittest.TestCase):
        pass

if __name__ == '__main__':
    unittest.main()


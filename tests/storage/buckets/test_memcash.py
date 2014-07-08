# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/7/14'

"""
    
    ~~~~~~~~~~~~~
    TODO: description

"""
import unittest

from georest.storage import MemcacheFeatureStorage, FeatureMapper, \
    DuplicatedBucket


class TestMemcacheFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.storage = MemcacheFeatureStorage(hosts=['localhost'])

        self.bucket = self.storage.create_bucket(u'mem_test', overwrite=True)

        self.test_name = u'feature'
        self.test_mapper = FeatureMapper(
            properties=dict(x=1, y=1),
            metadata=dict(z=2),
            wkt='POINT (1 1)',
            srid=4326,
        )

    def tearDown(self):
        self.storage.close()

    def test_create_get_delete_bucket(self):
        bucket_name = u'bb1'

        self.storage.create_bucket(bucket_name, overwrite=True)
        self.assertTrue(self.storage.has_bucket(bucket_name))

        self.assertRaises(DuplicatedBucket, self.storage.create_bucket, bucket_name)

        bucket = self.storage.get_bucket(bucket_name)
        self.assertEqual(bucket.bucket_name, bucket_name)

        self.storage.delete_bucket(bucket_name)
        self.assertFalse(self.storage.has_bucket(bucket_name))


    def test_commit_checkout(self):
        commit1 = self.bucket.commit(self.test_name, self.test_mapper)
        self.assertEqual(commit1.name, self.test_name)
        self.assertIsNone(commit1.revision)
        self.assertIsNone(commit1.create_at)
        self.assertIsNone(commit1.expire_at)

        commit2, mapper = self.bucket.checkout(self.test_name)
        self.assertEqual(commit2.name, self.test_name)
        self.assertIsNone(commit2.revision)
        self.assertIsNone(commit2.create_at)
        self.assertIsNone(commit2.expire_at)

    def test_commit_remove(self):
        commit1 = self.bucket.commit(self.test_name, self.test_mapper)
        self.assertEqual(commit1.name, self.test_name)
        self.assertIsNone(commit1.revision)
        self.assertIsNone(commit1.create_at)
        self.assertIsNone(commit1.expire_at)

        commit2 = self.bucket.remove(self.test_name)
        self.assertEqual(commit2.name, self.test_name)
        self.assertIsNone(commit2.revision)
        self.assertIsNone(commit2.create_at)
        self.assertIsNone(commit2.expire_at)

    def test_sequential_commit(self):
        commit1 = self.bucket.commit(self.test_name, self.test_mapper)
        self.assertEqual(commit1.name, self.test_name)
        self.assertIsNone(commit1.revision)
        self.assertIsNone(commit1.create_at)
        self.assertIsNone(commit1.expire_at)

        commit2 = self.bucket.commit(self.test_name, self.test_mapper)
        self.assertEqual(commit2.name, self.test_name)
        self.assertIsNone(commit2.revision)
        self.assertIsNone(commit2.create_at)
        self.assertIsNone(commit2.expire_at)

        commit3, mapper = self.bucket.checkout(self.test_name,
                                               self.test_mapper)
        self.assertEqual(commit2.name, self.test_name)
        self.assertIsNone(commit2.revision)
        self.assertIsNone(commit2.create_at)
        self.assertIsNone(commit2.expire_at)

        self.assertEqual(mapper, self.test_mapper)

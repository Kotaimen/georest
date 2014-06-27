# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/23/14'

"""
    tests.storage.test_storage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Test for FeatureStorage

"""
import os
import unittest

from georest.storage.buckets import DummyBucketFactory
from georest.storage import FeatureStorage, FeatureBucket, BucketNotFound, \
    DuplicatedBucket


class TestDummyFeatureStorage(unittest.TestCase):
    def setUp(self):
        factory = DummyBucketFactory()
        self.storage = FeatureStorage(factory)

    def test_create_bucket(self):
        bucket = self.storage.create_bucket('test_bucket')
        self.assertIsInstance(bucket, FeatureBucket)
        self.assertEqual(bucket.bucket_name, 'test_bucket')

    def test_create_duplicated_bucket(self):
        bucket = self.storage.create_bucket('test_bucket')
        self.assertRaises(
            DuplicatedBucket, self.storage.create_bucket, 'test_bucket')

    def test_get_bucket(self):
        bucket = self.storage.create_bucket('test_bucket')
        self.assertIsInstance(bucket, FeatureBucket)
        self.assertEqual(bucket.bucket_name, 'test_bucket')

        bucket = self.storage.get_bucket('test_bucket')
        self.assertIsInstance(bucket, FeatureBucket)
        self.assertEqual(bucket.bucket_name, 'test_bucket')

    def test_fail_to_get_bucket(self):
        self.assertRaises(BucketNotFound, self.storage.get_bucket, 'no_name')

    def test_delete_bucket(self):
        bucket = self.storage.create_bucket('test_bucket')
        self.assertIsInstance(bucket, FeatureBucket)
        self.assertEqual(bucket.bucket_name, 'test_bucket')

        self.storage.delete_bucket('test_bucket')
        self.assertRaises(
            BucketNotFound, self.storage.get_bucket, 'test_bucket')

    def test_delete_non_existent_bucket(self):
        self.assertRaises(
            BucketNotFound, self.storage.delete_bucket, 'test_bucket')

    def test_describe(self):
        self.assertIn('support_version', self.storage.describe())

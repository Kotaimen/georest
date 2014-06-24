# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/24/14'

"""
    tests.storage.buckets.test_factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TODO: description

"""
import os
import unittest
from georest.storage.exceptions import BucketNotFound, DuplicatedBucket
from georest.storage.buckets import PostGISFeatureBucketFactory

class TestPostGISBucketFactory(unittest.TestCase):

    @unittest.skipIf(os.environ.get('GEOREST_PG_STORAGE_HOST') is None, '')
    def setUp(self):
        host = os.environ.get('GEOREST_PG_STORAGE_HOST')
        port = os.environ.get('GEOREST_PG_STORAGE_PORT', 5432)
        username = os.environ.get('GEOREST_PG_STORAGE_USERNAME', 'username')
        password = os.environ.get('GEOREST_PG_STORAGE_PASSWORD', 'password')
        database = os.environ.get('GEOREST_PG_STORAGE_DATABASE', 'database')


        self.factory = PostGISFeatureBucketFactory(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database)

    def test_create_bucket(self):
        bucket = self.factory.create('b1', srid=4326, checkfirst=True)
        bucket = self.factory.create('b2', srid=3857, checkfirst=True)

        self.assertRaises(DuplicatedBucket, self.factory.create, 'b1')

        self.assertTrue(self.factory.has('b1'))
        self.assertTrue(self.factory.has('b2'))

        self.factory.delete('b1')
        self.factory.delete('b2')

    def test_get_bucket(self):

        self.factory.create('b1', srid=4326)

        bucket = self.factory.get('b1')
        self.assertIsNotNone(bucket)
        self.assertEqual(bucket.bucket_name, 'b1')
        self.assertTrue(self.factory.has('b1'))

        self.factory.delete('b1')

    def test_delete_bucket(self):

        self.factory.create('b1', srid=4326)

        bucket = self.factory.get('b1')
        self.assertIsNotNone(bucket)

        self.factory.delete('b1')
        self.assertRaises(BucketNotFound, self.factory.get, 'b1')


# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/24/14'

"""
    
    ~~~~~~~~~~~~~
    TODO: description

"""
import os
import unittest

from georest.geo import Key, Feature
from georest.storage import build_feature_storage, FeatureEntry, FeatureNotFound, BucketNotFound

class TestPostGISFeatureStorage(unittest.TestCase):
    @unittest.skipIf(os.environ.get('GEOREST_PG_STORAGE_HOST') is None, '')
    def setUp(self):
        host = os.environ.get('GEOREST_PG_STORAGE_HOST')
        port = os.environ.get('GEOREST_PG_STORAGE_PORT', 5432)
        username = os.environ.get('GEOREST_PG_STORAGE_USERNAME', 'username')
        password = os.environ.get('GEOREST_PG_STORAGE_PASSWORD', 'password')
        database = os.environ.get('GEOREST_PG_STORAGE_DATABASE', 'database')

        self.storage = build_feature_storage(
            'postgis',
            host=host,
            port=port,
            username=username,
            password=password,
            database=database
        )

    def test_buckets(self):
        self.storage.create_bucket('bob', srid=4326, checkfirst=True)

        bucket = self.storage.get_bucket('bob')
        self.assertIsNotNone(bucket)

        test_key = Key.make_key(bucket='test_bucket', name='alice')
        test_feature = Feature.build_from_geometry(
            'POINT (8 8)', properties=dict(x=8, y=8),
        )

        visitor = FeatureEntry(bucket)

        response = visitor.put_feature(test_key, test_feature)

        response, feature = visitor.get_feature(test_key)
        self.assertTrue(feature.equals(test_feature))

        response = visitor.delete_feature(test_key)
        self.assertRaises(FeatureNotFound, visitor.get_feature, test_key)

        self.storage.delete_bucket('bob')
        self.assertRaises(BucketNotFound, self.storage.get_bucket, 'bob')

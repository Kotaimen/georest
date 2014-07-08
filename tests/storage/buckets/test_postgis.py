# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/1/14'

"""
    tests.storage.buckets.test_postgis
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Tests for PostGIS bucket

"""

import os
import six
import datetime
import unittest
from georest.storage.buckets.postgis import *


class TestPostGISStorage(unittest.TestCase):

    @unittest.skipIf(os.environ.get('GEOREST_PG_STORAGE_HOST') is None, '')
    def setUp(self):
        host = os.environ.get('GEOREST_PG_STORAGE_HOST')
        port = os.environ.get('GEOREST_PG_STORAGE_PORT', 5432)
        username = os.environ.get('GEOREST_PG_STORAGE_USERNAME', 'username')
        password = os.environ.get('GEOREST_PG_STORAGE_PASSWORD', 'password')
        database = os.environ.get('GEOREST_PG_STORAGE_DATABASE', 'database')

        self.storage = PostGISFeatureStorage(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            debug=True)

        self.bucket = self.storage.create_bucket('formal_test', overwrite=True)

    def tearDown(self):
        self.storage.delete_bucket('formal_test')

    def test_describe(self):
        description = self.storage.describe()
        self.assertTrue(description['support_version'])

    def test_create_get_delete_bucket(self):
        bucket_name = 'bb1'

        self.storage.create_bucket(bucket_name, overwrite=True)
        self.assertTrue(self.storage.has_bucket(bucket_name))

        self.assertRaises(DuplicatedBucket, self.storage.create_bucket, bucket_name)

        bucket = self.storage.get_bucket(bucket_name)
        self.assertEqual(bucket.bucket_name, bucket_name)

        self.storage.delete_bucket(bucket_name)
        self.assertFalse(self.storage.has_bucket(bucket_name))

    def test_commit_chekcout(self):
        name = 'feature.test'
        mapper = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        commit2, mapper_result = self.bucket.checkout(name=name)
        self.assertEqual(commit2.name, name)
        self.assertEqual(commit2.revision, commit1.revision)
        self.assertEqual(commit2.create_at, commit1.create_at)
        self.assertEqual(commit2.expire_at, commit1.expire_at)

        self.assertEqual(mapper_result.properties, mapper.properties)
        self.assertEqual(mapper_result.metadata, mapper.metadata)
        self.assertEqual(mapper_result.wkt, mapper.wkt)
        self.assertEqual(mapper_result.srid, mapper.srid)

    def test_commit_remove(self):
        name = 'feature.test'
        mapper = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        commit2 = self.bucket.remove(name=name)
        self.assertEqual(commit2.name, name)
        self.assertIsNone(commit2.revision)
        self.assertIsInstance(commit2.create_at, datetime.datetime)
        self.assertGreaterEqual(commit2.create_at, commit1.create_at)
        self.assertIsInstance(commit2.expire_at, datetime.datetime)
        self.assertLess(commit2.expire_at, datetime.datetime.max)

    def test_sequential_commit(self):
        name = 'feature.test'
        mapper = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        mapper = FeatureMapper(
            properties={'z': 3},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit2 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit2.name, name)
        self.assertIsInstance(commit2.revision, six.string_types)
        self.assertIsInstance(commit2.create_at, datetime.datetime)
        self.assertEqual(commit2.expire_at, datetime.datetime.max)

        self.assertNotEqual(commit2.revision, commit1.revision)

    def test_commit_against_parent(self):
        name = 'feature.test'
        mapper = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        mapper = FeatureMapper(
            properties={'z': 3},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit2 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit2.name, name)
        self.assertIsInstance(commit2.revision, six.string_types)
        self.assertIsInstance(commit2.create_at, datetime.datetime)
        self.assertEqual(commit2.expire_at, datetime.datetime.max)

        self.assertRaises(NotHeadRevision, self.bucket.commit,
                          name=name, mapper=mapper, parent=commit1.revision)

        commit3 = self.bucket.commit(
            name=name, mapper=mapper, parent=commit2.revision)
        self.assertEqual(commit3.name, name)
        self.assertIsInstance(commit3.revision, six.string_types)
        self.assertIsInstance(commit3.create_at, datetime.datetime)
        self.assertEqual(commit3.expire_at, datetime.datetime.max)

    def test_checkout_old_revision(self):
        name = 'feature.test'
        mapper1 = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper1)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        mapper2 = FeatureMapper(
            properties={'z': 3},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit2 = self.bucket.commit(name=name, mapper=mapper2)
        self.assertEqual(commit2.name, name)
        self.assertIsInstance(commit2.revision, six.string_types)
        self.assertIsInstance(commit2.create_at, datetime.datetime)
        self.assertEqual(commit2.expire_at, datetime.datetime.max)


        commit3, mapper_result = self.bucket.checkout(
            name=name, revision=commit1.revision)
        self.assertEqual(commit3.name, name)
        self.assertEqual(commit3.revision, commit1.revision)
        self.assertEqual(commit3.create_at, commit1.create_at)
        self.assertLess(commit3.expire_at, commit1.expire_at)

        self.assertEqual(mapper_result.properties, mapper1.properties)
        self.assertEqual(mapper_result.metadata, mapper1.metadata)
        self.assertEqual(mapper_result.wkt, mapper1.wkt)
        self.assertEqual(mapper_result.srid, mapper1.srid)

    def test_remove_against_parent(self):
        name = 'feature.test'
        mapper = FeatureMapper(
            properties={'x': 1, 'y': 2},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit1 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit1.name, name)
        self.assertIsInstance(commit1.revision, six.string_types)
        self.assertIsInstance(commit1.create_at, datetime.datetime)
        self.assertEqual(commit1.expire_at, datetime.datetime.max)

        mapper = FeatureMapper(
            properties={'z': 3},
            metadata={'z': 3},
            wkt='POINT (1 2)',
            srid=4326)

        commit2 = self.bucket.commit(name=name, mapper=mapper)
        self.assertEqual(commit2.name, name)
        self.assertIsInstance(commit2.revision, six.string_types)
        self.assertIsInstance(commit2.create_at, datetime.datetime)
        self.assertEqual(commit2.expire_at, datetime.datetime.max)

        self.assertRaises(NotHeadRevision, self.bucket.remove,
                          name=name, parent=commit1.revision)

        commit3 = self.bucket.remove(name, commit2.revision)
        self.assertEqual(commit3.name, name)
        self.assertIsNone(commit3.revision)
        self.assertIsInstance(commit3.create_at, datetime.datetime)
        self.assertGreaterEqual(commit3.create_at, commit1.create_at)
        self.assertIsInstance(commit3.expire_at, datetime.datetime)
        self.assertLess(commit3.expire_at, datetime.datetime.max)

# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/19/14'

import os
import datetime
import unittest

from georest.geo import Feature, Key
from georest.storage import *


class TestPostGISDataSource(unittest.TestCase):
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

        self.test_key = Key.make_key(bucket='test_bucket', name='alice')
        self.test_feature = Feature.build_from_geometry(
            'POINT (8 8)', properties=dict(x=8, y=8),
        )

        bucket = self.storage.create_bucket(self.test_key.bucket)

        entry = FeatureEntry(bucket)
        self.test_commit = entry.put_feature(self.test_key, self.test_feature)

    def test_put_feature(self):
        # put a feature with a key of no name
        key = Key.make_key(bucket='test_bucket')
        feature = Feature.build_from_geometry(
            'POINT (2 2)', properties=dict(x=2, y=2),
        )

        bucket = self.storage.get_bucket(key.bucket)

        entry = FeatureEntry(bucket)
        commit1 = entry.put_feature(key, feature)

        self.assertIsNotNone(commit1.key.name)
        self.assertEqual(
            commit1.revision, '2562ee5c5ea7e546cf2520ce3b8c7e8dc4798f30')
        self.assertEqual(commit1.parent_revision, None)
        self.assertIsInstance(commit1.timestamp, datetime.datetime)

        # put a feature with same key
        commit2 = entry.put_feature(commit1.key, feature)

        self.assertEqual(
            commit2.revision, '8a44888182eec14d38677891b9d3ee7a8d3b6cdd')
        self.assertEqual(commit2.parent_revision, commit1.revision)
        self.assertIsInstance(commit2.timestamp, datetime.datetime)

        # put a feature with same key and parent revision
        commit3 = entry.put_feature(
            commit1.key, feature, revision=commit2.revision)

        self.assertEqual(
            commit3.revision, '5c0863f23ee65e1d6b6f992e8708119119cf6e8f')
        self.assertEqual(commit3.parent_revision, commit2.revision)
        self.assertIsInstance(commit3.timestamp, datetime.datetime)

        # put a feature with same key and wrong revision
        self.assertRaises(ParentRevisionNotFound, entry.put_feature,
                          commit1.key, feature, revision='bad revision')

        # put a feature with same key and old revision
        self.assertRaises(NotHeadRevision, entry.put_feature,
                          commit1.key, feature, revision=commit2.revision)


    def test_get_feature(self):
        # get a feature
        bucket = self.storage.get_bucket(self.test_key.bucket)

        entry = FeatureEntry(bucket)
        feature = entry.get_feature(self.test_key)

        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))

        # get a feature with a wrong key
        foo_key = Key.make_key(bucket='abc', name='efg')
        self.assertRaises(FeatureNotFound, entry.get_feature, foo_key)

        # get a feature with a revision
        feature = entry.get_feature(self.test_key, self.test_commit.revision)

        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))

        # get a feature with a wrong revision
        self.assertRaises(
            FeatureNotFound, entry.get_feature, self.test_key, 'bad revision')

    def test_delete_feature(self):
        bucket = self.storage.get_bucket('test_bucket')

        entry = FeatureEntry(bucket)

        # delete a feature
        commit = entry.delete_feature(self.test_key)

        self.assertEqual(commit.key, self.test_key)
        self.assertEqual(
            commit.revision, '2e580da5bb73c3d12167dd43ef1ad535b8d90ee5')
        self.assertIsInstance(commit.timestamp, datetime.datetime)

        # delete a feature with wrong key
        foo_key = Key.make_key(bucket='abc', name='efg')
        self.assertRaises(FeatureNotFound, entry.delete_feature, foo_key)


        # delete a feature with wrong revision
        self.assertRaises(
            NotHeadRevision, entry.delete_feature, self.test_key,
            'bad revision'
        )

        # get a deleted feature
        self.assertRaises(
            FeatureNotFound, entry.get_feature, self.test_key
        )

        # get a old version of the deleted feature
        feature = entry.get_feature(self.test_key, self.test_commit.revision)
        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))



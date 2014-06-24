# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/19/14'

import os
import datetime
import unittest

from georest.geo import Feature, Key
from georest.storage import *
from georest.storage.entry import make_mapper_from_feature, \
    make_feature_from_mapper


class TestPostGISDataSource(unittest.TestCase):
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

        self.test_key = Key.make_key(bucket='test_bucket', name='alice')
        self.test_feature = Feature.build_from_geometry(
            'POINT (8 8)', properties=dict(x=8, y=8),
        )

        self.bucket = self.factory.create('test_bucket', srid=4326,
                                          checkfirst=True)

        mapper = make_mapper_from_feature(self.test_feature)
        self.test_commit = self.bucket.commit(
            self.test_key.qualified_name, mapper)

    def tearDown(self):
        self.factory.delete('test_bucket')

    def test_commit_feature(self):
        # put a feature with a key of no name
        key = Key.make_key(bucket='test_bucket')
        feature = Feature.build_from_geometry(
            'POINT (2 2)', properties=dict(x=2, y=2),
        )

        name = key.qualified_name
        mapper = make_mapper_from_feature(feature)

        commit1 = self.bucket.commit(name, mapper)

        self.assertIsNotNone(commit1.name)
        self.assertIsNotNone(commit1.revision)
        self.assertEqual(commit1.parent_revision, None)
        self.assertIsInstance(commit1.timestamp, datetime.datetime)

        # put a feature with same key
        commit2 = self.bucket.commit(commit1.name, mapper)

        self.assertIsNotNone(commit2.revision)
        self.assertEqual(commit2.parent_revision, commit1.revision)
        self.assertIsInstance(commit2.timestamp, datetime.datetime)

        # put a feature with same key and parent revision
        commit3 = self.bucket.commit(
            commit1.name, mapper, parent=commit2.revision)

        self.assertIsNotNone(commit3.revision)
        self.assertEqual(commit3.parent_revision, commit2.revision)
        self.assertIsInstance(commit3.timestamp, datetime.datetime)

        # put a feature with same key and wrong revision
        self.assertRaises(ParentRevisionNotFound, self.bucket.commit,
                          commit1.name, mapper, parent='bad revision')

        # put a feature with same key and old revision
        self.assertRaises(NotHeadRevision, self.bucket.commit,
                          commit1.name, mapper, parent=commit2.revision)


    def test_checkout_feature(self):
        # get a feature
        name = self.test_key.qualified_name

        commit, mapper = self.bucket.checkout(name)

        feature = make_feature_from_mapper(self.test_key, mapper)
        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))

        # get a feature with a wrong key
        foo_key = Key.make_key(bucket='abc', name='efg')
        foo_name = foo_key.qualified_name
        self.assertRaises(FeatureNotFound, self.bucket.checkout, foo_name)

        # get a feature with a revision
        commit, mapper = self.bucket.checkout(
            name, self.test_commit.revision)

        feature = make_feature_from_mapper(self.test_key, mapper)
        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))

        # get a feature with a wrong revision
        self.assertRaises(
            FeatureNotFound, self.bucket.checkout, name, 'bad revision')

    def test_delete_feature(self):
        # delete a feature
        commit = self.bucket.remove(self.test_key.qualified_name)

        self.assertEqual(commit.name, self.test_key.qualified_name)
        self.assertIsNotNone(commit.revision)
        self.assertIsInstance(commit.timestamp, datetime.datetime)

        # delete a feature with wrong key
        foo_key = Key.make_key(bucket='abc', name='efg')
        foo_name = foo_key.qualified_name
        self.assertRaises(
            FeatureNotFound, self.bucket.remove, foo_name)


        # delete a feature with wrong revision
        self.assertRaises(
            NotHeadRevision, self.bucket.remove, self.test_key.qualified_name,
            'bad revision'
        )

        # get a deleted feature
        self.assertRaises(
            FeatureNotFound, self.bucket.checkout, self.test_key.qualified_name
        )

        # get a old version of the deleted feature
        commit, mapper = self.bucket.checkout(
            self.test_key.qualified_name, self.test_commit.revision)
        feature = make_feature_from_mapper(self.test_key, mapper)
        self.assertEqual(feature.key, self.test_key)
        self.assertTrue(feature.equals(self.test_feature))



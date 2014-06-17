# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/3/14'

import os
import unittest
from georest.geo.feature import Feature
from georest.storage.pgstorage import *


class TestPostGISDataSource(unittest.TestCase):
    @unittest.skipIf(os.environ.get('GEOREST_PG_STORAGE_HOST') is None, '')
    def setUp(self):
        host = os.environ.get('GEOREST_PG_STORAGE_HOST')
        port = os.environ.get('GEOREST_PG_STORAGE_PORT', 5432)
        username = os.environ.get('GEOREST_PG_STORAGE_USERNAME', 'username')
        password = os.environ.get('GEOREST_PG_STORAGE_PASSWORD', 'password')
        database = os.environ.get('GEOREST_PG_STORAGE_DATABASE', 'database')

        self.storage = PostgisFeatureStorage(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            create_table=True
        )

        full_key = Key.make_key(bucket='test_bucket', name='test_name')
        feature = Feature.build_from_geometry(
            'POINT (8 8)',
            properties=dict(x=1, y=2),
        )

        response = self.storage.put_feature(full_key, feature)

        self._test_key = full_key
        self._test_feature = feature
        self._test_rev = response.revision

    def tearDown(self):
        self.storage.close()

    def test_put_feature(self):
        partial_key = Key.make_key(bucket='test_bucket')
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        # put a new feature
        response = self.storage.put_feature(partial_key, feature, fetch=True)
        self.assertTrue(response.feature.equals(feature))
        self.assertEqual(response.key.bucket, partial_key.bucket)
        self.assertIsNotNone(response.key.name)
        self.assertIsNotNone(response.revision)

        # put a new feature with same key / update the whole feature
        self.storage.put_feature(self._test_key, feature, fetch=True)
        response = self.storage.get_feature(self._test_key)
        self.assertTrue(response.feature.equals(feature))
        head_rev = response.revision

        # put a new feature with same key, wrong old revision
        self.assertRaises(
            ConflictVersion,
            self.storage.put_feature,
            self._test_key, feature, 'wrong version'
        )

        # put a new feature with same key, correct revision
        response = self.storage.put_feature(
            self._test_key, feature, head_rev, fetch=True)
        self.assertTrue(response.feature.equals(feature))

    def test_get_feature(self):
        full_key = self._test_key

        # get a feature
        response = self.storage.get_feature(full_key)
        self.assertTrue(response.feature.equals(self._test_feature))

        # modify a feature
        feature = self._test_feature.duplicate()
        feature.properties['z'] = 3

        # put a modified feature
        self.storage.put_feature(full_key, feature)

        # get the modified feature
        response = self.storage.get_feature(full_key)
        self.assertTrue(response.feature.equals(feature))


    def test_delete_feature(self):
        full_key = self._test_key

        # delete the feature
        self.storage.delete_feature(full_key)
        self.assertRaises(FeatureNotFound, self.storage.get_feature, full_key)

        # get the old version
        response = self.storage.get_feature(full_key, self._test_rev)
        self.assertTrue(response.feature, self._test_feature)

    def test_update_geometry(self):
        geom = Geometry.build_geometry('POINT (2 2)', srid=4326)

        # update the geometry
        response = self.storage.update_geometry(
            self._test_key, geom, fetch=True)
        self.assertEqual(response.feature.geometry.wkt, 'POINT (2 2)')

        # get the feature to validate
        response = self.storage.get_feature(self._test_key)
        self.assertEqual(response.feature.geometry.wkt, 'POINT (2 2)')

        # get the old revision
        response = self.storage.get_feature(self._test_key, self._test_rev)
        self.assertEqual(response.feature.geometry.wkt, 'POINT (8 8)')

    def test_update_properties(self):
        new_properties = dict(z=3)

        # update the properties
        response = self.storage.update_properties(
            self._test_key, new_properties, fetch=True)
        self.assertEqual(response.feature.properties, new_properties)

        # get the feature to validate
        response = self.storage.get_feature(self._test_key)
        self.assertEqual(response.feature.properties, new_properties)

        # get the old revision
        response = self.storage.get_feature(self._test_key, self._test_rev)
        self.assertEqual(response.feature.properties, dict(x=1, y=2))

    def test_get_properties(self):
        prop = self.storage.get_properties(self._test_key, self._test_rev)
        self.assertEqual(prop, dict(x=1, y=2))

    def test_get_geometry(self):
        geom = self.storage.get_geometry(self._test_key, self._test_rev)
        self.assertEqual(geom.wkt, 'POINT (8 8)')

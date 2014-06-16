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

    def tearDown(self):
        self.storage.close()

    def test_put_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature, fetch=True)
        self.assertEqual(response1.feature.metadata, feature.metadata)
        self.assertEqual(response1.feature.properties, feature.properties)
        self.assertEqual(response1.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response1.feature.key.bucket, feature.key.bucket)
        self.assertIsNotNone(response1.feature.key.name)
        self.assertIsNotNone(response1.revision)

        response2 = self.storage.put_feature(feature, fetch=True)
        self.assertEqual(response2.feature.metadata, feature.metadata)
        self.assertEqual(response2.feature.properties, feature.properties)
        self.assertEqual(response2.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response2.feature.key.bucket, feature.key.bucket)
        self.assertEqual(response2.feature.key.name, feature.key.name)
        self.assertNotEqual(response2.revision, response1.revision)

        self.assertRaises(
            ConflictVersion,
            self.storage.put_feature,
            feature, response1.revision
        )

        response3 = self.storage.put_feature(feature, response2.revision,
                                             fetch=True)
        self.assertEqual(response3.feature.key, feature.key)
        self.assertEqual(response3.feature.properties, feature.properties)
        self.assertEqual(response3.feature.metadata, feature.metadata)
        self.assertEqual(response3.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response3.feature.key, feature.key)
        self.assertNotEqual(response3.revision, response2.revision)

    def test_get_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature)
        key = response1.key

        response2 = self.storage.get_feature(key)
        self.assertEqual(response2.feature.key, feature.key)
        self.assertEqual(response2.feature.properties, feature.properties)
        self.assertEqual(response2.feature.metadata, feature.metadata)
        self.assertEqual(response2.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response2.revision, response1.revision)

        feature.properties['z'] = 3

        response3 = self.storage.put_feature(feature)

        response4 = self.storage.get_feature(key)
        self.assertNotEqual(response1.revision, response4.revision)
        self.assertEqual(response4.feature.properties['z'], 3)

    def test_delete_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature, fetch=True)
        key = response1.key

        response2 = self.storage.delete_feature(key)
        self.assertNotEqual(response1.revision, response2.revision)

        self.assertRaises(FeatureNotFound, self.storage.get_feature, key)

        response3 = self.storage.get_feature(key, response1.revision)
        self.assertEqual(response3.feature.key, response1.feature.key)
        self.assertEqual(response3.feature.metadata,
                         response1.feature.metadata)
        self.assertEqual(response3.feature.properties,
                         response1.feature.properties)
        self.assertEqual(response3.feature.geometry.wkt,
                         response1.feature.geometry.wkt)
        self.assertEqual(response3.revision, response1.revision)

    def test_update_geometry(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature, fetch=True)
        key = response1.feature.key

        geom = Geometry.build_geometry('POINT (2 2)', srid=4326)
        response2 = self.storage.update_geometry(key, geom, fetch=True)
        self.assertEqual(response2.feature.geometry.wkt, 'POINT (2 2)')

        response3 = self.storage.get_feature(key)
        self.assertEqual(response3.feature.geometry.wkt, 'POINT (2 2)')

        response4 = self.storage.get_feature(key, response1.revision)
        self.assertEqual(response4.feature.geometry.wkt, 'POINT (1 2)')

    def test_update_properties(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature, fetch=True)
        key = response1.feature.key

        new_properties = dict(z=3)
        response2 = self.storage.update_properties(key, new_properties,
                                                   fetch=True)
        self.assertEqual(response2.feature.properties, new_properties)

        response3 = self.storage.get_feature(key)
        self.assertEqual(response3.feature.properties, new_properties)

        response4 = self.storage.get_feature(key, response1.revision)
        self.assertEqual(response4.feature.properties, feature.properties)

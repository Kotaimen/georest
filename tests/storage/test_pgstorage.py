# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/3/14'

import unittest
from georest.geo.feature import *
from georest.storage.pgstorage import *


class TestPostGISDataSource(unittest.TestCase):
    def setUp(self):
        self.storage = PostgisFeatureStorage(
            host='172.26.183.193',
            database='georest-test',
            create_table=True
        )

    def tearDown(self):
        self.storage.close()

    def test_put_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature)
        self.assertTrue(response1.success)
        self.assertEqual(response1.feature.metadata, feature.metadata)
        self.assertEqual(response1.feature.properties, feature.properties)
        self.assertEqual(response1.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response1.feature.key.bucket, feature.key.bucket)
        self.assertIsNotNone(response1.feature.key.name)
        self.assertIsNotNone(response1.version)

        response2 = self.storage.put_feature(feature)
        self.assertTrue(response2.success)
        self.assertEqual(response2.feature.metadata, feature.metadata)
        self.assertEqual(response2.feature.properties, feature.properties)
        self.assertEqual(response2.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response2.feature.key.bucket, feature.key.bucket)
        self.assertEqual(response2.feature.key.name, feature.key.name)
        self.assertNotEqual(response2.version, response1.version)

        self.assertRaises(
            VersionConflicted,
            self.storage.put_feature,
            feature, response1.version
        )

        response3 = self.storage.put_feature(feature, response2.version)
        self.assertTrue(response3.success)
        self.assertEqual(response3.feature.key, feature.key)
        self.assertEqual(response3.feature.properties, feature.properties)
        self.assertEqual(response3.feature.metadata, feature.metadata)
        self.assertEqual(response3.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response3.feature.key, feature.key)
        self.assertNotEqual(response3.version, response2.version)

    def test_get_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature)
        key = response1.feature.key

        response2 = self.storage.get_feature(key)
        self.assertEqual(response2.feature.key, feature.key)
        self.assertEqual(response2.feature.properties, feature.properties)
        self.assertEqual(response2.feature.metadata, feature.metadata)
        self.assertEqual(response2.feature.geometry.wkt, feature.geometry.wkt)
        self.assertEqual(response2.version, response1.version)

        feature.properties['z'] = 3

        response3 = self.storage.put_feature(feature)

        response4 = self.storage.get_feature(key)
        self.assertNotEqual(response1.version, response4.version)
        self.assertEqual(response4.feature.properties['z'], 3)

    def test_delete_feature(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature)
        key = response1.feature.key

        response2 = self.storage.delete_feature(key)
        self.assertNotEqual(response1.version, response2.version)

        self.assertRaises(FeatureNotFound, self.storage.get_feature, key)

        response3 = self.storage.get_feature(key, response1.version)
        self.assertEqual(response3.feature.key, response1.feature.key)
        self.assertEqual(response3.feature.metadata, response1.feature.metadata)
        self.assertEqual(response3.feature.properties, response1.feature.properties)
        self.assertEqual(response3.feature.geometry.wkt, response1.feature.geometry.wkt)
        self.assertEqual(response3.version, response1.version)

    def test_update_properties(self):
        feature = Feature.build_from_geometry(
            'POINT (1 2)',
            properties=dict(x=1, y=2)
        )

        response1 = self.storage.put_feature(feature)
        key = response1.feature.key

        geom = Geometry.build_geometry('POINT (2 2)', srid=4326)
        response2 = self.storage.update_geometry(key, geom)
        self.assertEqual(response2.feature.geometry.wkt, 'POINT (2 2)')

        response3 = self.storage.get_feature(key)
        self.assertEqual(response3.feature.geometry.wkt, 'POINT (2 2)')

        response4 = self.storage.get_feature(key, response1.version)
        self.assertEqual(response4.feature.geometry.wkt, 'POINT (1 2)')

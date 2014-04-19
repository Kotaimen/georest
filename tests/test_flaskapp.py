# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

from georest import GeoRestApp

import unittest
import os


class TestGeoRestApp(unittest.TestCase):
    def setUp(self):
        settings = {
            'GEOREST_DOC_DIR': os.path.abspath(os.path.dirname(__file__))
        }
        self.app = GeoRestApp(settings=settings)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()


    def test_doc(self):
        rv = self.client.get('/doc/helloworld.md')
        self.assertEqual(200, rv.status_code)

    def test_rediect(self):
        rv = self.client.get('/')
        self.assertEqual(302, rv.status_code)

    def test_doc_index(self):
        rv = self.client.get('/doc/')
        self.assertEqual(404, rv.status_code)

if __name__ == '__main__':
    unittest.main()

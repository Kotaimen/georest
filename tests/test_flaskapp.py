# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

from georest import GeoRestApp

import unittest
import json
from pprint import pprint


class TestGeoRestApp(unittest.TestCase):
    def setUp(self):
        app = GeoRestApp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(200, rv.status_code)

    def test_get_stat(self):
        rv = self.app.get('/stat')
        self.assertEqual(200, rv.status_code)


if __name__ == '__main__':
    unittest.main()

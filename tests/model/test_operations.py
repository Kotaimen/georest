# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/26/14'


import unittest

from georest import geo
from georest.model import OperationsModel
from georest.model.operations import NoSuchOperation


class TestOperationsModel(unittest.TestCase):
    def setUp(self):
        self.model = OperationsModel()

    def test_no_op(self):
        with self.assertRaises(NoSuchOperation):
            self.model.invoke('kangaroo',
                              geo.Geometry.build_geometry('{"type":"Point","coordinates":[30,10]}'))

    def test_pod_op(self):
        geom = geo.Geometry.build_geometry('{"type":"LineString","coordinates":[[10.0,0.0],[10.0,10.0]]}')
        result = self.model.invoke('length', geom)
        self.assert_(result.is_pod)
        self.assertEqual(result.value, 10.0)

    def test_geom_op(self):
        geom = geo.Geometry.build_geometry('{"type":"Point","coordinates":[30,10]}')
        result = self.model.invoke('centroid', geom)
        self.assertFalse(result.is_pod)
        self.assert_(geom.equals(result.value))

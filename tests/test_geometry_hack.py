# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/19/14'

"""Verify our geometry hack still works against shapely

The implement is slightly different from georest.geo.geometry
"""

import unittest

import six

import shapely.geometry
import shapely.geometry.base
import shapely.wkt

from tests.geo.data import pydata

pydata = pydata.copy()
del pydata['geometrycollection']


class Geometry(object):
    @property
    def fancy_new_property(self):
        return 'yeah!'


def hack_geometry(geom):
    new_bases = (geom.__class__, Geometry)
    new_class = type('_' + geom.__class__.__name__,
                     new_bases,
                     dict(geom.__class__.__dict__))
    geom.__class__ = new_class


class TestGeometryHack(unittest.TestCase):
    def setUp(self):
        self.geometries = list()
        for k, v in six.iteritems(pydata):
            self.geometries.append(shapely.geometry.shape(v))
            self.geometries.append(shapely.geometry.asShape(v))

        self.geometries.append(shapely.wkt.loads(
            'GEOMETRYCOLLECTION ( POINT (1 1), LINESTRING(0 0, 1 1) )'))
        self.geometries.append(shapely.wkt.loads(
            'GEOMETRYCOLLECTION EMPTY'))

        # print {v.__class__.__name__ for v in self.geometries}


    def test_hacking(self):
        for g in self.geometries:
            orig_type = g.__class__
            hack_geometry(g)
            hacked_type = g.__class__
            self.assertIsInstance(g, orig_type)
            self.assertEqual(g.fancy_new_property, 'yeah!')
            self.assertTrue(issubclass(hacked_type, orig_type))
            self.assertEqual(hacked_type.__mro__[0], hacked_type)
            self.assertNotIsInstance(g.buffer(0.01), hacked_type)


if __name__ == '__main__':
    unittest.main()


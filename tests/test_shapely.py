# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/30/14'

""" Verify the "Ooops" in shapely are still broken """

import unittest
import functools
import geojson.base
import shapely
import shapely.geometry
import shapely.wkt
import shapely.ops
import pyproj


class TestGeometryCreation(unittest.TestCase):
    def test_load_geometrycollection(self):
        """ shapely don't support create GeometryCollection unless underlying
        geos returns one.  This means GeometryCollection can only be created
        from WKT/WKB or returned as a geometry operation result.

        According to https://github.com/Toblerity/Shapely/issues/115, this is
        good because GEOS don't handle GeometryCollection very well .... except
        python-gdal supports it very well, and also that geodjango thing...

        Personally I think this is a result of irregular geometry creation...
        """
        geom = geojson.loads('''{"type": "GeometryCollection",
                                "geometries": [
                                {"type": "Point",
                                 "coordinates": [100.0, 0.0]
                                },
                                {"type": "LineString",
                                 "coordinates": [[101.0, 0.0], [102.0, 1.0]]
                                }
                             ]}''')
        self.assertRaises(ValueError, shapely.geometry.asShape, geom)
        self.assertRaises(ValueError, shapely.geometry.shape, geom)


class TestTransformOps(unittest.TestCase):
    def setUp(self):
        self.project = functools.partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'),
            pyproj.Proj(init='epsg:3857'))
        self.project2 = functools.partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:3857'),
            pyproj.Proj(init='epsg:4326'))

    def test_geometry_collection_transform(self):
        """shapely don't support transform on GeometryCollection "by design"

        See: https://github.com/Toblerity/Shapely/issues/74
        """
        g1 = shapely.wkt.loads(
            'GEOMETRYCOLLECTION (POINT (100 0), LINESTRING (101 0, 102 1))')

        self.assertRaises(TypeError, shapely.ops.transform, self.project, g1)

    def test_geometry_multipoint_transform(self):
        """shapely's multi geometry adapter doesn't perfectly mimics a geometry
        object, and fails if a multi geometry is transformed more than once.
        """
        # load using geojson, which implements __geo_interface__
        mp = geojson.loads('''{"type": "MultiPoint",
            "coordinates": [[100.0, 0.0], [101.0, 1.0]]}''')
        # everything will be fine if this calls shape instead of asShape
        g1 = shapely.geometry.asShape(mp)
        g2 = shapely.ops.transform(self.project, g1)
        self.assertRaises(TypeError, shapely.ops.transform, self.project2, g2)


if __name__ == '__main__':
    unittest.main()
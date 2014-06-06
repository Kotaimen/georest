# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/29/14'

"""
    georest.geo
    ~~~~~~~~~~~

    This package provides GeoJSON a-like Feature data model.

    Overall goal is fast json/wkb/wkt io without magical python code... there
    are already too much pain in various python geo packages:

    - Geometry Engine:
        - shapely
        - geos
        - osgeo.ogr
        - django.contrib.gis.geos
    - Coordinate Reference System:
        - pyproj
        - django.contrib.gis.gdal
        - osgeo.osr
    - GeoJson IO:
        - json
        - geojson
        - ujson
        - yajl
    - Feature Abstraction:
        - geojson.Feature
        - osgeo.ogr.Feature
    
    Note on packages (after a lot of painful research):
    - shapely: good geometry abstraction, fast, much better API than the 
               official python binding, no out-of-box CRS support.
    - geos/osgeo.ogr/osgeo.osr: official binding of c++ interface, powerful,
                                too complex, not pythonic at all, requires 
                                convert `GEOSGeometry` to `OGRGeometry` to do
                                coordinate transform, very slow GeoJson 
                                serialization (load/dump json...).
    - django.contrib.gis: very nice python bindings, still requires convert 
                          geometry for transform, and it feels strange to use
                          `django` in a `Flask` project ... (used in Mark1,
                          for they don't require python-gdal)
    - geojson: Feature abstraction is what we want but uses `simplejson` for
               serialization which is slow.
    - ujson: Fast, stable, not as much options as standard library `json`, and
             does not preserve float point xxx (smaller dump result)
    - yajl: Promising but crashes interpreter ...slower than `ujson` anyway.
    - pyshape: Very slow (10x-20x) compared to `osgeo.ogr.DataSource`,
               can't read a lot of shapefiles, implemented in pure python.
    - pyproj: Very weird abstraction compared to `osgeo.osr`, don't require
              `python-gdal` and `gdal`.
    
"""

from .exceptions import GeoException

from .key import Key
from .metadata import Metadata
from .spatialref import SpatialReference
from .geometry import Geometry
from .feature import Feature

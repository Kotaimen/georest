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
        - django.contrib.geos
    - Coordinate Reference System:
        - pyproj
        - django.contrib.gdal
        - osgeo.osr
    - Geoson IO:
        - json
        - geojson
        - ujson
        - yajl
    - Feature Abstraction:
        - geojson.Feature
        - osgeo.ogr.Feature

"""

from .exceptions import GeoException

from .key import Key
from .metadata import Metadata
from .spatialref import SpatialReference
from .geometry import Geometry
from .feature import Feature

# -*- encoding: utf-8 -*-

"""
    georest.geo
    ~~~~~~~~~~~

    Package contains spatial data model, geo engine.

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

#
# Use geodjango as driver
#

# NOTE: Its also quite possible to use osgeo.ogr as driver
import django.contrib.gis.geos as geos
import django.contrib.gis.gdal as gdal

if not geos.HAS_GEOS:
    raise ImportError

if not gdal.HAS_GDAL:
    raise ImportError


GEOS_VERSION = geos.geos_version_info()
GDAL_VERSION = gdal.gdal_full_version()

#
# Mock IF, as of now
#

# TODO: Is it possible to switch driver?
class Geometry(object):
    pass


class Feature(object):
    pass


class Properties(dict):
    pass
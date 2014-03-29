# -*- encoding: utf-8 -*-

"""
    Geodjango Engine
    ~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

import django.contrib.gis.geos as geos
import django.contrib.gis.gdal as gdal

if not geos.HAS_GEOS:
    raise ImportError('Requires libgeos installed')

if not gdal.HAS_GDAL:
    raise ImportError('Requires libgdal installed')


def describe():
    return {'geometry': 'GEOS Geometry',
            'geos': geos.geos_version(),
            'gdal': gdal.gdal_full_version(), }


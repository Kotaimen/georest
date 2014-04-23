# -*- encoding: utf-8 -*-

"""
    georest.geo
    ~~~~~~~~~~~

    Package contains spatial data model, geo engine.

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

from .geometry import Geometry, build_geometry, build_srs
from .feature import Feature, json2feature, feature2json, \
    build_feature, build_feature_from_geojson, \
    check_properties, build_properties_from_json

import jsonhelper

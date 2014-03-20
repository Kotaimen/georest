# -*- encoding: utf-8 -*-

"""
    georest.geo
    ~~~~~~~~~~~

    Package contains spatial data model, geo engine.

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

from .exception import GeoException
from .geometry import Geometry, build_geometry
from .feature import Feature, build_feature
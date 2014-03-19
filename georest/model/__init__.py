# -*- encoding: utf-8 -*-

"""
    georest.model
    ~~~~~~~~~~~~~

    Defines application logic

"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from ..geo import GEOS_VERSION, GDAL_VERSION, Feature


#
# Mock IF
#


class VeryDumbGeoModel(object):
    """
        Application logic
    """
    # XXX: Returns python POD?
    def __init__(self, store):
        self.store = store

    def describe_engine(self):
        return dict(geos=GEOS_VERSION, gdal=GDAL_VERSION)

    def put_feature(self, geom, props=None, key=None):
        pass

    def get_feature(self, key):
        return Feature()
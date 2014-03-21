# -*- encoding: utf-8 -*-

"""
    georest.model
    ~~~~~~~~~~~~~

    Defines application logic

"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from ..geo.engine import VERSION
from ..geo import build_feature, build_geometry


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
        return VERSION

    def describe_capabilities(self):
        return dict(storage=False,
                    version=False,
                    changeset=False,
                    property_query=False,
                    spatial_query=False)

    def put_feature(self, geom, props=None, key=None):
        pass

    def get_feature(self, key):
        return build_feature('POINT(1 2)', 4326, {'hello,': 'world!'})

    def get_geometry(self, key):
        return build_geometry('POINT(1 2)')

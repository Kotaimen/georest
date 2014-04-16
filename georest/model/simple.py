# -*- encoding: utf-8 -*-

"""
    georest.model.simple
    ~~~~~~~~~~~~~~~~~~~~

    Defines application logic

"""
__author__ = 'kotaimen'
__date__ = '3/22/14'

from ..geo import build_feature, build_feature_from_geojson

from ..store.simple import SimpleGeoStore


class SimpleGeoModel(object):
    """ Application logic, always return python objects """

    def __init__(self, store):
        assert isinstance(store, SimpleGeoStore)
        self.store = store

    def describe_capabilities(self):
        raise NotImplementedError

    def put_geometry(self, geometry_input, key=None):
        feature = build_feature(geometry_input, srid=4326, key=key)
        self.store.put_feature(feature, key=key)
        return feature

    def get_feature(self, key):
        feature = self.store.get_feature(key)
        return feature

    def put_feature(self, feature_input, key=None):
        feature = build_feature_from_geojson(feature_input, key=key)
        self.store.put_feature(feature, key=key)
        return feature

    def delete_feature(self, key):
        self.store.delete_feature(key)

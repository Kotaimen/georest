# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/22/14'

from ..geo import build_feature
from ..geo.engine import VERSION

from ..store.simple import SimpleGeoStore


class SimpleGeoModel(object):
    """ Application logic, always return python objects """

    def __init__(self, store):
        assert isinstance(store, SimpleGeoStore)
        self.store = store

    def describe_engine(self):
        return VERSION

    def describe_capabilities(self):
        return dict(presistence=False,
                    cached=True,
                    versioning=False,
                    changeset=False,
                    property_query=False,
                    spatial_query=False,
                    efficient_lookup=True, )

    def get_feature(self, key):
        feature = self.store.get_feature(key)
        return feature

    def put_feature(self, key, geometry_input, properties=None):
        feature = build_feature(geometry_input, srid=4326, properties=properties)
        self.store.put_feature(feature, key=key)
        return feature

    def delete_feature(self, key):
        self.store.delete_feature(key)

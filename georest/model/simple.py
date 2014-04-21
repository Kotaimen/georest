# -*- encoding: utf-8 -*-

"""
    georest.model.simple
    ~~~~~~~~~~~~~~~~~~~~

    Defines application logic

"""
__author__ = 'kotaimen'
__date__ = '3/22/14'

import json

from ..geo import build_geometry, build_feature_from_geojson, \
    build_properties_from_json
from ..geo.exception import InvalidProperty
from ..store.simple import SimpleGeoStore


class SimpleGeoModel(object):
    """ Application logic, always return python objects """

    PREFIX = 'feature.'

    def __init__(self, store):
        assert isinstance(store, SimpleGeoStore)
        self.store = store

    def describe(self):
        raise NotImplementedError

    def get_feature(self, key, prefix=None):
        """Get a existing feature

        :param key: key of the feature
        :param prefix: prefix of the key
        :return: feature object
        """
        feature = self.store.get_feature(key, prefix)
        return feature

    def put_feature(self, feature_input, key=None, prefix=None):
        """Put a new feature using given key and prefix

        :param feature_input: feature input
        :param key: key of the feature, a random key is selected if omitted
        :param prefix: prefix of the key, default to 'feature.' if key is omitted
        :return: feature object
        """
        if key is None and prefix is None:
            prefix = self.PREFIX
        feature = build_feature_from_geojson(feature_input)
        return self.store.put_feature(feature, key=key, prefix=prefix)

    def delete_feature(self, key, prefix=None):
        """Delete feature with given key

        :param key: key of the feature
        :param prefix: prefix of the key
        :return: None
        """
        self.store.delete_feature(key, prefix)

    def update_geometry(self, geometry_input, key=None, prefix=None):
        """ Update geometry of a existing feature or create a new one

        :param geometry_input: geometry input
        :param key: key of the feature
        :param prefix: prefix of the key
        :return: updated feature
        """
        if key is None and prefix is None:
            prefix = self.PREFIX
        geometry = build_geometry(geometry_input, srid=4326)
        return self.store.update_geometry(geometry, key, prefix=prefix)

    def update_properties(self, props_input, key, prefix=None):
        """ Update properties of the feature

        :param props_input:
        :param key: key of the feature
        :param prefix: prefix of the key
        :return: updated feature
        """
        properties = build_properties_from_json(props_input)
        return self.store.update_properties(properties, key, prefix=prefix)

    def delete_properties(self, names, key, prefix=None):

        return self.store.delete_properties(names, key, prefix=prefix)

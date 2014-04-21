# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import pickle
import threading
import re
import collections

from ..geo import build_feature
from .exception import InvalidKey, FeatureAlreadyExists, FeatureDoesNotExist, \
    PropertyDoesNotExist

from .base import is_key_valid, Capability


class SimpleGeoStore(object):
    """ Simple storage uses a python dict

    For test only, thread safe via explicit locking.
    """

    CAPABILITY = Capability(
        efficient_key_lookup=True,
        in_memory_cache=True,
    )

    def __init__(self):
        self._lock = threading.Lock()
        self._features = dict()
        self._counter = 0

    def describe(self):
        return {
            'backend': 'Simple',
            'capabilities': self.CAPABILITY
        }

    def put_feature(self, feature, key=None, prefix=None):
        with self._lock:
            key = self._make_key(key, prefix)

            if key in self._features:
                raise FeatureAlreadyExists(
                    'Geometry already exists: "%s"' % key)

            self._write_feature(feature, key)
            return feature

    def get_feature(self, key, prefix=None):
        return self._load_feature(key, prefix)

    def delete_feature(self, key, prefix=None):
        key = self._make_key(key, prefix)

        with self._lock:
            try:
                del self._features[key]
            except KeyError as e:
                raise FeatureDoesNotExist(
                    'Feature does not exist: "%s"' % key)

    def update_geometry(self, geometry, key, prefix=None):
        with self._lock:
            key = self._make_key(key, prefix)

            if key in self._features:
                # Update existing feature
                feature = pickle.loads(self._features[key])
                feature.update_geometry(geometry)
            else:
                # Otherwise, create the new feature
                feature = build_feature(geometry)

            self._write_feature(feature, key)
            return feature

    def update_properties(self, properties, key, prefix=None):
        with self._lock:
            feature = self._load_feature(key, prefix)
            feature.update_properties(properties)
            self._write_feature(feature, key, prefix)
            return feature

    def delete_properties(self, key, prefix=None):
        with self._lock:
            feature = self._load_feature(key, prefix)
            feature.properties.clear()
            feature.recalculate()
            self._write_feature(feature, key, prefix)

    def get_property(self, name, key, prefix=None):
        with self._lock:
            feature = self._load_feature(key, prefix)
            try:
                return feature.properties[name]
            except KeyError:
                raise PropertyDoesNotExist(name)

    def delete_property(self, name, key, prefix=None):
        with self._lock:
            feature = self._load_feature(key, prefix)
            try:
                del feature.properties[name]
            except KeyError:
                raise PropertyDoesNotExist(name)
            feature.recalculate()
            self._write_feature(feature, key, prefix)

    def update_property(self, name, value, key, prefix=None):
        with self._lock:
            feature = self._load_feature(key, prefix)
            feature[name] = value
            feature.recalculate()
            self._write_feature(feature, key, prefix)

    def _make_key(self, key, prefix):
        if key is None:
            assert prefix is not None
            key = '%s%d' % (prefix, self._counter)
            self._counter += 1
        elif prefix is not None:
            key = '%s%s' % (prefix, key)
        if not is_key_valid(key):
            raise InvalidKey('Invalid key: "%s"' % key)
        return key

    def _load_feature(self, key, prefix=None):
        if prefix is not None:
            key = prefix + key
        try:
            return pickle.loads(self._features[key])
        except KeyError as e:
            raise FeatureDoesNotExist(
                'Feature does not exist: "%s"' % key)

    def _write_feature(self, feature, key, prefix=None):
        if prefix is not None:
            key = prefix + key
        feature.key = key
        self._features[key] = pickle.dumps(feature)
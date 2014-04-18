# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import pickle
import threading
import re
import collections

from ..geo import build_feature
from .exception import InvalidKey, FeatureAlreadyExists, FeatureDoesNotExist


def is_key_valid(key):
    if key in ['geometry', 'properties']:
        return False
    else:
        m = re.match(r'^[a-zA-Z][a-zA-Z0-9_\-\.]+$', key)
        return m is not None


class Capability(collections.OrderedDict):
    def __init__(self, **kwargs):
        super(Capability, self).__init__(
            efficient_key_lookup=False,
            in_memory_cache=False,
            presistence=False,

            prefix_query=False,
            property_query=False,
            spatial_query=False,
            full_text_search=False,

            versioning=False,
            changeset=False,
        )
        self.update(**kwargs)


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
            # Put prefix and key together
            null = self._make_key(key, prefix)

            if key in self._features:
                raise FeatureAlreadyExists(
                    'Geometry already exists: "%s"' % key)

            # Overwrite random key generated in the feature
            feature.key = key

            # Simulate storage behaviour by pickling the feature object
            self._features[key] = pickle.dumps(feature)

            return feature

    def get_feature(self, key, prefix=None):
        key = self._make_key(key, prefix)

        with self._lock:
            try:
                return pickle.loads(self._features[key])
            except KeyError as e:
                raise FeatureDoesNotExist(
                    'Feature does not exist: "%s"' % key)

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

            # Overwrite random key generated in the feature
            feature.key = key
            self._features[key] = pickle.dumps(feature)

            return feature

    def update_properties(self, properties, key, prefix=None):
        if prefix is not None:
            key = prefix + key

        with self._lock:
            feature = pickle.loads(self._features[key])
            feature.update(properties)
            self._features[key] = pickle.dumps(feature)


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
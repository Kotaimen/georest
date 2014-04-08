# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import pickle
import threading
import re

from .exception import InvalidKey, GeometryAlreadyExists, GeometryDoesNotExist


def is_key_valid(key):
    return re.match(r'^[a-zA-Z][a-zA-Z0-9_-]+$', key) is not None


class SimpleGeoStore(object):
    """ Store features in a python dict, thread safe via locking, for test only
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._features = dict()

    def describe(self):
        return {
            'backend': 'Magic',
            'capabilities': dict(presistence=False,
                                 efficient_lookup=True,
                                 key_namepace=False,
                                 in_memory=True,
                                 distributed=False,
                                 versioning=False,
                                 changeset=False,
                                 property_query=False,
                                 spatial_query=False,
                                 full_text_search=False, )
        }

    def put_feature(self, feature, key=None, overwrite=False):
        if key is not None and not is_key_valid(key):
            raise InvalidKey('Invalid key: "%s"' % key)

        with self._lock:
            if key is None:
                key = 'feature-%d' % len(self._features)

            if not overwrite and key in self._features:
                raise GeometryAlreadyExists(
                    'Geometry already exists: "%s"' % key)

            feature.id = key
            # Simulate storage by pickling the feature object
            self._features[key] = pickle.dumps(feature)

    def get_feature(self, key):
        if not is_key_valid(key):
            raise InvalidKey(key)
        with self._lock:
            try:
                return pickle.loads(self._features[key])
            except KeyError as e:
                raise GeometryDoesNotExist(
                    'Geometry does not exist: "%s"' % key)

    def delete_feature(self, key):
        with self._lock:
            try:
                del self._features[key]
            except KeyError as e:
                raise GeometryDoesNotExist(
                    'Geometry does not exist: "%s"' % key)

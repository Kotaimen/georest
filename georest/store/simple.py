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

    def put_feature(self, feature, key=None):
        with self._lock:
            if key is None:
                key = 'feature-%d' % len(self._features)
            if not is_key_valid(key):
                raise InvalidKey(key)

            if key in self._features:
                raise GeometryAlreadyExists(key)

            # Simulate storage by pickling the feature object
            self._features[key] = pickle.dumps(feature)

    def get_feature(self, key):
        with self._lock:
            try:
                return pickle.loads(self._features[key])
            except KeyError as e:
                raise GeometryDoesNotExist(e)

    def delete_feature(self, key):
        with self._lock:
            try:
                del self._features[key]
            except KeyError as e:
                raise GeometryDoesNotExist(e)

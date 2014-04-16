# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/19/14'

import pickle
import threading
import re
import collections

from .exception import InvalidKey, GeometryAlreadyExists, GeometryDoesNotExist


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
    """ Store features in a python dict, thread safe via
    locking, designed for unittest only.
    """

    CAPABILITY = Capability(
        efficient_key_lookup=True,
        in_memory_cache=True,
    )

    def __init__(self):
        self._lock = threading.Lock()
        self._features = dict()

    def describe(self):
        return {
            'backend': 'Simple',
            'capabilities': self.CAPABILITY
        }

    def put_feature(self, feature, key=None, prefix=None):

        with self._lock:
            # Put prefix and key together
            if key is None:
                assert prefix is not None
                key = '%s%d' % (prefix, len(self._features))
            elif prefix is not None:
                key = '%s%s' % (prefix, key)

            # Check key
            if not is_key_valid(key):
                raise InvalidKey('Invalid key: "%s"' % key)

            if key in self._features:
                raise GeometryAlreadyExists(
                    'Geometry already exists: "%s"' % key)

            # Overwrite random key generated in the feature
            feature.key = key

            # Simulate storage behaviour by pickling the feature object
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

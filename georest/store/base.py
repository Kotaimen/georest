# -*- encoding: utf-8 -*-
"""
    georest.store.base
    ~~~~~~~~~~~~~~~~~~

    Storage IF
"""

__author__ = 'kotaimen'
__date__ = '4/3/14'

import re
import collections


def is_key_valid(key):
    """Check whether key is valid"""
    if key in ['geometry', 'properties']:
        return False
    else:
        m = re.match(r'^[a-zA-Z][a-zA-Z0-9_\-\.]+$', key)
        return m is not None


class Capability(collections.OrderedDict):
    """Describe storage capabilities"""

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
    NAME = None
    CAPABILITY = None

    def describe(self):
        return {
            'backend': self.NAME,
            'capabilities': self.CAPABILITY
        }

    def put_feature(self, feature, key=None, prefix=None):
        raise NotImplementedError

    def get_feature(self, key, prefix=None):
        raise NotImplementedError

    def delete_feature(self, key, prefix=None):
        raise NotImplementedError

    def update_geometry(self, geometry, key, prefix=None):
        raise NotImplementedError

    def update_properties(self, properties, key, prefix=None):
        raise NotImplementedError

    def delete_properties(self, key, prefix=None):
        raise NotImplementedError

    def get_property(self, name, key, prefix=None):
        raise NotImplementedError

    def delete_property(self, name, key, prefix=None):
        raise NotImplementedError

    def update_property(self, name, value, key, prefix=None):
        raise NotImplementedError

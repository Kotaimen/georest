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


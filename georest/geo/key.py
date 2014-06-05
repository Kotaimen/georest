# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

"""
    georest.geo.key
    ~~~~~~~~~~~~~~~
    Key of the Feature
"""

import collections


class Key(collections.namedtuple('Key', 'bucket name')):
    @staticmethod
    def make_key(name=None, bucket=None):
        if bucket is None:
            bucket = 'default'
        return Key(bucket, name)

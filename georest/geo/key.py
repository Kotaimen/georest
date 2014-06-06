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
    """Object database friendly key

    Storage is expected to generate a random unique name if name is not
    provided.
    Different bucket can be stored in different bucket/table/schema/databases.
    """

    @staticmethod
    def make_key(name=None, bucket=None):
        if bucket is None:
            bucket = 'default'
        return Key(bucket, name)

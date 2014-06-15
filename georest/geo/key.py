# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

"""
    georest.geo.key
    ~~~~~~~~~~~~~~~
    Key of the Feature
"""

import collections
import re

from .exceptions import InvalidKey


class Key(collections.namedtuple('Key', 'bucket name')):
    """ A object database friendly key

    Storage is free to map bucket to bucket/cluster/table/schema/database, and
    is expected to generate a random name if its not provided.

    """

    @classmethod
    def make_key(cls, name=None, bucket=None):

        if bucket is None:
            bucket = 'default'
        else:
            if not isinstance(bucket, str):
                raise InvalidKey('Invalid bucket: %r' % bucket)
            if not re.match(r'^(\w+\.)*\w+$', bucket):
                raise InvalidKey('Invalid bucket: %r' % bucket)

        if name is not None:
            if not isinstance(name, str):
                raise InvalidKey('Invalid name: %r' % name)
            if not re.match(r'^\w+$', name):
                raise InvalidKey('Invalid name: %r' % name)

        return Key(bucket, name)

    @classmethod
    def build_from_qualified_name(cls, qualified_name):
        assert isinstance(qualified_name, str)
        ret = qualified_name.rsplit('.', 1)
        if len(ret) != 2:
            raise InvalidKey('Not a valid qualified name: %s' % qualified_name)
        bucket, name = tuple(ret)
        return cls.make_key(name=name, bucket=bucket)

    @property
    def qualified_name(self):
        if self.name is not None:
            return '.'.join(self)
        else:
            return '%s.?' % self.bucket

    def __str__(self):
        return self.qualified_name

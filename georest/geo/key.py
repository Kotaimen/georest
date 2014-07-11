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

import six

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
            if not isinstance(bucket, six.string_types):
                raise InvalidKey('Invalid bucket: %r' % bucket)
            if not re.match(r'^[A-Za-z][A-Za-z0-9_]+$', bucket):
                raise InvalidKey('Invalid bucket: %r' % bucket)

        if name is not None:
            if not isinstance(name, six.string_types):
                raise InvalidKey('Invalid name: %r' % name)
            if not re.match(r'^([A-Za-z0-9_]+\.)*[A-Za-z0-9_]+$', name):
                raise InvalidKey('Invalid name: %r' % name)

        return Key(bucket, name)

    @classmethod
    def build_from_qualified_name(cls, qualified_name):
        assert isinstance(qualified_name, six.string_types)
        try:
            bucket, name = qualified_name.split('.', 1)
        except ValueError:
            raise InvalidKey('Not a valid qualified name: %s' % qualified_name)
        return cls.make_key(name=name, bucket=bucket)

    @property
    def qualified_name(self):
        if self.name is not None:
            return '.'.join(self)
        else:
            return '%s.?' % self.bucket

    def __str__(self):
        return self.qualified_name

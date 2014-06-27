# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/23/14'

"""
    georest.storage.buckets.dummy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    A Dummy feature bucket

"""
import uuid
import datetime

from ..bucket import FeatureBucket, Commit
from ..exceptions import FeatureNotFound, DuplicatedBucket, BucketNotFound
from .factory import FeatureBucketFactory


class DummyBucketFactory(FeatureBucketFactory):
    def __init__(self):
        self._collection = dict()

    def describe(self):

        description = {
            'support_version': False
        }

        return description

    def create(self, name, **kwargs):
        if name in self._collection:
            raise DuplicatedBucket(name)

        bucket = DummyFeatureBucket(name)
        self._collection[name] = bucket
        return bucket

    def get(self, name):
        try:
            return self._collection[name]
        except KeyError:
            raise BucketNotFound(name)

    def delete(self, name):
        try:
            del self._collection[name]
        except KeyError:
            raise BucketNotFound(name)

    def has(self, name):
        return name in self._collection


class DummyFeatureBucket(FeatureBucket):
    def __init__(self, name):
        FeatureBucket.__init__(self, name)

        self._storage = dict()

    def commit(self, name, mapper, parent=None):
        timestamp = datetime.datetime.now()
        self._storage[name] = mapper, timestamp
        commit = Commit(name=name, revision=None, parent_revision=None,
                        timestamp=timestamp)
        return commit

    def checkout(self, name, revision=None):
        try:
            mapper, timestamp = self._storage[name]
            commit = Commit(name=name, revision=None, parent_revision=None,
                            timestamp=timestamp)
        except KeyError:
            raise FeatureNotFound(name)
        return commit, mapper

    def head(self, name):
        try:
            mapper, timestamp = self._storage[name]
        except KeyError:
            raise FeatureNotFound(name)
        commit = Commit(name=name, revision=None, parent_revision=None,
                        timestamp=timestamp)
        return commit

    def status(self, name, revision=None):
        return self.head(name)

    def remove(self, name, parent=None):
        timestamp = datetime.datetime.now()
        try:
            del self._storage[name]
        except KeyError:
            raise FeatureNotFound(name)
        commit = Commit(name=name, revision=None, parent_revision=None,
                        timestamp=timestamp)
        return commit

    def make_random_name(self):
        name = uuid.uuid4().hex
        return name

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

from ..storage import FeatureStorage
from ..bucket import FeatureBucket, Commit
from ..exceptions import FeatureNotFound, DuplicatedBucket, BucketNotFound


class DummyStorage(FeatureStorage):
    def __init__(self):
        self._collection = dict()

    def create_bucket(self, name, overwrite=False, **kwargs):
        if name in self._collection:
            raise DuplicatedBucket(name)

        bucket = DummyFeatureBucket(name)
        self._collection[name] = bucket
        return bucket

    def get_bucket(self, name):
        try:
            return self._collection[name]
        except KeyError:
            raise BucketNotFound(name)

    def delete_bucket(self, name):
        try:
            del self._collection[name]
        except KeyError:
            raise BucketNotFound(name)

    def has_bucket(self, name):
        return name in self._collection


class DummyFeatureBucket(FeatureBucket):
    def __init__(self, name):
        FeatureBucket.__init__(self, name)

        self._storage = dict()

    def commit(self, name, mapper, parent=None):
        timestamp = datetime.datetime.now()
        self._storage[name] = mapper, timestamp
        commit = Commit(name=name,
                        revision=None,
                        create_at=timestamp,
                        expire_at=datetime.datetime.max)
        return commit

    def checkout(self, name, revision=None):
        try:
            mapper, timestamp = self._storage[name]
            commit = Commit(name=name,
                            revision=None,
                            create_at=timestamp,
                            expire_at=datetime.datetime.max)
        except KeyError:
            raise FeatureNotFound(name)
        return commit, mapper

    def head(self, name):
        try:
            mapper, timestamp = self._storage[name]
        except KeyError:
            raise FeatureNotFound(name)
        commit = Commit(name=name,
                        revision=None,
                        create_at=timestamp,
                        expire_at=datetime.datetime.max)
        return commit

    def status(self, name, revision=None):
        return self.head(name)

    def remove(self, name, parent=None):
        timestamp = datetime.datetime.now()
        try:
            del self._storage[name]
        except KeyError:
            raise FeatureNotFound(name)
        commit = Commit(name=name,
                        revision=None,
                        create_at=timestamp,
                        expire_at=datetime.datetime.max)
        return commit

    def make_random_name(self):
        name = uuid.uuid4().hex
        return name

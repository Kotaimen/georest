# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/23/14'

"""
    georest.storage.buckets.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Bucket Factories

"""
from ..exceptions import DuplicatedBucket, BucketNotFound
from .dummy import DummyFeatureBucket
from .postgis import PostGISConnectionPool, PostGISFeatureBucket


class FeatureBucketFactory(object):
    def create(self, name, **kwargs):
        raise NotImplementedError

    def get(self, name):
        raise NotImplementedError

    def has(self, name):
        raise NotImplementedError

    def delete(self, name):
        raise NotImplementedError


class DummyBucketFactory(FeatureBucketFactory):
    def __init__(self):
        self._collection = dict()

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


class PostGISFeatureBucketFactory(FeatureBucketFactory):
    def __init__(self, **kwargs):
        self._pool = PostGISConnectionPool(**kwargs)

    def create(self, bucket_name, srid=4326, checkfirst=False):
        if self.has(bucket_name):
            if checkfirst:
                return self.get(bucket_name)
            raise DuplicatedBucket(bucket_name)
        bucket = PostGISFeatureBucket(bucket_name, self._pool, srid=srid)
        return bucket

    def get(self, bucket_name):
        srid = self._inspect_bucket_srid(bucket_name)
        if srid is None:
            raise BucketNotFound(bucket_name)
        bucket = PostGISFeatureBucket(bucket_name, self._pool, srid)
        return bucket

    def has(self, bucket_name):
        srid = self._inspect_bucket_srid(bucket_name)
        return srid is not None

    def delete(self, bucket_name):
        if not self.has(bucket_name):
            raise BucketNotFound(bucket_name)

        conn = self._pool.connect()
        with conn.begin() as trans:
            conn.execute('''DROP SCHEMA %s CASCADE''' % bucket_name)
        return True

    def _inspect_bucket_srid(self, bucket_name):
        conn = self._pool.connect()
        with conn.begin() as trans:
            row = conn.execute(
                '''SELECT * FROM geometry_columns WHERE f_table_schema=%(name)s''',
                name=bucket_name).fetchone()
            if row:
                return row.srid
        return None

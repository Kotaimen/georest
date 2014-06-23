# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/23/14'

"""
    georest.storage.buckets.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Bucket Factories

"""
from .dummy import DummyFeatureBucket
from .postgis import PostGISConnectionPool, PostGISFeatureBucket


class FeatureBucketFactory(object):
    def __call__(self, name, **kwargs):
        raise NotImplementedError


class DummyBucketFactory(FeatureBucketFactory):
    def __call__(self, name, **kwargs):
        bucket = DummyFeatureBucket(name)
        return bucket


class PostGISFeatureBucketFactory(FeatureBucketFactory):
    def __init__(self, **kwargs):
        self._pool = PostGISConnectionPool(**kwargs)

    def __call__(self, name, **kwargs):
        srid = kwargs.get('srid', 4326)
        max_revision_num = kwargs.get('max_revision_num', 10)

        bucket = PostGISFeatureBucket(
            name, self._pool, srid=srid, max_revision_num=max_revision_num)

        return bucket

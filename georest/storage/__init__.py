# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

"""
    georest.storage
    ~~~~~~~~~~~~~~~

    A Geo Feature Storage.

    This package provides a versioned, bucket based storage system for geo
    features. The storage backend is flexible, and can be configured to use
    a large variety popular storage, including relational database and
    no-sql store.

    Current supported back-ends:
        PostgreSQL + PostGIS

    Usages:

        storage = build_feature_storage()

        try:
            bucket = storage.get_bucket(...)
        execept:
            bucket = storage.create()

        bucket = storage.create_bucket('bucket_name', **params)

        visitor = FeatureEntry(bucket)

        response = visitor.put_feature(key, feature, revision)
        key = response.key
        revision = response.revision
        parent_revision = response.parent_revision
        timestamp = response.timestamp

"""

from .storage import FeatureStorage
from .bucket import Commit, FeatureBucket, FeatureMapper
from .entry import FeatureEntry, Response
from .buckets import DummyBucketFactory, PostGISFeatureBucketFactory
from .exceptions import (
    StorageError,
    DuplicatedBucket,
    BucketNotFound,
    FeatureNotFound,
    NotHeadRevision,
    ParentRevisionNotFound,
    UnknownStoragePrototype
)



def build_feature_storage(prototype, **kwargs):
    if prototype == 'dummy':
        factory = DummyBucketFactory()
    elif prototype == 'postgis':
        factory = PostGISFeatureBucketFactory(**kwargs)
    else:
        raise UnknownStoragePrototype(prototype)

    return FeatureStorage(factory)

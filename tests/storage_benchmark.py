# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/26/14'

"""
    tests.storage_benchmark
    ~~~~~~~~~~~~~
    TODO: description

"""
import logging
import cProfile
from georest.geo import *
from georest.storage import *

logging.basicConfig(level=logging.INFO)

storage = build_feature_storage('postgis',
                                host='172.26.183.193',
                                port=6432,
                                username='postgres',
                                password=123456,
                                database='georest-test',
                                pool_size=0,
)

bucket = storage.create_bucket('benchmark', overwrite=True)

feature = Feature.build_from_geometry(
    'POINT (2 2)', properties=dict(x=2, y=2),
)

mapper = FeatureMapper(
    properties=dict(x=1, y=2),
    metadata=dict(z=3),
    wkt='POINT (2 2)',
    srid=4326,
)


def benchmark_put_feature(iteration=1000):
    entry = FeatureEntry(bucket)
    key = Key.make_key(bucket='test_bucket')

    logging.info('Start benchmark: put %d features.' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('Put %d features' % i)
        entry.put_feature(key, feature)
    logging.info('Finish benchmark.')


def benchmark_commit_feature(iteration=1000):
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('Put %d features' % i)
        name = bucket.make_random_name()
        bucket.commit(name, mapper)


def benchmark_update_feature(iteration=1000):
    entry = FeatureEntry(bucket)
    key = Key.make_key(bucket='test_bucket', name='feature.test')

    logging.info('Start benchmark: update same feature %d times.' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('Update %d features' % i)
        entry.put_feature(key, feature)
    logging.info('Finish benchmark.')


if __name__ == '__main__':
    cProfile.run('benchmark_update_feature()', sort='tottime')

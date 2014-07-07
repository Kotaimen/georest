# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/26/14'

"""
    tests.storage_benchmark
    ~~~~~~~~~~~~~
    TODO: description

"""
import gevent
import logging
import cProfile
from georest.geo import *
from georest.storage import *
#
# import gevent
# import gevent.monkey
#
# gevent.monkey.patch_all()
#
# import psycogreen.gevent

# psycogreen.gevent.patch_psycopg()

# logging.basicConfig(level=logging.INFO)

storage = build_feature_storage(
    'postgis',
    host='172.26.183.193',
    port=5432,
    username='postgres',
    password=123456,
    database='georest-test',
    pool_size=5,
    debug=True,
)

bucket = storage.get_bucket('benchmark')

entry = FeatureEntry(bucket)

feature = Feature.build_from_geometry(
    'POINT (2 2)', properties=dict(x=2, y=2),
)

mapper = FeatureMapper(
    properties=dict(x=1, y=2),
    metadata=dict(z=3),
    wkt='POINT (2 2)',
    srid=4326,
)


# =============================================================================
# Benchmark for put
# =============================================================================
def put_feature(i):
    bucket = storage.get_bucket('benchmark')
    entry = FeatureEntry(bucket)

    name = Key.make_key(bucket='test_bucket', name=str(i))
    response = entry.put_feature(name, feature)
    return response


def put_feature_simple(i):
    name = Key.make_key(bucket='test_bucket', name=str(i))
    response = entry.put_feature(name, feature)
    return response


def benchmark_put_feature(iteration=1000):
    logging.info('Start benchmark: put_feature: %d' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('put_feature: %d' % i)
        put_feature(i)
    logging.info('Finish benchmark.')


def benchmark_put_feature_simple(iteration=1000)
    logging.info('Start benchmark: put_feature_simple: %d' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('put_feature_simple: %d' % i)
        put_feature(i)
    logging.info('Finish benchmark.')


# =============================================================================
# Benchmark for get
# =============================================================================
def get_feature(i):
    bucket = storage.get_bucket('benchmark')
    entry = FeatureEntry(bucket)

    name = Key.make_key(bucket='test_bucket', name=str(i))
    response, feature = entry.get_feature(name)
    return response, feature


def get_feature_simple(i):
    name = Key.make_key(bucket='test_bucket', name=str(i))
    response, feature = entry.get_feature(name)
    return response, feature


def benchmark_get_feature(iteration=1000):
    logging.info('Start benchmark: get_feature: %d' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('get_feature: %d' % i)
        get_feature(i)
    logging.info('Finish benchmark.')


def benchmark_get_feature_simple(iteration=1000):
    logging.info('Start benchmark: get_feature: %d' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('get_feature: %d' % i)
        get_feature_simple(i)
    logging.info('Finish benchmark.')


# =============================================================================
# Benchmark for update
# =============================================================================
def benchmark_update_feature(iteration=1000):
    entry = FeatureEntry(bucket)
    key = Key.make_key(bucket='test_bucket', name='feature.test')

    logging.info('Start benchmark: update same feature %d times.' % iteration)
    for i in range(iteration):
        if i % 100 == 0:
            logging.info('Update %d features' % i)
        entry.put_feature(key, feature)
    logging.info('Finish benchmark.')


# def benchmark_async_put_feature(iteration=1000):
# entry = FeatureEntry(bucket)
#     key = Key.make_key(bucket='test_bucket')
#
#     logging.info('Start spawning %d workers' % iteration)
#     jobs = list(gevent.spawn(entry.put_feature, key, feature)
#                 for i in range(iteration))
#
#     logging.info("join begin")
#     gevent.joinall(jobs)
#     logging.info("join end")
#
#
# def benchmark_async_update_feature(iteration=1000):
#     entry = FeatureEntry(bucket)
#     key = Key.make_key(bucket='test_bucket', name='feature.test')
#
#     logging.info('Start spawning %d workers' % iteration)
#     jobs = list(gevent.spawn(entry.put_feature, key, feature)
#                 for i in range(iteration))
#
#     logging.info("join begin")
#     gevent.joinall(jobs)
#     logging.info("join end")


if __name__ == '__main__':
    cProfile.run('put_feature(1)', sort='tottime')

# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/23/14'

"""
    georest.storage.buckets.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Bucket Factories

"""

class FeatureBucketFactory(object):
    def create(self, name, **kwargs):
        raise NotImplementedError

    def get(self, name):
        raise NotImplementedError

    def has(self, name):
        raise NotImplementedError

    def delete(self, name):
        raise NotImplementedError






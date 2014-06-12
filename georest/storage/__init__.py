# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

from .storage import FeatureStorage, FeatureStorageResult


def build_feature_storage(**kwargs):
    return FeatureStorage()
